"""Compatibility imports for the packaged screen-state implementation."""

from geometry_dash_env.game_state import (
    classify_screen,
    death_screen_features,
    is_death_screen,
    results_progress_ratio,
)

__all__ = [
    "classify_screen",
    "death_screen_features",
    "is_death_screen",
    "results_progress_ratio",
]
