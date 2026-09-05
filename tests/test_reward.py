"""Tests for the sparse terminal reward contract."""

from __future__ import annotations

import unittest

from geometry_dash_env.reward import calculate_reward


class RewardContractTests(unittest.TestCase):
    """Protect reward invariants before any shaping experiment."""

    def test_alive_and_truncation_have_no_reward(self) -> None:
        self.assertEqual(calculate_reward("alive").total, 0.0)
        self.assertEqual(calculate_reward("truncation").total, 0.0)
        self.assertEqual(calculate_reward("invalid_state").total, 0.0)

    def test_death_reward_includes_terminal_progress_once(self) -> None:
        reward = calculate_reward("death", progress_ratio=0.5)

        self.assertEqual(reward.total, -0.5)
        self.assertEqual(reward.progress, 0.5)
        self.assertEqual(reward.death, -1.0)
        self.assertEqual(reward.as_dict()["total"], -0.5)

    def test_completion_is_better_than_death_at_same_progress(self) -> None:
        completion = calculate_reward("completion", progress_ratio=0.5)
        death = calculate_reward("death", progress_ratio=0.5)

        self.assertGreater(completion.total, death.total)
        self.assertEqual(completion.progress, 0.0)

    def test_nonterminal_outcomes_cannot_accumulate_progress(self) -> None:
        for outcome in ("alive", "truncation", "invalid_state"):
            with self.subTest(outcome=outcome):
                reward = calculate_reward(outcome, progress_ratio=1.0)
                self.assertEqual(reward.total, 0.0)
                self.assertEqual(reward.progress, 0.0)

    def test_reward_components_are_bounded_and_explicit(self) -> None:
        for outcome in ("alive", "death", "completion", "truncation", "invalid_state"):
            with self.subTest(outcome=outcome):
                reward = calculate_reward(outcome, progress_ratio=1.0)
                self.assertLessEqual(abs(reward.total), 1.0)
                self.assertEqual(
                    set(reward.as_dict()),
                    {
                        "progress",
                        "survival",
                        "death",
                        "completion",
                        "truncation",
                        "invalid_state",
                        "total",
                    },
                )

    def test_invalid_progress_is_rejected(self) -> None:
        for value in (-0.1, 1.1, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                calculate_reward("death", progress_ratio=value)


if __name__ == "__main__":
    unittest.main()
