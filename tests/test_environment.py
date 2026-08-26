from __future__ import annotations

import unittest
from typing import Any, cast
from unittest.mock import patch

import gymnasium as gym
import numpy as np
from PIL import Image, ImageDraw

from geometry_dash_env import GeometryDashEnv
from geometry_dash_env.game_state import is_death_screen

GAMEPLAY_IMAGE = Image.new("RGB", (800, 600), (25, 40, 165))


def results_image() -> Image.Image:
    image = Image.new("RGB", (800, 600), (0, 0, 0))
    ImageDraw.Draw(image).rectangle((80, 390, 720, 570), fill=(0, 255, 0))
    return image


class FakeScreen:
    def grab(self, _monitor):
        return None

    def close(self) -> None:
        pass


class EnvironmentTests(unittest.TestCase):
    def make_env(self, **kwargs) -> GeometryDashEnv:
        with patch("geometry_dash_env.environment.MSS", return_value=FakeScreen()):
            env = GeometryDashEnv(**kwargs)
        self.addCleanup(env.close)
        return env

    def activate(self, env: GeometryDashEnv) -> None:
        env._episode_active = True
        env._hwnd = cast(Any, 123)
        env._bbox = (0, 0, 800, 600)

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
        self.assertEqual(info["screen_state"], "gameplay_or_transition")

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

    def test_jump_action_dispatches_space_and_returns_observation(self) -> None:
        env = self.make_env(frame_skip=1)
        self.activate(env)
        with (
            patch("geometry_dash_env.environment.send_jump") as send_jump,
            patch.object(env, "_wait_for_frame_deadline"),
            patch.object(env, "_capture", return_value=GAMEPLAY_IMAGE),
            patch("geometry_dash_env.environment.is_death_screen", return_value=False),
        ):
            observation, reward, terminated, truncated, _info = env.step(1)

        send_jump.assert_called_once_with(123)
        self.assertEqual(observation.shape, (90, 160, 3))
        self.assertEqual(reward, 0.0)
        self.assertFalse(terminated)
        self.assertFalse(truncated)

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
        env = self.make_env()
        env._hwnd = cast(Any, 123)
        env._bbox = (0, 0, 800, 600)
        shot = type("Shot", (), {"size": (640, 480), "rgb": b""})()
        with (
            patch(
                "geometry_dash_env.environment.game_client_bbox",
                return_value=(20, 30, 660, 510),
            ),
            patch.object(env._screen, "grab", return_value=shot),
            patch(
                "geometry_dash_env.environment.Image.frombytes",
                return_value=GAMEPLAY_IMAGE,
            ),
        ):
            env._capture()
        self.assertEqual(env._bbox, (20, 30, 660, 510))


if __name__ == "__main__":
    unittest.main()
