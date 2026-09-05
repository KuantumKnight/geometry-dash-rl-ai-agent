"""Verify public tool help and parser exit-code contracts."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_TOOLS = (
    "baseline_agent.py",
    "benchmark_detector_offline.py",
    "benchmark_env.py",
    "capture_action.py",
    "evaluate_detector.py",
    "profile_env_step.py",
    "record_frames.py",
    "reset_episode.py",
    "scan_episode.py",
    "stress_reset.py",
    "verify_capture_stability.py",
)


class CliHelpTests(unittest.TestCase):
    def run_tool(self, tool: str, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["GEOMETRY_DASH_EXE"] = str(
            ROOT / "missing-game" / "GeometryDash.exe"
        )
        return subprocess.run(
            [sys.executable, str(ROOT / "tools" / tool), *arguments],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_every_public_tool_exposes_help(self) -> None:
        for tool in PUBLIC_TOOLS:
            with self.subTest(tool=tool):
                result = self.run_tool(tool, "--help")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(result.stdout.strip(), tool)

    def test_every_public_parser_rejects_unknown_options_with_code_two(self) -> None:
        for tool in PUBLIC_TOOLS:
            with self.subTest(tool=tool):
                result = self.run_tool(tool, "--definitely-invalid")
                self.assertEqual(result.returncode, 2, result.stderr)


if __name__ == "__main__":
    unittest.main()
