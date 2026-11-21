"""
UniFlash Tool — Reboot Tab
3×3 grid of reboot/ADB control buttons with device-mode awareness.
Cyber Black & Orange theme with bold, clear command labels.
"""

import customtkinter as ctk
import subprocess
import threading
import os

from assets.styles.theme import (
    ACCENT, ACCENT_HOVER, DANGER, DANGER_HOVER, SUCCESS, WARNING,
    BG, SIDEBAR_BG, CARD_BG, CARD_HOVER, CARD_BORDER, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
)


from core.paths import resolve_adb_path, resolve_fastboot_path


def _adb_path() -> str:
    return resolve_adb_path()


def _fb_path() -> str:
    return resolve_fastboot_path()


class _RebootButton(ctk.CTkButton):
    """
    Single reboot action tile.
    Uses native CTkButton multi-line text to ensure text is ALWAYS crystal clear and visible,
    eliminating any canvas layering or invisible overlay bugs.
    """

    def __init__(self, parent, emoji: str, label: str, cmd_hint: str,
                 is_danger: bool = False, action=None, **kwargs):
        color = DANGER if is_danger else CARD_BG
        hover = DANGER_HOVER if is_danger else ACCENT_HOVER
        border = "#FF5566" if is_danger else CARD_BORDER
        text_color = "#FFFFFF" if is_danger else TEXT_PRIMARY

        # Multiline text with distinct bold title and command subtitle
        text = f"{emoji}  {label}\n\n▶  {cmd_hint}"

        super().__init__(
            parent,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=text_color,
            fg_color=color,
            hover_color=hover,
            border_width=1,
            border_color=border,
            corner_radius=12,
            command=action,
            cursor="hand2",
            height=95,
            anchor="center",
            **kwargs,
        )


