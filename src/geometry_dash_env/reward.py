"""Versioned sparse-terminal reward contract."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

REWARD_CONTRACT_VERSION = "reward-sparse-terminal-v1"
RewardOutcome = Literal["alive", "death", "completion", "truncation", "invalid_state"]


@dataclass(frozen=True)
class RewardBreakdown:
    """Explicit components for one environment decision."""

    total: float
    progress: float
    survival: float
    death: float
    completion: float
    truncation: float
    invalid_state: float

    def as_dict(self) -> dict[str, float]:
        """Return component names suitable for info records and logs."""

        return {
            "progress": self.progress,
            "survival": self.survival,
            "death": self.death,
            "completion": self.completion,
            "truncation": self.truncation,
            "invalid_state": self.invalid_state,
            "total": self.total,
        }


def calculate_reward(
    outcome: RewardOutcome,
    *,
    progress_ratio: float | None = None,
) -> RewardBreakdown:
    """Calculate the bounded sparse-terminal reward for one outcome."""

    if progress_ratio is not None and (
        not math.isfinite(progress_ratio) or not 0.0 <= progress_ratio <= 1.0
    ):
        raise ValueError("progress_ratio must be finite and between 0 and 1")
    progress = progress_ratio or 0.0
    death = -1.0 if outcome == "death" else 0.0
    completion = 1.0 if outcome == "completion" else 0.0
    if outcome != "death":
        progress = 0.0
    total = death + completion + progress
    return RewardBreakdown(
        total=total,
        progress=progress,
        survival=0.0,
        death=death,
        completion=completion,
        truncation=0.0,
        invalid_state=0.0,
    )
