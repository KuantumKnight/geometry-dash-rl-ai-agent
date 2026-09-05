"""Tests for importable deterministic baseline policies."""

from __future__ import annotations

import unittest

import numpy as np

from geometry_dash_env import (
    AlwaysNoopPolicy,
    BrightnessHeuristicPolicy,
    PeriodicJumpPolicy,
    RandomJumpPolicy,
    policy_actions,
)


class BaselinePolicyTests(unittest.TestCase):
    def test_noop_policy_is_constant_and_valid(self) -> None:
        self.assertEqual(policy_actions(AlwaysNoopPolicy(), 5), [0] * 5)

    def test_periodic_policy_sequence_is_one_based(self) -> None:
        self.assertEqual(
            policy_actions(PeriodicJumpPolicy(period=3), 7), [0, 0, 1, 0, 0, 1, 0]
        )

    def test_random_policy_seed_reproduces_sequence(self) -> None:
        first = policy_actions(RandomJumpPolicy(seed=17), 20)
        second = policy_actions(RandomJumpPolicy(seed=17), 20)
        self.assertEqual(first, second)
        self.assertTrue(set(first) <= {0, 1})

    def test_heuristic_uses_observation_without_learning(self) -> None:
        policy = BrightnessHeuristicPolicy(threshold=90)
        dark = np.zeros((10, 10, 3), dtype=np.uint8)
        bright = np.full((10, 10, 3), 200, dtype=np.uint8)
        self.assertEqual(policy.action(0, dark), 1)
        self.assertEqual(policy.action(0, bright), 0)

    def test_invalid_policy_configuration_and_count_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            PeriodicJumpPolicy(period=0)
        with self.assertRaises(ValueError):
            BrightnessHeuristicPolicy(threshold=-1)
        with self.assertRaises(ValueError):
            policy_actions(AlwaysNoopPolicy(), -1)


if __name__ == "__main__":
    unittest.main()
