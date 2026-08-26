"""Windows window discovery and input control for Geometry Dash."""

from __future__ import annotations

import ctypes
import os
import time
from ctypes import wintypes
from pathlib import Path
from typing import Any

GAME_PATH_ENV = "GEOMETRY_DASH_EXE"
DEFAULT_GAME_PATH = Path.cwd() / "Geometry Dash" / "GeometryDash.exe"
GAME_PATH = Path(os.environ.get(GAME_PATH_ENV, DEFAULT_GAME_PATH)).expanduser()

VK_SPACE = 0x20
KEYEVENTF_KEYUP = 0x0002
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
SW_RESTORE = 9


class RECT(ctypes.Structure):
    """Win32 rectangle."""

    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class POINT(ctypes.Structure):
    """Win32 point."""

    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


_WIN32_AVAILABLE = os.name == "nt"
USER32: Any | None = None
KERNEL32: Any | None = None


def _load_win32() -> tuple[Any, Any]:
    """Load Win32 libraries only when a Windows operation is requested."""

    if not _WIN32_AVAILABLE:
        raise OSError("Geometry Dash platform control requires Windows")

    global KERNEL32, USER32
    if USER32 is None or KERNEL32 is None:
        USER32 = ctypes.WinDLL("user32", use_last_error=True)
        KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
        enum_windows_proc = ctypes.WINFUNCTYPE(
            wintypes.BOOL,
            wintypes.HWND,
            wintypes.LPARAM,
        )
        USER32.EnumWindows.argtypes = [enum_windows_proc, wintypes.LPARAM]
        USER32.EnumWindows.restype = wintypes.BOOL
        USER32.IsWindowVisible.argtypes = [wintypes.HWND]
        USER32.IsWindowVisible.restype = wintypes.BOOL
        USER32.IsIconic.argtypes = [wintypes.HWND]
        USER32.IsIconic.restype = wintypes.BOOL
        USER32.GetWindowThreadProcessId.argtypes = [
            wintypes.HWND,
            ctypes.POINTER(wintypes.DWORD),
        ]
        USER32.GetWindowThreadProcessId.restype = wintypes.DWORD
        USER32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
        USER32.GetClientRect.restype = wintypes.BOOL
        USER32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(POINT)]
        USER32.ClientToScreen.restype = wintypes.BOOL
        USER32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        USER32.SetForegroundWindow.argtypes = [wintypes.HWND]
        USER32.SetForegroundWindow.restype = wintypes.BOOL
        USER32.GetForegroundWindow.restype = wintypes.HWND
        USER32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
        USER32.SetCursorPos.restype = wintypes.BOOL
        USER32.mouse_event.argtypes = [
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.DWORD,
            ctypes.c_ulonglong,
        ]

        KERNEL32.OpenProcess.argtypes = [
            wintypes.DWORD,
            wintypes.BOOL,
            wintypes.DWORD,
        ]
        KERNEL32.OpenProcess.restype = wintypes.HANDLE
        KERNEL32.QueryFullProcessImageNameW.argtypes = [
            wintypes.HANDLE,
            wintypes.DWORD,
            wintypes.LPWSTR,
            ctypes.POINTER(wintypes.DWORD),
        ]
        KERNEL32.QueryFullProcessImageNameW.restype = wintypes.BOOL
        KERNEL32.CloseHandle.argtypes = [wintypes.HANDLE]
        KERNEL32.CloseHandle.restype = wintypes.BOOL

    return USER32, KERNEL32


def enable_dpi_awareness() -> None:
    """Keep Win32 window coordinates consistent with capture pixels."""

    user32, _ = _load_win32()
    try:
        shcore = ctypes.WinDLL("shcore", use_last_error=True)
        shcore.SetProcessDpiAwareness.argtypes = [ctypes.c_int]
        shcore.SetProcessDpiAwareness.restype = ctypes.HRESULT
        shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        user32.SetProcessDPIAware()


