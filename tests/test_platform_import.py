"""Tests that platform control stays inert until a live operation is requested."""

from __future__ import annotations

import unittest

from geometry_dash_env import platform_control


class PlatformImportTests(unittest.TestCase):
    """Protect offline imports from eager Win32 side effects."""

    def test_win32_libraries_are_lazy_loaded(self) -> None:
        """Importing the module must not open user32 or kernel32."""

        self.assertIsNone(platform_control.USER32)
        self.assertIsNone(platform_control.KERNEL32)


if __name__ == "__main__":
    unittest.main()
