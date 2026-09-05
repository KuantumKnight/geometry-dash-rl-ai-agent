"""A minimal reset/step interface for pixel-based Geometry Dash control."""

from __future__ import annotations

import time
from collections import deque
from threading import Event
from typing import Any, ClassVar, Protocol, cast

import gymnasium as gym
import numpy as np
from mss import MSS
from PIL import Image

from .game_state import classify_screen, is_death_screen, results_progress_ratio
from .platform_control import (
    DEFAULT_PRESS_DURATION,
    PlatformBackend,
    Win32Platform,
    validate_game_path,
)
from .reward import REWARD_CONTRACT_VERSION, calculate_reward
from .state_machine import ScreenState, StateMachine

ENVIRONMENT_VERSION = "phase1-contract-v1"
OBSERVATION_CONTRACT_VERSION = "observation-v1"
OBSERVATION_LAYOUT = "HWC"
ACTION_CONTRACT_VERSION = "action-v1"


class CaptureBackend(Protocol):
    """Minimal screen-capture interface required by the environment."""

    def grab(self, monitor: Any) -> Any:
        """Capture the requested screen rectangle."""
        ...

    def close(self) -> None:
        """Release capture resources."""
        ...


class EmergencyStop:
    """Thread-safe latch for an operator-controlled episode stop."""

    def __init__(self) -> None:
        """Create a clear emergency-stop latch."""

        self._event = Event()

    def request(self) -> None:
        """Request immediate suppression of future actions."""

        self._event.set()

    def clear(self) -> None:
        """Clear the latch before starting a new controlled run."""

        self._event.clear()

    @property
    def requested(self) -> bool:
        """Return whether an operator has requested an emergency stop."""

        return self._event.is_set()


