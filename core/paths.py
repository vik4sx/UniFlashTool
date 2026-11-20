"""
UniFlash Tool — Paths and Executable Resolver
Works seamlessly in both Python script execution and PyInstaller standalone .exe mode.
"""

import sys
import os
import shutil


def get_project_root() -> str:
    """Return root directory, handling PyInstaller _MEIPASS extraction folder."""
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_adb_path() -> str:
    """Find adb.exe in bundled tools, next to exe, C:\\adb, or in system PATH."""
    root = get_project_root()
    candidates = [
        os.path.join(root, "tools", "platform-tools", "adb.exe"),
        r"C:\adb\adb.exe",
    ]
    if getattr(sys, 'frozen', False):
        candidates.insert(1, os.path.join(os.path.dirname(sys.executable), "tools", "platform-tools", "adb.exe"))

    for c in candidates:
        if c and os.path.isfile(c):
            return c

    system_path = shutil.which("adb")
    if system_path:
        return system_path

    return candidates[0]


def resolve_fastboot_path() -> str:
    """Find fastboot.exe in bundled tools, next to exe, C:\\adb, or in system PATH."""
    root = get_project_root()
    candidates = [
        os.path.join(root, "tools", "platform-tools", "fastboot.exe"),
        r"C:\adb\fastboot.exe",
    ]
    if getattr(sys, 'frozen', False):
        candidates.insert(1, os.path.join(os.path.dirname(sys.executable), "tools", "platform-tools", "fastboot.exe"))

    for c in candidates:
        if c and os.path.isfile(c):
            return c

    system_path = shutil.which("fastboot")
    if system_path:
        return system_path

    return candidates[0]
