"""Capture a screen frame and optionally send one jump action.

This is deliberately a manual, capture-only prototype. It never launches the
game. Start Geometry Dash yourself, focus its window, and use --action jump
only when you are ready to test input delivery.
"""

from __future__ import annotations

import argparse
import ctypes
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from ctypes import wintypes

from PIL import ImageGrab


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GAME_PATH = PROJECT_ROOT / "Geometry Dash" / "GeometryDash.exe"
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts" / "frames"
VK_SPACE = 0x20
KEYEVENTF_KEYUP = 0x0002
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
SW_RESTORE = 9


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


USER32 = ctypes.WinDLL("user32", use_last_error=True)
KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
ENUM_WINDOWS_PROC = ctypes.WINFUNCTYPE(
    wintypes.BOOL, wintypes.HWND, wintypes.LPARAM
)

USER32.EnumWindows.argtypes = [ENUM_WINDOWS_PROC, wintypes.LPARAM]
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

KERNEL32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
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


def enable_dpi_awareness() -> None:
    """Keep Win32 window coordinates consistent with Pillow screen pixels."""

    try:
        shcore = ctypes.WinDLL("shcore", use_last_error=True)
        shcore.SetProcessDpiAwareness.argtypes = [ctypes.c_int]
        shcore.SetProcessDpiAwareness.restype = ctypes.HRESULT
        shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware.
    except (AttributeError, OSError):
        USER32.SetProcessDPIAware()


enable_dpi_awareness()


def normalized_path(path: Path) -> str:
    return os.path.normcase(str(path.resolve(strict=False)))


def window_process_path(hwnd: wintypes.HWND) -> Path | None:
    process_id = wintypes.DWORD()
    USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
    process_handle = KERNEL32.OpenProcess(
        PROCESS_QUERY_LIMITED_INFORMATION, False, process_id.value
    )
    if not process_handle:
        return None

    try:
        buffer_size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(buffer_size.value)
        if not KERNEL32.QueryFullProcessImageNameW(
            process_handle, 0, buffer, ctypes.byref(buffer_size)
        ):
            return None
        return Path(buffer.value)
    finally:
        KERNEL32.CloseHandle(process_handle)


def find_game_window() -> wintypes.HWND | None:
    """Find a visible top-level window owned by the local game executable."""

    target_path = normalized_path(GAME_PATH)
    matching_window: list[wintypes.HWND] = []

    @ENUM_WINDOWS_PROC
    def visit_window(hwnd: wintypes.HWND, _lparam: wintypes.LPARAM) -> bool:
        # Minimized windows are still valid targets; focus_window() restores
        # them before we calculate the client-area bounding box.
        if USER32.IsWindowVisible(hwnd):
            process_path = window_process_path(hwnd)
            if process_path and normalized_path(process_path) == target_path:
                matching_window.append(hwnd)
                return False
        return True

    USER32.EnumWindows(visit_window, 0)
    return matching_window[0] if matching_window else None


def focus_window(hwnd: wintypes.HWND) -> None:
    """Restore and focus the game window before capture or input."""

    if USER32.IsIconic(hwnd):
        USER32.ShowWindow(hwnd, SW_RESTORE)
    USER32.SetForegroundWindow(hwnd)
    time.sleep(0.25)


def focus_window_if_needed(hwnd: wintypes.HWND) -> None:
    """Restore focus only when another window currently owns the foreground."""

    if USER32.GetForegroundWindow() != hwnd:
        focus_window(hwnd)


def game_client_bbox(hwnd: wintypes.HWND) -> tuple[int, int, int, int]:
    """Return the game client area in screen coordinates."""

    client_rect = RECT()
    origin = POINT()
    if not USER32.GetClientRect(hwnd, ctypes.byref(client_rect)):
        raise ctypes.WinError(ctypes.get_last_error())
    if not USER32.ClientToScreen(hwnd, ctypes.byref(origin)):
        raise ctypes.WinError(ctypes.get_last_error())

    width = client_rect.right - client_rect.left
    height = client_rect.bottom - client_rect.top
    if width <= 0 or height <= 0:
        raise RuntimeError("Geometry Dash window has no visible client area")
    return (origin.x, origin.y, origin.x + width, origin.y + height)


def send_key(hwnd: wintypes.HWND, virtual_key: int) -> None:
    """Send one key press, restoring focus only if it was lost."""

    focus_window_if_needed(hwnd)
    USER32.keybd_event(virtual_key, 0, 0, 0)
    time.sleep(0.005)
    USER32.keybd_event(virtual_key, 0, KEYEVENTF_KEYUP, 0)


def send_jump(hwnd: wintypes.HWND) -> None:
    """Send a short space-bar press to the already-focused game window."""

    send_key(hwnd, VK_SPACE)


def click_client(
    hwnd: wintypes.HWND, relative_x: float = 0.29, relative_y: float = 0.82
) -> None:
    """Click a normalized point inside the focused game client area."""

    left, top, right, bottom = game_client_bbox(hwnd)
    x = left + round((right - left) * relative_x)
    y = top + round((bottom - top) * relative_y)
    focus_window(hwnd)
    USER32.SetCursorPos(x, y)
    time.sleep(0.05)
    USER32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    USER32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def capture_frame(path: Path, hwnd: wintypes.HWND) -> tuple[int, int]:
    """Capture only the focused game's client area."""

    image = ImageGrab.grab(bbox=game_client_bbox(hwnd))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return image.size


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--action",
        choices=("noop", "jump"),
        default="noop",
        help="Action between the before and after captures (default: noop).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory for captured PNG frames.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not GAME_PATH.is_file():
        raise FileNotFoundError(f"Geometry Dash executable not found: {GAME_PATH}")

    print(f"Game executable found: {GAME_PATH}")
    print("Start Geometry Dash manually. Searching for its window in 3 seconds...")
    time.sleep(3)

    hwnd = find_game_window()
    if hwnd is None:
        raise RuntimeError(
            "No visible Geometry Dash window found. Start the game and try again."
        )
    focus_window(hwnd)
    print("Geometry Dash window found and focused.")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    before_path = args.output_dir / f"{timestamp}_before.png"
    after_path = args.output_dir / f"{timestamp}_after.png"

    before_size = capture_frame(before_path, hwnd)
    if args.action == "jump":
        print("Sending jump action: space bar")
        send_jump(hwnd)
    else:
        print("Sending no-op action")
    time.sleep(0.25)
    after_size = capture_frame(after_path, hwnd)

    print(f"Before frame: {before_path} ({before_size[0]}x{before_size[1]})")
    print(f"After frame:  {after_path} ({after_size[0]}x{after_size[1]})")


if __name__ == "__main__":
    main()
