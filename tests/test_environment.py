from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import gymnasium as gym
import numpy as np
from PIL import Image, ImageDraw

from geometry_dash_env import (
    ACTION_CONTRACT_VERSION,
    ENVIRONMENT_VERSION,
    OBSERVATION_CONTRACT_VERSION,
    OBSERVATION_LAYOUT,
    REWARD_CONTRACT_VERSION,
    EmergencyStop,
    GeometryDashEnv,
    ScreenState,
    StateMachine,
)
from geometry_dash_env.game_state import is_death_screen

GAMEPLAY_IMAGE = Image.new("RGB", (800, 600), (25, 40, 165))


def results_image() -> Image.Image:
    image = Image.new("RGB", (800, 600), (0, 0, 0))
    ImageDraw.Draw(image).rectangle((80, 390, 720, 570), fill=(0, 255, 0))
    return image


class FakeScreen:
    def __init__(self) -> None:
        self.close_calls = 0

    def grab(self, monitor: Any) -> Any:
        del monitor
        return None

    def close(self) -> None:
        self.close_calls += 1


class FakePlatform:
    """Offline platform adapter used to exercise environment orchestration."""

    game_path = Path("fake-GeometryDash.exe")

    def __init__(self) -> None:
        self.game_path = (Path.cwd() / "Geometry Dash" / "GeometryDash.exe").resolve()
        self.bbox: tuple[int, int, int, int] = (0, 0, 800, 600)
        self.valid = True
        self.window_handle: Any = 123
        self.jump_calls: list[Any] = []
        self.jump_press_durations: list[float] = []
        self.click_calls: list[Any] = []

    def find_game_window(self):
        self.valid = True
        return self.window_handle

    def game_client_bbox(self, hwnd: Any) -> tuple[int, int, int, int]:
        del hwnd
        return self.bbox

    def is_window(self, hwnd: Any) -> bool:
        del hwnd
        return self.valid

    def focus_window(self, hwnd: Any) -> None:
        del hwnd
        pass

    def focus_window_if_needed(self, hwnd: Any) -> None:
        del hwnd
        pass

    def send_jump(
        self,
        hwnd: Any,
        *,
        ensure_focus: bool = True,
        press_duration: float = 0.005,
    ) -> None:
        self.jump_calls.append((hwnd, ensure_focus))
        self.jump_press_durations.append(press_duration)

    def click_client(self, hwnd) -> None:
        self.click_calls.append(hwnd)


