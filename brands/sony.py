"""
Sony Xperia brand flash handler.

Uses fastboot flash for partition images.
Bootloader must be unlocked via Sony's official unlock portal.
"""
import os
from .base_handler import BaseBrandHandler


class SonyHandler(BaseBrandHandler):
    """Flash handler for Sony Xperia devices."""

    # ------------------------------------------------------------------ #
    # BaseBrandHandler overrides                                           #
    # ------------------------------------------------------------------ #

    def requires_unlocked_bootloader(self) -> bool:
        return True

    def get_flash_instructions(self) -> str:
        return (
            "Sony Xperia device flashing steps:\n"
            "1. Unlock the bootloader at:\n"
            "   https://developer.sony.com/open-devices/unlock-bootloader\n"
            "   Enter your IMEI (dial *#06#) and follow the instructions.\n"
            "2. Enable USB debugging and OEM unlocking in Developer Options.\n"
            "3. Boot to Fastboot mode:\n"
            "   - Power off, hold Vol Up, then connect USB cable while holding Vol Up.\n"
            "   - Blue LED indicates Fastboot mode on most Xperia models.\n"
            "4. Run: fastboot oem unlock <unlock_code>  (using code from Sony's site)\n"
            "5. Download open-devices firmware from:\n"
            "   https://developer.sony.com/open-source/aosp-on-xperia-open-devices\n"
            "6. Flash using UniFlash (fastboot flash per partition or full update)."
        )

    def flash(self, file_path: str, options: dict, callback) -> bool:
        """
        Flash firmware to a Sony Xperia device via fastboot.

        Supports:
          - .img  → fastboot flash <partition> <img>
          - .zip  → fastboot update <zip>

        Args:
            file_path: Path to .img or factory .zip.
            options: Dict with optional keys:
                       'partition' (str) — required for .img files
            callback: Callable(str) for log output.

        Returns:
            True on success, False on failure.
        """
        def log(msg: str):
            if callback:
                callback(msg)

        if not os.path.isfile(file_path):
            log(f"[Sony] ERROR: File not found: {file_path}")
            return False

        ext = os.path.splitext(file_path)[1].lower()
        partition = (options or {}).get("partition", "")

        try:
            if ext == ".img":
                if not partition:
                    log("[Sony] ERROR: 'partition' option is required for .img files.")
                    return False
                log(f"[Sony] fastboot flash {partition} {file_path}")
                self.fastboot.flash(self.serial, partition, file_path, callback=callback)
                log("[Sony] Flash completed successfully.")
                return True

            elif ext == ".zip":
                log(f"[Sony] Running fastboot update: {file_path}")
                self.fastboot.update(self.serial, file_path, callback=callback)
                log("[Sony] fastboot update completed successfully.")
                return True

            else:
                log(f"[Sony] ERROR: Unsupported file type '{ext}'. Use .img or .zip.")
                return False

        except Exception as exc:
            log(f"[Sony] Flash failed: {exc}")
            return False
