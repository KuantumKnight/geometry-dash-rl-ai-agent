"""A minimal reset/step interface for pixel-based Geometry Dash control."""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
from mss import MSS
from PIL import Image

from tools.capture_action import (
    GAME_PATH,
    click_client,
    find_game_window,
    focus_window,
    game_client_bbox,
    send_jump,
)
from tools.game_state import classify_screen, is_death_screen, results_progress_ratio


class GeometryDashEnv:
    """Minimal environment with pixel observations and two discrete actions.

    Actions:
        0: no-op
        1: jump (space bar)

    The current reward is deliberately provisional: zero while alive and -1
    when the results screen is detected. Progress-based reward comes later.
    """

    def __init__(
        self,
        *,
        observation_size: tuple[int, int] = (160, 90),
        fps: float = 60.0,
        frame_skip: int = 4,
        max_steps: int = 900,
        reset_timeout: float = 3.0,
        reset_settle: float = 1.0,
        reset_stable_frames: int = 3,
    ) -> None:
        if observation_size[0] <= 0 or observation_size[1] <= 0:
            raise ValueError("observation_size dimensions must be positive")
        if fps <= 0 or frame_skip <= 0 or max_steps <= 0:
            raise ValueError("fps, frame_skip, and max_steps must be positive")
        if reset_timeout <= 0 or reset_settle < 0 or reset_stable_frames <= 0:
            raise ValueError(
                "reset_timeout must be positive, reset_settle cannot be negative, "
                "and reset_stable_frames must be positive"
            )
        self.observation_size = observation_size
        self.fps = fps
        self.frame_interval = 1.0 / fps
        self.frame_skip = frame_skip
        self.max_steps = max_steps
        self.reset_timeout = reset_timeout
        self.reset_settle = reset_settle
        self.reset_stable_frames = reset_stable_frames
        self._screen = MSS()
        self._hwnd = None
        self._bbox: tuple[int, int, int, int] | None = None
        self._episode_active = False
        self._step_count = 0

    def close(self) -> None:
        self._screen.close()

    def _ensure_window(self) -> None:
        if not GAME_PATH.is_file():
            raise FileNotFoundError(f"Geometry Dash executable not found: {GAME_PATH}")
        self._hwnd = find_game_window()
        if self._hwnd is None:
            raise RuntimeError("No visible Geometry Dash window found. Start the game first.")
        focus_window(self._hwnd)
        self._bbox = game_client_bbox(self._hwnd)

    def _capture(self) -> Image.Image:
        if self._bbox is None:
            raise RuntimeError("Environment is not connected to a game window")
        left, top, right, bottom = self._bbox
        shot = self._screen.grab(
            {"left": left, "top": top, "width": right - left, "height": bottom - top}
        )
        return Image.frombytes("RGB", shot.size, shot.rgb)

    def _observation(self, image: Image.Image) -> np.ndarray:
        resized = image.resize(self.observation_size, Image.Resampling.BILINEAR)
        return np.asarray(resized, dtype=np.uint8).copy()

    def _wait_for_ready_gameplay(self) -> Image.Image:
        """Wait for consecutive level-like frames after retry or transition."""

        deadline = time.monotonic() + self.reset_timeout
        stable_frames = 0
        last_state = "unknown"
        image: Image.Image | None = None
        while time.monotonic() < deadline:
            image = self._capture()
            last_state = classify_screen(image)
            if last_state == "main_menu":
                raise RuntimeError(
                    "Reset encountered the main menu; enter the target level before retrying."
                )
            if last_state == "gameplay_or_transition":
                stable_frames += 1
                if stable_frames >= self.reset_stable_frames:
                    return image
            else:
                stable_frames = 0
            time.sleep(self.frame_interval)

        raise TimeoutError(
            "Level did not reach stable gameplay during reset "
            f"(last_state={last_state})"
        )

    def _wait_for_frame_deadline(self, deadline: float) -> None:
        """Wait only until the next frame deadline, if computation is ahead."""

        remaining = deadline - time.perf_counter()
        if remaining > 0:
            time.sleep(remaining)

    def reset(self) -> tuple[np.ndarray, dict[str, object]]:
        """Start or retry an episode and return the first pixel observation."""

        self._ensure_window()
        image = self._capture()
        screen_state = classify_screen(image)
        if screen_state == "results":
            click_client(self._hwnd)
            time.sleep(self.reset_settle)
            image = self._wait_for_ready_gameplay()
        elif screen_state == "gameplay_or_transition":
            image = self._wait_for_ready_gameplay()
        else:
            raise RuntimeError(
                "Reset requires a results screen or active level; "
                f"detected screen_state={screen_state}"
            )

        self._episode_active = True
        self._step_count = 0
        return self._observation(image), {
            "screen_state": "gameplay_or_transition",
            "observation_size": self.observation_size,
            "frame_skip": self.frame_skip,
        }

    def step(
        self, action: int
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, object]]:
        """Apply one action and return observation, reward, and termination."""

        if not self._episode_active or self._hwnd is None:
            raise RuntimeError("Call reset() before step()")
        if action not in (0, 1):
            raise ValueError("action must be 0 (no-op) or 1 (jump)")

        if action == 1:
            send_jump(self._hwnd)
        image = None
        terminated = False
        frames_elapsed = 0
        frame_deadline = time.perf_counter() + self.frame_interval
        for _ in range(self.frame_skip):
            self._wait_for_frame_deadline(frame_deadline)
            image = self._capture()
            frames_elapsed += 1
            if is_death_screen(image):
                terminated = True
                break
            frame_deadline += self.frame_interval

        self._step_count += 1
        truncated = not terminated and self._step_count >= self.max_steps
        if terminated or truncated:
            self._episode_active = False
        progress_ratio = results_progress_ratio(image) if terminated else None
        reward = (-1.0 + progress_ratio) if terminated and progress_ratio is not None else 0.0
        return self._observation(image), reward, terminated, truncated, {
            "screen_state": "results" if terminated else "gameplay_or_transition",
            "frames_elapsed": frames_elapsed,
            "decision_step": self._step_count,
            "truncated": truncated,
            "progress_ratio": progress_ratio,
        }
