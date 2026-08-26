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
from datetime import UTC, datetime
from pathlib import Path

from mss import MSS
from PIL import Image

from geometry_dash_env.platform_control import (
    GAME_PATH,
    find_game_window,
    focus_window,
    game_client_bbox,
)

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
        default=60.0,
        help="Approximate capture rate (default: 60 frames per second).",
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
        help="Skip MP4 creation and save sampled PNG frames only.",
    )
    parser.add_argument(
        "--png-fps",
        type=float,
        default=5.0,
        help="PNG sample rate; video still targets --fps (default: 5 FPS).",
    )
    return parser.parse_args()


def start_video_encoder(
    episode_dir: Path, fps: float, width: int, height: int
) -> tuple[subprocess.Popen[bytes], Path] | None:
    """Start ffmpeg to receive raw BGRA frames at the requested rate."""

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
        "-f",
        "rawvideo",
        "-pix_fmt",
        "bgra",
        "-s",
        f"{width}x{height}",
        "-r",
        str(fps),
        "-i",
        "-",
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
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    return process, video_path


def finish_video_encoder(
    video: tuple[subprocess.Popen[bytes], Path] | None,
) -> Path | None:
    if video is None:
        return None

    process, video_path = video
    if process.stdin is not None:
        process.stdin.close()
    stderr = process.stderr.read().decode(errors="replace") if process.stderr else ""
    return_code = process.wait()
    if return_code != 0:
        video_path.unlink(missing_ok=True)
        message = stderr.strip() or f"exit code {return_code}"
        print(f"ffmpeg failed ({message}); keeping PNG samples.")
        return None
    return video_path


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
    if args.seconds <= 0 or args.fps <= 0 or args.png_fps <= 0:
        raise ValueError("--seconds, --fps, and --png-fps must be greater than zero")
    if not GAME_PATH.is_file():
        raise FileNotFoundError(f"Geometry Dash executable not found: {GAME_PATH}")

    print("Searching for the running Geometry Dash window...")
    hwnd = find_game_window()
    if hwnd is None:
        raise RuntimeError(
            "No visible Geometry Dash window found. Start the game first."
        )
    focus_window(hwnd)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    episode_dir = args.output_dir / timestamp
    episode_dir.mkdir(parents=True, exist_ok=True)
    bbox = game_client_bbox(hwnd)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    interval = 1.0 / args.fps
    recording_started = time.monotonic()
    deadline = recording_started + args.seconds
    frame_count = 0
    png_every = max(1, round(args.fps / args.png_fps))
    video = (
        None
        if args.no_video
        else start_video_encoder(episode_dir, args.fps, width, height)
    )

    print(f"Recording {args.seconds:g}s at approximately {args.fps:g} FPS.")
    print(f"Saving PNG samples at approximately {args.png_fps:g} FPS.")
    print("Play normally and allow the episode to reach a death screen.")
    monitor = {"left": bbox[0], "top": bbox[1], "width": width, "height": height}
    with MSS() as screen:
        while time.monotonic() < deadline:
            shot = screen.grab(monitor)
            if video and video[0].stdin is not None:
                try:
                    video[0].stdin.write(shot.raw)
                except BrokenPipeError:
                    video = None
                    print("ffmpeg stopped early; continuing with PNG samples.")

            if frame_count % png_every == 0:
                frame_path = episode_dir / f"frame_{frame_count // png_every:05d}.png"
                Image.frombytes("RGB", shot.size, shot.rgb).save(frame_path)

            frame_count += 1
            sleep_for = interval - (
                time.monotonic() - recording_started - (frame_count - 1) * interval
            )
            if sleep_for > 0:
                time.sleep(sleep_for)

    recording_elapsed = time.monotonic() - recording_started
    actual_fps = frame_count / recording_elapsed if recording_elapsed else 0.0
    video_path = finish_video_encoder(video)
    metadata = {
        "game_executable": str(GAME_PATH),
        "capture_bbox": bbox,
        "requested_seconds": args.seconds,
        "requested_fps": args.fps,
        "actual_fps": round(actual_fps, 3),
        "frame_count": frame_count,
        "png_sample_fps": round(frame_count / png_every / recording_elapsed, 3)
        if recording_elapsed
        else 0.0,
        "started_utc": timestamp,
        "video_file": video_path.name if video_path else None,
    }
    (episode_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(f"Saved {frame_count} frames to {episode_dir}")
    print(f"Measured capture rate: {actual_fps:.1f} FPS")
    if video_path:
        print(f"Saved video to {video_path}")


if __name__ == "__main__":
    main()
