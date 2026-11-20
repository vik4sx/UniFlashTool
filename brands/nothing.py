"""
Nothing Phone brand flash handler.

Nothing Phone runs near-stock Android (Nothing OS) and uses standard
AOSP fastboot procedures — identical to Google Pixel in approach.
Bootloader unlock is done through Developer Options.
"""
import os
from .base_handler import BaseBrandHandler


class NothingHandler(BaseBrandHandler):
    """Flash handler for Nothing Phone devices (Nothing OS / AOSP)."""

    # ------------------------------------------------------------------ #
    # BaseBrandHandler overrides                                           #
    # ------------------------------------------------------------------ #

    def requires_unlocked_bootloader(self) -> bool:
        return True

    def get_flash_instructions(self) -> str:
        return (
            "Nothing Phone flashing steps:\n"
            "1. Standard Android fastboot — no special tools required.\n"
            "2. Enable 'OEM unlocking' in Developer Options.\n"
            "3. Boot to Fastboot mode: power off, hold Power + Vol Down.\n"
            "4. Unlock the bootloader:\n"
            "   fastboot flashing unlock\n"
            "   (This wipes all user data — back up first!)\n"
            "5. Flash using UniFlash:\n"
            "   - Full factory .zip via fastboot update\n"
            "   - Individual partition .img via fastboot flash\n"
            "6. Factory images and OTA packages available from:\n"
            "   https://nothing.tech/pages/update  or community mirrors.\n"
            "7. First boot after unlock may take 3–5 minutes."
        )

    def flash(self, file_path: str, options: dict, callback) -> bool:
        """
        Flash firmware to a Nothing Phone via fastboot.

        Routing logic:
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
            log(f"[Nothing] ERROR: File not found: {file_path}")
            return False

        ext = os.path.splitext(file_path)[1].lower()
        partition = (options or {}).get("partition", "")

        try:
            if ext == ".img":
                if not partition:
                    log("[Nothing] ERROR: 'partition' option is required for .img files.")
                    return False
                log(f"[Nothing] fastboot flash {partition} {file_path}")
                self.fastboot.flash(self.serial, partition, file_path, callback=callback)
                log("[Nothing] Flash completed successfully.")
                return True

            elif ext == ".zip":
                log(f"[Nothing] Running fastboot update (standard AOSP): {file_path}")
                self.fastboot.update(self.serial, file_path, callback=callback)
                log("[Nothing] fastboot update completed successfully.")
                return True

            else:
                log(f"[Nothing] ERROR: Unsupported file type '{ext}'. Use .img or .zip.")
                return False

        except Exception as exc:
            log(f"[Nothing] Flash failed: {exc}")
            return False
