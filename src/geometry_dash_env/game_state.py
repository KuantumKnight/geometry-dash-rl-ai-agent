"""Pixel heuristics for Geometry Dash screen-state and progress detection."""

from __future__ import annotations

from typing import cast

import numpy as np
from PIL import Image

NormalizedRegion = tuple[float, float, float, float]


def _is_bright_green(pixel: tuple[int, int, int]) -> bool:
    red, green, blue = pixel
    return green > 170 and green > red * 1.25 and green > blue * 1.1


def death_screen_features(image: Image.Image) -> dict[str, float]:
    """Return normalized visual features used by the baseline detector."""

    sampled = image.convert("RGB").resize(
        (320, 180),
        Image.Resampling.BILINEAR,
    )

    arr = np.asarray(sampled, dtype=np.uint16)

    red = arr[..., 0]
    green = arr[..., 1]
    blue = arr[..., 2]

    green_mask = (green > 170) & (green * 100 > red * 125) & (green * 100 > blue * 110)
    dark_mask = arr.sum(axis=2) < 80
    height, width = green_mask.shape

    def region_mean(mask: np.ndarray, region: NormalizedRegion) -> float:
        left = int(region[0] * width)
        top = int(region[1] * height)
        right = int(region[2] * width)
        bottom = int(region[3] * height)
        return float(mask[top:bottom, left:right].mean())

    return {
        "bottom_green_ratio": region_mean(
            green_mask,
            (0.10, 0.65, 0.90, 0.95),
        ),
        "progress_green_ratio": region_mean(
            green_mask,
            (0.18, 0.18, 0.82, 0.30),
        ),
        "center_dark_ratio": region_mean(
            dark_mask,
            (0.10, 0.10, 0.90, 0.90),
        ),
    }


def results_progress_ratio(image: Image.Image) -> float:
    """Estimate the normal-mode progress bar fill from a results screen."""

    sampled = image.convert("RGB").resize((320, 180), Image.Resampling.BILINEAR)
    width, height = sampled.size
    left = int(0.08 * width)
    right = int(0.92 * width)
    # The results panel shifts vertically between window layouts. Exclude the
    # decorative top beam and bottom controls, then search the central band.
    top = int(0.18 * height)
    bottom = int(0.65 * height)
    best_fill = 0

    for y in range(top, bottom):
        run = 0
        for x in range(left, right):
            pixel = cast(tuple[int, int, int], sampled.getpixel((x, y)))
            if _is_bright_green(pixel):
                run += 1
            else:
                best_fill = max(best_fill, run)
                run = 0
        best_fill = max(best_fill, run)

    return best_fill / max(1, right - left)


def is_death_screen(image: Image.Image) -> bool:
    """Detect the static Geometry Dash death/results overlay.

    This baseline is calibrated against recorded episodes. It must be
    strengthened with a labeled multi-episode dataset before training claims.
    """

    features = death_screen_features(image)
    return (
        features["bottom_green_ratio"] > 0.04 and features["center_dark_ratio"] > 0.50
    )


def classify_screen(image: Image.Image) -> str:
    """Classify the coarse screen state needed by the reset controller."""

    if is_death_screen(image):
        return "results"

    sampled = image.convert("RGB").resize((160, 90), Image.Resampling.BILINEAR)
    arr = np.asarray(sampled, dtype=np.uint16)
    red = arr[..., 0]
    green = arr[..., 1]
    blue = arr[..., 2]

    blue_level = (blue > 60) & (blue * 100 > red * 125) & (blue * 100 > green * 115)
    if float(blue_level[:68].mean()) > 0.75:
        return "gameplay_or_transition"

    warm_menu = (
        (red > 80)
        & (green > 60)
        & (red * 100 > blue * 160)
        & (green * 100 > blue * 160)
    )
    if float(warm_menu.mean()) > 0.50:
        return "main_menu"

    return "unknown"
