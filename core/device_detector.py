"""
device_detector.py — Device detection for UniFlash Tool
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from core.adb_manager import ADBManager
from core.fastboot_manager import FastbootManager


# ------------------------------------------------------------------ #
#  Data model                                                          #
# ------------------------------------------------------------------ #

@dataclass
class DeviceInfo:
    serial: str
    state: str                     # "adb", "fastboot", "offline", "recovery"
    brand: str = ""
    model: str = ""
    android_version: str = ""
    build_number: str = ""
    bootloader: str = ""
    cpu_abi: str = ""
    platform: str = ""
    is_ab_device: bool = False
    slot_suffix: str = ""
    bootloader_locked: bool = True  # assume locked by default

    def __str__(self) -> str:  # pragma: no cover
        return (
            f"DeviceInfo(serial={self.serial!r}, state={self.state!r}, "
            f"brand={self.brand!r}, model={self.model!r}, "
            f"android={self.android_version!r}, ab={self.is_ab_device})"
        )


# ------------------------------------------------------------------ #
#  Detector                                                            #
# ------------------------------------------------------------------ #

class DeviceDetector:
    # Known brand keywords → canonical brand key
    _BRAND_ALIASES = {
        "samsung": "samsung",
        "xiaomi": "xiaomi",
        "redmi": "xiaomi",
        "poco": "xiaomi",
        "mi": "xiaomi",
        "oneplus": "oneplus",
        "one plus": "oneplus",
        "google": "google",
        "pixel": "google",
        "motorola": "motorola",
        "moto": "motorola",
        "oppo": "oppo",
        "realme": "realme",
        "vivo": "vivo",
        "iqoo": "vivo",
        "sony": "sony",
        "xperia": "sony",
        "asus": "asus",
        "nothing": "nothing",
        "huawei": "huawei",
        "honor": "honor",
        "tecno": "tecno",
        "infinix": "infinix",
        "itel": "itel",
    }

    def __init__(self, adb: Optional[ADBManager] = None, fastboot: Optional[FastbootManager] = None):
        self.adb = adb or ADBManager()
        self.fastboot = fastboot or FastbootManager()

    # ---- Public API ---------------------------------------------------- #

    def detect_all(self) -> List[DeviceInfo]:
        """Return DeviceInfo for every connected ADB + fastboot device."""
        devices: List[DeviceInfo] = []

        # ADB devices
        for serial, state in self.adb.get_devices():
            if state == "device":
                devices.append(self._populate_adb_device(serial, "adb"))
            elif state == "recovery":
                devices.append(self._populate_adb_device(serial, "recovery"))
            elif state == "offline":
                devices.append(DeviceInfo(serial=serial, state="offline"))
            else:
                devices.append(DeviceInfo(serial=serial, state=state))

        # Fastboot devices (avoid duplicates)
        adb_serials = {d.serial for d in devices}
        for serial in self.fastboot.get_devices():
            if serial not in adb_serials:
                devices.append(self._populate_fastboot_device(serial))

        return devices

    def detect_one(self, serial: str) -> DeviceInfo:
        """Return DeviceInfo for a single serial, checking ADB first then fastboot."""
        # Check ADB
        for adb_serial, state in self.adb.get_devices():
            if adb_serial == serial:
                if state in ("device", "recovery"):
                    return self._populate_adb_device(serial, state if state == "recovery" else "adb")
                return DeviceInfo(serial=serial, state=state)

        # Check fastboot
        if serial in self.fastboot.get_devices():
            return self._populate_fastboot_device(serial)

        return DeviceInfo(serial=serial, state="offline")

    def get_brand_handler(self, device_info: DeviceInfo) -> str:
        """Return the canonical brand key string for a DeviceInfo."""
        return self._normalise_brand(device_info.brand)

    # ---- Private helpers ----------------------------------------------- #

    def _populate_adb_device(self, serial: str, state: str) -> DeviceInfo:
        """Fill in a DeviceInfo using ADB getprop calls."""
        def prop(key: str) -> str:
            return self.adb.get_prop(serial, key)

        brand = prop("ro.product.brand") or prop("ro.product.manufacturer")
        model = prop("ro.product.model")
        android_version = prop("ro.build.version.release")
        build_number = prop("ro.build.display.id") or prop("ro.build.id")
        bootloader = prop("ro.bootloader") or prop("ro.boot.bootloader")
        cpu_abi = prop("ro.product.cpu.abi")
        platform = prop("ro.board.platform") or prop("ro.hardware")

        # A/B device detection
        ab_update = prop("ro.build.ab_update").lower()
        is_ab = ab_update == "true"
        slot_suffix = prop("ro.boot.slot_suffix").lstrip("_") if is_ab else ""

        # Bootloader lock state
        lock_state = prop("ro.boot.verifiedbootstate") or prop("ro.boot.flash.locked")
        bootloader_locked = lock_state.lower() not in ("orange", "0", "unlocked")

        return DeviceInfo(
            serial=serial,
            state=state,
            brand=brand.lower(),
            model=model,
            android_version=android_version,
            build_number=build_number,
            bootloader=bootloader,
            cpu_abi=cpu_abi,
            platform=platform,
            is_ab_device=is_ab,
            slot_suffix=slot_suffix,
            bootloader_locked=bootloader_locked,
        )

    def _populate_fastboot_device(self, serial: str) -> DeviceInfo:
        """Fill in a DeviceInfo using fastboot getvar calls."""
        def var(name: str) -> str:
            return self.fastboot.get_var(serial, name)

        product = var("product")
        # fastboot rarely gives brand; derive from product name heuristics
        brand = self._guess_brand_from_product(product)
        slot_count = var("slot-count")
        is_ab = slot_count not in ("", "0", "1")
        current_slot = var("current-slot").lstrip("_") if is_ab else ""
        unlocked_raw = var("unlocked")
        bootloader_locked = unlocked_raw.lower() not in ("yes", "true", "1")

        return DeviceInfo(
            serial=serial,
            state="fastboot",
            brand=brand.lower(),
            model=product,
            android_version="",
            build_number="",
            bootloader=var("version-bootloader"),
            cpu_abi="",
            platform="",
            is_ab_device=is_ab,
            slot_suffix=current_slot,
            bootloader_locked=bootloader_locked,
        )

    def _guess_brand_from_product(self, product: str) -> str:
        """Very rough brand guess from fastboot product string."""
        p = product.lower()
        for keyword, brand in self._BRAND_ALIASES.items():
            if keyword in p:
                return brand
        return "generic"

    def _normalise_brand(self, raw_brand: str) -> str:
        """Map a raw brand string to a canonical key used in device_profiles.json."""
        b = raw_brand.lower().strip()
        for keyword, canonical in self._BRAND_ALIASES.items():
            if keyword in b:
                return canonical
        return "generic"
