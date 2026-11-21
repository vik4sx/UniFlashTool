"""
Motorola brand flash handler.

Supports fastboot flash for individual .img files, as well as the
flash-all.xml / flash-all.bat approach used in Motorola factory packages.
Bootloader must be unlocked via motorola.com/unlock.
"""
import os
import xml.etree.ElementTree as ET
from .base_handler import BaseBrandHandler


class MotorolaHandler(BaseBrandHandler):
    """Flash handler for Motorola / Moto devices."""

    # ------------------------------------------------------------------ #
    # BaseBrandHandler overrides                                           #
    # ------------------------------------------------------------------ #

    def requires_unlocked_bootloader(self) -> bool:
        return True

    def get_flash_instructions(self) -> str:
        return (
            "Motorola device flashing steps:\n"
            "1. Unlock the bootloader at: https://motorola.com/unlock\n"
            "   (Requires a Motorola account; bootloader unlock code sent by email)\n"
            "2. Enable USB debugging and OEM unlocking in Developer Options.\n"
            "3. Boot to Fastboot mode: power off, hold Power + Vol Down.\n"
            "4. Run: fastboot oem unlock <unlock_code>  (using code from email)\n"
            "5. Download official factory images from:\n"
            "   https://mirrors.lolinet.com/firmware/moto/  or Motorola's support site.\n"
            "6. UniFlash supports:\n"
            "   - Individual .img partition flashing\n"
            "   - Full factory package via flash-all.xml\n"
            "7. First boot after unlock may take 5+ minutes."
        )

    def flash(self, file_path: str, options: dict, callback) -> bool:
        """
        Flash firmware to a Motorola device via fastboot.

        Routing logic:
          - .img           → fastboot flash <partition> <img>
          - .xml (flash-all.xml) → parse and flash each step
          - .zip           → fastboot update <zip>

        Args:
            file_path: Path to .img, flash-all.xml, or factory .zip.
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
            log(f"[Motorola] ERROR: File not found: {file_path}")
            return False

        ext = os.path.splitext(file_path)[1].lower()
        partition = (options or {}).get("partition", "")

        try:
            if ext == ".img":
                if not partition:
                    log("[Motorola] ERROR: 'partition' option required for .img files.")
                    return False
                log(f"[Motorola] fastboot flash {partition} {file_path}")
                self.fastboot.flash(self.serial, partition, file_path, callback=callback)
                log("[Motorola] Flash completed.")
                return True

            elif ext == ".xml":
                return self._flash_from_xml(file_path, callback)

            elif ext == ".zip":
                log(f"[Motorola] Running fastboot update: {file_path}")
                self.fastboot.update(self.serial, file_path, callback=callback)
                log("[Motorola] fastboot update completed.")
                return True

            else:
                log(f"[Motorola] ERROR: Unsupported file type '{ext}'. Use .img, .xml, or .zip.")
                return False

        except Exception as exc:
            log(f"[Motorola] Flash failed: {exc}")
            return False

    # ------------------------------------------------------------------ #
    # Motorola-specific helpers                                            #
    # ------------------------------------------------------------------ #

    def _flash_from_xml(self, xml_path: str, callback) -> bool:
        """
        Parse a Motorola flash-all.xml and execute each flash step.

        The XML schema used by Motorola factory packages looks like:
          <FlashFile>
            <Step operation="flash" partition="boot" filename="boot.img" />
            <Step operation="erase" partition="userdata" />
            ...
          </FlashFile>

        Args:
            xml_path: Path to flash-all.xml.
            callback: Log callback.

        Returns:
            True if all steps succeeded, False on first failure.
        """
        def log(msg: str):
            if callback:
                callback(msg)

        base_dir = os.path.dirname(xml_path)
        log(f"[Motorola] Parsing flash-all.xml: {xml_path}")

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError as exc:
            log(f"[Motorola] ERROR: Failed to parse XML: {exc}")
            return False

        steps = root.findall(".//Step")
        if not steps:
            log("[Motorola] WARNING: No <Step> elements found in XML.")
            return False

        for step in steps:
            operation = step.get("operation", "").lower()
            partition = step.get("partition", "")
            filename = step.get("filename", "")

            if operation == "flash":
                img_path = os.path.join(base_dir, filename)
                if not os.path.isfile(img_path):
                    log(f"[Motorola] ERROR: Image not found: {img_path}")
                    return False
                log(f"[Motorola] Flashing partition '{partition}' ← {filename}")
                self.fastboot.flash(self.serial, partition, img_path, callback=callback)

            elif operation == "erase":
                log(f"[Motorola] Erasing partition '{partition}'")
                self.fastboot.erase(self.serial, partition, callback=callback)

            elif operation == "reboot":
                mode = step.get("mode", "")
                log(f"[Motorola] Rebooting: {mode if mode else 'normal'}")
                self.fastboot.reboot(self.serial, mode=mode, callback=callback)

            else:
                log(f"[Motorola] WARNING: Unknown operation '{operation}' — skipping.")

        log("[Motorola] flash-all.xml processing complete.")
        return True
