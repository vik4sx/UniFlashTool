"""
UniFlash Tool — Main Window
Root CTk window with sidebar navigation, top bar, log console, and device status.
Cyber Black & Orange Theme.
Credits: Tejas Jadhav (github.com/vik4sx)
"""

import customtkinter as ctk
from datetime import datetime
import webbrowser
import json
import sys
import os

from assets.styles.theme import (
    ACCENT, ACCENT_HOVER, ACCENT_MUTED, DANGER, SUCCESS, WARNING,
    BG, SIDEBAR_BG, CARD_BG, CARD_HOVER, CARD_BORDER,
    CONSOLE_BG, CONSOLE_HEADER, CONSOLE_TEXT,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    THEME_DARK, THEME_LIGHT, THEME_OPTIONS,
    DEV_NAME, DEV_GITHUB, DEV_GITHUB_URL
)


# ---------------------------------------------------------------------------
# Lazy imports for tab modules (avoids circular refs)
# ---------------------------------------------------------------------------
def _import_tabs():
    from ui.device_tab   import DeviceTab
    from ui.flash_tab    import FlashTab
    from ui.reboot_tab   import RebootTab
    from ui.backup_tab   import BackupTab
    from ui.drivers_tab  import DriversTab
    from ui.info_tab     import InfoTab
    from ui.settings_tab import SettingsTab
    return DeviceTab, FlashTab, RebootTab, BackupTab, DriversTab, InfoTab, SettingsTab


