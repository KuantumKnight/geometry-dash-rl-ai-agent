"""Capture a screen frame and optionally send one jump action.

This is deliberately a manual, capture-only prototype. It never launches the
game. Start Geometry Dash yourself, focus its window, and use --action jump
only when you are ready to test input delivery.
"""

from __future__ import annotations

import argparse
import ctypes
import time
from datetime import datetime, timezone
from pathlib import Path

from PIL import ImageGrab


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GAME_PATH = PROJECT_ROOT / "Geometry Dash" / "GeometryDash.exe"
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts" / "frames"
VK_SPACE = 0x20
KEYEVENTF_KEYUP = 0x0002


def send_jump() -> None:
    """Send a short space-bar press to the focused window on Windows."""

    user32 = ctypes.windll.user32
    user32.keybd_event(VK_SPACE, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_SPACE, 0, KEYEVENTF_KEYUP, 0)


def capture_frame(path: Path) -> tuple[int, int]:
    """Capture the primary display and return its dimensions."""

    image = ImageGrab.grab()
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return image.size


def parse_args() -> argparse.Namespace:
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
    args = parse_args()

    if not GAME_PATH.is_file():
        raise FileNotFoundError(f"Geometry Dash executable not found: {GAME_PATH}")

    print(f"Game executable found: {GAME_PATH}")
    print("Focus the Geometry Dash window. Capturing in 3 seconds...")
    time.sleep(3)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    before_path = args.output_dir / f"{timestamp}_before.png"
    after_path = args.output_dir / f"{timestamp}_after.png"

    before_size = capture_frame(before_path)
    if args.action == "jump":
        print("Sending jump action: space bar")
        send_jump()
    else:
        print("Sending no-op action")
    time.sleep(0.25)
    after_size = capture_frame(after_path)

    print(f"Before frame: {before_path} ({before_size[0]}x{before_size[1]})")
    print(f"After frame:  {after_path} ({after_size[0]}x{after_size[1]})")


if __name__ == "__main__":
    main()
