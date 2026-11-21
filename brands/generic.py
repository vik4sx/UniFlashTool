"""
Generic / unknown brand flash handler.

Attempts ADB sideload first (for .zip files) and falls back to
fastboot flash for .img files.  Suitable for any standard Android device.
"""
import os
from .base_handler import BaseBrandHandler


class GenericHandler(BaseBrandHandler):
    """
    Fallback flash handler for unrecognised Android devices.

    Strategy:
      - .zip  → ADB sideload (try first)
      - .img  → fastboot flash <partition>
      - If sideload is unavailable, falls back to fastboot update for .zip
    """

    # ------------------------------------------------------------------ #
    # BaseBrandHandler overrides                                           #
    # ------------------------------------------------------------------ #

    def requires_unlocked_bootloader(self) -> bool:
        # May or may not be needed depending on the actual device
        return False

    def get_flash_instructions(self) -> str:
        return (
            "Generic Android device flashing steps:\n"
            "1. Enable USB debugging in Developer Options\n"
            "   (Settings → About Phone → tap Build Number 7 times → Developer Options).\n"
            "2. For ADB Sideload (.zip):\n"
            "   a. Boot to Recovery (Vol Up + Power, or device-specific combo).\n"
            "   b. Select 'Apply update from ADB' or 'ADB Sideload'.\n"
            "   c. Connect via USB and proceed.\n"
            "3. For Fastboot (.img):\n"
            "   a. Enable OEM unlocking and unlock the bootloader if required.\n"
            "   b. Boot to Fastboot (Vol Down + Power, or 'adb reboot bootloader').\n"
            "   c. Connect via USB and proceed.\n"
            "4. If neither method works, check your device's specific flashing guide."
        )

    def flash(self, file_path: str, options: dict, callback) -> bool:
        """
        Flash firmware to a generic Android device.

        Strategy:
          1. .zip → try ADB sideload; on failure, attempt fastboot update.
          2. .img → fastboot flash <partition> (requires 'partition' option).

        Args:
            file_path: Path to firmware .zip or partition .img.
            options: Dict with optional keys:
                       'partition' (str) — required for .img files
                       'force_fastboot' (bool) — skip sideload and use fastboot update for .zip
            callback: Callable(str) for log output.

        Returns:
            True on success, False on failure.
        """
        def log(msg: str):
            if callback:
                callback(msg)

        if not os.path.isfile(file_path):
            log(f"[Generic] ERROR: File not found: {file_path}")
            return False

        ext = os.path.splitext(file_path)[1].lower()
        partition = (options or {}).get("partition", "")
        force_fastboot = bool((options or {}).get("force_fastboot", False))

        try:
            if ext == ".zip":
                if force_fastboot:
                    return self._fastboot_update(file_path, log)

                # Try sideload first
                log(f"[Generic] Attempting ADB sideload: {file_path}")
                log("[Generic] Ensure device is in Recovery → 'ADB Sideload' mode.")
                try:
                    self.adb.sideload(self.serial, file_path, callback=callback)
                    log("[Generic] ADB sideload completed successfully.")
                    return True
                except Exception as sideload_exc:
                    log(f"[Generic] ADB sideload failed ({sideload_exc}). Falling back to fastboot update…")
                    return self._fastboot_update(file_path, log)

            elif ext == ".img":
                if not partition:
                    log("[Generic] ERROR: 'partition' option is required when flashing a .img file.")
                    return False
                log(f"[Generic] fastboot flash {partition} {file_path}")
                self.fastboot.flash(self.serial, partition, file_path, callback=callback)
                log("[Generic] Flash completed successfully.")
                return True

            else:
                log(
                    f"[Generic] ERROR: Unsupported file type '{ext}'.\n"
                    "          Use .zip (sideload/update) or .img (fastboot partition)."
                )
                return False

        except Exception as exc:
            log(f"[Generic] Flash failed: {exc}")
            return False

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _fastboot_update(self, zip_path: str, log) -> bool:
        """Run fastboot update and return success/failure."""
        log(f"[Generic] Running fastboot update: {zip_path}")
        log("[Generic] Ensure device is in Fastboot mode.")
        try:
            self.fastboot.update(self.serial, zip_path, callback=log)
            log("[Generic] fastboot update completed successfully.")
            return True
        except Exception as exc:
            log(f"[Generic] fastboot update failed: {exc}")
            return False
