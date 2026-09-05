"""Versioned progress tracking primitives for Geometry Dash episodes."""

from __future__ import annotations

import math
from dataclasses import dataclass

PROGRESS_CONTRACT_VERSION = "progress-v1"


@dataclass(frozen=True)
class ProgressUpdate:
    """One safe progress measurement and its diagnostics."""

    raw_progress: float | None
    filtered_progress: float | None
    progress_delta: float
    missing: bool
    clamped: bool
    backward_anomaly: bool


class ProgressTracker:
    """Filter per-step progress without rewarding repeated absolute values."""

    def __init__(
        self,
        *,
        jitter_tolerance: float = 0.005,
        max_forward_delta: float = 0.10,
    ) -> None:
        """Create a tracker with normalized progress limits."""

        if not math.isfinite(jitter_tolerance) or jitter_tolerance < 0:
            raise ValueError("jitter_tolerance must be finite and non-negative")
        if not math.isfinite(max_forward_delta) or max_forward_delta <= 0:
            raise ValueError("max_forward_delta must be finite and positive")
        if max_forward_delta > 1:
            raise ValueError("max_forward_delta cannot exceed 1")
        self.jitter_tolerance = jitter_tolerance
        self.max_forward_delta = max_forward_delta
        self._filtered_progress: float | None = None
        self.clamped_count = 0
        self.backward_anomaly_count = 0
        self.missing_count = 0

    @property
    def filtered_progress(self) -> float | None:
        """Return the most recent filtered progress value."""

        return self._filtered_progress

    def reset(self) -> None:
        """Start a new progress episode without carrying prior progress."""

        self._filtered_progress = None

    def update(
        self,
        raw_progress: float | None,
        *,
        valid_state: bool = True,
    ) -> ProgressUpdate:
        """Record one measurement and return its newly achieved delta."""

        if (
            raw_progress is None
            or not math.isfinite(raw_progress)
            or not 0 <= raw_progress <= 1
            or not valid_state
        ):
            self.missing_count += 1
            return ProgressUpdate(
                raw_progress=None if raw_progress is None else raw_progress,
                filtered_progress=self._filtered_progress,
                progress_delta=0.0,
                missing=True,
                clamped=False,
                backward_anomaly=False,
            )

        if self._filtered_progress is None:
            self._filtered_progress = raw_progress
            return ProgressUpdate(
                raw_progress=raw_progress,
                filtered_progress=raw_progress,
                progress_delta=0.0,
                missing=False,
                clamped=False,
                backward_anomaly=False,
            )

        previous = self._filtered_progress
        change = raw_progress - previous
        if change < -self.jitter_tolerance:
            self.backward_anomaly_count += 1
            return ProgressUpdate(
                raw_progress=raw_progress,
                filtered_progress=previous,
                progress_delta=0.0,
                missing=False,
                clamped=False,
                backward_anomaly=True,
            )
        if abs(change) <= self.jitter_tolerance:
            return ProgressUpdate(
                raw_progress=raw_progress,
                filtered_progress=previous,
                progress_delta=0.0,
                missing=False,
                clamped=False,
                backward_anomaly=False,
            )
        if change > self.max_forward_delta:
            self._filtered_progress = min(1.0, previous + self.max_forward_delta)
            self.clamped_count += 1
            return ProgressUpdate(
                raw_progress=raw_progress,
                filtered_progress=self._filtered_progress,
                progress_delta=self._filtered_progress - previous,
                missing=False,
                clamped=True,
                backward_anomaly=False,
            )

        self._filtered_progress = raw_progress
        return ProgressUpdate(
            raw_progress=raw_progress,
            filtered_progress=raw_progress,
            progress_delta=change,
            missing=False,
            clamped=False,
            backward_anomaly=False,
        )
