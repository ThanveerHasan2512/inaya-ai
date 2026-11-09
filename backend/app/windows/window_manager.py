import os
import sys
import time
import ctypes
from typing import List, Dict, Any, Optional

import psutil
try:
    import win32gui
    import win32process
    import win32con
    import win32service
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


def ensure_desktop() -> bool:
    """
    Ensures the current thread is attached to the interactive user desktop
    (WinSta0\\default) so window enumeration and foreground switching work.
    """
    if not HAS_WIN32:
        return False
    try:
        hdesk = win32service.OpenDesktop("default", 0, False, win32con.MAXIMUM_ALLOWED)
        if hdesk:
            ctypes.windll.user32.SetThreadDesktop(int(hdesk))
            return True
    except Exception:
        pass
    return False


def get_visible_windows() -> List[Dict[str, Any]]:
    """
    Enumerates all visible top-level application windows on the desktop.
    """
    ensure_desktop()
    windows = []

    if not HAS_WIN32:
        return windows

    def enum_cb(hwnd, _):
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd).strip()
                if title:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    # Get process name
                    pname = ""
                    try:
                        pname = psutil.Process(pid).name()
                    except Exception:
                        pass

                    # Filter out system utility windows (e.g., Program Manager)
                    if title not in ["Program Manager", "Default IME", "MSCTFIME UI"]:
                        windows.append({
                            "hwnd": hwnd,
                            "title": title,
                            "pid": pid,
                            "process_name": pname,
                        })
        except Exception:
            pass
        return True

    try:
        win32gui.EnumWindows(enum_cb, None)
    except Exception:
        pass

    return windows


def find_window_by_process(process_names: List[str], title_contains: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Finds a visible window matching any of the given process names or title substring.
    """
    ensure_desktop()
    visible = get_visible_windows()
    lower_names = [p.lower() for p in process_names]

    for win in visible:
        win_pname = win.get("process_name", "").lower()
        win_title = win.get("title", "").lower()

        # Check process name match
        if any(win_pname == p for p in lower_names):
            if not title_contains or title_contains.lower() in win_title:
                return win

        # Check title substring match
        if title_contains and title_contains.lower() in win_title:
            return win

    return None


def focus_window(hwnd: int) -> bool:
    """
    Brings a window to the foreground and un-minimizes it.
    """
    ensure_desktop()
    if not HAS_WIN32:
        return False
    try:
        # Restore if minimized
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.05)
        # Bring to foreground
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        return True
    except Exception:
        return False


def close_window(hwnd: int) -> bool:
    """
    Gracefully requests a window to close by posting WM_CLOSE.
    """
    ensure_desktop()
    if not HAS_WIN32:
        return False
    try:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        return True
    except Exception:
        return False


def close_process(process_name: str, force: bool = False) -> Dict[str, Any]:
    """
    Closes all processes matching process_name.
    First tries closing visible windows gracefully, then terminates if force=True.
    """
    closed_count = 0
    lower_name = process_name.lower()
    if not lower_name.endswith(".exe"):
        lower_name += ".exe"

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == lower_name:
                if force:
                    proc.kill()
                else:
                    proc.terminate()
                closed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return {
        "success": closed_count > 0,
        "process_name": process_name,
        "closed_count": closed_count,
        "message": f"Closed {closed_count} instances of {process_name}." if closed_count > 0 else f"No running instances of {process_name} found."
    }
