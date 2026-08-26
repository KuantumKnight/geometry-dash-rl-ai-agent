"""Tests for executable path discovery and validation."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from geometry_dash_env.platform_control import resolve_game_path, validate_game_path


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


if __name__ == "__main__":
    unittest.main()
