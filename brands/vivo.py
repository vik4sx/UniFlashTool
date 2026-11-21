"""
Vivo / iQOO brand flash handler.

Uses fastboot flash for partition images.
Bootloader must be unlocked via Vivo developer settings.
"""
import os
from .base_handler import BaseBrandHandler


class VivoHandler(BaseBrandHandler):
    """Flash handler for Vivo and iQOO devices."""

    # ------------------------------------------------------------------ #
    # BaseBrandHandler overrides                                           #
    # ------------------------------------------------------------------ #

    def requires_unlocked_bootloader(self) -> bool:
        return True

    def get_flash_instructions(self) -> str:
        return (
            "Vivo / iQOO device flashing steps:\n"
            "1. Enable Fastboot mode from Developer Settings:\n"
            "   Settings → Developer Options → Turn on USB debugging.\n"
            "   Some Vivo models: dial *#*#112#*#* to access the Engineer menu.\n"
            "2. Unlock the bootloader:\n"
            "   - In Developer Options, enable 'OEM unlocking' (if available).\n"
            "   - Some Vivo models require contacting Vivo support for an unlock token.\n"
            "   - iQOO models: Developers Options → Bootloader unlock.\n"
            "3. Boot to Fastboot mode: power off, hold Power + Vol Down.\n"
            "4. Connect via USB — device should appear as a fastboot device.\n"
            "5. Flash using UniFlash. For A/B devices, select the inactive slot."
        )

    def flash(self, file_path: str, options: dict, callback) -> bool:
        """
        Flash firmware to a Vivo / iQOO device via fastboot.

        Supports:
          - .img  → fastboot flash <partition> <img>
          - .zip  → fastboot update <zip>

        Args:
            file_path: Path to .img or .zip firmware file.
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
            log(f"[Vivo] ERROR: File not found: {file_path}")
            return False

        ext = os.path.splitext(file_path)[1].lower()
        partition = (options or {}).get("partition", "")

        try:
            if ext == ".img":
                if not partition:
                    log("[Vivo] ERROR: 'partition' option is required for .img files.")
                    return False
                log(f"[Vivo] fastboot flash {partition} {file_path}")
                self.fastboot.flash(self.serial, partition, file_path, callback=callback)
                log("[Vivo] Flash completed successfully.")
                return True

            elif ext == ".zip":
                log(f"[Vivo] Running fastboot update: {file_path}")
                self.fastboot.update(self.serial, file_path, callback=callback)
                log("[Vivo] fastboot update completed successfully.")
                return True

            else:
                log(f"[Vivo] ERROR: Unsupported file type '{ext}'. Use .img or .zip.")
                return False

        except Exception as exc:
            log(f"[Vivo] Flash failed: {exc}")
            return False
