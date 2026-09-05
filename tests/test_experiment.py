"""Tests for reproducible experiment configuration and artifacts."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import cast
from unittest.mock import patch

from geometry_dash_env.experiment import (
    EXPERIMENT_PROTOCOL_VERSION,
    ConsecutiveFailureBudget,
    DiagnosticRingBuffer,
    RunFailureMonitor,
    RunManager,
    config_hash,
    detector_telemetry,
    heartbeat_line,
    load_config,
    resolve_config,
)


class ExperimentInfrastructureTests(unittest.TestCase):
    def test_defaults_resolve_and_hash_is_stable(self) -> None:
        first = resolve_config({"training": {"budget_steps": 100}})
        second = resolve_config({"training": {"budget_steps": 100}})
        self.assertEqual(config_hash(first), config_hash(second))
        training = cast(dict[str, object], first["training"])
        reward = cast(dict[str, object], first["reward"])
        self.assertEqual(training["budget_steps"], 100)
        self.assertEqual(reward["version"], "reward-sparse-terminal-v1")

    def test_committed_baseline_config_is_loadable(self) -> None:
        config = load_config(Path(__file__).parents[1] / "configs" / "baseline.json")
        self.assertEqual(
            cast(dict[str, object], config["algorithm"])["name"], "baseline"
        )
        self.assertEqual(
            cast(dict[str, object], config["evaluation"])["split"], "held_out"
        )

    def test_unknown_sections_and_keys_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            resolve_config({"unknown": {}})
        with self.assertRaises(ValueError):
            resolve_config({"training": {"unknown": 1}})

    def test_run_creation_writes_identity_before_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manager = RunManager.create(
                Path(directory),
                {"system": {"min_free_bytes": 1, "exploratory": True}},
                command="test",
                seed=7,
            )
            self.assertEqual(manager.state, "created")
            metadata = json.loads((manager.run_dir / "metadata.json").read_text())
            self.assertEqual(metadata["protocol_version"], EXPERIMENT_PROTOCOL_VERSION)
            self.assertEqual(metadata["seeds"]["policy"], 7)
            self.assertTrue((manager.run_dir / "resolved-config.json").exists())
            manager.set_state("running")
            self.assertEqual(manager.state, "running")

    def test_raw_records_checkpoint_summary_and_resume_survive_interruption(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manager = RunManager.create(
                Path(directory), {"system": {"min_free_bytes": 1, "exploratory": True}}
            )
            manager.set_state("running")
            manager.record_step({"step": 1, "reward_components": {"total": 0.0}})
            manager.record_episode({"episode": 1, "return": 0.0, "progress": 0.0})
            checkpoint = manager.save_checkpoint(
                "latest", {"step": 1, "policy": {"seed": 4}}
            )
            self.assertTrue(checkpoint.exists())
            manager.write_summary({"episodes": 1, "completion_rate": 0.0})
            manager.set_state("interrupted", reason="operator stop")
            resumed = RunManager.resume(manager.run_dir)
            self.assertEqual(resumed.state, "running")
            resumed.record_step({"step": 2, "reward_components": {"total": 0.0}})
            telemetry = (manager.run_dir / "telemetry.jsonl").read_text().splitlines()
            self.assertEqual(len(telemetry), 2)
            self.assertIn(
                "operator stop", (manager.run_dir / "metadata.json").read_text()
            )
            self.assertTrue((manager.run_dir / "summary.json").exists())
            self.assertTrue((manager.run_dir / "report.md").exists())

    def test_official_run_rejects_dirty_tree(self) -> None:
        with (
            tempfile.TemporaryDirectory() as directory,
            patch("geometry_dash_env.experiment._git_dirty", return_value=True),
            self.assertRaisesRegex(RuntimeError, "clean git tree"),
        ):
            RunManager.create(Path(directory))

    def test_failure_budget_resets_and_exhausts(self) -> None:
        budget = ConsecutiveFailureBudget(limit=2)
        self.assertFalse(budget.record_failure())
        self.assertTrue(budget.record_failure())
        budget.record_success()
        self.assertEqual(budget.consecutive, 0)

    def test_diagnostic_ring_buffer_is_bounded_and_event_saved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            buffer = DiagnosticRingBuffer(capacity=2)
            buffer.add({"step": 1})
            buffer.add({"step": 2})
            buffer.add({"step": 3})
            self.assertEqual(buffer.records(), [{"step": 2}, {"step": 3}])
            path = Path(directory) / "diagnostics.json"
            buffer.save_event(path)
            self.assertEqual(json.loads(path.read_text()), buffer.records())

    def test_heartbeat_contains_operational_fields(self) -> None:
        line = heartbeat_line(
            step=4, episode=2, progress=0.5, speed=1.25, eta=8.0, last_error=None
        )
        self.assertIn("step=4", line)
        self.assertIn("episode=2", line)
        self.assertIn("progress=0.500", line)
        self.assertIn("speed=1.25/s", line)
        self.assertIn("eta=8.0s", line)

    def test_detector_telemetry_validates_and_normalizes_fields(self) -> None:
        telemetry = detector_telemetry(
            state="gameplay",
            confidence=0.8,
            errors=("late-frame",),
            missed_deadline=True,
            deadline_lateness_seconds=0.012,
        )
        self.assertEqual(telemetry["detector_errors"], ["late-frame"])
        self.assertTrue(telemetry["missed_deadline"])
        with self.assertRaises(ValueError):
            detector_telemetry(state="gameplay", confidence=1.1)
        with self.assertRaises(ValueError):
            detector_telemetry(state="gameplay", confidence=0.5, errors=("",))

    def test_failure_monitor_categorizes_supported_failures(self) -> None:
        monitor = RunFailureMonitor(limit=2)
        self.assertFalse(monitor.record_failure("detector", "low confidence"))
        self.assertTrue(monitor.record_failure("capture", "timeout"))
        self.assertEqual(monitor.last_kind, "capture")
        monitor.record_success()
        self.assertEqual(monitor.budget.consecutive, 0)
        with self.assertRaises(ValueError):
            monitor.record_failure("other", "unsupported")  # type: ignore[arg-type]

    def test_retention_keeps_named_checkpoints_and_recent_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manager = RunManager.create(
                Path(directory),
                {
                    "system": {"min_free_bytes": 1, "exploratory": True},
                    "recording": {
                        "checkpoint_retention": {"periodic": 3},
                        "artifact_retention": {"diagnostics": 2},
                    },
                },
            )
            for name in (
                "best",
                "latest",
                "final",
                "periodic-001",
                "periodic-002",
                "periodic-003",
                "periodic-004",
            ):
                manager.save_checkpoint(name, {"step": 1})
            checkpoints = list((manager.run_dir / "checkpoints").glob("*.json"))
            self.assertEqual(len(checkpoints), 6)
            buffer = DiagnosticRingBuffer(capacity=1)
            for event in ("one", "two", "three"):
                manager.save_diagnostics(buffer, event)
            self.assertEqual(len(list(manager.run_dir.glob("diagnostics-*.json"))), 2)

    def test_interruption_guard_saves_latest_checkpoint_and_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manager = RunManager.create(
                Path(directory), {"system": {"min_free_bytes": 1, "exploratory": True}}
            )
            manager.set_state("running")
            with (
                self.assertRaises(KeyboardInterrupt),
                manager.interruption_guard(lambda: {"step": 7}),
            ):
                raise KeyboardInterrupt
            self.assertEqual(manager.state, "interrupted")
            self.assertTrue((manager.run_dir / "checkpoints" / "latest.json").exists())
            self.assertIn(
                "operator interrupt", (manager.run_dir / "metadata.json").read_text()
            )

    def test_only_interrupted_runs_can_resume(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manager = RunManager.create(
                Path(directory), {"system": {"min_free_bytes": 1, "exploratory": True}}
            )
            with self.assertRaises(ValueError):
                RunManager.resume(manager.run_dir)


if __name__ == "__main__":
    unittest.main()