class EnvironmentTests(unittest.TestCase):
    def make_env(self, **kwargs) -> GeometryDashEnv:
        self.platform = FakePlatform()
        env = GeometryDashEnv(
            platform_backend=self.platform,
            capture_backend=FakeScreen(),
            **kwargs,
        )
        self.addCleanup(env.close)
        return env

    def activate(self, env: GeometryDashEnv) -> None:
        env._episode_active = True
        env._hwnd = cast(Any, 123)
        env._bbox = (0, 0, 800, 600)
        env._state_machine = StateMachine()
        env._state_machine.start(ScreenState.RESETTING, reason="test reset")
        env._state_machine.transition(ScreenState.ATTEMPT_INTRO, reason="test intro")
        env._state_machine.transition(ScreenState.GAMEPLAY, reason="test gameplay")

    def test_spaces_match_observation_and_actions(self) -> None:
        env = self.make_env()
        action_space = cast(gym.spaces.Discrete, env.action_space)
        self.assertEqual(action_space.n, 2)
        self.assertEqual(env.observation_space.shape, (90, 160, 3))
        self.assertTrue(
            env.observation_space.contains(np.zeros((90, 160, 3), dtype=np.uint8))
        )

    def test_four_frame_stack_preserves_oldest_to_newest_order(self) -> None:
        env = self.make_env(frame_stack=4)
        first_image = Image.new("RGB", (800, 600), (10, 20, 30))
        second_image = Image.new("RGB", (800, 600), (200, 210, 220))

        initial = env._reset_observation(first_image)
        updated = env._observation(second_image)

        self.assertEqual(initial.shape, (4, 90, 160, 3))
        self.assertEqual(env.observation_space.shape, (4, 90, 160, 3))
        self.assertTrue(env.observation_space.contains(updated))
        np.testing.assert_array_equal(updated[0], initial[1])
        np.testing.assert_array_equal(
            updated[-1], env._single_observation(second_image)
        )

    def test_reset_smoke_returns_valid_observation(self) -> None:
        env = self.make_env(reset_settle=0)
        env._hwnd = cast(Any, 123)
        with (
            patch.object(env, "_ensure_window"),
            patch.object(env, "_capture", return_value=GAMEPLAY_IMAGE),
            patch(
                "geometry_dash_env.environment.classify_screen",
                return_value="gameplay_or_transition",
            ),
            patch.object(env, "_wait_for_ready_gameplay", return_value=GAMEPLAY_IMAGE),
        ):
            observation, info = env.reset(seed=7)

        self.assertEqual(observation.shape, (90, 160, 3))
        self.assertEqual(observation.dtype, np.uint8)
        self.assertTrue(env.observation_space.contains(observation))
        self.assertEqual(info["screen_state"], "gameplay")
        self.assertEqual(info["environment_version"], ENVIRONMENT_VERSION)
        self.assertEqual(
            info["observation_contract_version"], OBSERVATION_CONTRACT_VERSION
        )
        self.assertEqual(info["observation_layout"], OBSERVATION_LAYOUT)
        self.assertEqual(info["action_contract_version"], ACTION_CONTRACT_VERSION)
        self.assertEqual(info["reward_contract_version"], REWARD_CONTRACT_VERSION)

    def test_reset_rejects_main_menu(self) -> None:
        env = self.make_env()
        env._hwnd = cast(Any, 123)
        with (
            patch.object(env, "_ensure_window"),
            patch.object(env, "_capture", return_value=GAMEPLAY_IMAGE),
            patch(
                "geometry_dash_env.environment.classify_screen",
                return_value="main_menu",
            ),
            self.assertRaisesRegex(RuntimeError, "main_menu"),
        ):
            env.reset()

    def test_reset_rejects_unsupported_options(self) -> None:
        env = self.make_env()

        with self.assertRaisesRegex(ValueError, "options are unsupported"):
            env.reset(options={"level": "Stereo Madness"})

    def test_invalid_constructor_values_are_rejected(self) -> None:
        invalid_values: tuple[dict[str, Any], ...] = (
            {"observation_size": (0, 90)},
            {"fps": 0},
            {"frame_skip": 0},
            {"frame_stack": 0},
            {"max_steps": 0},
            {"reset_timeout": 0},
            {"reset_settle": -1},
            {"reset_stable_frames": 0},
            {"max_action_rate": 0},
            {"press_duration": 0},
            {"press_duration": float("nan")},
        )

        for kwargs in invalid_values:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                GeometryDashEnv(
                    platform_backend=FakePlatform(),
                    capture_backend=FakeScreen(),
                    **kwargs,
                )

    def test_close_is_idempotent_and_context_manager_safe(self) -> None:
        screen = FakeScreen()
        env = GeometryDashEnv(
            platform_backend=FakePlatform(),
            capture_backend=screen,
        )

        env.close()
        env.close()
        self.assertEqual(screen.close_calls, 1)

        with GeometryDashEnv(
            platform_backend=FakePlatform(),
            capture_backend=screen,
        ):
            pass
        self.assertEqual(screen.close_calls, 2)

    def test_invalid_actions_are_rejected_before_input(self) -> None:
        env = self.make_env(frame_skip=1)
        self.activate(env)

        for invalid_action in (2, 1.0, None):
            with (
                self.subTest(invalid_action=invalid_action),
                self.assertRaisesRegex(ValueError, "action must be"),
            ):
                env.step(cast(Any, invalid_action))
        self.assertEqual(self.platform.jump_calls, [])

    def test_jump_action_dispatches_space_and_returns_observation(self) -> None:
        env = self.make_env(frame_skip=4)
        self.activate(env)
        with (
            patch.object(env, "_wait_for_frame_deadline"),
            patch.object(env, "_capture", return_value=GAMEPLAY_IMAGE),
            patch("geometry_dash_env.environment.is_death_screen", return_value=False),
        ):
            observation, reward, terminated, truncated, info = env.step(1)

        self.assertEqual(self.platform.jump_calls, [(123, True)])
        self.assertEqual(info["requested_action"], 1)
        self.assertEqual(info["dispatched_action"], 1)
        self.assertIsInstance(info["action_dispatch_timestamp"], float)
        self.assertIsNone(info["suppressed_action"])
        self.assertEqual(self.platform.jump_press_durations, [0.005])
        self.assertEqual(observation.shape, (90, 160, 3))
        self.assertEqual(reward, 0.0)
        self.assertFalse(terminated)
        self.assertFalse(truncated)

    def test_time_limit_truncates_and_disables_episode(self) -> None:
        env = self.make_env(frame_skip=1, max_steps=1)
        self.activate(env)
        with (
            patch.object(env, "_wait_for_frame_deadline"),
            patch.object(env, "_capture", return_value=GAMEPLAY_IMAGE),
            patch("geometry_dash_env.environment.is_death_screen", return_value=False),
        ):
            _observation, _reward, terminated, truncated, info = env.step(0)

        self.assertFalse(terminated)
        self.assertTrue(truncated)
        self.assertEqual(info["decision_step"], 1)
        reward_components = cast(dict[str, float], info["reward_components"])
        self.assertEqual(reward_components["total"], 0.0)
        self.assertFalse(env._episode_active)

    def test_step_after_truncation_is_rejected(self) -> None:
        env = self.make_env(frame_skip=1, max_steps=1)
        self.activate(env)
        with (
            patch.object(env, "_wait_for_frame_deadline"),
            patch.object(env, "_capture", return_value=GAMEPLAY_IMAGE),
            patch("geometry_dash_env.environment.is_death_screen", return_value=False),
        ):
            env.step(0)

        with self.assertRaisesRegex(RuntimeError, "Call reset"):
            env.step(0)

        with self.assertRaisesRegex(RuntimeError, "resettable state"):
            env.reset()

    def test_terminal_reason_and_post_terminal_step_are_explicit(self) -> None:
        env = self.make_env(frame_skip=1)
        self.activate(env)
        with (
            patch.object(env, "_wait_for_frame_deadline"),
            patch.object(env, "_capture", return_value=results_image()),
            patch("geometry_dash_env.environment.is_death_screen", return_value=True),
            patch(
                "geometry_dash_env.environment.results_progress_ratio", return_value=0.5
            ),
        ):
            _observation, _reward, terminated, truncated, info = env.step(0)

        self.assertTrue(terminated)
        self.assertFalse(truncated)
        self.assertEqual(info["termination_reason"], "results_screen")
        self.assertIsNone(info["truncation_reason"])
        reward_components = cast(dict[str, float], info["reward_components"])
        self.assertEqual(reward_components["death"], -1.0)
        self.assertEqual(reward_components["progress"], 0.5)
        with self.assertRaisesRegex(RuntimeError, "Call reset"):
            env.step(0)

    def test_double_reset_is_rejected_while_episode_is_active(self) -> None:
        env = self.make_env(reset_settle=0)
        env._hwnd = cast(Any, 123)
        with (
            patch.object(env, "_ensure_window"),
            patch.object(env, "_capture", return_value=GAMEPLAY_IMAGE),
            patch(
                "geometry_dash_env.environment.classify_screen",
                return_value="gameplay_or_transition",
            ),
            patch.object(env, "_wait_for_ready_gameplay", return_value=GAMEPLAY_IMAGE),
        ):
            env.reset()

        with self.assertRaisesRegex(RuntimeError, "resettable state"):
            env.reset()

    def test_focus_on_action_is_explicitly_opt_in(self) -> None:
        """A caller can suppress automatic focus stealing for actions."""

        env = self.make_env(frame_skip=1, focus_on_action=False)
        self.activate(env)
        with (
            patch.object(env, "_wait_for_frame_deadline"),
            patch.object(env, "_capture", return_value=GAMEPLAY_IMAGE),
            patch("geometry_dash_env.environment.is_death_screen", return_value=False),
        ):
            env.step(1)

        self.assertEqual(self.platform.jump_calls, [(123, False)])

    def test_action_rate_limit_throttles_dispatches(self) -> None:
        """Configured action limits insert only the required wait."""

        env = self.make_env(frame_skip=1, max_action_rate=10.0)
        with (
            patch(
                "geometry_dash_env.environment.time.monotonic",
                side_effect=[1.0, 1.0, 1.05, 1.15],
            ),
            patch("geometry_dash_env.environment.time.sleep") as sleep,
        ):
            env._enforce_action_rate()
            env._enforce_action_rate()

        sleep.assert_called_once()
        self.assertAlmostEqual(sleep.call_args.args[0], 0.05, places=6)

    def test_emergency_stop_suppresses_actions(self) -> None:
        """An operator latch halts before any input dispatch."""

        stop = EmergencyStop()
        env = self.make_env(emergency_stop=stop)
        self.activate(env)
        stop.request()

        with self.assertRaisesRegex(RuntimeError, "Emergency stop"):
            env.step(1)

        self.assertEqual(self.platform.jump_calls, [])
        self.assertFalse(env._episode_active)

    def test_actions_are_suppressed_outside_gameplay(self) -> None:
        """Transition frames never receive normal jump/no-op actions."""

        env = self.make_env(frame_skip=1)
        env._episode_active = True
        env._hwnd = cast(Any, 123)
        env._state_machine = StateMachine()
        env._state_machine.start(ScreenState.RESETTING, reason="test reset")
        env._state_machine.transition(ScreenState.ATTEMPT_INTRO, reason="test intro")

        with self.assertRaisesRegex(RuntimeError, "outside GAMEPLAY"):
            env.step(1)

        self.assertEqual(self.platform.jump_calls, [])

    def test_reset_input_is_suppressed_from_active_gameplay(self) -> None:
        """Reset cannot click while a gameplay episode is still active."""

        env = self.make_env()
        self.activate(env)

        with self.assertRaisesRegex(RuntimeError, "resettable state"):
            env.reset()

        self.assertEqual(self.platform.click_calls, [])

    def test_death_detector_recognizes_results_and_rejects_gameplay(self) -> None:
        self.assertTrue(is_death_screen(results_image()))
        self.assertFalse(is_death_screen(GAMEPLAY_IMAGE))

    def test_terminal_reward_uses_progress_ratio(self) -> None:
        env = self.make_env(frame_skip=1)
        self.activate(env)
        with (
            patch.object(env, "_wait_for_frame_deadline"),
            patch.object(env, "_capture", return_value=results_image()),
            patch("geometry_dash_env.environment.is_death_screen", return_value=True),
            patch(
                "geometry_dash_env.environment.results_progress_ratio", return_value=0.5
            ),
        ):
            _observation, reward, terminated, truncated, info = env.step(0)

        self.assertEqual(reward, -0.5)
        self.assertTrue(terminated)
        self.assertFalse(truncated)
        self.assertEqual(info["screen_state"], "results")

    def test_deadline_waits_only_for_remaining_time(self) -> None:
        env = self.make_env()
        with (
            patch("geometry_dash_env.environment.time.perf_counter", return_value=10.0),
            patch("geometry_dash_env.environment.time.sleep") as sleep,
        ):
            env._wait_for_frame_deadline(10.25)
        sleep.assert_called_once()
        self.assertAlmostEqual(sleep.call_args.args[0], 0.25, places=6)

    def test_deadline_does_not_sleep_when_late(self) -> None:
        env = self.make_env()
        with (
            patch("geometry_dash_env.environment.time.perf_counter", return_value=10.5),
            patch("geometry_dash_env.environment.time.sleep") as sleep,
        ):
            env._wait_for_frame_deadline(10.25)
        sleep.assert_not_called()

    def test_capture_refreshes_moved_bbox(self) -> None:
        """A moved client area terminates safely instead of mixing pixels."""

        env = self.make_env()
        env._hwnd = cast(Any, 123)
        env._bbox = (0, 0, 800, 600)
        self.platform.bbox = (20, 30, 660, 510)
        shot = type("Shot", (), {"size": (640, 480), "rgb": b""})()
        with (
            patch.object(env._screen, "grab", return_value=shot),
            patch(
                "geometry_dash_env.environment.Image.frombytes",
                return_value=GAMEPLAY_IMAGE,
            ),
            self.assertRaisesRegex(RuntimeError, "changed.*reset required"),
        ):
            env._capture()
        self.assertEqual(env._bbox, (20, 30, 660, 510))
        self.assertFalse(env._episode_active)

    def test_capture_failure_deactivates_episode(self) -> None:
        """Focus and visibility failures cannot leave input enabled."""

        env = self.make_env()
        self.activate(env)
        with (
            patch.object(
                self.platform,
                "game_client_bbox",
                side_effect=RuntimeError("Geometry Dash window is not foreground"),
            ),
            self.assertRaisesRegex(RuntimeError, "not foreground"),
        ):
            env._capture()

        self.assertFalse(env._episode_active)

    def test_capture_reacquires_invalid_window_handle(self) -> None:
        """A restarted game is reacquired before the next capture."""

        env = self.make_env()
        env._hwnd = cast(Any, 123)
        env._bbox = (0, 0, 800, 600)
        self.platform.valid = False
        self.platform.window_handle = 456
        shot = type("Shot", (), {"size": (800, 600), "rgb": b""})()
        with (
            patch("geometry_dash_env.environment.validate_game_path"),
            patch.object(env._screen, "grab", return_value=shot),
            patch(
                "geometry_dash_env.environment.Image.frombytes",
                return_value=GAMEPLAY_IMAGE,
            ),
        ):
            env._capture()

        self.assertEqual(env._hwnd, 456)

    def test_reset_from_results_clicks_and_waits_for_gameplay(self) -> None:
        env = self.make_env(reset_settle=0, reset_stable_frames=1)
        env._hwnd = cast(Any, 123)
        with (
            patch("geometry_dash_env.environment.validate_game_path"),
            patch.object(env, "_capture", side_effect=[GAMEPLAY_IMAGE, GAMEPLAY_IMAGE]),
            patch(
                "geometry_dash_env.environment.classify_screen",
                side_effect=["results", "gameplay_or_transition"],
            ),
            patch("geometry_dash_env.environment.time.monotonic", side_effect=[0, 0]),
            patch("geometry_dash_env.environment.time.sleep"),
        ):
            _observation, info = env.reset()

        self.assertEqual(self.platform.click_calls, [123])
        self.assertEqual(info["screen_state"], "gameplay")
        self.assertTrue(env._episode_active)

    def test_reset_rejects_unknown_screen_state(self) -> None:
        env = self.make_env()
        env._hwnd = cast(Any, 123)
        with (
            patch.object(env, "_ensure_window"),
            patch.object(env, "_capture", return_value=GAMEPLAY_IMAGE),
            patch(
                "geometry_dash_env.environment.classify_screen",
                return_value="unknown",
            ),
            self.assertRaisesRegex(RuntimeError, "unknown"),
        ):
            env.reset()

    def test_capture_fails_when_reacquisition_finds_no_window(self) -> None:
        env = self.make_env()
        env._hwnd = cast(Any, 123)
        self.platform.valid = False
        self.platform.window_handle = None
        with (
            patch("geometry_dash_env.environment.validate_game_path"),
            self.assertRaisesRegex(RuntimeError, "No visible Geometry Dash window"),
        ):
            env._capture()

    def test_single_frame_observation_does_not_alias_internal_buffer(self) -> None:
        env = self.make_env()
        initial = env._reset_observation(GAMEPLAY_IMAGE)
        initial.fill(0)
        updated = env._observation(results_image())
        self.assertFalse(np.array_equal(updated, initial))

    def test_transition_timeout_is_bounded(self) -> None:
        env = self.make_env(reset_timeout=3)
        env._hwnd = cast(Any, 123)
        env._bbox = (0, 0, 800, 600)
        with (
            patch.object(env, "_capture", return_value=GAMEPLAY_IMAGE),
            patch(
                "geometry_dash_env.environment.classify_screen",
                return_value="unknown",
            ),
            patch(
                "geometry_dash_env.environment.time.monotonic",
                side_effect=[0, 4],
            ),
            self.assertRaisesRegex(TimeoutError, "stable gameplay"),
        ):
            env._wait_for_ready_gameplay()


if __name__ == "__main__":
    unittest.main()
