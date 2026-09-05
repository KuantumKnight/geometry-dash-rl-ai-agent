"""Reproducible experiment configuration and artifact management."""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import uuid
from collections import deque
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Literal, cast

EXPERIMENT_PROTOCOL_VERSION = "experiment-protocol-v1"
RUN_METADATA_VERSION = "run-metadata-v1"
RunState = Literal[
    "created", "running", "interrupted", "failed", "completed", "evaluated"
]

_CONFIG_KEYS: dict[str, set[str]] = {
    "environment": {"observation_size", "frame_skip", "frame_stack", "max_steps"},
    "observation": {"mode", "crop", "size"},
    "reward": {"version"},
    "algorithm": {"name"},
    "training": {"budget_steps", "budget_seconds", "seeds"},
    "evaluation": {"episodes", "seeds", "split"},
    "recording": {
        "telemetry_interval",
        "save_frames",
        "checkpoint_retention",
        "artifact_retention",
    },
    "system": {"min_free_bytes", "exploratory"},
}

DEFAULT_CONFIG: dict[str, dict[str, object]] = {
    "environment": {
        "observation_size": [160, 90],
        "frame_skip": 4,
        "frame_stack": 1,
        "max_steps": 900,
    },
    "observation": {"mode": "rgb", "crop": None, "size": [160, 90]},
    "reward": {"version": "reward-sparse-terminal-v1"},
    "algorithm": {"name": "baseline"},
    "training": {"budget_steps": 0, "budget_seconds": 0, "seeds": [42]},
    "evaluation": {"episodes": 10, "seeds": [42], "split": "held_out"},
    "recording": {
        "telemetry_interval": 1,
        "save_frames": False,
        "checkpoint_retention": {"periodic": 3},
        "artifact_retention": {"diagnostics": 10},
    },
    "system": {"min_free_bytes": 100_000_000, "exploratory": False},
}


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()


def config_hash(config: Mapping[str, object]) -> str:
    """Return the stable SHA-256 identity of a resolved config."""

    return hashlib.sha256(_canonical_json(config)).hexdigest()


def validate_config(config: Mapping[str, object]) -> None:
    """Reject unknown top-level sections and nested settings."""

    expected = set(_CONFIG_KEYS)
    unknown_sections = set(config) - expected
    missing_sections = expected - set(config)
    if unknown_sections:
        raise ValueError(f"unknown config sections: {sorted(unknown_sections)}")
    if missing_sections:
        raise ValueError(f"missing config sections: {sorted(missing_sections)}")
    for section, allowed in _CONFIG_KEYS.items():
        value = config[section]
        if not isinstance(value, Mapping):
            raise ValueError(f"config section {section!r} must be an object")
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"unknown keys in {section}: {sorted(unknown)}")


def _deep_merge(
    base: Mapping[str, object], updates: Mapping[str, object]
) -> dict[str, object]:
    merged: dict[str, object] = dict(base)
    for key, value in updates.items():
        original = merged.get(key)
        if isinstance(original, Mapping) and isinstance(value, Mapping):
            merged[key] = _deep_merge(original, value)
        else:
            merged[key] = value
    return merged


def resolve_config(overrides: Mapping[str, object] | None = None) -> dict[str, object]:
    """Resolve defaults and overrides, then validate the complete config."""

    resolved = _deep_merge(DEFAULT_CONFIG, overrides or {})
    validate_config(resolved)
    return resolved


def load_config(path: Path) -> dict[str, object]:
    """Load and strictly validate a JSON experiment config."""

    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("config root must be an object")
    return resolve_config(value)


def _atomic_write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_bytes(_canonical_json(value) + b"\n")
    os.replace(temporary, path)


def _git_value(args: list[str], fallback: str) -> str:
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return fallback
    return result.stdout.strip() or fallback


def _git_dirty() -> bool:
    return bool(_git_value(["git", "status", "--porcelain"], "unavailable"))


def _package_versions() -> dict[str, str]:
    """Return versions for packages that define the run execution surface."""

    packages = ("geometry-dash-rl", "gymnasium", "numpy", "pillow")
    versions: dict[str, str] = {}
    for package in packages:
        try:
            versions[package] = version(package)
        except PackageNotFoundError:
            versions[package] = "unavailable"
    return versions


