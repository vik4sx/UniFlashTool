"""
UniFlash Tool — Device Tab
Displays connected device information in a card layout with brand logos and photos.
Cyber Black & Orange Theme.
"""

import customtkinter as ctk
import webbrowser
import tkinter as tk
import os

from assets.styles.theme import (
    ACCENT, ACCENT_HOVER, DANGER, SUCCESS, WARNING,
    BG, SIDEBAR_BG, CARD_BG, CARD_HOVER, CARD_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
)
from core.brand_logos import get_brand_ctk_image

# Brand driver URLs
DRIVER_URLS = {
    "samsung":  "https://developer.samsung.com/mobile/android-usb-driver.html",
    "xiaomi":   "https://xiaomifirmwareupdater.com/drivers/",
    "oneplus":  "https://www.oneplus.com/support/softwareupgrade",
    "google":   "https://developer.android.com/studio/run/win-usb",
    "motorola": "https://motorola-global-portal.custhelp.com/app/answers/detail/a_id/88481",
    "realme":   "https://www.realme.com/in/support/kw/doc/2001573",
    "oppo":     "https://support.oppo.com/en/software-and-device-manager/",
    "vivo":     "https://www.vivo.com/en/support/searchResult?q=usb+driver",
    "sony":     "https://developer.sony.com/open-source/aosp-on-xperia-open-devices/",
    "asus":     "https://www.asus.com/support/Download-Center/",
    "nothing":  "https://nothing.tech/pages/support",
    "generic":  "https://developer.android.com/studio/run/device",
}


