"""Tests for the offline screen-state evaluator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DetectorEvaluationTests(unittest.TestCase):
    """Keep detector metrics reproducible without game assets."""

    def test_evaluator_emits_metrics_and_transition_latency(self) -> None:
        truth = [
            {
                "frame_id": "f1",
                "episode_id": "episode-1",
                "timestamp_utc": "2026-01-01T00:00:00Z",
                "state": "attempt_intro",
                "split": "held_out",
            },
            {
                "frame_id": "f2",
                "episode_id": "episode-1",
                "timestamp_utc": "2026-01-01T00:00:01Z",
                "state": "gameplay",
                "split": "held_out",
            },
        ]
        predictions = [
            {
                "frame_id": "f1",
                "episode_id": "episode-1",
                "timestamp_utc": "2026-01-01T00:00:00Z",
                "state": "attempt_intro",
            },
            {
                "frame_id": "f2",
                "episode_id": "episode-1",
                "timestamp_utc": "2026-01-01T00:00:01.125Z",
                "state": "gameplay",
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            truth_path = directory_path / "truth.jsonl"
            prediction_path = directory_path / "predictions.jsonl"
            truth_path.write_text(
                "".join(json.dumps(record) + "\n" for record in truth),
                encoding="utf-8",
            )
            prediction_path.write_text(
                "".join(json.dumps(record) + "\n" for record in predictions),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "evaluate_detector.py"),
                    "--ground-truth",
                    str(truth_path),
                    "--predictions",
                    str(prediction_path),
                    "--split",
                    "held_out",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        metrics = json.loads(result.stdout)
        self.assertEqual(metrics["sample_count"], 2)
        self.assertEqual(metrics["accuracy"], 1.0)
        self.assertEqual(metrics["transition_latency_ms"]["matched_count"], 1)
        self.assertAlmostEqual(metrics["transition_latency_ms"]["mean"], 125.0)

    def test_evaluator_rejects_missing_predictions(self) -> None:
        record = {
            "frame_id": "f1",
            "episode_id": "episode-1",
            "timestamp_utc": "2026-01-01T00:00:00Z",
            "state": "gameplay",
            "split": "development",
        }
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            truth_path = directory_path / "truth.jsonl"
            prediction_path = directory_path / "predictions.jsonl"
            truth_path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            prediction_path.write_text(
                json.dumps({**record, "frame_id": "other"}) + "\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "evaluate_detector.py"),
                    "--ground-truth",
                    str(truth_path),
                    "--predictions",
                    str(prediction_path),
                    "--split",
                    "development",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("missing frame IDs", result.stderr)


if __name__ == "__main__":
    unittest.main()
