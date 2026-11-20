"""
fastboot_manager.py — Full Fastboot wrapper for UniFlash Tool
"""

import subprocess
import threading
import re
from core.paths import resolve_fastboot_path
from typing import Callable, List, Optional


class FastbootManager:
    def __init__(self, fastboot_path: str = None):
        self.fastboot_path = fastboot_path or resolve_fastboot_path()

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _build_cmd(self, *args) -> List[str]:
        return [self.fastboot_path, *args]

    def _run_sync(self, *args, timeout: int = 30) -> subprocess.CompletedProcess:
        """Run fastboot synchronously and return CompletedProcess."""
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
        """Launch *cmd* in a background thread, streaming each output line to *callback*."""

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
                    callback(f"[FASTBOOT] Process exited with code {proc.returncode}")
            except FileNotFoundError:
                t.returncode = 127
                if callback:
                    callback(
                        f"[FASTBOOT ERROR] fastboot executable not found: {self.fastboot_path}"
                    )
            except Exception as exc:
                t.returncode = 1
                if callback:
                    callback(f"[FASTBOOT ERROR] {exc}")

        t = threading.Thread(target=_worker, daemon=True)
        t.cancel = lambda: getattr(t, "process", None) and t.process.terminate()
        t.start()
        return t

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def run(self, *args, callback: Optional[Callable[[str], None]] = None) -> threading.Thread:
        """Run an arbitrary fastboot command in a background thread, streaming output."""
        cmd = self._build_cmd(*args)
        return self._run_in_thread(cmd, callback)

    # ---- Device listing ------------------------------------------------ #

    def get_devices(self) -> List[str]:
        """Return list of device serials currently in fastboot mode."""
        try:
            result = self._run_sync("devices", timeout=10)
            serials: List[str] = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or line.startswith("List of devices"):
                    continue
                # fastboot devices output: "<serial>\tfastboot"
                parts = line.split()
                if parts:
                    serials.append(parts[0])
            return serials
        except Exception:
            return []

    # ---- Flash --------------------------------------------------------- #

    def flash(
        self,
        serial: str,
        partition: str,
        img_path: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """Flash an image to a named partition."""
        cmd = self._build_cmd("-s", serial, "flash", partition, img_path)
        return self._run_in_thread(cmd, callback)

    # ---- Erase --------------------------------------------------------- #

    def erase(
        self,
        serial: str,
        partition: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """Erase a named partition."""
        cmd = self._build_cmd("-s", serial, "erase", partition)
        return self._run_in_thread(cmd, callback)

    # ---- Reboot -------------------------------------------------------- #

    def reboot(
        self,
        serial: str,
        mode: str = "",
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """Reboot device.  mode can be '', 'bootloader', 'recovery', 'fastboot'."""
        cmd_parts = ["-s", serial, "reboot"]
        if mode:
            cmd_parts.append(mode)
        cmd = self._build_cmd(*cmd_parts)
        return self._run_in_thread(cmd, callback)

    # ---- Get variable -------------------------------------------------- #

    def get_var(self, serial: str, var: str) -> str:
        """Return the value of a fastboot variable (synchronous)."""
        try:
            result = self._run_sync("-s", serial, "getvar", var, timeout=10)
            # fastboot getvar output is on stderr, but we merge via STDOUT pipe
            for line in result.stdout.splitlines():
                line = line.strip()
                # Typical: "current-slot: a" or "OKAY [  0.044s]"
                if line.lower().startswith(var.lower() + ":"):
                    value = line.split(":", 1)[1].strip()
                    return value
            return ""
        except Exception:
            return ""

    # ---- OEM unlock ---------------------------------------------------- #

    def oem_unlock(
        self,
        serial: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """Send the OEM unlock command."""
        cmd = self._build_cmd("-s", serial, "oem", "unlock")
        return self._run_in_thread(cmd, callback)

    # ---- Update (factory zip) ------------------------------------------ #

    def update(
        self,
        serial: str,
        zip_path: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """Run 'fastboot update <zip>' — flashes a factory image zip."""
        cmd = self._build_cmd("-s", serial, "update", zip_path)
        return self._run_in_thread(cmd, callback)

    # ---- flash-all via XML --------------------------------------------- #

    def flash_all(
        self,
        serial: str,
        xml_path: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """Flash all partitions described in an XML flash-all manifest (Motorola style)."""
        # We parse the XML and issue individual flash commands sequentially in a thread.
        import xml.etree.ElementTree as ET
        import os

        base_dir = os.path.dirname(xml_path)

        def _worker():
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                # Common Motorola XML tags: <step operation="flash" partition="..." filename="..."/>
                steps = root.findall(".//step") or root.findall(".//Step")
                for step in steps:
                    operation = step.get("operation", "").lower()
                    partition = step.get("partition", "")
                    filename = step.get("filename", "")
                    if operation == "flash" and partition and filename:
                        img_path = os.path.join(base_dir, filename)
                        if callback:
                            callback(f"[FASTBOOT] Flashing {partition} ← {filename}")
                        proc = subprocess.run(
                            self._build_cmd("-s", serial, "flash", partition, img_path),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                        )
                        for line in proc.stdout.splitlines():
                            if callback:
                                callback(line)
                    elif operation == "erase" and partition:
                        if callback:
                            callback(f"[FASTBOOT] Erasing {partition}")
                        proc = subprocess.run(
                            self._build_cmd("-s", serial, "erase", partition),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                        )
                        for line in proc.stdout.splitlines():
                            if callback:
                                callback(line)
                    elif operation == "oem" and partition:
                        if callback:
                            callback(f"[FASTBOOT] OEM {partition}")
                        proc = subprocess.run(
                            self._build_cmd("-s", serial, "oem", partition),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                        )
                        for line in proc.stdout.splitlines():
                            if callback:
                                callback(line)
                if callback:
                    callback("[FASTBOOT] flash_all completed.")
            except FileNotFoundError as e:
                if callback:
                    callback(f"[FASTBOOT ERROR] XML or image not found: {e}")
            except Exception as exc:
                if callback:
                    callback(f"[FASTBOOT ERROR] flash_all failed: {exc}")

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        return t