class MainWindow(ctk.CTk):
    """Root application window for UniFlash Tool."""

    def __init__(self):
        super().__init__()

        # App-level theme: load saved preference
        self._active_tab = "device"
        self._current_theme = THEME_DARK
        cfg_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "settings.json")
        try:
            if os.path.isfile(cfg_file):
                with open(cfg_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self._current_theme = cfg.get("theme", THEME_DARK)
        except Exception:
            pass

        app_mode = "light" if "light" in self._current_theme.lower() else "dark"
        ctk.set_appearance_mode(app_mode)
        ctk.set_default_color_theme("blue")

        self.title("🔧 UniFlash Tool v1.0 — by Tejas Jadhav")
        self.geometry("1240x730")
        self.minsize(1050, 640)
        self.configure(fg_color=BG)

        # Shared state
        self._current_device = None          # DeviceInfo | None
        self._device_mode    = "none"        # "adb" | "fastboot" | "none"
        self._dot_state      = 0             # animation frame counter

        # Build layout
        self._build_top_bar()
        self._build_sidebar()
        self._build_content_area()
        self._build_log_console()

        # Load tab frames
        (DeviceTab, FlashTab, RebootTab,
         BackupTab, DriversTab, InfoTab, SettingsTab) = _import_tabs()

        self._frames: dict[str, ctk.CTkFrame] = {}
        for name, Cls in [
            ("device",   DeviceTab),
            ("flash",    FlashTab),
            ("reboot",   RebootTab),
            ("backup",   BackupTab),
            ("drivers",  DriversTab),
            ("info",     InfoTab),
            ("settings", SettingsTab),
        ]:
            frame = Cls(self._content_area, self)
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._frames[name] = frame

        # Show default tab
        self.show_frame("device")

        # Initial log entry
        self.log(f"UniFlash Tool v1.0 initialized | Developed by {DEV_NAME} (@{DEV_GITHUB})")

        # Start periodic tasks
        self._animate_dot()
        self._auto_refresh()

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------
    def _build_top_bar(self):
        self._top_bar = ctk.CTkFrame(self, height=54, fg_color=SIDEBAR_BG, corner_radius=0)
        self._top_bar.pack(side="top", fill="x")
        self._top_bar.pack_propagate(False)

        # App title & icon
        title_frame = ctk.CTkFrame(self._top_bar, fg_color="transparent")
        title_frame.pack(side="left", padx=16, pady=8)

        ctk.CTkLabel(
            title_frame,
            text="⚡ UniFlash Tool",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            text_color=ACCENT,
        ).pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="v1.0",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(side="left", padx=(6, 12), pady=(4, 0))

        # Creator credit badge in topbar
        credit_chip = ctk.CTkFrame(title_frame, fg_color=CARD_BG, corner_radius=6, border_width=1, border_color=CARD_BORDER)
        credit_chip.pack(side="left", padx=4)
        ctk.CTkLabel(
            credit_chip,
            text=f"By {DEV_NAME} • @{DEV_GITHUB}",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=TEXT_SECONDARY,
        ).pack(padx=8, pady=2)

        # Right-side device status cluster
        status_frame = ctk.CTkFrame(self._top_bar, fg_color="transparent")
        status_frame.pack(side="right", padx=16)

        self._dot_label = ctk.CTkLabel(
            status_frame,
            text="●",
            font=ctk.CTkFont(size=18),
            text_color="#555555",
        )
        self._dot_label.pack(side="left", padx=(0, 6))

        self._status_label = ctk.CTkLabel(
            status_frame,
            text="🔴 No Device",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#ff5555",
        )
        self._status_label.pack(side="left")

        self._device_name_label = ctk.CTkLabel(
            self._top_bar,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_PRIMARY,
        )
        self._device_name_label.pack(side="right", padx=12)

    def _build_sidebar(self):
        self._sidebar = ctk.CTkFrame(self, width=210, fg_color=SIDEBAR_BG, corner_radius=0)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Brand header in sidebar
        brand_box = ctk.CTkFrame(self._sidebar, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=CARD_BORDER)
        brand_box.pack(fill="x", padx=12, pady=(16, 14))

        ctk.CTkLabel(
            brand_box,
            text="⚡ UniFlash",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=ACCENT,
        ).pack(pady=(10, 2))
        ctk.CTkLabel(
            brand_box,
            text="Universal Android Suite",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=TEXT_MUTED,
        ).pack(pady=(0, 10))

        # Divider
        ctk.CTkFrame(self._sidebar, height=1, fg_color=CARD_BORDER).pack(fill="x", padx=12, pady=(0, 10))

        nav_items = [
            ("📱  Device",      "device"),
            ("⚡  Flash",       "flash"),
            ("🔄  Reboot",      "reboot"),
            ("📦  Backup",      "backup"),
            ("🔧  Drivers",     "drivers"),
            ("📊  Device Info", "info"),
            ("⚙️  Settings",    "settings"),
        ]
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        for label, key in nav_items:
            btn = ctk.CTkButton(
                self._sidebar,
                text=label,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                fg_color="transparent",
                hover_color=CARD_HOVER,
                text_color=TEXT_SECONDARY,
                corner_radius=8,
                height=42,
                command=lambda k=key: self.show_frame(k),
            )
            btn.pack(fill="x", padx=10, pady=3)
            self._nav_buttons[key] = btn

        # Bottom Creator Credits Section
        credits_frame = ctk.CTkFrame(self._sidebar, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=CARD_BORDER)
        credits_frame.pack(side="bottom", fill="x", padx=12, pady=14)

        ctk.CTkLabel(
            credits_frame,
            text="DEVELOPED BY",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=ACCENT,
        ).pack(pady=(10, 2))

        ctk.CTkLabel(
            credits_frame,
            text=DEV_NAME,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack()

        # Clickable GitHub Button
        github_btn = ctk.CTkButton(
            credits_frame,
            text=f"🐙 @{DEV_GITHUB}",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=CARD_HOVER,
            hover_color=ACCENT,
            border_width=1,
            border_color=CARD_BORDER,
            text_color=ACCENT,
            corner_radius=6,
            height=28,
            command=lambda: webbrowser.open(DEV_GITHUB_URL),
            cursor="hand2",
        )
        github_btn.pack(fill="x", padx=10, pady=(6, 10))

    def _build_content_area(self):
        self._content_area = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self._content_area.pack(side="top", fill="both", expand=True)

    def _build_log_console(self):
        console_frame = ctk.CTkFrame(self, height=140, fg_color=CONSOLE_BG, corner_radius=0)
        console_frame.pack(side="bottom", fill="x")
        console_frame.pack_propagate(False)

        header = ctk.CTkFrame(console_frame, height=26, fg_color=CONSOLE_HEADER, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header,
            text="  📋  Console Output",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=ACCENT,
            anchor="w",
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            header,
            text="Clear",
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            hover_color=CARD_BG,
            text_color=TEXT_MUTED,
            width=50,
            height=20,
            command=self._clear_log,
        ).pack(side="right", padx=6)

        self._log_box = ctk.CTkTextbox(
            console_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=CONSOLE_BG,
            text_color=CONSOLE_TEXT,
            wrap="word",
            state="disabled",
        )
        self._log_box.pack(fill="both", expand=True, padx=6, pady=(2, 6))

    def _clear_log(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_app_theme(self, theme_choice: str, mode: str):
        """Live switch application theme between Dark and Light."""
        self._current_theme = theme_choice
        ctk.set_appearance_mode(mode)
        self.show_frame(self._active_tab)

    def show_frame(self, key: str):
        """Raise the named frame and highlight its nav button with Orange Accent."""
        self._active_tab = key
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=ACCENT,
                    hover_color=ACCENT_HOVER,
                    text_color="#FFFFFF"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=CARD_HOVER,
                    text_color=TEXT_SECONDARY
                )
        frame = self._frames.get(key)
        if frame:
            frame.tkraise()

    def log(self, message: str):
        """Append a timestamped line to the log console and auto-scroll."""
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {message}\n"
        self._log_box.configure(state="normal")
        self._log_box.insert("end", line)
        self._log_box.configure(state="disabled")
        self._log_box.see("end")

    def update_device_status(self, device_info=None):
        """Called with a DeviceInfo (or None) to refresh top-bar indicators."""
        self._current_device = device_info
        if device_info is None:
            self._device_mode = "none"
            self._status_label.configure(text="🔴 No Device", text_color="#ff5555")
            self._device_name_label.configure(text="")
        elif device_info.state == "fastboot":
            self._device_mode = "fastboot"
            self._status_label.configure(text="🟡 Fastboot Mode", text_color=WARNING)
            self._device_name_label.configure(
                text=f"{device_info.brand or 'Fastboot'} {device_info.model or 'Device'}  [{device_info.serial}]"
            )
        elif device_info.state == "unauthorized":
            self._device_mode = "unauthorized"
            self._status_label.configure(text="🟠 Unauthorized", text_color=WARNING)
            self._device_name_label.configure(
                text=f"⚠️ [{device_info.serial}] Unlock phone & tap 'Allow USB Debugging'"
            )
        elif device_info.state == "offline":
            self._device_mode = "offline"
            self._status_label.configure(text="⚪ Device Offline", text_color=TEXT_MUTED)
            self._device_name_label.configure(
                text=f"[{device_info.serial}] Offline — reconnect USB cable"
            )
        else:
            self._device_mode = "adb"
            self._status_label.configure(text="🟢 ADB Online", text_color=SUCCESS)
            self._device_name_label.configure(
                text=f"{device_info.brand or 'Android'} {device_info.model or 'Device'}  [{device_info.serial}]"
            )

        # Propagate to Device tab
        dev_tab = self._frames.get("device")
        if dev_tab and hasattr(dev_tab, "refresh"):
            dev_tab.refresh(device_info)
        # Propagate to Reboot tab
        reboot_tab = self._frames.get("reboot")
        if reboot_tab and hasattr(reboot_tab, "set_device_mode"):
            reboot_tab.set_device_mode(self._device_mode)

    def get_device(self):
        return self._current_device

    def get_device_mode(self) -> str:
        return self._device_mode

    # ------------------------------------------------------------------
    # Animation & periodic tasks
    # ------------------------------------------------------------------
    def _animate_dot(self):
        """Pulse the status dot colour."""
        colours = {
            "adb":      [SUCCESS, "#008844", SUCCESS],
            "fastboot": [WARNING, "#CC8800", WARNING],
            "none":     ["#444455", "#222233", "#444455"],
        }
        palette = colours.get(self._device_mode, colours["none"])
        colour = palette[self._dot_state % len(palette)]
        self._dot_label.configure(text_color=colour)
        self._dot_state += 1
        self.after(600, self._animate_dot)

    def _auto_refresh(self):
        """Auto-detect connected devices every 5 seconds."""
        try:
            self._do_device_scan()
        except Exception as exc:
            self.log(f"[Auto-refresh error] {exc}")
        self.after(5000, self._auto_refresh)

    def _do_device_scan(self):
        """Scan for ADB/Fastboot devices and update UI."""
        try:
            import sys, os
            root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if root not in sys.path:
                sys.path.insert(0, root)
            from core.adb_manager import ADBManager
            from core.fastboot_manager import FastbootManager
            from core.device_detector import DeviceDetector
            detector = DeviceDetector(ADBManager(), FastbootManager())
            devices = detector.detect_all()
            if devices:
                self.update_device_status(devices[0])
            else:
                self.update_device_status(None)
        except Exception as exc:
            self.log(f"[Device Scan Error] {exc}")


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------
def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
