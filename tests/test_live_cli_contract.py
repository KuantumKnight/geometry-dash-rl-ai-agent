"""Contract tests for safe, actionable live-command failures."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MISSING_GAME = ROOT / "missing-game" / "GeometryDash.exe"


class LiveCliContractTests(unittest.TestCase):
    def test_capture_fails_before_input_when_game_executable_is_missing(self) -> None:
        environment = os.environ.copy()
        environment["GEOMETRY_DASH_EXE"] = str(MISSING_GAME)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "capture_action.py"),
                "--action",
                "jump",
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Geometry Dash executable not found", result.stderr)
        self.assertIn(str(MISSING_GAME), result.stderr)


if __name__ == "__main__":
    unittest.main()
