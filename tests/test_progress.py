"""Tests for versioned progress tracking behavior."""

from __future__ import annotations

import unittest

from geometry_dash_env.progress import ProgressTracker


class ProgressTrackerTests(unittest.TestCase):
    """Protect progress invariants before reward integration."""

    def test_first_measurement_has_no_delta(self) -> None:
        tracker = ProgressTracker()

        update = tracker.update(0.2)

        self.assertEqual(update.progress_delta, 0.0)
        self.assertEqual(update.filtered_progress, 0.2)

    def test_forward_progress_is_counted_once(self) -> None:
        tracker = ProgressTracker(jitter_tolerance=0.01)

        tracker.update(0.2)
        repeated = tracker.update(0.205)
        advanced = tracker.update(0.25)

        self.assertEqual(repeated.progress_delta, 0.0)
        self.assertAlmostEqual(advanced.progress_delta, 0.05)

    def test_jitter_and_backward_anomalies_do_not_create_reward(self) -> None:
        tracker = ProgressTracker(jitter_tolerance=0.01)
        tracker.update(0.5)

        jitter = tracker.update(0.495)
        backward = tracker.update(0.3)

        self.assertFalse(jitter.backward_anomaly)
        self.assertTrue(backward.backward_anomaly)
        self.assertEqual(backward.progress_delta, 0.0)
        self.assertEqual(tracker.backward_anomaly_count, 1)

    def test_impossible_forward_jump_is_clamped_and_counted(self) -> None:
        tracker = ProgressTracker(max_forward_delta=0.1)
        tracker.update(0.1)

        update = tracker.update(0.8)

        self.assertTrue(update.clamped)
        assert update.filtered_progress is not None
        self.assertAlmostEqual(update.filtered_progress, 0.2)
        self.assertAlmostEqual(update.progress_delta, 0.1)
        self.assertEqual(tracker.clamped_count, 1)

    def test_missing_or_invalid_measurements_are_explicit(self) -> None:
        tracker = ProgressTracker()
        tracker.update(0.3)

        for value in (None, float("nan"), -0.1, 1.1):
            with self.subTest(value=value):
                update = tracker.update(value)
                self.assertTrue(update.missing)
                self.assertEqual(update.progress_delta, 0.0)
                self.assertEqual(update.filtered_progress, 0.3)

        self.assertEqual(tracker.missing_count, 4)

    def test_invalid_state_does_not_measure_progress(self) -> None:
        tracker = ProgressTracker()
        tracker.update(0.3)

        update = tracker.update(0.6, valid_state=False)

        self.assertTrue(update.missing)
        self.assertEqual(update.progress_delta, 0.0)
        self.assertEqual(update.filtered_progress, 0.3)

    def test_reset_clears_episode_progress(self) -> None:
        tracker = ProgressTracker()
        tracker.update(0.4)
        tracker.reset()

        update = tracker.update(0.1)

        self.assertEqual(update.progress_delta, 0.0)
        self.assertEqual(update.filtered_progress, 0.1)

    def test_tracker_configuration_is_validated(self) -> None:
        for kwargs in (
            {"jitter_tolerance": -0.1},
            {"jitter_tolerance": float("nan")},
            {"max_forward_delta": 0},
            {"max_forward_delta": 1.1},
            {"max_forward_delta": float("inf")},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                ProgressTracker(**kwargs)


if __name__ == "__main__":
    unittest.main()