class DeviceTab(ctk.CTkFrame):
    """Tab showing detailed connected device information."""

    def __init__(self, parent, main_window):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self._main = main_window
        self._device = None
        self._field_labels: dict[str, ctk.CTkLabel] = {}
        self._build_ui()
        self._show_placeholder()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Header row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 6))

        ctk.CTkLabel(
            header,
            text="📱  Connected Device",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=ACCENT,
        ).pack(side="left")

        btn_row = ctk.CTkFrame(header, fg_color="transparent")
        btn_row.pack(side="right")

        ctk.CTkButton(
            btn_row, text="🔄 Refresh", width=110,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            text_color="#FFFFFF", font=ctk.CTkFont(weight="bold"),
            corner_radius=8,
            command=self._on_refresh,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_row, text="🔧 Install Drivers", width=130,
            fg_color=CARD_BG, hover_color=CARD_HOVER,
            border_width=1, border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY, corner_radius=8,
            command=self._on_install_drivers,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_row, text="📋 Copy Info", width=110,
            fg_color=CARD_BG, hover_color=CARD_HOVER,
            border_width=1, border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY, corner_radius=8,
            command=self._on_copy_info,
        ).pack(side="left", padx=4)

        # Main device card
        self._card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER)
        self._card.pack(fill="both", expand=True, padx=20, pady=10)

        # Placeholder label
        self._placeholder = ctk.CTkLabel(
            self._card,
            text="🔌  No Device Detected\n\n1. Connect your phone via USB cable\n2. Enable Developer Options & USB Debugging\n3. Tap 'Always allow from this computer' on your phone",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=TEXT_MUTED,
            justify="center",
        )

        # Top Device Brand Display Frame (with brand image + title)
        self._brand_frame = ctk.CTkFrame(self._card, fg_color=SIDEBAR_BG, corner_radius=10, border_width=1, border_color=CARD_BORDER)

        # Brand logo / photo image label
        self._brand_img_label = ctk.CTkLabel(self._brand_frame, text="")
        self._brand_img_label.pack(side="left", padx=16, pady=12)

        # Brand text titles
        brand_meta = ctk.CTkFrame(self._brand_frame, fg_color="transparent")
        brand_meta.pack(side="left", padx=10, pady=12, fill="both", expand=True)

        self._brand_label = ctk.CTkLabel(
            brand_meta,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=ACCENT,
            anchor="w",
        )
        self._brand_label.pack(anchor="w")

        self._model_subtitle = ctk.CTkLabel(
            brand_meta,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self._model_subtitle.pack(anchor="w", pady=(2, 0))

        # Status Badge on right of brand frame
        self._status_badge = ctk.CTkLabel(
            self._brand_frame,
            text="ONLINE",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#000000",
            fg_color=SUCCESS,
            corner_radius=6,
            padx=12,
            pady=4,
        )
        self._status_badge.pack(side="right", padx=20, pady=20)

        # Info grid container
        self._info_scroll = ctk.CTkScrollableFrame(self._card, fg_color="transparent")

        fields = [
            ("Model",             "model"),
            ("Serial Number",     "serial"),
            ("State",             "state"),
            ("Android Version",   "android_version"),
            ("Build Number",      "build_number"),
            ("CPU Architecture",  "cpu_abi"),
            ("Platform/Chipset",  "platform"),
            ("Bootloader Status", "bootloader_locked"),
            ("A/B Device",        "is_ab_device"),
            ("Active Slot",       "slot_suffix"),
        ]

        for idx, (display_name, key) in enumerate(fields):
            row = idx // 2
            col = (idx % 2) * 2

            lbl_title = ctk.CTkLabel(
                self._info_scroll,
                text=f"{display_name}:",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=TEXT_MUTED,
                anchor="w",
                width=140,
            )
            lbl_title.grid(row=row, column=col, padx=(16, 6), pady=8, sticky="w")

            lbl_val = ctk.CTkLabel(
                self._info_scroll,
                text="—",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=TEXT_PRIMARY,
                anchor="w",
            )
            lbl_val.grid(row=row, column=col + 1, padx=(0, 20), pady=8, sticky="w")
            self._field_labels[key] = lbl_val

        self._info_scroll.columnconfigure(1, weight=1)
        self._info_scroll.columnconfigure(3, weight=1)

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------
    def _show_placeholder(self):
        self._brand_frame.pack_forget()
        self._info_scroll.pack_forget()
        self._placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def _show_info(self):
        self._placeholder.place_forget()
        self._brand_frame.pack(fill="x", padx=16, pady=(16, 8))
        self._info_scroll.pack(fill="both", expand=True, padx=16, pady=8)

    def refresh(self, device_info=None):
        """Called with DeviceInfo or None to update the view."""
        self._device = device_info
        if device_info is None:
            self._show_placeholder()
            return

        self._show_info()
        brand_name = device_info.brand or "Generic"
        model_name = device_info.model or "Android Device"
        self._brand_label.configure(text=f"{brand_name} {model_name}".strip())
        self._model_subtitle.configure(text=f"Serial: {device_info.serial} • Mode: {device_info.state.upper()}")

        # Update brand photo/logo
        logo_img = get_brand_ctk_image(brand_name, width=150, height=65)
        if logo_img:
            self._brand_img_label.configure(image=logo_img, text="")
        else:
            self._brand_img_label.configure(image=None, text="📱", font=ctk.CTkFont(size=32))

        # Status badge
        if device_info.state == "fastboot":
            self._status_badge.configure(text="⚡ FASTBOOT", fg_color=WARNING, text_color="#000000")
        else:
            self._status_badge.configure(text="🟢 ADB ONLINE", fg_color=SUCCESS, text_color="#000000")

        # Field values
        self._set_field("model", device_info.model)
        self._set_field("serial", device_info.serial)
        self._set_field("state", device_info.state.upper() if device_info.state else "—")
        self._set_field("android_version", device_info.android_version or "—")
        self._set_field("build_number", device_info.build_number or "—")
        self._set_field("cpu_abi", device_info.cpu_abi or "—")
        self._set_field("platform", device_info.platform or "—")

        # Bootloader badge
        bl_label = self._field_labels.get("bootloader_locked")
        if bl_label:
            if device_info.bootloader_locked is True:
                bl_label.configure(text="🔒 LOCKED", text_color=DANGER)
            elif device_info.bootloader_locked is False:
                bl_label.configure(text="🔓 UNLOCKED", text_color=SUCCESS)
            else:
                bl_label.configure(text="UNKNOWN", text_color=TEXT_MUTED)

        # A/B slot
        ab_label = self._field_labels.get("is_ab_device")
        if ab_label:
            ab_label.configure(
                text="YES (Dual Slot)" if device_info.is_ab_device else "NO (Single Slot)",
                text_color=ACCENT if device_info.is_ab_device else TEXT_PRIMARY,
            )

        slot_label = self._field_labels.get("slot_suffix")
        if slot_label:
            slot_label.configure(
                text=device_info.slot_suffix or "N/A",
                text_color=ACCENT if device_info.slot_suffix else TEXT_MUTED,
            )

    def _set_field(self, key: str, value: str | None):
        lbl = self._field_labels.get(key)
        if lbl:
            lbl.configure(text=value if value else "—", text_color=TEXT_PRIMARY)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _on_refresh(self):
        self._main.log("Scanning for connected devices …")
        self._main._do_device_scan()

    def _on_install_drivers(self):
        self._main.log("Switching to Driver Installation Hub …")
        self._main.show_frame("drivers")

    def _on_copy_info(self):
        if not self._device:
            self._main.log("No device info to copy.")
            return
        lines = [
            f"Brand:             {self._device.brand}",
            f"Model:             {self._device.model}",
            f"Serial:            {self._device.serial}",
            f"State:             {self._device.state}",
            f"Android:           {self._device.android_version}",
            f"Build:             {self._device.build_number}",
            f"CPU:               {self._device.cpu_abi}",
            f"Platform:          {self._device.platform}",
            f"Bootloader Locked: {self._device.bootloader_locked}",
            f"A/B Device:        {self._device.is_ab_device}",
            f"Active Slot:       {self._device.slot_suffix}",
        ]
        text = "\n".join(lines)
        self.clipboard_clear()
        self.clipboard_append(text)
        self._main.log("Device info copied to clipboard.")
