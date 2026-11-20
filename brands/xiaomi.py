"""
Xiaomi / Redmi / POCO brand flash handler.

Uses fastboot flash with automatic A/B slot detection.
Bootloader MUST be unlocked via Mi Unlock Tool before flashing.
"""
import os
from .base_handler import BaseBrandHandler


class XiaomiHandler(BaseBrandHandler):
    """Flash handler for Xiaomi, Redmi, and POCO devices."""

    # ------------------------------------------------------------------ #
    # BaseBrandHandler overrides                                           #
    # ------------------------------------------------------------------ #

    def requires_unlocked_bootloader(self) -> bool:
        return True

    def get_driver_url(self) -> str:
        return "https://xiaomifirmwareupdater.com/drivers/"

    def get_flash_instructions(self) -> str:
        return (
            "Xiaomi / Redmi / POCO flashing steps:\n"
            "1. Unlock the bootloader FIRST using the official Mi Unlock Tool\n"
            "   (requires Mi account binding + 72–168-hour waiting period).\n"
            "2. Enable USB debugging and OEM unlocking in Developer Options.\n"
            "3. Boot to Fastboot mode: power off, then hold Power + Vol Down.\n"
            "4. Connect via USB — the device should appear as a fastboot device.\n"
            "5. For A/B (seamless update) devices, UniFlash detects the active slot\n"
            "   automatically and flashes the inactive slot.\n"
            "6. Reboot after flashing; first boot may take 3–5 minutes."
        )

    def flash(self, file_path: str, options: dict, callback) -> bool:
        """
        Flash firmware to a Xiaomi device via fastboot.

        Supports:
          - .img  → fastboot flash <partition> <img>
          - .zip  → fastboot update <zip>  (or per-partition from extracted zip)

        A/B slot detection is performed automatically.

        Args:
            file_path: Path to the firmware image or zip.
            options: Dict with optional keys:
                       'partition' (str) — target partition for .img files
                       'wipe'      (bool) — wipe userdata after flash
            callback: Callable(str) for log output.

        Returns:
            True on success, False on failure.
        """
        def log(msg: str):
            if callback:
                callback(msg)

        if not os.path.isfile(file_path):
            log(f"[Xiaomi] ERROR: File not found: {file_path}")
            return False

        ext = os.path.splitext(file_path)[1].lower()
        partition = (options or {}).get("partition", "")
        wipe = bool((options or {}).get("wipe", False))

        # Detect A/B slot
        try:
            slot = self.get_ab_slot(self.serial)
            if slot:
                log(f"[Xiaomi] A/B device detected. Current slot: {slot}")
            else:
                log("[Xiaomi] Non-A/B (single-slot) device detected.")
        except Exception as exc:
            log(f"[Xiaomi] WARNING: Could not detect slot ({exc}). Proceeding without slot info.")
            slot = None

        try:
            if ext == ".img":
                if not partition:
                    log("[Xiaomi] ERROR: 'partition' option is required when flashing a .img file.")
                    return False

                # On A/B devices, flash to the inactive slot partition
                target_partition = partition
                if slot:
                    other_slot = "b" if slot == "a" else "a"
                    # Only append slot suffix if the partition name doesn't already have one
                    if not (partition.endswith("_a") or partition.endswith("_b")):
                        target_partition = f"{partition}_{other_slot}"
                        log(f"[Xiaomi] Flashing to inactive slot partition: {target_partition}")

                log(f"[Xiaomi] fastboot flash {target_partition} {file_path}")
                self.fastboot.flash(self.serial, target_partition, file_path, callback=callback)

            elif ext == ".zip":
                log(f"[Xiaomi] Running fastboot update: {file_path}")
                extra_args = []
                if wipe:
                    log("[Xiaomi] --wipe flag set: userdata will be erased.")
                    extra_args.append("--wipe")
                self.fastboot.update(self.serial, file_path, callback=callback)

            else:
                log(f"[Xiaomi] ERROR: Unsupported file type '{ext}'. Use .img or .zip.")
                return False

            log("[Xiaomi] Flash completed successfully.")
            return True

        except Exception as exc:
            log(f"[Xiaomi] Flash failed: {exc}")
            return False

    # ------------------------------------------------------------------ #
    # Xiaomi-specific helpers                                              #
    # ------------------------------------------------------------------ #

    def get_ab_slot(self, serial: str) -> str:
        """
        Query the current A/B boot slot via fastboot.

        Args:
            serial: Device serial number (fastboot).

        Returns:
            'a' or 'b' if the device is A/B, empty string if single-slot,
            or raises RuntimeError on communication failure.
        """
        try:
            result = self.fastboot.get_var(serial, "current-slot")
            if result and result.strip() in ("a", "b"):
                return result.strip()
            return ""
        except Exception as exc:
            raise RuntimeError(f"Failed to query current-slot: {exc}") from exc