class GeometryDashEnv(gym.Env):
    """Minimal environment with pixel observations and two discrete actions.

    Actions:
        0: no-op
        1: jump (space bar)

    The current reward is deliberately provisional: zero while alive and -1
    when the results screen is detected. Progress-based reward comes later.
    """

    metadata: ClassVar[dict[str, list[str]]] = {"render_modes": []}

    def __init__(
        self,
        *,
        observation_size: tuple[int, int] = (160, 90),
        fps: float = 60.0,
        frame_skip: int = 4,
        frame_stack: int = 1,
        max_steps: int = 900,
        reset_timeout: float = 3.0,
        reset_settle: float = 1.0,
        reset_stable_frames: int = 3,
        focus_on_reset: bool = True,
        focus_on_action: bool = True,
        max_action_rate: float | None = 30.0,
        press_duration: float = DEFAULT_PRESS_DURATION,
        emergency_stop: EmergencyStop | None = None,
        platform_backend: PlatformBackend | None = None,
        capture_backend: CaptureBackend | None = None,
    ) -> None:
        """Create a pixel-based environment with validated timing settings."""
        if observation_size[0] <= 0 or observation_size[1] <= 0:
            raise ValueError("observation_size dimensions must be positive")
        if fps <= 0 or frame_skip <= 0 or frame_stack <= 0 or max_steps <= 0:
            raise ValueError(
                "fps, frame_skip, frame_stack, and max_steps must be positive"
            )
        if reset_timeout <= 0 or reset_settle < 0 or reset_stable_frames <= 0:
            raise ValueError(
                "reset_timeout must be positive, reset_settle cannot be negative, "
                "and reset_stable_frames must be positive"
            )
        if max_action_rate is not None and max_action_rate <= 0:
            raise ValueError("max_action_rate must be positive when configured")
        if not np.isfinite(press_duration) or not 0.0 < press_duration <= 1.0:
            raise ValueError(
                "press_duration must be finite and between 0 and 1 seconds"
            )
        self.observation_size = observation_size
        self.fps = fps
        self.frame_interval = 1.0 / fps
        self.frame_skip = frame_skip
        self.frame_stack = frame_stack
        self.max_steps = max_steps
        self.reset_timeout = reset_timeout
        self.reset_settle = reset_settle
        self.reset_stable_frames = reset_stable_frames
        self.focus_on_reset = focus_on_reset
        self.focus_on_action = focus_on_action
        self.max_action_rate = max_action_rate
        self.press_duration = press_duration
        self.emergency_stop = emergency_stop or EmergencyStop()
        self._screen: CaptureBackend = cast(CaptureBackend, capture_backend or MSS())
        self._platform = platform_backend or Win32Platform()
        self._state_machine = StateMachine()
        self._hwnd = None
        self._bbox: tuple[int, int, int, int] | None = None
        self._episode_active = False
        self._step_count = 0
        self._last_action_time: float | None = None
        self._closed = False
        self._frame_buffer: deque[np.ndarray] = deque(maxlen=frame_stack)
        self.action_space = gym.spaces.Discrete(2)
        observation_shape = (observation_size[1], observation_size[0], 3)
        if frame_stack > 1:
            observation_shape = (frame_stack, *observation_shape)
        self.observation_space = gym.spaces.Box(
            low=0,
            high=255,
            shape=observation_shape,
            dtype=np.uint8,
        )

    def close(self) -> None:
        """Release the screen-capture backend, safely and only once."""
        if not self._closed:
            self._screen.close()
            self._closed = True

    def __enter__(self) -> GeometryDashEnv:
        """Return this environment for context-manager use."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        """Close the environment when leaving a context-manager block."""
        del exc_type, exc_value, traceback
        self.close()

    def _ensure_window(self) -> None:
        game_path = self._platform.game_path
        validate_game_path(game_path, require_exists=True)
        self._hwnd = self._platform.find_game_window()
        if self._hwnd is None:
            raise RuntimeError(
                "No visible Geometry Dash window found. Start the game first."
            )
        if self.focus_on_reset:
            self._platform.focus_window(self._hwnd)
        self._bbox = self._platform.game_client_bbox(self._hwnd)

    def _capture(self) -> Image.Image:
        if self._hwnd is None:
            raise RuntimeError("Environment is not connected to a game window")
        if not self._platform.is_window(self._hwnd):
            try:
                self._ensure_window()
            except RuntimeError:
                self._episode_active = False
                raise
            if self._hwnd is None:
                self._episode_active = False
                raise RuntimeError("Geometry Dash window disappeared during capture")
        try:
            current_bbox = self._platform.game_client_bbox(self._hwnd)
        except RuntimeError:
            self._episode_active = False
            raise
        if current_bbox != self._bbox:
            previous_bbox = self._bbox
            self._bbox = current_bbox
            self._episode_active = False
            raise RuntimeError(
                "Geometry Dash client area changed during an episode; "
                f"previous_bbox={previous_bbox}, current_bbox={current_bbox}; "
                "reset required"
            )
        if self._bbox is None:
            raise RuntimeError("Geometry Dash client bounding box is unavailable")
        left, top, right, bottom = self._bbox
        shot = self._screen.grab(
            {"left": left, "top": top, "width": right - left, "height": bottom - top}
        )
        return Image.frombytes("RGB", shot.size, shot.rgb)

    def _single_observation(self, image: Image.Image) -> np.ndarray:
        resized = image.resize(self.observation_size, Image.Resampling.BILINEAR)
        return np.asarray(resized, dtype=np.uint8).copy()

    def _stacked_observation(self) -> np.ndarray:
        if self.frame_stack == 1:
            return self._frame_buffer[0].copy()
        return np.stack(tuple(self._frame_buffer), axis=0)

    def _reset_observation(self, image: Image.Image) -> np.ndarray:
        frame = self._single_observation(image)
        self._frame_buffer.clear()
        for _ in range(self.frame_stack):
            self._frame_buffer.append(frame.copy())
        return self._stacked_observation()

    def _observation(self, image: Image.Image) -> np.ndarray:
        self._frame_buffer.append(self._single_observation(image))
        return self._stacked_observation()

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
                    "Reset encountered the main menu; enter the target level "
                    "before retrying."
                )
            if last_state == "gameplay_or_transition":
                stable_frames += 1
                if stable_frames >= self.reset_stable_frames:
                    if self._state_machine.state in {
                        ScreenState.RESETTING,
                        ScreenState.RESULTS,
                    }:
                        self._state_machine.transition(
                            ScreenState.ATTEMPT_INTRO,
                            reason="level-like frame observed after reset",
                        )
                    self._state_machine.transition(
                        ScreenState.GAMEPLAY,
                        reason="gameplay frame stability threshold reached",
                    )
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

    def _enforce_action_rate(self) -> None:
        """Throttle dispatches so a control bug cannot flood the game."""

        if self.max_action_rate is None:
            self._last_action_time = time.monotonic()
            return
        interval = 1.0 / self.max_action_rate
        now = time.monotonic()
        if self._last_action_time is not None:
            remaining = interval - (now - self._last_action_time)
            if remaining > 0:
                time.sleep(remaining)
        self._last_action_time = time.monotonic()

    def _check_emergency_stop(self) -> None:
        """Stop the episode before dispatch if the operator latch is set."""

        if self.emergency_stop.requested:
            self._episode_active = False
            raise RuntimeError(
                "Emergency stop requested; episode halted and input suppressed"
            )

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, object] | None = None,
    ) -> tuple[np.ndarray, dict[str, object]]:
        """Start or retry an episode and return the first pixel observation."""

        if options:
            raise ValueError(
                "reset options are unsupported; pass None or an empty dictionary"
            )

        resettable_states = {
            ScreenState.DISCONNECTED,
            ScreenState.MAIN_MENU,
            ScreenState.RESULTS,
            ScreenState.LEVEL_COMPLETE,
            ScreenState.ERROR,
        }
        if self._state_machine.state not in resettable_states:
            raise RuntimeError(
                "Reset input is suppressed until a resettable state is validated "
                f"(screen_state={self._state_machine.state.value})"
            )
        super().reset(seed=seed)
        self._state_machine = StateMachine()
        self._state_machine.start(
            ScreenState.RESETTING,
            reason="reset requested",
        )
        self._ensure_window()
        hwnd = self._hwnd
        if hwnd is None:
            raise RuntimeError("Geometry Dash window disappeared during reset")
        image = self._capture()
        screen_state = classify_screen(image)
        if screen_state == "results":
            self._state_machine.transition(
                ScreenState.RESULTS,
                reason="results detector matched before reset click",
            )
            self._platform.click_client(hwnd)
            self._state_machine.transition(
                ScreenState.RESETTING,
                reason="retry clicked from results screen",
            )
            time.sleep(self.reset_settle)
            image = self._wait_for_ready_gameplay()
        elif screen_state == "gameplay_or_transition":
            self._state_machine.transition(
                ScreenState.ATTEMPT_INTRO,
                reason="level-like frame observed before reset wait",
            )
            image = self._wait_for_ready_gameplay()
        else:
            raise RuntimeError(
                "Reset requires a results screen or active level; "
                f"detected screen_state={screen_state}"
            )

        if self._state_machine.state == ScreenState.ATTEMPT_INTRO:
            self._state_machine.transition(
                ScreenState.GAMEPLAY,
                reason="reset wait returned a ready frame",
            )

        self._episode_active = True
        self._step_count = 0
        self._last_action_time = None
        transition = self._state_machine.history[-1]
        return self._reset_observation(image), {
            "environment_version": ENVIRONMENT_VERSION,
            "observation_contract_version": OBSERVATION_CONTRACT_VERSION,
            "observation_layout": OBSERVATION_LAYOUT,
            "action_contract_version": ACTION_CONTRACT_VERSION,
            "reward_contract_version": REWARD_CONTRACT_VERSION,
            "screen_state": self._state_machine.state.value,
            "previous_state": transition.previous.value,
            "transition_reason": transition.reason,
            "detector_confidence": transition.confidence,
            "observation_size": self.observation_size,
            "frame_skip": self.frame_skip,
            "frame_stack": self.frame_stack,
            "capture_bbox": self._bbox,
        }

    def step(
        self, action: int
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, object]]:
        """Apply one action and return observation, reward, and termination."""

        if not self._episode_active or self._hwnd is None:
            raise RuntimeError("Call reset() before step()")
        if self._state_machine.state != ScreenState.GAMEPLAY:
            self._episode_active = False
            raise RuntimeError(
                "Actions are suppressed outside GAMEPLAY "
                f"(screen_state={self._state_machine.state.value})"
            )
        hwnd = self._hwnd
        if not self.action_space.contains(action):
            raise ValueError("action must be 0 (no-op) or 1 (jump)")
        action = int(action)

        self._check_emergency_stop()
        self._enforce_action_rate()
        if action == 1:
            self._platform.send_jump(
                hwnd,
                ensure_focus=self.focus_on_action,
                press_duration=self.press_duration,
            )
        image: Image.Image | None = None
        terminated = False
        frames_elapsed = 0
        frame_deadline = time.perf_counter() + self.frame_interval
        for _ in range(self.frame_skip):
            self._check_emergency_stop()
            self._wait_for_frame_deadline(frame_deadline)
            image = self._capture()
            frames_elapsed += 1
            if is_death_screen(image):
                terminated = True
                self._state_machine.transition(
                    ScreenState.RESULTS,
                    reason="terminal results detector matched",
                )
                break
            frame_deadline += self.frame_interval

        if image is None:
            raise RuntimeError("No frame was captured during the environment step")

        self._step_count += 1
        truncated = not terminated and self._step_count >= self.max_steps
        if terminated or truncated:
            self._episode_active = False
        progress_ratio = results_progress_ratio(image) if terminated else None
        termination_reason = "results_screen" if terminated else None
        truncation_reason = "max_steps" if truncated else None
        reward_breakdown = calculate_reward(
            "death" if terminated else "truncation" if truncated else "alive",
            progress_ratio=progress_ratio,
        )
        return (
            self._observation(image),
            reward_breakdown.total,
            terminated,
            truncated,
            {
                "environment_version": ENVIRONMENT_VERSION,
                "observation_contract_version": OBSERVATION_CONTRACT_VERSION,
                "observation_layout": OBSERVATION_LAYOUT,
                "action_contract_version": ACTION_CONTRACT_VERSION,
                "reward_contract_version": REWARD_CONTRACT_VERSION,
                "screen_state": self._state_machine.state.value,
                "previous_state": (
                    self._state_machine.history[-1].previous.value
                    if self._state_machine.history
                    else None
                ),
                "transition_reason": (
                    self._state_machine.history[-1].reason
                    if self._state_machine.history
                    else None
                ),
                "detector_confidence": (
                    self._state_machine.history[-1].confidence
                    if self._state_machine.history
                    else None
                ),
                "frames_elapsed": frames_elapsed,
                "decision_step": self._step_count,
                "truncated": truncated,
                "termination_reason": termination_reason,
                "truncation_reason": truncation_reason,
                "progress_ratio": progress_ratio,
                "reward_components": reward_breakdown.as_dict(),
                "capture_bbox": self._bbox,
            },
        )