def normalized_path(path: Path) -> str:
    """Return a case-normalized absolute Windows path for comparison."""

    return os.path.normcase(str(path.resolve(strict=False)))


def window_process_path(hwnd: wintypes.HWND) -> Path | None:
    """Return the executable path that owns a top-level window."""

    _, kernel32 = _load_win32()
    process_id = wintypes.DWORD()
    user32, _ = _load_win32()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
    process_handle = kernel32.OpenProcess(
        PROCESS_QUERY_LIMITED_INFORMATION,
        False,
        process_id.value,
    )
    if not process_handle:
        return None

    try:
        buffer_size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(buffer_size.value)
        if not kernel32.QueryFullProcessImageNameW(
            process_handle,
            0,
            buffer,
            ctypes.byref(buffer_size),
        ):
            return None
        return Path(buffer.value)
    finally:
        kernel32.CloseHandle(process_handle)


def find_game_window() -> wintypes.HWND | None:
    """Find a visible top-level window owned by the configured executable."""

    user32, _ = _load_win32()
    target_path = normalized_path(GAME_PATH)
    matching_windows: list[wintypes.HWND] = []

    enum_windows_proc = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HWND,
        wintypes.LPARAM,
    )

    @enum_windows_proc
    def visit_window(hwnd: wintypes.HWND, _lparam: wintypes.LPARAM) -> bool:
        if user32.IsWindowVisible(hwnd):
            process_path = window_process_path(hwnd)
            if process_path and normalized_path(process_path) == target_path:
                matching_windows.append(hwnd)
                return False
        return True

    user32.EnumWindows(visit_window, 0)
    return matching_windows[0] if matching_windows else None


def focus_window(hwnd: wintypes.HWND) -> None:
    """Restore and focus the game window before capture or input."""

    user32, _ = _load_win32()
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.25)


def focus_window_if_needed(hwnd: wintypes.HWND) -> None:
    """Restore focus only when another window owns the foreground."""

    user32, _ = _load_win32()
    if user32.GetForegroundWindow() != hwnd:
        focus_window(hwnd)


def game_client_bbox(hwnd: wintypes.HWND) -> tuple[int, int, int, int]:
    """Return the game client area in screen coordinates."""

    user32, _ = _load_win32()
    client_rect = RECT()
    origin = POINT()
    if not user32.GetClientRect(hwnd, ctypes.byref(client_rect)):
        raise ctypes.WinError(ctypes.get_last_error())
    if not user32.ClientToScreen(hwnd, ctypes.byref(origin)):
        raise ctypes.WinError(ctypes.get_last_error())

    width = client_rect.right - client_rect.left
    height = client_rect.bottom - client_rect.top
    if width <= 0 or height <= 0:
        raise RuntimeError("Geometry Dash window has no visible client area")
    return (origin.x, origin.y, origin.x + width, origin.y + height)


def send_key(hwnd: wintypes.HWND, virtual_key: int) -> None:
    """Send one key press, restoring focus only if it was lost."""

    user32, _ = _load_win32()
    focus_window_if_needed(hwnd)
    user32.keybd_event(virtual_key, 0, 0, 0)
    time.sleep(0.005)
    user32.keybd_event(virtual_key, 0, KEYEVENTF_KEYUP, 0)


def send_jump(hwnd: wintypes.HWND) -> None:
    """Send a short space-bar press to the focused game window."""

    send_key(hwnd, VK_SPACE)


def click_client(
    hwnd: wintypes.HWND,
    relative_x: float = 0.29,
    relative_y: float = 0.82,
) -> None:
    """Click a normalized point inside the focused game client area."""

    user32, _ = _load_win32()
    left, top, right, bottom = game_client_bbox(hwnd)
    x = left + round((right - left) * relative_x)
    y = top + round((bottom - top) * relative_y)
    focus_window(hwnd)
    user32.SetCursorPos(x, y)
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
