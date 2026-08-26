"""Compare the legacy and NumPy death detectors on saved frames only."""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import cast

from PIL import Image

from geometry_dash_env.game_state import (
    death_screen_features as new_death_screen_features,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def old_death_screen_features(image: Image.Image) -> dict[str, float]:
    """The pre-NumPy pixel-loop implementation kept for comparison."""

    sampled = image.convert("RGB").resize((320, 180), Image.Resampling.BILINEAR)
    width, height = sampled.size

    def region_ratio(region, predicate) -> float:
        left = int(region[0] * width)
        top = int(region[1] * height)
        right = int(region[2] * width)
        bottom = int(region[3] * height)
        matching = 0
        total = max(1, (right - left) * (bottom - top))
        for y in range(top, bottom):
            for x in range(left, right):
                pixel = cast(tuple[int, int, int], sampled.getpixel((x, y)))
                matching += predicate(pixel)
        return matching / total

    def is_bright_green(pixel: tuple[int, int, int]) -> bool:
        red, green, blue = pixel
        return green > 170 and green > red * 1.25 and green > blue * 1.1

    def is_nearly_black(pixel: tuple[int, int, int]) -> bool:
        return sum(pixel) < 80

    return {
        "bottom_green_ratio": region_ratio((0.10, 0.65, 0.90, 0.95), is_bright_green),
        "progress_green_ratio": region_ratio((0.18, 0.18, 0.82, 0.30), is_bright_green),
        "center_dark_ratio": region_ratio((0.10, 0.10, 0.90, 0.90), is_nearly_black),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark old and NumPy death-screen feature extraction offline."
    )
    parser.add_argument(
        "--frames-dir",
        type=Path,
        default=PROJECT_ROOT / "artifacts",
        help="Directory recursively containing saved PNG frames.",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=5,
        help="Timed passes per frame and implementation (default: 5).",
    )
    args = parser.parse_args()
    if args.repeats <= 0:
        parser.error("--repeats must be positive")
    return args


def main() -> None:
    args = parse_args()
    paths = sorted(args.frames_dir.rglob("*.png"))
    if not paths:
        raise FileNotFoundError(f"No PNG frames found under {args.frames_dir}")

    old_total = 0.0
    new_total = 0.0
    mismatches = 0
    max_difference = 0.0

    for path in paths:
        with Image.open(path) as image:
            image.load()
            old_features = old_death_screen_features(image)
            new_features = new_death_screen_features(image)
            difference = max(
                abs(old_features[key] - new_features[key]) for key in old_features
            )
            max_difference = max(max_difference, difference)
            if difference != 0.0:
                mismatches += 1

            for repeat in range(args.repeats):
                if repeat % 2 == 0:
                    started = time.perf_counter()
                    old_death_screen_features(image)
                    old_total += time.perf_counter() - started

                    started = time.perf_counter()
                    new_death_screen_features(image)
                    new_total += time.perf_counter() - started
                else:
                    started = time.perf_counter()
                    new_death_screen_features(image)
                    new_total += time.perf_counter() - started

                    started = time.perf_counter()
                    old_death_screen_features(image)
                    old_total += time.perf_counter() - started

    samples = len(paths) * args.repeats
    old_mean_ms = old_total / samples * 1000.0
    new_mean_ms = new_total / samples * 1000.0
    speedup = old_mean_ms / new_mean_ms

    print(f"frames:             {len(paths)}")
    print(f"repeats:            {args.repeats}")
    print(f"old mean/frame:     {old_mean_ms:.4f} ms")
    print(f"new mean/frame:     {new_mean_ms:.4f} ms")
    print(f"speedup:            {speedup:.2f}x")
    print(f"old/new mismatches: {mismatches}")
    print(f"max feature diff:   {max_difference:.12f}")


if __name__ == "__main__":
    main()
