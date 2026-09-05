"""Tests for executable path discovery and validation."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock, call, patch

from geometry_dash_env.platform_control import (
    click_client,
    resolve_game_path,
    select_game_window,
    send_key,
    validate_client_bbox,
    validate_game_path,
)


class PlatformConfigTests(unittest.TestCase):
    """Keep executable configuration deterministic and explicit."""

    def test_relative_path_is_normalized_to_absolute(self) -> None:
        """Relative overrides resolve without changing the configured target."""

        resolved = resolve_game_path(Path("Geometry Dash") / "GeometryDash.exe")
        self.assertTrue(resolved.is_absolute())
        self.assertEqual(resolved.name, "GeometryDash.exe")

    def test_validation_rejects_non_executable_paths(self) -> None:
        """Only Windows executable paths are accepted by the live adapter."""

        with self.assertRaisesRegex(ValueError, r"\.exe"):
            validate_game_path("game.dll")

    def test_validation_can_require_existing_file(self) -> None:
        """Existence checks are opt-in so discovery remains testable offline."""

        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "GeometryDash.exe"
            executable.touch()
            self.assertEqual(
                os.path.normcase(
                    str(validate_game_path(executable, require_exists=True))
                ),
                os.path.normcase(str(executable.resolve(strict=False))),
            )

    def test_multiple_matching_windows_fail_closed(self) -> None:
        """Ambiguous live targets require operator cleanup before input."""

        with self.assertRaisesRegex(RuntimeError, "Multiple visible"):
            select_game_window(cast(Any, [1, 2]))

    def test_single_matching_window_is_selected(self) -> None:
        """A single process-owned visible window is safe to select."""

        self.assertEqual(select_game_window(cast(Any, [42])), 42)

    def test_client_bbox_rejects_minimized_window(self) -> None:
        """Minimized windows cannot provide valid pixels."""

        with self.assertRaisesRegex(RuntimeError, "minimized"):
            validate_client_bbox((0, 0, 800, 600), minimized=True)

    def test_client_bbox_rejects_off_screen_area(self) -> None:
        """Capture must remain inside the virtual desktop bounds."""

        with self.assertRaisesRegex(RuntimeError, "outside"):
            validate_client_bbox(
                (0, 0, 1200, 600),
                screen_bounds=(0, 0, 800, 600),
            )

    def test_client_bbox_rejects_non_foreground_window(self) -> None:
        """A covered/non-foreground client is unsafe to sample."""

        with self.assertRaisesRegex(RuntimeError, "occluded"):
            validate_client_bbox((0, 0, 800, 600), foreground=False)

    def test_reset_click_restores_cursor_position(self) -> None:
        """Normalized reset clicks do not leave the user's cursor displaced."""

        user32 = MagicMock()

        def get_cursor(pointer: Any) -> bool:
            pointer._obj.x = 11
            pointer._obj.y = 22
            return True

        user32.GetCursorPos.side_effect = get_cursor
        with (
            patch(
                "geometry_dash_env.platform_control._load_win32",
                return_value=(user32, MagicMock()),
            ),
            patch(
                "geometry_dash_env.platform_control.game_client_bbox",
                return_value=(0, 0, 100, 100),
            ),
            patch("geometry_dash_env.platform_control.focus_window"),
            patch("geometry_dash_env.platform_control.time.sleep"),
        ):
            click_client(cast(Any, 123))

        self.assertEqual(
            user32.SetCursorPos.call_args_list,
            [call(29, 82), call(11, 22)],
        )

    def test_reset_click_rejects_invalid_normalized_coordinates(self) -> None:
        """Calibration errors fail before any live Win32 operation."""

        for relative_x, relative_y in (
            (-0.01, 0.82),
            (1.01, 0.82),
            (0.29, float("nan")),
            (0.29, float("inf")),
        ):
            with (
                self.subTest(relative_x=relative_x, relative_y=relative_y),
                patch("geometry_dash_env.platform_control._load_win32") as load_win32,
                self.assertRaisesRegex(ValueError, "between 0 and 1"),
            ):
                click_client(
                    cast(Any, 123),
                    relative_x=relative_x,
                    relative_y=relative_y,
                )

            load_win32.assert_not_called()

    def test_key_press_duration_is_forwarded_and_validated(self) -> None:
        """Short press timing is explicit and rejects unsafe values."""

        user32 = MagicMock()
        with (
            patch(
                "geometry_dash_env.platform_control._load_win32",
                return_value=(user32, MagicMock()),
            ),
            patch("geometry_dash_env.platform_control.focus_window_if_needed"),
            patch("geometry_dash_env.platform_control.time.sleep") as sleep,
        ):
            send_key(cast(Any, 123), 0x20, press_duration=0.012)

        sleep.assert_called_once_with(0.012)
        self.assertEqual(user32.keybd_event.call_count, 2)

        for invalid_duration in (0.0, -0.001, 1.001, float("nan")):
            with (
                self.subTest(invalid_duration=invalid_duration),
                patch("geometry_dash_env.platform_control._load_win32") as load_win32,
                self.assertRaisesRegex(ValueError, "press_duration"),
            ):
                send_key(
                    cast(Any, 123),
                    0x20,
                    press_duration=invalid_duration,
                )
            load_win32.assert_not_called()


if __name__ == "__main__":
    unittest.main()
