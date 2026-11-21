"""
UniFlash Tool — Drivers Tab
Driver Installation Hub: Official OEM Drivers, Universal ADB, Qualcomm 9008, MediaTek VCOM.
Cyber Black & Orange Theme.
"""

import customtkinter as ctk
import webbrowser
import subprocess
import threading
import os

from assets.styles.theme import (
    ACCENT, ACCENT_HOVER, DANGER, SUCCESS, WARNING,
    BG, SIDEBAR_BG, CARD_BG, CARD_HOVER, CARD_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
)
from core.brand_logos import get_brand_ctk_image


def _bundled_installer_path() -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "tools", "drivers", "15_Second_ADB_Installer.exe")


# Driver catalog with descriptions and official download links
DRIVERS_CATALOG = [
    {
        "category": "Universal & Chipset Drivers",
        "items": [
            {
                "id": "google",
                "name": "Google USB Driver (Official)",
                "brand": "google",
                "desc": "Official Google Android USB Driver for Pixel, Fastboot & Bootloader interfaces.",
                "modes": "Fastboot • Bootloader • ADB",
                "url": "https://developer.android.com/studio/run/win-usb",
                "tag": "Essential for Fastboot",
            },
            {
                "id": "universal_adb",
                "name": "Universal ADB Driver (Koush)",
                "brand": "generic",
                "desc": "Automated 1-click installer supporting virtually all Android devices on Windows 10/11.",
                "modes": "ADB • Composite USB",
                "url": "https://github.com/koush/UniversalAdbDriver/releases",
                "tag": "Recommended for All",
            },
            {
                "id": "qualcomm",
                "name": "Qualcomm HS-USB QDLoader 9008",
                "brand": "generic",
                "desc": "Emergency Download (EDL) mode driver for Qualcomm Snapdragon processors (unbrick mode).",
                "modes": "EDL 9008 Mode",
                "url": "https://androiddatahost.com/2m6ep",
                "tag": "For EDL Flashing",
            },
            {
                "id": "mediatek",
                "name": "MediaTek (MTK) USB VCOM Driver",
                "brand": "generic",
                "desc": "Preloader & VCOM Port driver for all Helio & Dimensity MediaTek smartphones.",
                "modes": "MTK Preloader • VCOM",
                "url": "https://androiddatahost.com/64s37",
                "tag": "MTK Devices",
            },
        ],
    },
    {
        "category": "Brand-Specific OEM Drivers",
        "items": [
            {
                "id": "samsung",
                "name": "Samsung Android USB Driver",
                "brand": "samsung",
                "desc": "Official Samsung Mobile USB driver for Galaxy smartphones & tablets (Odin / Sideload).",
                "modes": "Download Mode • MTP • ADB",
                "url": "https://developer.samsung.com/mobile/android-usb-driver.html",
                "tag": "Galaxy S/A/M Series",
            },
            {
                "id": "xiaomi",
                "name": "Xiaomi / Redmi / POCO Driver",
                "brand": "xiaomi",
                "desc": "Official Mi Flash driver pack & Fastboot interface driver for all MIUI / HyperOS phones.",
                "modes": "Fastboot • EDL • Sideload",
                "url": "https://xiaomifirmwareupdater.com/drivers/",
                "tag": "Xiaomi / Redmi / POCO",
            },
            {
                "id": "oneplus",
                "name": "OnePlus USB Driver",
                "brand": "oneplus",
                "desc": "Official OnePlus OxygenOS driver for Fastboot, Recovery, and MSM unbrick tools.",
                "modes": "Fastboot • Sideload • MSM",
                "url": "https://www.oneplus.com/support/softwareupgrade",
                "tag": "OnePlus Nord / Flagship",
            },
            {
                "id": "motorola",
                "name": "Motorola Device Manager & Driver",
                "brand": "motorola",
                "desc": "Motorola Mobile Drivers with support for fastboot flash-all and rescue mode.",
                "modes": "Fastboot • Rescue Mode",
                "url": "https://motorola-global-portal.custhelp.com/app/answers/detail/a_id/88481",
                "tag": "Moto G / Edge / Razr",
            },
            {
                "id": "realme",
                "name": "Realme USB Driver Pack",
                "brand": "realme",
                "desc": "Realme UI USB driver suite for recovery mode sideloading and deep-testing unlock.",
                "modes": "Recovery • Fastboot",
                "url": "https://www.realme.com/in/support/kw/doc/2001573",
                "tag": "Realme UI",
            },
            {
                "id": "oppo",
                "name": "OPPO USB Driver",
                "brand": "oppo",
                "desc": "ColorOS communication drivers for firmware sideloading and flashing.",
                "modes": "Recovery Sideload",
                "url": "https://support.oppo.com/en/software-and-device-manager/",
                "tag": "OPPO Reno / Find",
            },
            {
                "id": "vivo",
                "name": "Vivo & iQOO USB Driver",
                "brand": "vivo",
                "desc": "Official FuntouchOS / OriginOS driver for Vivo and iQOO devices in fastboot mode.",
                "modes": "Fastboot • ADB",
                "url": "https://www.vivo.com/en/support/searchResult?q=usb+driver",
                "tag": "Vivo V / X / iQOO",
            },
            {
                "id": "sony",
                "name": "Sony Xperia Driver",
                "brand": "sony",
                "desc": "Xperia Open Devices Fastboot and Flashmode drivers for developer flashing.",
                "modes": "Fastboot • Flashmode",
                "url": "https://developer.sony.com/open-source/aosp-on-xperia-open-devices/",
                "tag": "Sony Xperia",
            },
            {
                "id": "asus",
                "name": "ASUS ROG & Zenfone Driver",
                "brand": "asus",
                "desc": "ASUS Android USB driver with Rescue Mode and Fastboot compatibility.",
                "modes": "Fastboot • Rescue",
                "url": "https://www.asus.com/support/Download-Center/",
                "tag": "ROG Phone / Zenfone",
            },
            {
                "id": "nothing",
                "name": "Nothing Phone USB Driver",
                "brand": "nothing",
                "desc": "Nothing OS standard AOSP Fastboot & bootloader USB driver.",
                "modes": "Fastboot • ADB",
                "url": "https://nothing.tech/pages/support",
                "tag": "Nothing Phone (1)/(2)/(2a)",
            },
        ],
    },
]


