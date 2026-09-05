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
    RunManager,
    config_hash,
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
        self.assertEqual(cast(dict[str, object], config["algorithm"])["name"], "baseline")
        self.assertEqual(cast(dict[str, object], config["evaluation"])["split"], "held_out")

    def test_unknown_sections_and_keys_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            resolve_config({"unknown": {}})
        with self.assertRaises(ValueError):
            resolve_config({"training": {"unknown": 1}})

    def test_run_creation_writes_identity_before_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manager = RunManager.create(
                Path(directory), {"system": {"min_free_bytes": 1, "exploratory": True}}, command="test", seed=7
            )
            self.assertEqual(manager.state, "created")
            metadata = json.loads((manager.run_dir / "metadata.json").read_text())
            self.assertEqual(metadata["protocol_version"], EXPERIMENT_PROTOCOL_VERSION)
            self.assertEqual(metadata["seeds"]["policy"], 7)
            self.assertTrue((manager.run_dir / "resolved-config.json").exists())
            manager.set_state("running")
            self.assertEqual(manager.state, "running")

    def test_raw_records_checkpoint_summary_and_resume_survive_interruption(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manager = RunManager.create(Path(directory), {"system": {"min_free_bytes": 1, "exploratory": True}})
            manager.set_state("running")
            manager.record_step({"step": 1, "reward_components": {"total": 0.0}})
            manager.record_episode({"episode": 1, "return": 0.0, "progress": 0.0})
            checkpoint = manager.save_checkpoint("latest", {"step": 1, "policy": {"seed": 4}})
            self.assertTrue(checkpoint.exists())
            manager.write_summary({"episodes": 1, "completion_rate": 0.0})
            manager.set_state("interrupted", reason="operator stop")
            resumed = RunManager.resume(manager.run_dir)
            self.assertEqual(resumed.state, "running")
            resumed.record_step({"step": 2, "reward_components": {"total": 0.0}})
            telemetry = (manager.run_dir / "telemetry.jsonl").read_text().splitlines()
            self.assertEqual(len(telemetry), 2)
            self.assertIn("operator stop", (manager.run_dir / "metadata.json").read_text())
            self.assertTrue((manager.run_dir / "summary.json").exists())
            self.assertTrue((manager.run_dir / "report.md").exists())

    def test_official_run_rejects_dirty_tree(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch("geometry_dash_env.experiment._git_dirty", return_value=True):
                with self.assertRaisesRegex(RuntimeError, "clean git tree"):
                    RunManager.create(Path(directory))
    def test_only_interrupted_runs_can_resume(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manager = RunManager.create(Path(directory), {"system": {"min_free_bytes": 1, "exploratory": True}})
            with self.assertRaises(ValueError):
                RunManager.resume(manager.run_dir)


if __name__ == "__main__":
    unittest.main()
