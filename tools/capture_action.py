"""Capture a game frame and optionally send one jump action.

The tool never launches Geometry Dash. Start the game yourself and use
``--action jump`` only when you are ready for it to focus the game window and
send a space-bar press.
"""

from __future__ import annotations

import argparse
import time
from ctypes import wintypes
from datetime import UTC, datetime
from pathlib import Path

from PIL import ImageGrab

from geometry_dash_env.platform_control import (
    GAME_PATH,
    click_client,
    find_game_window,
    focus_window,
    game_client_bbox,
    send_jump,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts" / "frames"

# These names remain module attributes so older tools importing them from
# tools.capture_action continue to work while the implementation lives in the
# installable package.
__all__ = [
    "GAME_PATH",
    "click_client",
    "find_game_window",
    "focus_window",
    "game_client_bbox",
    "send_jump",
]


def capture_frame(path: Path, hwnd: wintypes.HWND) -> tuple[int, int]:
    """Capture only the focused game's client area."""

    image = ImageGrab.grab(bbox=game_client_bbox(hwnd))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return image.size


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--action",
        choices=("noop", "jump"),
        default="noop",
        help="Action between the before and after captures (default: noop).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory for captured PNG frames.",
    )
    return parser.parse_args()


def main() -> None:
    """Capture before/after frames around a no-op or jump action."""

    args = parse_args()

    if not GAME_PATH.is_file():
        raise FileNotFoundError(f"Geometry Dash executable not found: {GAME_PATH}")

    print(f"Game executable found: {GAME_PATH}")
    print("Start Geometry Dash manually. Searching for its window in 3 seconds...")
    time.sleep(3)

    hwnd = find_game_window()
    if hwnd is None:
        raise RuntimeError(
            "No visible Geometry Dash window found. Start the game and try again."
        )
    focus_window(hwnd)
    print("Geometry Dash window found and focused.")

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    before_path = args.output_dir / f"{timestamp}_before.png"
    after_path = args.output_dir / f"{timestamp}_after.png"

    before_size = capture_frame(before_path, hwnd)
    if args.action == "jump":
        print("Sending jump action: space bar")
        send_jump(hwnd)
    else:
        print("Sending no-op action")
    time.sleep(0.25)
    after_size = capture_frame(after_path, hwnd)

    print(f"Before frame: {before_path} ({before_size[0]}x{before_size[1]})")
    print(f"After frame:  {after_path} ({after_size[0]}x{after_size[1]})")


if __name__ == "__main__":
    main()