@dataclass
class ConsecutiveFailureBudget:
    """Stop a run after a configured number of consecutive failures."""

    limit: int = 3
    consecutive: int = 0

    def __post_init__(self) -> None:
        if self.limit <= 0:
            raise ValueError("failure limit must be positive")

    def record_success(self) -> None:
        """Reset the consecutive failure count after a successful operation."""

        self.consecutive = 0

    def record_failure(self) -> bool:
        """Record one failure and return whether the budget is exhausted."""

        self.consecutive += 1
        return self.consecutive >= self.limit


FailureKind = Literal["reset", "capture", "detector", "focus", "disk"]
_FAILURE_KINDS = frozenset({"reset", "capture", "detector", "focus", "disk"})


@dataclass
class RunFailureMonitor:
    """Classify operational failures and stop after consecutive failures."""

    limit: int = 3
    _budget: ConsecutiveFailureBudget | None = None
    last_kind: FailureKind | None = None
    last_error: str | None = None

    def __post_init__(self) -> None:
        self._budget = ConsecutiveFailureBudget(self.limit)

    @property
    def budget(self) -> ConsecutiveFailureBudget:
        """Return the initialized consecutive-failure budget."""

        assert self._budget is not None
        return self._budget

    def record_success(self) -> None:
        """Reset the failure budget after any successful operation."""

        self.budget.record_success()

    def record_failure(self, kind: FailureKind, error: str) -> bool:
        """Record a supported operational failure and return whether to stop."""

        if kind not in _FAILURE_KINDS:
            raise ValueError(f"unsupported failure kind: {kind}")
        if not error:
            raise ValueError("failure error must not be empty")
        self.last_kind = kind
        self.last_error = error
        return self.budget.record_failure()


@dataclass
class DiagnosticRingBuffer:
    """Bound recent diagnostic records and persist them only on an event."""

    capacity: int = 32

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise ValueError("diagnostic capacity must be positive")
        self._records: deque[dict[str, object]] = deque(maxlen=self.capacity)

    def add(self, record: Mapping[str, object]) -> None:
        """Keep one recent diagnostic record."""

        self._records.append(dict(record))

    def records(self) -> list[dict[str, object]]:
        """Return a snapshot of the bounded records."""

        return list(self._records)

    def save_event(self, path: Path) -> None:
        """Persist the current snapshot for a milestone or failure event."""

        _atomic_write_json(path, self.records())


def heartbeat_line(
    *,
    step: int,
    episode: int,
    progress: float | None,
    speed: float,
    eta: float | None,
    last_error: str | None,
) -> str:
    """Format one compact operational status line."""

    progress_text = "n/a" if progress is None else f"{progress:.3f}"
    eta_text = "n/a" if eta is None else f"{eta:.1f}s"
    error_text = "none" if last_error is None else last_error
    return (
        f"step={step} episode={episode} progress={progress_text} "
        f"speed={speed:.2f}/s eta={eta_text} last_error={error_text}"
    )


def detector_telemetry(
    *,
    state: str,
    confidence: float | None,
    errors: Sequence[str] = (),
    missed_deadline: bool = False,
    deadline_lateness_seconds: float | None = None,
) -> dict[str, object]:
    """Build the stable per-step detector and deadline telemetry fields."""

    if not state:
        raise ValueError("detector state must not be empty")
    if confidence is not None and (
        not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0
    ):
        raise ValueError("detector confidence must be between 0 and 1")
    if not isinstance(missed_deadline, bool):
        raise ValueError("missed_deadline must be a boolean")
    if deadline_lateness_seconds is not None and (
        not math.isfinite(deadline_lateness_seconds) or deadline_lateness_seconds < 0.0
    ):
        raise ValueError("deadline lateness must be finite and non-negative")
    normalized_errors = list(errors)
    if any(not isinstance(error, str) or not error for error in normalized_errors):
        raise ValueError("detector errors must be non-empty strings")
    return {
        "detector_state": state,
        "detector_confidence": confidence,
        "detector_errors": normalized_errors,
        "missed_deadline": missed_deadline,
        "deadline_lateness_seconds": deadline_lateness_seconds,
    }


