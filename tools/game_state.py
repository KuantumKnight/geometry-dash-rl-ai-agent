"""Pixel heuristics for the first Geometry Dash game-state detector."""

from __future__ import annotations

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

    sampled = image.convert("RGB").resize((320, 180), Image.Resampling.BILINEAR)
    return {
        "bottom_green_ratio": _region_ratio(
            sampled, (0.10, 0.65, 0.90, 0.95), _is_bright_green
        ),
        "progress_green_ratio": _region_ratio(
            sampled, (0.18, 0.18, 0.82, 0.30), _is_bright_green
        ),
        "center_dark_ratio": _region_ratio(
            sampled, (0.10, 0.10, 0.90, 0.90), _is_nearly_black
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
