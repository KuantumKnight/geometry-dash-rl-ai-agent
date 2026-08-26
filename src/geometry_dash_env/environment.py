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
from tools.game_state import is_death_screen


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
        reset_timeout: float = 3.0,
        reset_settle: float = 0.5,
    ) -> None:
        if observation_size[0] <= 0 or observation_size[1] <= 0:
            raise ValueError("observation_size dimensions must be positive")
        if fps <= 0 or reset_timeout <= 0 or reset_settle < 0:
            raise ValueError("fps and reset_timeout must be positive")
        self.observation_size = observation_size
        self.fps = fps
        self.reset_timeout = reset_timeout
        self.reset_settle = reset_settle
        self._screen = MSS()
        self._hwnd = None
        self._bbox: tuple[int, int, int, int] | None = None
        self._episode_active = False

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

    def reset(self) -> tuple[np.ndarray, dict[str, object]]:
        """Start or retry an episode and return the first pixel observation."""

        self._ensure_window()
        image = self._capture()
        if is_death_screen(image):
            click_client(self._hwnd)
            deadline = time.monotonic() + self.reset_timeout
            while time.monotonic() < deadline:
                time.sleep(0.05)
                image = self._capture()
                if not is_death_screen(image):
                    break
            else:
                raise TimeoutError("Results screen did not clear during reset")
            time.sleep(self.reset_settle)
            image = self._capture()

        self._episode_active = True
        return self._observation(image), {
            "screen_state": "gameplay_or_transition",
            "observation_size": self.observation_size,
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
        time.sleep(1.0 / self.fps)
        image = self._capture()
        terminated = is_death_screen(image)
        if terminated:
            self._episode_active = False
        reward = -1.0 if terminated else 0.0
        return self._observation(image), reward, terminated, False, {
            "screen_state": "results" if terminated else "gameplay_or_transition",
        }
