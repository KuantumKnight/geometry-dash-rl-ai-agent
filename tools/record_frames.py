"""Record game-window frames for inspecting an episode transition.

Start Geometry Dash and enter a level manually before running this tool. It
does not launch the game or send keyboard input.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from PIL import ImageGrab

try:
    from .capture_action import (
        GAME_PATH,
        find_game_window,
        focus_window,
        game_client_bbox,
    )
except ImportError:  # Direct execution: `py tools\\record_frames.py`.
    from capture_action import GAME_PATH, find_game_window, focus_window, game_client_bbox


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts" / "episodes"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seconds",
        type=float,
        default=12.0,
        help="How long to record (default: 12 seconds).",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=5.0,
        help="Approximate capture rate (default: 5 frames per second).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory for the recorded episode.",
    )
    parser.add_argument(
        "--no-video",
        action="store_true",
        help="Skip MP4 creation and save PNG frames only.",
    )
    return parser.parse_args()


def create_video(episode_dir: Path, fps: float) -> Path | None:
    """Encode the recorded PNG sequence as a browser-friendly MP4."""

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        print("ffmpeg not found; skipping video creation.")
        return None

    video_path = episode_dir / "episode.mp4"
    command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-framerate",
        str(fps),
        "-i",
        str(episode_dir / "frame_%05d.png"),
        "-c:v",
        "libx264",
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(video_path),
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        video_path.unlink(missing_ok=True)
        print(f"ffmpeg failed with exit code {exc.returncode}; keeping PNG frames.")
        return None
    return video_path


def main() -> None:
    args = parse_args()
    if args.seconds <= 0 or args.fps <= 0:
        raise ValueError("--seconds and --fps must be greater than zero")
    if not GAME_PATH.is_file():
        raise FileNotFoundError(f"Geometry Dash executable not found: {GAME_PATH}")

    print("Searching for the running Geometry Dash window...")
    hwnd = find_game_window()
    if hwnd is None:
        raise RuntimeError("No visible Geometry Dash window found. Start the game first.")
    focus_window(hwnd)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    episode_dir = args.output_dir / timestamp
    episode_dir.mkdir(parents=True, exist_ok=True)
    bbox = game_client_bbox(hwnd)
    interval = 1.0 / args.fps
    deadline = time.monotonic() + args.seconds
    frame_count = 0

    print(f"Recording {args.seconds:g}s at approximately {args.fps:g} FPS.")
    print("Play normally and allow the episode to reach a death screen.")
    started = time.monotonic()
    while time.monotonic() < deadline:
        frame_path = episode_dir / f"frame_{frame_count:05d}.png"
        image = ImageGrab.grab(bbox=bbox, all_screens=True)
        image.save(frame_path)
        frame_count += 1
        sleep_for = interval - (time.monotonic() - started - (frame_count - 1) * interval)
        if sleep_for > 0:
            time.sleep(sleep_for)

    video_path = None if args.no_video else create_video(episode_dir, args.fps)
    metadata = {
        "game_executable": str(GAME_PATH),
        "capture_bbox": bbox,
        "requested_seconds": args.seconds,
        "requested_fps": args.fps,
        "frame_count": frame_count,
        "started_utc": timestamp,
        "video_file": video_path.name if video_path else None,
    }
    (episode_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(f"Saved {frame_count} frames to {episode_dir}")
    if video_path:
        print(f"Saved video to {video_path}")


if __name__ == "__main__":
    main()
