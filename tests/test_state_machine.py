"""Offline contract tests for canonical screen-state transitions."""

from __future__ import annotations

import unittest

from geometry_dash_env import ScreenState, StateMachine, StateTransitionError


class StateMachineTests(unittest.TestCase):
    """Verify legal transitions, history, and validation boundaries."""

    def test_canonical_states_and_history(self) -> None:
        """A reset path records each state with detector metadata."""

        machine = StateMachine()
        machine.transition(ScreenState.MAIN_MENU, reason="window discovered")
        machine.transition(
            ScreenState.LEVEL_INFO, reason="level selected", confidence=0.9
        )
        machine.transition(ScreenState.ATTEMPT_INTRO, reason="retry accepted")
        machine.transition(ScreenState.GAMEPLAY, reason="intro settled")

        self.assertEqual(machine.state, ScreenState.GAMEPLAY)
        self.assertEqual(len(machine.history), 4)
        self.assertEqual(machine.history[-1].previous, ScreenState.ATTEMPT_INTRO)
        self.assertEqual(machine.history[-1].confidence, None)

    def test_illegal_transition_fails_closed(self) -> None:
        """A detector cannot jump from disconnected to gameplay."""

        machine = StateMachine()
        with self.assertRaises(StateTransitionError):
            machine.transition(ScreenState.GAMEPLAY, reason="ambiguous frame")

    def test_transition_metadata_is_validated(self) -> None:
        """Reasons and confidence values remain useful diagnostic data."""

        machine = StateMachine()
        with self.assertRaises(ValueError):
            machine.transition(ScreenState.MAIN_MENU, reason=" ")
        with self.assertRaises(ValueError):
            machine.transition(ScreenState.MAIN_MENU, reason="bad", confidence=1.1)


if __name__ == "__main__":
    unittest.main()
