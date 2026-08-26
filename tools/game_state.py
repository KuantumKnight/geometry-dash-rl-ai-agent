"""Pixel heuristics for the first Geometry Dash game-state detector."""

from __future__ import annotations

import numpy as np
from PIL import Image


def _is_bright_green(pixel: tuple[int, int, int]) -> bool:
    red, green, blue = pixel
    return green > 170 and green > red * 1.25 and green > blue * 1.1


def _is_nearly_black(pixel: tuple[int, int, int]) -> bool:
    return sum(pixel) < 80


def _region_ratio(image: Image.Image, region, predicate) -> float:
    width, height = image.size
    left, top, right, bottom = (
        int(region[0] * width),
        int(region[1] * height),
        int(region[2] * width),
        int(region[3] * height),
    )
    pixels = image.load()
    matching = 0
    total = max(1, (right - left) * (bottom - top))
    for y in range(top, bottom):
        for x in range(left, right):
            matching += predicate(pixels[x, y])
    return matching / total


def death_screen_features(image: Image.Image) -> dict[str, float]:
    """Return normalized visual features used by the baseline detector."""

    sampled = image.convert("RGB").resize(
        (320, 180),
        Image.Resampling.BILINEAR,
    )

    arr = np.asarray(sampled, dtype=np.uint16)

    r = arr[..., 0]
    g = arr[..., 1]
    b = arr[..., 2]

    green_mask = (
        (g > 170)
        & (g * 100 > r * 125)
        & (g * 100 > b * 110)
    )

    dark_mask = arr.sum(axis=2) < 80

    height, width = green_mask.shape

    def region_mean(mask, region):
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
    pixels = sampled.load()
    best_fill = 0

    for y in range(top, bottom):
        run = 0
        for x in range(left, right):
            if _is_bright_green(pixels[x, y]):
                run += 1
            else:
                best_fill = max(best_fill, run)
                run = 0
        best_fill = max(best_fill, run)

    return best_fill / max(1, right - left)


def is_death_screen(image: Image.Image) -> bool:
    """Detect the static Geometry Dash death/results overlay.

    This is a first baseline calibrated against recorded episodes. It should
    be replaced or strengthened after testing across multiple levels and
    display layouts.
    """

    features = death_screen_features(image)
    return (
        features["bottom_green_ratio"] > 0.04
        and features["center_dark_ratio"] > 0.50
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

    blue_level = (
        (blue > 60)
        & (blue * 100 > red * 125)
        & (blue * 100 > green * 115)
    )
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
