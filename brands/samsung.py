"""
Samsung brand flash handler.

Supports ADB sideload (.zip) and warns about Odin-only .tar.md5 files.
Samsung devices do NOT require an unlocked bootloader for OTA sideloads.
"""
import os
from .base_handler import BaseBrandHandler


class SamsungHandler(BaseBrandHandler):
    """Flash handler for Samsung devices."""

    # ------------------------------------------------------------------ #
    # BaseBrandHandler overrides                                           #
    # ------------------------------------------------------------------ #

    def requires_unlocked_bootloader(self) -> bool:
        return False  # ADB sideload works without bootloader unlock

    def get_driver_url(self) -> str:
        return "https://developer.samsung.com/mobile/android-usb-driver.html"

    def get_flash_instructions(self) -> str:
        return (
            "Samsung device flashing steps:\n"
            "1. Enable USB debugging in Developer Options.\n"
            "2. Enter Download Mode: hold Vol Down + Home + Power simultaneously\n"
            "   (or Vol Down + Bixby/Power on newer models) until the warning screen\n"
            "   appears, then press Vol Up to confirm.\n"
            "3. For Recovery/Sideload: power off, hold Vol Up + Home + Power to boot\n"
            "   into Recovery, choose 'Apply update from ADB'.\n"
            "4. .tar.md5 files require Odin (Windows only) — not supported here.\n"
            "5. Connect the device via USB and proceed with flashing."
        )

    def flash(self, file_path: str, options: dict, callback) -> bool:
        """
        Flash a firmware file to a Samsung device.

        Supports:
          - .zip  → ADB sideload
          - .tar.md5 → warns the user; Odin format is not natively supported.

        Args:
            file_path: Path to the firmware file.
            options: Optional dict (unused for Samsung sideload).
            callback: Callable(str) for log output.

        Returns:
            True on success, False on failure.
        """
        def log(msg: str):
            if callback:
                callback(msg)

        if not os.path.isfile(file_path):
            log(f"[Samsung] ERROR: File not found: {file_path}")
            return False

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".tar" or file_path.lower().endswith(".tar.md5"):
            log(
                "[Samsung] WARNING: .tar.md5 files are Odin format.\n"
                "          Odin flashing requires the Odin tool on Windows and is\n"
                "          NOT supported by UniFlash. Please use Odin3 or Odin4\n"
                "          from Samsung's official channels.\n"
                "          Aborting."
            )
            return False

        if ext == ".zip":
            log(f"[Samsung] Starting ADB sideload: {file_path}")
            log("[Samsung] Make sure device is in 'ADB Sideload' mode (Recovery → Apply update from ADB).")
            try:
                self.adb.sideload(self.serial, file_path, callback=callback)
                log("[Samsung] Sideload complete.")
                return True
            except Exception as exc:
                log(f"[Samsung] Sideload failed: {exc}")
                return False

        log(f"[Samsung] ERROR: Unsupported file type '{ext}'. Only .zip (sideload) is supported.")
        return False

    # ------------------------------------------------------------------ #
    # Samsung-specific extras                                              #
    # ------------------------------------------------------------------ #

    def supports_odin_format(self) -> bool:
        """
        Indicate whether Odin .tar.md5 format is relevant for this device.

        UniFlash itself cannot flash Odin packages, but callers can use this
        flag to show an informational message to the user.
        """
        return True  # The format exists; we just warn and refuse to flash it
