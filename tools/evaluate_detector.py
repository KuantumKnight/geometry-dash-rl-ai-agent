"""Evaluate screen-state predictions against versioned JSONL annotations."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

STATES = (
    "disconnected",
    "main_menu",
    "level_info",
    "attempt_intro",
    "gameplay",
    "death_animation",
    "results",
    "level_complete",
    "resetting",
    "error",
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read non-empty JSON objects from a JSONL file."""

    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from error
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            records.append(value)
    if not records:
        raise ValueError(f"{path}: no JSONL records found")
    return records


def require_string(record: dict[str, Any], field: str, index: int) -> str:
    """Read one required non-empty string field."""

    value = record.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"record {index}: {field} must be a non-empty string")
    return value


def parse_timestamp(record: dict[str, Any], index: int) -> datetime:
    """Read an ISO-8601 timestamp and normalize it to local UTC."""

    raw = require_string(record, "timestamp_utc", index)
    try:
        timestamp = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"record {index}: timestamp_utc is not ISO-8601") from error
    if timestamp.tzinfo is None:
        raise ValueError(f"record {index}: timestamp_utc must include a timezone")
    return timestamp.astimezone()


def validate_records(
    records: list[dict[str, Any]],
    *,
    label: str,
) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    """Validate IDs/states and return indexed records plus episode groups."""

    indexed: dict[str, dict[str, Any]] = {}
    episodes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, record in enumerate(records, start=1):
        frame_id = require_string(record, "frame_id", index)
        episode_id = require_string(record, "episode_id", index)
        state = require_string(record, "state", index)
        if state not in STATES:
            raise ValueError(f"{label} record {index}: unknown state {state!r}")
        parse_timestamp(record, index)
        if frame_id in indexed:
            raise ValueError(f"{label} record {index}: duplicate frame_id {frame_id!r}")
        indexed[frame_id] = record
        episodes[episode_id].append(record)
    for episode_records in episodes.values():
        episode_records.sort(key=lambda record: parse_timestamp(record, 0))
    return indexed, episodes


def select_split(
    records: list[dict[str, Any]],
    split: str,
) -> list[dict[str, Any]]:
    """Select records by the ground-truth split field."""

    if split == "all":
        return records
    selected = [record for record in records if record.get("split") == split]
    if not selected:
        raise ValueError(f"ground truth contains no records for split {split!r}")
    return selected


def transition_latencies(
    ground_truth_episodes: dict[str, list[dict[str, Any]]],
    prediction_episodes: dict[str, list[dict[str, Any]]],
) -> tuple[list[float], int]:
    """Measure prediction latency for each observed ground-truth transition."""

    latencies_ms: list[float] = []
    transition_count = 0
    for episode_id, truth in ground_truth_episodes.items():
        predictions = prediction_episodes.get(episode_id, [])
        for previous, current in zip(truth, truth[1:]):
            previous_state = previous["state"]
            current_state = current["state"]
            if previous_state == current_state:
                continue
            transition_count += 1
            boundary = parse_timestamp(current, 0)
            matches = [
                prediction
                for prediction in predictions
                if prediction["state"] == current_state
                and parse_timestamp(prediction, 0) >= boundary
            ]
            if matches:
                latency = parse_timestamp(matches[0], 0) - boundary
                latencies_ms.append(latency.total_seconds() * 1000.0)
    return latencies_ms, transition_count


def evaluate(
    ground_truth: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    *,
    split: str,
) -> dict[str, Any]:
    """Compute confusion, per-state metrics, and transition latency."""

    truth_index, truth_episodes = validate_records(ground_truth, label="ground truth")
    prediction_index, prediction_episodes = validate_records(
        predictions,
        label="prediction",
    )
    selected_truth = select_split(ground_truth, split)
    selected_ids = {record["frame_id"] for record in selected_truth}
    missing_predictions = selected_ids - prediction_index.keys()
    extra_predictions = prediction_index.keys() - selected_ids
    if missing_predictions:
        raise ValueError(
            "predictions are missing frame IDs: "
            + ", ".join(sorted(missing_predictions))
        )
    if extra_predictions:
        raise ValueError(
            "predictions contain frame IDs outside the selected ground truth: "
            + ", ".join(sorted(extra_predictions))
        )
    matrix = {
        truth_state: {predicted: 0 for predicted in STATES}
        for truth_state in STATES
    }
    for truth_record in selected_truth:
        truth_state = truth_record["state"]
        predicted_state = prediction_index[truth_record["frame_id"]]["state"]
        matrix[truth_state][predicted_state] += 1

    per_state: dict[str, dict[str, float | int]] = {}
    total = len(selected_truth)
    correct = sum(matrix[state][state] for state in STATES)
    for state in STATES:
        true_positive = matrix[state][state]
        false_positive = sum(
            matrix[other][state] for other in STATES if other != state
        )
        false_negative = sum(
            matrix[state][other] for other in STATES if other != state
        )
        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive
            else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else 0.0
        )
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
        per_state[state] = {
            "support": true_positive + false_negative,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    selected_episode_ids = {record["episode_id"] for record in selected_truth}
    selected_truth_episodes = {
        episode_id: records
        for episode_id, records in truth_episodes.items()
        if episode_id in selected_episode_ids
    }
    selected_prediction_episodes = {
        episode_id: records
        for episode_id, records in prediction_episodes.items()
        if episode_id in selected_episode_ids
    }
    latencies, transition_count = transition_latencies(
        selected_truth_episodes,
        selected_prediction_episodes,
    )
    return {
        "evaluation_version": "detector-evaluation-v1",
        "split": split,
        "sample_count": total,
        "episode_count": len(selected_episode_ids),
        "accuracy": correct / total,
        "confusion_matrix": matrix,
        "per_state": per_state,
        "transition_latency_ms": {
            "matched_count": len(latencies),
            "missing_count": transition_count - len(latencies),
            "mean": statistics.mean(latencies) if latencies else None,
            "median": statistics.median(latencies) if latencies else None,
            "min": min(latencies) if latencies else None,
            "max": max(latencies) if latencies else None,
        },
    }


def parse_args() -> argparse.Namespace:
    """Parse offline evaluator arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument(
        "--split",
        choices=("all", "development", "held_out"),
        default="all",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    """Run the evaluator and write JSON metrics."""

    args = parse_args()
    try:
        metrics = evaluate(
            read_jsonl(args.ground_truth),
            read_jsonl(args.predictions),
            split=args.split,
        )
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    payload = json.dumps(metrics, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
