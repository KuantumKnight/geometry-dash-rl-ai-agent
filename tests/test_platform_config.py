"""Tests for executable path discovery and validation."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from typing import Any, cast

from geometry_dash_env.platform_control import (
    resolve_game_path,
    select_game_window,
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


if __name__ == "__main__":
    unittest.main()
