"""Canonical screen-state contract for live environment orchestration."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import StrEnum


class ScreenState(StrEnum):
    """States exposed by the live environment state machine."""

    DISCONNECTED = "disconnected"
    MAIN_MENU = "main_menu"
    LEVEL_INFO = "level_info"
    ATTEMPT_INTRO = "attempt_intro"
    GAMEPLAY = "gameplay"
    DEATH_ANIMATION = "death_animation"
    RESULTS = "results"
    LEVEL_COMPLETE = "level_complete"
    RESETTING = "resetting"
    ERROR = "error"


class StateTransitionError(RuntimeError):
    """Raised when a detector proposes an illegal state transition."""


@dataclass(frozen=True)
class StateTransition:
    """One accepted state transition and its detector reason/confidence."""

    previous: ScreenState
    current: ScreenState
    reason: str
    confidence: float | None


LEGAL_TRANSITIONS: dict[ScreenState, frozenset[ScreenState]] = {
    ScreenState.DISCONNECTED: frozenset(
        {
            ScreenState.MAIN_MENU,
            ScreenState.LEVEL_INFO,
            ScreenState.RESETTING,
            ScreenState.ERROR,
        }
    ),
    ScreenState.MAIN_MENU: frozenset(
        {ScreenState.LEVEL_INFO, ScreenState.DISCONNECTED, ScreenState.ERROR}
    ),
    ScreenState.LEVEL_INFO: frozenset(
        {ScreenState.ATTEMPT_INTRO, ScreenState.MAIN_MENU, ScreenState.ERROR}
    ),
    ScreenState.ATTEMPT_INTRO: frozenset(
        {ScreenState.GAMEPLAY, ScreenState.RESETTING, ScreenState.ERROR}
    ),
    ScreenState.GAMEPLAY: frozenset(
        {
            ScreenState.DEATH_ANIMATION,
            ScreenState.RESULTS,
            ScreenState.LEVEL_COMPLETE,
            ScreenState.DISCONNECTED,
            ScreenState.RESETTING,
            ScreenState.ERROR,
        }
    ),
    ScreenState.DEATH_ANIMATION: frozenset(
        {ScreenState.RESULTS, ScreenState.RESETTING, ScreenState.ERROR}
    ),
    ScreenState.RESULTS: frozenset(
        {ScreenState.RESETTING, ScreenState.LEVEL_COMPLETE, ScreenState.ERROR}
    ),
    ScreenState.LEVEL_COMPLETE: frozenset(
        {ScreenState.RESETTING, ScreenState.MAIN_MENU, ScreenState.ERROR}
    ),
    ScreenState.RESETTING: frozenset(
        {
            ScreenState.ATTEMPT_INTRO,
            ScreenState.GAMEPLAY,
            ScreenState.MAIN_MENU,
            ScreenState.RESULTS,
            ScreenState.ERROR,
        }
    ),
    ScreenState.ERROR: frozenset({ScreenState.DISCONNECTED, ScreenState.RESETTING}),
}


class StateMachine:
    """Track canonical states and reject transitions outside the contract."""

    def __init__(self, *, history_size: int = 32) -> None:
        """Create a machine starting in ``DISCONNECTED``."""

        if history_size <= 0:
            raise ValueError("history_size must be positive")
        self._state = ScreenState.DISCONNECTED
        self._history: deque[StateTransition] = deque(maxlen=history_size)

    @property
    def state(self) -> ScreenState:
        """Return the current canonical state."""

        return self._state

    @property
    def history(self) -> tuple[StateTransition, ...]:
        """Return an immutable snapshot of recent transitions."""

        return tuple(self._history)

    def can_transition(self, current: ScreenState) -> bool:
        """Return whether the requested state is legal from the current state."""

        return current in LEGAL_TRANSITIONS[self._state]

    def start(
        self,
        current: ScreenState,
        *,
        reason: str,
        confidence: float | None = None,
    ) -> StateTransition:
        """Record the first detector state observed after connection."""

        if self._state != ScreenState.DISCONNECTED:
            raise StateTransitionError("state machine has already started")
        return self.transition(
            current,
            reason=reason,
            confidence=confidence,
        )

    def transition(
        self,
        current: ScreenState,
        *,
        reason: str,
        confidence: float | None = None,
    ) -> StateTransition:
        """Accept a legal transition and record its reason/confidence."""

        if not reason.strip():
            raise ValueError("transition reason must not be empty")
        if confidence is not None and not 0.0 <= confidence <= 1.0:
            raise ValueError("transition confidence must be between 0 and 1")
        if not self.can_transition(current):
            raise StateTransitionError(
                f"Illegal state transition: {self._state.value} -> {current.value}"
            )
        transition = StateTransition(
            previous=self._state,
            current=current,
            reason=reason,
            confidence=confidence,
        )
        self._history.append(transition)
        self._state = current
        return transition