class DriversTab(ctk.CTkFrame):
    """Driver Installation Hub tab."""

    def __init__(self, parent, main_window):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self._main = main_window
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        # Header Row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 6))

        ctk.CTkLabel(
            header,
            text="🔧  Driver Installation Hub",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=ACCENT,
        ).pack(side="left")

        btn_row = ctk.CTkFrame(header, fg_color="transparent")
        btn_row.pack(side="right")

        ctk.CTkButton(
            btn_row,
            text="💻 Open Device Manager",
            width=160,
            fg_color=CARD_BG,
            hover_color=CARD_HOVER,
            border_width=1,
            border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            command=self._open_device_manager,
            cursor="hand2",
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_row,
            text="🔍 Scan USB Drivers",
            width=150,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(weight="bold"),
            corner_radius=8,
            command=self._scan_drivers,
            cursor="hand2",
        ).pack(side="left", padx=4)

        # Quick info banner
        info_bar = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=8, border_width=1, border_color=CARD_BORDER)
        info_bar.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            info_bar,
            text="💡 Tip: If your phone is stuck on 'Waiting for device' in Fastboot or ADB, install the corresponding OEM driver below and reconnect.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_SECONDARY,
        ).pack(side="left", padx=14, pady=8)

        # Scrollable catalog
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Hero Card: Bundled 15-Second ADB & Driver Installer
        hero = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=ACCENT)
        hero.pack(fill="x", pady=(4, 14))

        hero_inner = ctk.CTkFrame(hero, fg_color="transparent")
        hero_inner.pack(fill="x", padx=16, pady=14)

        left_box = ctk.CTkFrame(hero_inner, fg_color="transparent")
        left_box.pack(side="left", fill="both", expand=True)

        badge_row = ctk.CTkFrame(left_box, fg_color="transparent")
        badge_row.pack(anchor="w")

        ctk.CTkLabel(
            badge_row,
            text="⚡ BUNDLED 1-CLICK INSTALLER",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#0A0A0D",
            fg_color=ACCENT,
            corner_radius=4,
            padx=8,
            pady=2,
        ).pack(side="left")

        ctk.CTkLabel(
            badge_row,
            text="v2.0.7 (2024)",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=TEXT_SECONDARY,
            fg_color=CARD_HOVER,
            corner_radius=4,
            padx=6,
            pady=2,
        ).pack(side="left", padx=8)

        ctk.CTkLabel(
            left_box,
            text="15 Seconds ADB, Fastboot & Google USB Driver Installer",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w", pady=(6, 2))

        ctk.CTkLabel(
            left_box,
            text="Automated setup package that configures system-wide ADB & Fastboot paths and installs all required 32/64-bit Google USB Drivers.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_SECONDARY,
            wraplength=600,
            justify="left",
            anchor="w",
        ).pack(anchor="w")

        right_box = ctk.CTkFrame(hero_inner, fg_color="transparent")
        right_box.pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            right_box,
            text="🚀  RUN INSTALLER NOW",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=46,
            width=220,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            corner_radius=8,
            cursor="hand2",
            command=self._run_bundled_installer,
        ).pack()

        for section in DRIVERS_CATALOG:
            # Section header
            ctk.CTkLabel(
                scroll,
                text=f"📁  {section['category']}",
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color=ACCENT,
            ).pack(anchor="w", pady=(12, 6))

            # Grid of driver cards (2 columns)
            grid_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            grid_frame.pack(fill="x", pady=(0, 8))

            for idx, item in enumerate(section["items"]):
                row = idx // 2
                col = idx % 2
                card = self._create_driver_card(grid_frame, item)
                card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

            grid_frame.columnconfigure(0, weight=1)
            grid_frame.columnconfigure(1, weight=1)

    def _create_driver_card(self, parent, item: dict) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=CARD_BORDER)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(10, 4))

        # Brand / category thumbnail
        logo_img = get_brand_ctk_image(item["brand"], width=70, height=32)
        if logo_img:
            ctk.CTkLabel(top_row, image=logo_img, text="").pack(side="left", padx=(0, 8))
        else:
            ctk.CTkLabel(top_row, text="🔧", font=ctk.CTkFont(size=18)).pack(side="left", padx=(0, 8))

        # Title & Badge
        meta = ctk.CTkFrame(top_row, fg_color="transparent")
        meta.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            meta,
            text=item["name"],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            meta,
            text=f"Modes: {item['modes']}",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=ACCENT,
            anchor="w",
        ).pack(anchor="w")

        # Tag
        ctk.CTkLabel(
            top_row,
            text=item["tag"],
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color="#0A0A0D",
            fg_color=WARNING,
            corner_radius=4,
            padx=6,
            pady=2,
        ).pack(side="right")

        # Description
        ctk.CTkLabel(
            card,
            text=item["desc"],
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=TEXT_MUTED,
            anchor="w",
            wraplength=450,
            justify="left",
        ).pack(anchor="w", padx=12, pady=(2, 8))

        # Bottom actions
        action_row = ctk.CTkFrame(card, fg_color="transparent")
        action_row.pack(fill="x", padx=12, pady=(0, 10))

        url = item["url"]
        ctk.CTkButton(
            action_row,
            text="⬇️ Download / Install Driver",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            height=30,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            corner_radius=6,
            command=lambda u=url, n=item["name"]: self._download_driver(n, u),
            cursor="hand2",
        ).pack(side="left", padx=(0, 8))

        return card

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _run_bundled_installer(self):
        exe = _bundled_installer_path()
        if os.path.isfile(exe):
            self._main.log(f"Launching 15-Second ADB & Driver Installer: {exe}")
            try:
                os.startfile(exe)
            except Exception as exc:
                self._main.log(f"Failed to launch installer: {exc}")
        else:
            self._main.log(f"[Driver Installer Error] File not found at: {exe}")

    def _download_driver(self, name: str, url: str):
        self._main.log(f"Opening official driver package for {name} → {url}")
        webbrowser.open(url)

    def _open_device_manager(self):
        self._main.log("Opening Windows Device Manager (devmgmt.msc) …")
        try:
            subprocess.Popen(["devmgmt.msc"], shell=True)
        except Exception as exc:
            self._main.log(f"Failed to open Device Manager: {exc}")

    def _scan_drivers(self):
        self._main.log("Scanning Windows Device Manager for Android / USB devices …")
        def _worker():
            try:
                # Query PNP devices matching Android, ADB, or Fastboot
                cmd = ["powershell", "-NoProfile", "-Command",
                       "Get-PnpDevice -Class USB, AndroidUsbDeviceType, WPD -ErrorAction SilentlyContinue | "
                       "Select-Object -First 10 FriendlyName, Status | Format-Table -AutoSize | Out-String"]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
                out = proc.stdout.strip()
                if out:
                    self.after(0, lambda: self._main.log(f"[USB Devices Found]:\n{out}"))
                else:
                    self.after(0, lambda: self._main.log("[Scan] No Android USB devices currently flagged."))
            except Exception as exc:
                self.after(0, lambda: self._main.log(f"[Scan Error] {exc}"))
        threading.Thread(target=_worker, daemon=True).start()
