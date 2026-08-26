"""Reset a Geometry Dash episode from the results screen.

The game must already be running and showing the results screen. This tool
never launches the game and refuses to send reset input from another screen.
"""

from __future__ import annotations

import argparse
import time
from datetime import UTC, datetime
from pathlib import Path

from mss import MSS
from PIL import Image

from geometry_dash_env.game_state import is_death_screen
from geometry_dash_env.platform_control import (
    GAME_PATH,
    click_client,
    find_game_window,
    focus_window,
    game_client_bbox,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts" / "reset_checks"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout",
        type=float,
        default=3.0,
        help="Seconds to wait for the results screen to clear (default: 3).",
    )
    parser.add_argument(
        "--settle",
        type=float,
        default=1.0,
        help="Seconds to wait after the overlay clears (default: 1).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory for before/after reset screenshots.",
    )
    return parser.parse_args()


def capture_game_frame(screen: MSS, bbox: tuple[int, int, int, int]) -> Image.Image:
    left, top, right, bottom = bbox
    shot = screen.grab(
        {"left": left, "top": top, "width": right - left, "height": bottom - top}
    )
    return Image.frombytes("RGB", shot.size, shot.rgb)


def main() -> None:
    args = parse_args()
    if args.timeout <= 0 or args.settle < 0:
        raise ValueError("--timeout must be positive and --settle cannot be negative")
    if not GAME_PATH.is_file():
        raise FileNotFoundError(f"Geometry Dash executable not found: {GAME_PATH}")

    hwnd = find_game_window()
    if hwnd is None:
        raise RuntimeError(
            "No visible Geometry Dash window found. Start the game first."
        )
    focus_window(hwnd)
    bbox = game_client_bbox(hwnd)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_dir = args.output_dir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    with MSS() as screen:
        before = capture_game_frame(screen, bbox)
        if not is_death_screen(before):
            before.save(output_dir / "rejected_before_reset.png")
            raise RuntimeError(
                "Reset refused: the current screen is not classified as RESULTS. "
                "Die in the level and wait for the results screen first."
            )
        before.save(output_dir / "results_before_reset.png")
        print("RESULTS detected; clicking the retry button.")
        click_client(hwnd)

        deadline = time.monotonic() + args.timeout
        cleared = False
        while time.monotonic() < deadline:
            time.sleep(0.05)
            current = capture_game_frame(screen, bbox)
            if not is_death_screen(current):
                cleared = True
                break

        if not cleared:
            raise TimeoutError("Results screen did not clear after clicking retry.")

        time.sleep(args.settle)
        after = capture_game_frame(screen, bbox)
        after.save(output_dir / "after_reset.png")

    print(f"Reset succeeded; saved verification frames to {output_dir}")


if __name__ == "__main__":
    main()
