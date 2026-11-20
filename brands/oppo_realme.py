"""
OPPO and Realme brand flash handlers.

Both brands share the same ColorOS recovery sideload approach.
Supports .zip and .ozip firmware packages via ADB sideload.
Bootloader unlock is NOT required for sideloading official OTA packages.
"""
import os
from .base_handler import BaseBrandHandler


class OppoHandler(BaseBrandHandler):
    """Flash handler for OPPO devices (ColorOS)."""

    # ------------------------------------------------------------------ #
    # BaseBrandHandler overrides                                           #
    # ------------------------------------------------------------------ #

    def requires_unlocked_bootloader(self) -> bool:
        return False  # Official ColorOS OTAs sideload without unlock

    def supports_sideload(self) -> bool:
        return True

    def get_flash_instructions(self) -> str:
        return (
            "OPPO device flashing steps:\n"
            "1. Enable USB debugging in Developer Options.\n"
            "2. Download a compatible ColorOS firmware package (.zip or .ozip).\n"
            "3. Enter ColorOS Recovery:\n"
            "   - Power off, then hold Power + Vol Down (device-specific).\n"
            "   - On some models: dial *#801# in the dialer and select Recovery.\n"
            "4. In Recovery, choose 'Install from USB' or 'ADB Sideload'.\n"
            "5. Connect via USB and proceed in UniFlash.\n"
            "6. .ozip packages are encrypted; use official ColorOS tools if sideload fails.\n"
            "7. Do NOT interrupt power during flashing."
        )

    def flash(self, file_path: str, options: dict, callback) -> bool:
        """
        Flash firmware to an OPPO device via ADB sideload.

        Supports:
          - .zip  → standard ADB sideload
          - .ozip → ADB sideload (accepted by ColorOS recovery natively)

        Args:
            file_path: Path to .zip or .ozip firmware file.
            options: Unused for OPPO sideload.
            callback: Callable(str) for log output.

        Returns:
            True on success, False on failure.
        """
        return _sideload_oppo_realme(
            brand="OPPO",
            serial=self.serial,
            adb=self.adb,
            file_path=file_path,
            callback=callback,
        )


class RealmeHandler(BaseBrandHandler):
    """Flash handler for Realme devices (Realme UI / ColorOS-based)."""

    # ------------------------------------------------------------------ #
    # BaseBrandHandler overrides                                           #
    # ------------------------------------------------------------------ #

    def requires_unlocked_bootloader(self) -> bool:
        return False  # Realme OTA sideloads don't need unlock

    def supports_sideload(self) -> bool:
        return True

    def get_flash_instructions(self) -> str:
        return (
            "Realme device flashing steps:\n"
            "1. Enable USB debugging in Developer Options.\n"
            "2. Download the correct Realme UI / ColorOS firmware package (.zip or .ozip).\n"
            "3. Enter Realme Recovery:\n"
            "   - Power off, hold Power + Vol Down.\n"
            "4. Select 'ADB Sideload' in the recovery menu.\n"
            "5. Connect via USB and proceed in UniFlash.\n"
            "6. .ozip files are accepted directly by Realme recovery.\n"
            "7. Do NOT interrupt power during flashing."
        )

    def flash(self, file_path: str, options: dict, callback) -> bool:
        """
        Flash firmware to a Realme device via ADB sideload.

        Supports:
          - .zip  → ADB sideload
          - .ozip → ADB sideload (Realme recovery handles decryption)

        Args:
            file_path: Path to .zip or .ozip firmware file.
            options: Unused.
            callback: Callable(str) for log output.

        Returns:
            True on success, False on failure.
        """
        return _sideload_oppo_realme(
            brand="Realme",
            serial=self.serial,
            adb=self.adb,
            file_path=file_path,
            callback=callback,
        )


# ------------------------------------------------------------------ #
# Shared sideload implementation                                        #
# ------------------------------------------------------------------ #

def _sideload_oppo_realme(brand: str, serial: str, adb, file_path: str, callback) -> bool:
    """
    Shared ADB sideload logic for OPPO and Realme devices.

    Args:
        brand: Display name for log messages ('OPPO' or 'Realme').
        serial: Device serial number.
        adb: ADBManager instance.
        file_path: Path to .zip or .ozip file.
        callback: Log callback.

    Returns:
        True on success, False on failure.
    """
    def log(msg: str):
        if callback:
            callback(msg)

    if not os.path.isfile(file_path):
        log(f"[{brand}] ERROR: File not found: {file_path}")
        return False

    ext = os.path.splitext(file_path)[1].lower()

    if ext not in (".zip", ".ozip"):
        log(f"[{brand}] ERROR: Unsupported file type '{ext}'. Use .zip or .ozip.")
        return False

    log(f"[{brand}] Starting ADB sideload: {file_path}")
    log(f"[{brand}] Make sure device is in Recovery → 'ADB Sideload' mode.")

    if ext == ".ozip":
        log(
            f"[{brand}] NOTE: .ozip is an encrypted ColorOS package.\n"
            f"         The recovery will handle decryption automatically.\n"
            f"         If sideload fails, decrypt using official ColorOS tools first."
        )

    try:
        adb.sideload(serial, file_path, callback=callback)
        log(f"[{brand}] Sideload completed successfully.")
        return True
    except Exception as exc:
        log(f"[{brand}] Sideload failed: {exc}")
        return False