@dataclass
class RunManager:
    """Own a run directory and write recoverable machine-readable artifacts."""

    run_dir: Path
    config: dict[str, object]
    metadata: dict[str, object]

    @classmethod
    def create(
        cls,
        output_root: Path,
        config: Mapping[str, object] | None = None,
        *,
        command: str = "",
        seed: int = 42,
    ) -> RunManager:
        """Create identity, config, and metadata before environment interaction."""

        resolved = resolve_config(config)
        system_config = cast(Mapping[str, object], resolved["system"])
        if _git_dirty() and not bool(system_config["exploratory"]):
            raise RuntimeError("official comparison runs require a clean git tree")
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        run_id = f"{timestamp}-{uuid.uuid4().hex[:8]}"
        run_dir = output_root / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        metadata: dict[str, object] = {
            "metadata_version": RUN_METADATA_VERSION,
            "protocol_version": EXPERIMENT_PROTOCOL_VERSION,
            "run_id": run_id,
            "state": "created",
            "created_utc": _utc_now(),
            "start_utc": None,
            "end_utc": None,
            "command": command,
            "git_sha": _git_value(["git", "rev-parse", "HEAD"], "unavailable"),
            "dirty_tree": _git_dirty(),
            "python": sys.version,
            "package_versions": _package_versions(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "config_hash": config_hash(resolved),
            "config": resolved,
            "contract_versions": {
                "environment": "phase1-contract-v1",
                "observation": "observation-rgb-hwc-v1",
                "action": "action-v1",
                "reward": str(
                    cast(Mapping[str, object], resolved["reward"])["version"]
                ),
            },
            "seeds": {"policy": seed, "library": seed},
            "stop_reason": None,
        }
        manager = cls(run_dir, resolved, metadata)
        manager._write_config()
        manager._write_metadata()
        return manager

    @classmethod
    def resume(cls, run_dir: Path) -> RunManager:
        """Reopen an interrupted run without replacing prior metrics."""

        with (run_dir / "metadata.json").open(encoding="utf-8") as handle:
            metadata = json.load(handle)
        if not isinstance(metadata, dict) or metadata.get("state") != "interrupted":
            raise ValueError("only interrupted runs can be resumed")
        config_value = metadata.get("config")
        if not isinstance(config_value, dict):
            raise ValueError("run metadata has no resolved config")
        config = resolve_config(config_value)
        manager = cls(run_dir, config, metadata)
        manager.set_state("running")
        return manager

    @property
    def run_id(self) -> str:
        """Return the stable run identity."""

        return str(self.metadata["run_id"])

    @property
    def state(self) -> RunState:
        """Return the current lifecycle state."""

        return self.metadata["state"]  # type: ignore[return-value]

    def _write_config(self) -> None:
        _atomic_write_json(self.run_dir / "resolved-config.json", self.config)

    def _write_metadata(self) -> None:
        _atomic_write_json(self.run_dir / "metadata.json", self.metadata)

    def set_state(self, state: RunState, *, reason: str | None = None) -> None:
        """Update lifecycle state atomically and record a stop reason if given."""

        self.metadata["state"] = state
        if state == "running" and self.metadata["start_utc"] is None:
            self.metadata["start_utc"] = _utc_now()
        if state in {"interrupted", "failed", "completed", "evaluated"}:
            self.metadata["end_utc"] = _utc_now()
            self.metadata["stop_reason"] = reason
        self._write_metadata()

    @contextmanager
    def interruption_guard(
        self, checkpoint: Callable[[], Mapping[str, object]] | None = None
    ) -> Iterator[RunManager]:
        """Persist recovery state when an operator interrupts a run."""

        try:
            yield self
        except KeyboardInterrupt:
            if checkpoint is not None:
                self.save_checkpoint("latest", checkpoint())
            self.set_state("interrupted", reason="operator interrupt")
            raise

    def ensure_disk_space(self, minimum_bytes: int | None = None) -> None:
        """Fail before writing artifacts when the output volume is too full."""

        required = minimum_bytes
        if required is None:
            system_config = cast(Mapping[str, object], self.config["system"])
            required = int(cast(int, system_config["min_free_bytes"]))
        if shutil.disk_usage(self.run_dir).free < required:
            raise OSError(f"insufficient free disk space for run artifacts: {required}")

    def retain_checkpoints(self) -> None:
        """Keep named checkpoints and the newest configured periodic files."""

        recording = cast(Mapping[str, object], self.config["recording"])
        policy = cast(Mapping[str, object], recording["checkpoint_retention"])
        periodic_limit = int(cast(int, policy.get("periodic", 3)))
        if periodic_limit < 0:
            raise ValueError("periodic checkpoint retention must be non-negative")
        directory = self.run_dir / "checkpoints"
        periodic = sorted(
            directory.glob("periodic-*.json"),
            key=lambda path: path.stat().st_mtime_ns,
            reverse=True,
        )
        for path in periodic[periodic_limit:]:
            path.unlink()

    def retain_artifacts(self) -> None:
        """Keep only the newest diagnostic snapshots under the run policy."""

        recording = cast(Mapping[str, object], self.config["recording"])
        policy = cast(Mapping[str, object], recording["artifact_retention"])
        diagnostic_limit = int(cast(int, policy.get("diagnostics", 10)))
        if diagnostic_limit < 0:
            raise ValueError("diagnostic retention must be non-negative")
        diagnostics = sorted(
            self.run_dir.glob("diagnostics-*.json"),
            key=lambda path: path.stat().st_mtime_ns,
            reverse=True,
        )
        for path in diagnostics[diagnostic_limit:]:
            path.unlink()

    def save_diagnostics(self, buffer: DiagnosticRingBuffer, event: str) -> Path:
        """Save a bounded diagnostic snapshot and enforce retention."""

        if not event or Path(event).name != event:
            raise ValueError("diagnostic event must be a simple filename")
        self.ensure_disk_space()
        path = self.run_dir / f"diagnostics-{event}.json"
        buffer.save_event(path)
        self.retain_artifacts()
        return path

    def record_step(self, row: Mapping[str, object]) -> None:
        """Append one telemetry row without replacing raw history."""

        self._append_jsonl("telemetry.jsonl", row)

    def record_episode(self, row: Mapping[str, object]) -> None:
        """Append one episode result row."""

        self._append_jsonl("episodes.jsonl", row)

    def _append_jsonl(self, name: str, row: Mapping[str, object]) -> None:
        self.ensure_disk_space()
        with (self.run_dir / name).open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(dict(row), sort_keys=True, ensure_ascii=True) + "\n"
            )

    def save_checkpoint(self, name: str, payload: Mapping[str, object]) -> Path:
        """Atomically save and immediately reload a checkpoint payload."""

        if not name or Path(name).name != name:
            raise ValueError("checkpoint name must be a simple filename")
        checkpoint = {"checkpoint_version": "checkpoint-v1", **dict(payload)}
        path = self.run_dir / "checkpoints" / f"{name}.json"
        self.ensure_disk_space()
        _atomic_write_json(path, checkpoint)
        with path.open(encoding="utf-8") as handle:
            loaded = json.load(handle)
        if loaded != checkpoint:
            raise OSError("checkpoint verification failed after save")
        self.retain_checkpoints()
        return path

    def write_summary(self, metrics: Mapping[str, object]) -> None:
        """Write machine-readable and human-readable summaries."""

        summary = {
            "protocol_version": EXPERIMENT_PROTOCOL_VERSION,
            "run_id": self.run_id,
            "config_hash": self.metadata["config_hash"],
            "contract_versions": self.metadata["contract_versions"],
            "metrics": dict(metrics),
        }
        _atomic_write_json(self.run_dir / "summary.json", summary)
        lines = [
            f"# Run {self.run_id}",
            "",
            f"Protocol: `{EXPERIMENT_PROTOCOL_VERSION}`",
            "",
        ]
        for key, value in metrics.items():
            lines.append(f"- {key}: {value}")
        (self.run_dir / "report.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
