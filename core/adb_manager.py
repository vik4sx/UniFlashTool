"""
adb_manager.py — Full ADB wrapper for UniFlash Tool
"""

import subprocess
import threading
import os
import re
from core.paths import resolve_adb_path
from typing import Callable, List, Tuple, Optional, Dict


class ADBManager:
    def __init__(self, adb_path: str = None):
        self.adb_path = adb_path or resolve_adb_path()

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _build_cmd(self, *args) -> List[str]:
        return [self.adb_path, *args]

    def _run_sync(self, *args, timeout: int = 30) -> subprocess.CompletedProcess:
        """Run an ADB command synchronously and return the CompletedProcess."""
        cmd = self._build_cmd(*args)
        return subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )

    def _run_in_thread(
        self,
        cmd: List[str],
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """Launch *cmd* in a background thread, streaming each line to *callback*."""

        def _worker():
            t.returncode = None
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                t.process = proc
                for line in proc.stdout:
                    line = line.rstrip("\n\r")
                    if callback:
                        callback(line)
                proc.wait()
                t.returncode = proc.returncode
                if callback:
                    callback(f"[ADB] Process exited with code {proc.returncode}")
            except FileNotFoundError:
                t.returncode = 127
                if callback:
                    callback(f"[ADB ERROR] adb executable not found: {self.adb_path}")
            except Exception as exc:
                t.returncode = 1
                if callback:
                    callback(f"[ADB ERROR] {exc}")

        t = threading.Thread(target=_worker, daemon=True)
        t.cancel = lambda: getattr(t, "process", None) and t.process.terminate()
        t.start()
        return t

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def run(self, *args, callback: Optional[Callable[[str], None]] = None) -> threading.Thread:
        """Run an arbitrary adb command in a background thread, streaming output."""
        cmd = self._build_cmd(*args)
        return self._run_in_thread(cmd, callback)

    # ---- Device listing ------------------------------------------------ #

    def get_devices(self) -> List[Tuple[str, str]]:
        """Return list of (serial, state) from 'adb devices'."""
        try:
            result = self._run_sync("devices")
            devices: List[Tuple[str, str]] = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or line.startswith("List of devices"):
                    continue
                parts = line.split("\t")
                if len(parts) == 2:
                    serial, state = parts[0].strip(), parts[1].strip()
                    devices.append((serial, state))
            return devices
        except Exception as exc:
            return []

    # ---- Properties ---------------------------------------------------- #

    def get_prop(self, serial: str, prop: str) -> str:
        """Return the string value of a device property via getprop."""
        try:
            result = self._run_sync("-s", serial, "shell", "getprop", prop, timeout=10)
            return result.stdout.strip()
        except Exception:
            return ""

    def get_all_props(self, serial: str) -> Dict[str, str]:
        """Return a dict of all ro.* properties from the device."""
        try:
            result = self._run_sync("-s", serial, "shell", "getprop", timeout=15)
            props: Dict[str, str] = {}
            # getprop output format: [key]: [value]
            pattern = re.compile(r"^\[([^\]]+)\]:\s*\[([^\]]*)\]$")
            for line in result.stdout.splitlines():
                m = pattern.match(line.strip())
                if m:
                    key, value = m.group(1), m.group(2)
                    if key.startswith("ro."):
                        props[key] = value
            return props
        except Exception:
            return {}

    # ---- Reboot -------------------------------------------------------- #

    def reboot(self, serial: str, mode: str = "") -> None:
        """Reboot device.  mode can be '', 'recovery', 'bootloader', 'fastboot'."""
        cmd_args = ["-s", serial, "reboot"]
        if mode:
            cmd_args.append(mode)
        self._run_sync(*cmd_args, timeout=15)

    # ---- Sideload ------------------------------------------------------ #

    def sideload(
        self,
        serial: str,
        zip_path: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """Run 'adb sideload <zip_path>' in a background thread."""
        cmd = self._build_cmd("-s", serial, "sideload", zip_path)
        return self._run_in_thread(cmd, callback)

    # ---- Push ---------------------------------------------------------- #

    def push(
        self,
        serial: str,
        local: str,
        remote: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """Push a local file/dir to remote path on device."""
        cmd = self._build_cmd("-s", serial, "push", local, remote)
        return self._run_in_thread(cmd, callback)

    # ---- Shell --------------------------------------------------------- #

    def shell(
        self,
        serial: str,
        *args,
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """Run an arbitrary shell command on device."""
        cmd = self._build_cmd("-s", serial, "shell", *args)
        return self._run_in_thread(cmd, callback)

    # ---- Server management --------------------------------------------- #

    def kill_server(self) -> None:
        """Kill the ADB server."""
        try:
            self._run_sync("kill-server", timeout=10)
        except Exception:
            pass

    def start_server(self) -> None:
        """Start the ADB server."""
        try:
            self._run_sync("start-server", timeout=15)
        except Exception:
            pass
