"""
ASUS brand flash handler.

Supports standard fastboot flash and ASUS Rescue Mode (ADB sideload).
"""
import os
from .base_handler import BaseBrandHandler


class AsusHandler(BaseBrandHandler):
    """Flash handler for ASUS devices (ROG Phone, Zenfone, etc.)."""

    # ------------------------------------------------------------------ #
    # BaseBrandHandler overrides                                           #
    # ------------------------------------------------------------------ #

    def requires_unlocked_bootloader(self) -> bool:
        return True

    def get_flash_instructions(self) -> str:
        return (
            "ASUS device flashing steps:\n"
            "1. Standard Fastboot:\n"
            "   a. Enable USB debugging and OEM unlocking in Developer Options.\n"
            "   b. Boot to Fastboot: power off, hold Power + Vol Down.\n"
            "   c. Unlock bootloader: fastboot flashing unlock\n"
            "2. ASUS Rescue Mode (alternative for some models):\n"
            "   a. Power off the device completely.\n"
            "   b. Hold Vol Down while connecting the USB cable to trigger Rescue Mode.\n"
            "   c. The ASUS Rescue Tool (Windows) or ADB sideload may be used.\n"
            "3. ROG Phone and Zenfone models may differ — check your model's specific guide\n"
            "   at https://www.asus.com/support/\n"
            "4. Factory firmware available from:\n"
            "   https://www.asus.com/support/ → select your model → Firmware."
        )

    def flash(self, file_path: str, options: dict, callback) -> bool:
        """
        Flash firmware to an ASUS device.

        Routing logic:
          - .img  → fastboot flash <partition> <img>
          - .zip  → fastboot update <zip>  OR  adb sideload (depending on 'mode' option)

        Args:
            file_path: Path to .img or .zip firmware file.
            options: Dict with optional keys:
                       'partition' (str) — required for .img files
                       'mode'      (str) — 'sideload' to force ADB sideload for .zip
            callback: Callable(str) for log output.

        Returns:
            True on success, False on failure.
        """
        def log(msg: str):
            if callback:
                callback(msg)

        if not os.path.isfile(file_path):
            log(f"[ASUS] ERROR: File not found: {file_path}")
            return False

        ext = os.path.splitext(file_path)[1].lower()
        partition = (options or {}).get("partition", "")
        mode = (options or {}).get("mode", "fastboot").lower()

        try:
            if ext == ".img":
                if not partition:
                    log("[ASUS] ERROR: 'partition' option is required for .img files.")
                    return False
                log(f"[ASUS] fastboot flash {partition} {file_path}")
                self.fastboot.flash(self.serial, partition, file_path, callback=callback)
                log("[ASUS] Flash completed successfully.")
                return True

            elif ext == ".zip":
                if mode == "sideload":
                    log(f"[ASUS] Using ADB sideload (Rescue Mode) for: {file_path}")
                    log("[ASUS] Ensure device is in ASUS Rescue Mode / ADB Sideload mode.")
                    self.adb.sideload(self.serial, file_path, callback=callback)
                    log("[ASUS] Sideload completed successfully.")
                else:
                    log(f"[ASUS] Running fastboot update: {file_path}")
                    self.fastboot.update(self.serial, file_path, callback=callback)
                    log("[ASUS] fastboot update completed successfully.")
                return True

            else:
                log(f"[ASUS] ERROR: Unsupported file type '{ext}'. Use .img or .zip.")
                return False

        except Exception as exc:
            log(f"[ASUS] Flash failed: {exc}")
            return False
