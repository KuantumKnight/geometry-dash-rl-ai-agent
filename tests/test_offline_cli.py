"""Contract tests proving offline CLI help does not need the game installation."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OfflineCliTests(unittest.TestCase):
    def run_help(self, script: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["GEOMETRY_DASH_EXE"] = str(
            ROOT / "missing-game" / "GeometryDash.exe"
        )
        return subprocess.run(
            [sys.executable, str(ROOT / "tools" / script), "--help"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_episode_scan_help_is_offline(self) -> None:
        result = self.run_help("scan_episode.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("episode_dir", result.stdout)

    def test_detector_benchmark_help_is_offline(self) -> None:
        result = self.run_help("benchmark_detector_offline.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("frames-dir", result.stdout)


if __name__ == "__main__":
    unittest.main()
