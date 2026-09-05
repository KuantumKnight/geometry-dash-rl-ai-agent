"""Importable deterministic policies for baseline comparisons."""

from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Protocol

import numpy as np


class ActionPolicy(Protocol):
    """Policy interface shared by baseline runners and tests."""

    def action(self, step_index: int, observation: np.ndarray | None = None) -> int:
        """Return a valid cube action for one decision."""
        ...


@dataclass(frozen=True)
class AlwaysNoopPolicy:
    """Always return the no-op action."""

    def action(self, step_index: int, observation: np.ndarray | None = None) -> int:
        del step_index, observation
        return 0


@dataclass
class RandomJumpPolicy:
    """Sample no-op or jump from a private reproducible random stream."""

    seed: int
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def action(self, step_index: int, observation: np.ndarray | None = None) -> int:
        del step_index, observation
        return self._rng.choice((0, 1))


@dataclass(frozen=True)
class PeriodicJumpPolicy:
    """Jump at a fixed one-based decision interval."""

    period: int = 6

    def __post_init__(self) -> None:
        if self.period <= 0:
            raise ValueError("period must be positive")

    def action(self, step_index: int, observation: np.ndarray | None = None) -> int:
        del observation
        return int((step_index + 1) % self.period == 0)


@dataclass(frozen=True)
class BrightnessHeuristicPolicy:
    """Simple observation-based baseline with no learned parameters."""

    threshold: float = 90.0

    def __post_init__(self) -> None:
        if not np.isfinite(self.threshold) or self.threshold < 0:
            raise ValueError("threshold must be finite and non-negative")

    def action(self, step_index: int, observation: np.ndarray | None = None) -> int:
        del step_index
        if observation is None or observation.size == 0:
            return 0
        bottom = np.asarray(observation)[-max(1, observation.shape[-3] // 10) :]
        return int(float(bottom.mean()) < self.threshold)


def policy_actions(policy: ActionPolicy, count: int) -> list[int]:
    """Return a validated action sequence for an offline baseline check."""

    if count < 0:
        raise ValueError("count must be non-negative")
    actions = [policy.action(index) for index in range(count)]
    if any(action not in (0, 1) for action in actions):
        raise ValueError("baseline produced an action outside Discrete(2)")
    return actions
