"""Episode aggregation and uncertainty metrics for experiment reports."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from statistics import median
from typing import Mapping, cast


@dataclass
class RollingMetrics:
    """Maintain append-only running return and progress statistics."""

    returns: list[float] = field(default_factory=list)
    progresses: list[float] = field(default_factory=list)

    def update(self, *, episode_return: float, progress: float | None = None) -> None:
        """Add one completed episode to the rolling state."""

        if not math.isfinite(episode_return):
            raise ValueError("episode_return must be finite")
        self.returns.append(float(episode_return))
        if progress is not None:
            if not math.isfinite(progress) or not 0 <= progress <= 1:
                raise ValueError("progress must be finite and between 0 and 1")
            self.progresses.append(float(progress))

    def snapshot(self) -> dict[str, object]:
        """Return aggregate values without discarding raw episode values."""

        return {
            "episodes": len(self.returns),
            "mean_return": sum(self.returns) / len(self.returns) if self.returns else None,
            "median_progress": median(self.progresses) if self.progresses else None,
            "best_progress": max(self.progresses) if self.progresses else None,
        }


def bootstrap_interval(
    values: list[float], *, seed: int = 0, samples: int = 2000, confidence: float = 0.95
) -> tuple[float, float]:
    """Return a deterministic percentile bootstrap interval for a mean."""

    if not values or samples <= 0 or not 0 < confidence < 1:
        raise ValueError("values, samples, and confidence must be valid")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("values must be finite")
    rng = random.Random(seed)
    means = [sum(rng.choices(values, k=len(values))) / len(values) for _ in range(samples)]
    means.sort()
    lower = int((1 - confidence) / 2 * samples)
    upper = int((1 + confidence) / 2 * samples)
    return means[lower], means[min(samples - 1, upper)]


def summarize_episodes(rows: list[Mapping[str, object]], *, seed: int = 0) -> dict[str, object]:
    """Aggregate episode rows and include uncertainty for progress."""

    if not rows:
        raise ValueError("at least one episode row is required")
    returns = [float(cast(float, row["return"])) for row in rows]
    progresses = [float(cast(float, row["progress"])) for row in rows if row.get("progress") is not None]
    completions = sum(row.get("outcome") == "completion" for row in rows)
    deaths = sum(row.get("outcome") == "death" for row in rows)
    truncations = sum(row.get("outcome") == "truncation" for row in rows)
    result: dict[str, object] = {
        "episodes": len(rows),
        "completion_rate": completions / len(rows),
        "median_progress": median(progresses) if progresses else None,
        "best_progress": max(progresses) if progresses else None,
        "mean_episode_length": sum(float(cast(float, row["length"])) for row in rows) / len(rows),
        "deaths": deaths,
        "truncations": truncations,
        "reset_failures": sum(float(cast(float, row.get("reset_failures", 0))) for row in rows),
        "environment_steps": sum(float(cast(float, row.get("length", 0))) for row in rows),
        "progress_mean_ci95": bootstrap_interval(progresses, seed=seed) if progresses else None,
    }
    return result
