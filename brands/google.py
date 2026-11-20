"""
Google Pixel brand flash handler.

Uses fastboot update for full factory .zip images and fastboot flash for
individual .img partition images.  Bootloader must be unlocked.
"""
import os
from .base_handler import BaseBrandHandler


class GoogleHandler(BaseBrandHandler):
    """Flash handler for Google Pixel devices."""

    # ------------------------------------------------------------------ #
    # BaseBrandHandler overrides                                           #
    # ------------------------------------------------------------------ #

    def requires_unlocked_bootloader(self) -> bool:
        return True

    def get_driver_url(self) -> str:
        return "https://developer.android.com/studio/run/win-usb"

    def get_flash_instructions(self) -> str:
        return (
            "Google Pixel device flashing steps:\n"
            "1. Download the correct factory image from:\n"
            "   https://developers.google.com/android/images\n"
            "   (match device codename and Android build number exactly)\n"
            "2. Enable OEM unlocking in Developer Options.\n"
            "3. Boot to Fastboot: power off, hold Power + Vol Down.\n"
            "4. Run: fastboot flashing unlock  (once; wipes all data)\n"
            "5. For a full factory image (.zip): UniFlash runs 'fastboot update'.\n"
            "6. For individual partitions (.img): select partition in UniFlash.\n"
            "7. After flashing, re-lock the bootloader if desired:\n"
            "   fastboot flashing lock"
        )

    def flash(self, file_path: str, options: dict, callback) -> bool:
        """
        Flash firmware to a Google Pixel device.

        Routing logic:
          - .zip  → fastboot update <zip>  (full factory image)
          - .img  → fastboot flash <partition> <img>

        Args:
            file_path: Path to factory .zip or partition .img.
            options: Dict with optional keys:
                       'partition' (str) — required when flashing a .img
                       'wipe'      (bool) — pass --skip-reboot or --wipe flag
            callback: Callable(str) for log output.

        Returns:
            True on success, False on failure.
        """
        def log(msg: str):
            if callback:
                callback(msg)

        if not os.path.isfile(file_path):
            log(f"[Google] ERROR: File not found: {file_path}")
            return False

        ext = os.path.splitext(file_path)[1].lower()
        partition = (options or {}).get("partition", "")

        try:
            if ext == ".zip":
                log(f"[Google] Detected factory image ZIP — running fastboot update.")
                log(f"[Google] fastboot update {file_path}")
                self.fastboot.update(self.serial, file_path, callback=callback)
                log("[Google] fastboot update completed successfully.")
                return True

            elif ext == ".img":
                if not partition:
                    log("[Google] ERROR: 'partition' option is required when flashing a .img file.")
                    return False
                log(f"[Google] Detected .img — running fastboot flash {partition}.")
                self.fastboot.flash(self.serial, partition, file_path, callback=callback)
                log("[Google] fastboot flash completed successfully.")
                return True

            else:
                log(f"[Google] ERROR: Unsupported file type '{ext}'. Use .zip (factory) or .img (partition).")
                return False

        except Exception as exc:
            log(f"[Google] Flash failed: {exc}")
            return False
