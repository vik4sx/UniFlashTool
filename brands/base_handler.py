"""
Base handler for all brand-specific flash handlers.
"""
from abc import ABC, abstractmethod


class BaseBrandHandler(ABC):
    """Abstract base class for all brand-specific flash handlers."""

    def __init__(self, serial: str, model: str, adb, fastboot):
        """
        Initialize the handler.

        Args:
            serial: Device serial number.
            model: Device model string.
            adb: ADBManager instance.
            fastboot: FastbootManager instance.
        """
        self.serial = serial
        self.model = model
        self.adb = adb
        self.fastboot = fastboot

    @abstractmethod
    def flash(self, file_path: str, options: dict, callback) -> bool:
        """
        Flash the given file to the device.

        Args:
            file_path: Absolute path to the firmware/image file.
            options: Dict of flashing options (partition, wipe, etc.).
            callback: Callable(str) for streaming log output.

        Returns:
            True on success, False on failure.
        """
        pass

    @abstractmethod
    def get_flash_instructions(self) -> str:
        """Return human-readable instructions for preparing the device."""
        pass

    # ------------------------------------------------------------------ #
    # Concrete helpers — may be overridden by subclasses                   #
    # ------------------------------------------------------------------ #

    def get_name(self) -> str:
        """Return the handler class name."""
        return self.__class__.__name__

    def supports_sideload(self) -> bool:
        """Whether this brand supports ADB sideload."""
        return True

    def requires_unlocked_bootloader(self) -> bool:
        """Whether an unlocked bootloader is required before flashing."""
        return True

    def get_driver_url(self) -> str:
        """Return URL to the official USB driver download page (if any)."""
        return ""
