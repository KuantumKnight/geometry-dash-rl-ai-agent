"""Scan a recorded episode and report alive/dead state transitions."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

try:
    from .game_state import is_death_screen
except ImportError:  # Direct execution: `py tools\\scan_episode.py`.
    from game_state import is_death_screen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode_dir", type=Path)
    args = parser.parse_args()

    frames = sorted(args.episode_dir.glob("frame_*.png"))
    if not frames:
        raise FileNotFoundError(f"No PNG frames found in {args.episode_dir}")

    previous: str | None = None
    transitions = 0
    for frame_path in frames:
        with Image.open(frame_path) as image:
            state = "dead/results" if is_death_screen(image) else "alive/gameplay"
        if state != previous:
            print(f"{frame_path.name}: {state}")
            previous = state
            transitions += 1

    print(f"Detected {transitions} state segments across {len(frames)} frames.")


if __name__ == "__main__":
    main()
