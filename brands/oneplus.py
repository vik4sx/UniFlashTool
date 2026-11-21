"""
OnePlus brand flash handler.

Supports both ADB sideload (.zip via Recovery) and fastboot flash (.img).
Bootloader unlock is required for fastboot operations.
"""
import os
from .base_handler import BaseBrandHandler


class OnePlusHandler(BaseBrandHandler):
    """Flash handler for OnePlus devices."""

    # ------------------------------------------------------------------ #
    # BaseBrandHandler overrides                                           #
    # ------------------------------------------------------------------ #

    def requires_unlocked_bootloader(self) -> bool:
        # Required for fastboot; sideload works without it on some models
        return True

    def get_flash_instructions(self) -> str:
        return (
            "OnePlus device flashing steps:\n"
            "1. For ADB Sideload (.zip):\n"
            "   a. Boot to Recovery: power off, hold Power + Vol Up.\n"
            "   b. Select 'Install from USB' or 'ADB Sideload'.\n"
            "   c. Connect via USB and proceed.\n"
            "2. For Fastboot (.img files):\n"
            "   a. Unlock the bootloader first via Developer Options → OEM unlocking.\n"
            "   b. Boot to Fastboot mode: power off, hold Power + Vol Up.\n"
            "   c. Connect via USB — device should appear as fastboot.\n"
            "3. OxygenOS ZIPs can be sideloaded; full factory images use fastboot.\n"
            "4. After unlock, all user data is wiped — back up first."
        )

    def flash(self, file_path: str, options: dict, callback) -> bool:
        """
        Flash firmware to a OnePlus device.

        Routing logic:
          - .zip  → ADB sideload (Recovery mode)
          - .img  → fastboot flash <partition>

        Args:
            file_path: Path to the firmware file.
            options: Dict with optional keys:
                       'partition' (str) — required for .img files
                       'wipe'      (bool) — wipe userdata (fastboot update path)
            callback: Callable(str) for log output.

        Returns:
            True on success, False on failure.
        """
        def log(msg: str):
            if callback:
                callback(msg)

        if not os.path.isfile(file_path):
            log(f"[OnePlus] ERROR: File not found: {file_path}")
            return False

        ext = os.path.splitext(file_path)[1].lower()
        partition = (options or {}).get("partition", "")

        try:
            if ext == ".zip":
                log(f"[OnePlus] Detected .zip — using ADB sideload.")
                log("[OnePlus] Ensure device is in Recovery → 'ADB Sideload' mode.")
                self.adb.sideload(self.serial, file_path, callback=callback)
                log("[OnePlus] Sideload completed successfully.")
                return True

            elif ext == ".img":
                if not partition:
                    log("[OnePlus] ERROR: 'partition' option is required when flashing a .img file.")
                    return False
                log(f"[OnePlus] Detected .img — using fastboot flash.")
                log(f"[OnePlus] fastboot flash {partition} {file_path}")
                self.fastboot.flash(self.serial, partition, file_path, callback=callback)
                log("[OnePlus] Fastboot flash completed successfully.")
                return True

            else:
                log(f"[OnePlus] ERROR: Unsupported file type '{ext}'. Use .zip (sideload) or .img (fastboot).")
                return False

        except Exception as exc:
            log(f"[OnePlus] Flash failed: {exc}")
            return False
