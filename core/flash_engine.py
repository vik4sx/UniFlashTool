"""
flash_engine.py — Flash orchestrator for UniFlash Tool
"""

from __future__ import annotations

import os
import threading
from typing import Callable, Dict, Optional

from core.adb_manager import ADBManager
from core.fastboot_manager import FastbootManager


class FlashEngine:
    """
    High-level orchestrator that delegates to ADBManager / FastbootManager.
    All public methods are non-blocking: they return a threading.Thread.
    """

    # Supported file extensions → type tokens
    _EXT_MAP: Dict[str, str] = {
        ".img": "img",
        ".zip": "zip",
        ".tar.md5": "tar.md5",
        ".ozip": "ozip",
        ".tar": "tar.md5",   # treat bare .tar the same as .tar.md5
    }

    def __init__(self, adb: ADBManager, fastboot: FastbootManager):
        self.adb = adb
        self.fastboot = fastboot

    # ------------------------------------------------------------------ #
    #  Sideload                                                            #
    # ------------------------------------------------------------------ #

    def flash_zip_sideload(
        self,
        serial: str,
        zip_path: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """
        Flash a ZIP package via 'adb sideload'.
        Device must already be in sideload/recovery mode.
        """
        if callback:
            callback(f"[FlashEngine] Starting ADB sideload: {zip_path}")
        return self.adb.sideload(serial, zip_path, callback=callback)

    # ------------------------------------------------------------------ #
    #  Single-partition fastboot flash                                     #
    # ------------------------------------------------------------------ #

    def flash_partition(
        self,
        serial: str,
        partition: str,
        img_path: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """
        Flash a single image to a named partition via fastboot.
        Device must already be in fastboot/bootloader mode.
        """
        if callback:
            callback(f"[FlashEngine] Flashing partition '{partition}' ← {img_path}")
        return self.fastboot.flash(serial, partition, img_path, callback=callback)

    # ------------------------------------------------------------------ #
    #  Multi-partition fastboot flash                                      #
    # ------------------------------------------------------------------ #

    def flash_all_partitions(
        self,
        serial: str,
        partition_dict: Dict[str, str],
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """
        Flash multiple partitions sequentially.
        partition_dict: {"boot": "/path/boot.img", "system": "/path/system.img", ...}
        Returns a thread that completes when all flashes are done.
        """

        def _worker():
            total = len(partition_dict)
            for idx, (partition, img_path) in enumerate(partition_dict.items(), start=1):
                if callback:
                    callback(
                        f"[FlashEngine] [{idx}/{total}] Flashing '{partition}' ← {img_path}"
                    )
                # Run synchronously within the worker thread
                import subprocess

                cmd = [self.fastboot.fastboot_path, "-s", serial, "flash", partition, img_path]
                try:
                    proc = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                    )
                    for line in proc.stdout:
                        if callback:
                            callback(line.rstrip("\n\r"))
                    proc.wait()
                    if callback:
                        callback(
                            f"[FlashEngine] '{partition}' exited with code {proc.returncode}"
                        )
                except Exception as exc:
                    if callback:
                        callback(f"[FlashEngine ERROR] {partition}: {exc}")
            if callback:
                callback("[FlashEngine] All partitions flashed.")

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        return t

    # ------------------------------------------------------------------ #
    #  Factory-image fastboot update                                       #
    # ------------------------------------------------------------------ #

    def flash_fastboot_update(
        self,
        serial: str,
        zip_path: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> threading.Thread:
        """
        Flash a factory image ZIP via 'fastboot update'.
        """
        if callback:
            callback(f"[FlashEngine] Starting fastboot update: {zip_path}")
        return self.fastboot.update(serial, zip_path, callback=callback)

    # ------------------------------------------------------------------ #
    #  Utilities                                                           #
    # ------------------------------------------------------------------ #

    def detect_file_type(self, path: str) -> str:
        """
        Return one of: "img", "zip", "tar.md5", "ozip", or "unknown".
        Multi-extension check handles '.tar.md5' correctly.
        """
        lower = path.lower()

        # Check compound extension first
        if lower.endswith(".tar.md5"):
            return "tar.md5"

        _, ext = os.path.splitext(lower)
        return self._EXT_MAP.get(ext, "unknown")

    def get_slot_info(self, serial: str) -> Optional[Dict[str, str]]:
        """
        Return {"current": "a", "other": "b"} for A/B devices via fastboot getvar.
        Returns None when the device is not A/B (slot-count == 1 or empty).
        Works regardless of whether the device is in ADB or fastboot mode,
        though fastboot is preferred for reliability.

        Strategy:
        1. Try fastboot getvar current-slot / slot-count.
        2. Fall back to ADB getprop ro.boot.slot_suffix / ro.build.ab_update.
        """
        # --- Attempt via fastboot ---
        slot_count_str = self.fastboot.get_var(serial, "slot-count")
        if slot_count_str not in ("", "0", "1"):
            current_slot = self.fastboot.get_var(serial, "current-slot").lstrip("_").lower()
            other_slot = "b" if current_slot == "a" else "a"
            return {"current": current_slot, "other": other_slot}

        # --- Attempt via ADB ---
        ab_update = self.adb.get_prop(serial, "ro.build.ab_update").lower()
        if ab_update == "true":
            slot_suffix = self.adb.get_prop(serial, "ro.boot.slot_suffix").lstrip("_").lower()
            if not slot_suffix:
                slot_suffix = "a"  # sensible default
            other_slot = "b" if slot_suffix == "a" else "a"
            return {"current": slot_suffix, "other": other_slot}

        return None