class RebootTab(ctk.CTkFrame):
    """Tab with 3×3 grid of reboot/ADB server buttons."""

    def __init__(self, parent, main_window):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self._main = main_window
        self._device_mode = "none"
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 8))

        ctk.CTkLabel(
            header,
            text="🔄  Reboot & ADB Controls",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=ACCENT,
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="Click any tile to execute immediate device state transition",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED,
        ).pack(side="left", padx=(12, 0), pady=(4, 0))

        # Device mode banner (initially hidden)
        self._mode_banner = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=WARNING,
            fg_color=CARD_BG,
            corner_radius=8,
            height=32,
        )

        # 3×3 grid container
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=20, pady=10)

        buttons = [
            # Row 0
            ("📱", "Reboot Normal",      "adb reboot",             False, self._reboot_normal),
            ("🔧", "Reboot Bootloader",  "adb reboot bootloader",  False, self._reboot_bootloader),
            ("🛠️", "Reboot Recovery",    "adb reboot recovery",    False, self._reboot_recovery),
            # Row 1
            ("⚡", "Reboot Fastbootd",   "fastboot reboot fastboot", False, self._reboot_fastbootd),
            ("🏭", "Reboot EDL Mode",    "adb reboot edl",         True,  self._reboot_edl),
            ("📡", "Reboot Sideload",    "adb reboot sideload",    False, self._reboot_sideload),
            # Row 2
            ("🔌", "Kill ADB Server",    "adb kill-server",        True,  self._kill_server),
            ("🔁", "Restart ADB Server", "adb kill + start-server", False, self._restart_adb),
            ("📲", "Open ADB Shell",     "cmd.exe /k adb shell",   False, self._open_shell),
        ]

        for idx, (emoji, label, hint, is_danger, action) in enumerate(buttons):
            row_idx = idx // 3
            col_idx = idx % 3
            tile = _RebootButton(
                grid, emoji=emoji, label=label, cmd_hint=hint,
                is_danger=is_danger, action=action,
            )
            tile.grid(row=row_idx, column=col_idx, padx=10, pady=10, sticky="nsew")

        for c in range(3):
            grid.columnconfigure(c, weight=1)
        for r in range(3):
            grid.rowconfigure(r, weight=1)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_device_mode(self, mode: str):
        """Called by MainWindow when device mode changes."""
        self._device_mode = mode
        if mode == "fastboot":
            self._mode_banner.configure(
                text="  ⚡ Device in Fastboot Mode — fastboot commands active"
            )
            self._mode_banner.pack(fill="x", padx=20, pady=(0, 6))
        else:
            self._mode_banner.pack_forget()

    # ------------------------------------------------------------------
    # Reboot actions
    # ------------------------------------------------------------------
    def _run_adb(self, *args):
        adb = _adb_path()
        def _worker():
            try:
                result = subprocess.run([adb, *args], capture_output=True, text=True, timeout=15)
                out = result.stdout.strip() or result.stderr.strip() or "(done)"
                self.after(0, lambda: self._main.log(f"[ADB] {' '.join(args)} → {out}"))
            except FileNotFoundError:
                self.after(0, lambda: self._main.log("[ADB] adb.exe not found. Check Settings → ADB Path."))
            except Exception as exc:
                self.after(0, lambda: self._main.log(f"[ADB] Error: {exc}"))
        threading.Thread(target=_worker, daemon=True).start()

    def _run_fb(self, *args):
        fb = _fb_path()
        def _worker():
            try:
                result = subprocess.run([fb, *args], capture_output=True, text=True, timeout=15)
                out = result.stdout.strip() or result.stderr.strip() or "(done)"
                self.after(0, lambda: self._main.log(f"[Fastboot] {' '.join(args)} → {out}"))
            except FileNotFoundError:
                self.after(0, lambda: self._main.log("[Fastboot] fastboot.exe not found."))
            except Exception as exc:
                self.after(0, lambda: self._main.log(f"[Fastboot] Error: {exc}"))
        threading.Thread(target=_worker, daemon=True).start()

    def _get_serial(self) -> str | None:
        d = self._main.get_device()
        return d.serial if d else None

    def _reboot_normal(self):
        self._main.log("Rebooting device …")
        if self._device_mode == "fastboot":
            self._run_fb("reboot")
        else:
            self._run_adb("reboot")

    def _reboot_bootloader(self):
        self._main.log("Rebooting to Bootloader …")
        self._run_adb("reboot", "bootloader")

    def _reboot_recovery(self):
        self._main.log("Rebooting to Recovery …")
        self._run_adb("reboot", "recovery")

    def _reboot_fastbootd(self):
        self._main.log("Rebooting to Fastbootd …")
        self._run_fb("reboot", "fastboot")

    def _reboot_edl(self):
        from tkinter import messagebox
        confirmed = messagebox.askyesno(
            "⚠️ EDL Mode — Qualcomm Only",
            "Rebooting to EDL (Emergency Download Mode) is for Qualcomm devices only.\n\n"
            "Only proceed if you have the correct EDL tools and drivers.\n\n"
            "Proceed?",
        )
        if confirmed:
            self._main.log("Rebooting to EDL mode (Qualcomm) …")
            self._run_adb("reboot", "edl")

    def _reboot_sideload(self):
        self._main.log("Rebooting to ADB Sideload mode …")
        self._run_adb("reboot", "sideload")

    def _kill_server(self):
        self._main.log("Killing ADB server …")
        self._run_adb("kill-server")

    def _restart_adb(self):
        self._main.log("Restarting ADB server …")
        adb = _adb_path()
        def _worker():
            try:
                subprocess.run([adb, "kill-server"], timeout=10)
                self.after(0, lambda: self._main.log("[ADB] Server stopped."))
                subprocess.run([adb, "start-server"], timeout=10)
                self.after(0, lambda: self._main.log("[ADB] Server started successfully."))
            except Exception as exc:
                self.after(0, lambda: self._main.log(f"[ADB] Restart error: {exc}"))
        threading.Thread(target=_worker, daemon=True).start()

    def _open_shell(self):
        self._main.log("Opening interactive ADB shell in Command Prompt …")
        adb = _adb_path()
        try:
            subprocess.Popen(
                ["cmd", "/k", adb, "shell"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        except Exception as exc:
            self._main.log(f"[Shell] Error: {exc}")
