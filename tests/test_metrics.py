"""Tests for rolling and uncertainty metrics."""

from __future__ import annotations

import unittest
from typing import cast

from geometry_dash_env.metrics import (
    RollingMetrics,
    bootstrap_interval,
    summarize_episodes,
)


class MetricsTests(unittest.TestCase):
    def test_rolling_snapshot_keeps_raw_values_and_updates(self) -> None:
        metrics = RollingMetrics()
        metrics.update(episode_return=1, progress=0.25)
        metrics.update(episode_return=-1, progress=0.75)
        snapshot = metrics.snapshot()
        self.assertEqual(snapshot["episodes"], 2)
        self.assertEqual(snapshot["mean_return"], 0.0)
        self.assertEqual(metrics.returns, [1.0, -1.0])

    def test_bootstrap_interval_is_seeded_and_bounded(self) -> None:
        values = [0.1, 0.2, 0.3, 0.4]
        first = bootstrap_interval(values, seed=4, samples=100)
        second = bootstrap_interval(values, seed=4, samples=100)
        self.assertEqual(first, second)
        self.assertGreaterEqual(first[0], min(values))
        self.assertLessEqual(first[1], max(values))

    def test_episode_summary_contains_primary_secondary_metrics(self) -> None:
        summary = summarize_episodes(
            [
                {"return": 1, "length": 10, "progress": 1.0, "outcome": "completion"},
                {"return": -0.5, "length": 5, "progress": 0.5, "outcome": "death"},
                {"return": 0, "length": 8, "progress": None, "outcome": "truncation"},
            ],
            seed=1,
        )
        self.assertAlmostEqual(cast(float, summary["completion_rate"]), 1 / 3)
        self.assertEqual(summary["deaths"], 1)
        self.assertEqual(summary["truncations"], 1)
        self.assertEqual(summary["environment_steps"], 23.0)
        self.assertIsNotNone(summary["progress_mean_ci95"])

    def test_invalid_metrics_are_rejected(self) -> None:
        metrics = RollingMetrics()
        with self.assertRaises(ValueError):
            metrics.update(episode_return=float("nan"))
        with self.assertRaises(ValueError):
            bootstrap_interval([], samples=10)
        with self.assertRaises(ValueError):
            summarize_episodes([])


if __name__ == "__main__":
    unittest.main()
