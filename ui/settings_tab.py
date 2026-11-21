"""
UniFlash Tool — Settings Tab
Persistent configuration: ADB path, timeouts, theme, log level, etc.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import json
import os
import sys

import webbrowser
from assets.styles.theme import (
    ACCENT, ACCENT_HOVER, DANGER, DANGER_HOVER, SUCCESS, WARNING,
    BG, SIDEBAR_BG, CARD_BG, CARD_HOVER, CARD_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    THEME_DARK, THEME_LIGHT, THEME_OPTIONS,
    DEV_NAME, DEV_GITHUB, DEV_GITHUB_URL
)

DEFAULTS = {
    "adb_path":          "tools/platform-tools/adb.exe",
    "adb_timeout":       10,
    "auto_refresh":      "5",
    "theme":             THEME_DARK,
    "log_level":         "INFO",
}


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _config_path() -> str:
    return os.path.join(_project_root(), "config", "settings.json")


def _load_settings() -> dict:
    path = _config_path()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {**DEFAULTS, **data}
        except Exception:
            pass
    return dict(DEFAULTS)


def _save_settings(data: dict):
    path = _config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class SettingsTab(ctk.CTkFrame):
    """Tab for persistent application settings."""

    def __init__(self, parent, main_window):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self._main = main_window
        self._settings = _load_settings()
        self._build_ui()
        self._populate()

    # ------------------------------------------------------------------
    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(
            scroll,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ACCENT,
        ).pack(anchor="w", padx=20, pady=(16, 4))

        # ---- ADB Path ----
        adb_card = self._make_card(scroll, "🔧 ADB / Fastboot Tools Path")

        adb_row = ctk.CTkFrame(adb_card, fg_color="transparent")
        adb_row.pack(fill="x", padx=16, pady=(4, 12))

        self._adb_path_entry = ctk.CTkEntry(
            adb_row, placeholder_text="Path to adb.exe …",
            font=ctk.CTkFont(size=12), height=34,
        )
        self._adb_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            adb_row, text="📂 Browse", width=90, height=34,
            fg_color=ACCENT, hover_color="#0077cc",
            command=self._browse_adb,
        ).pack(side="left")

        # ---- ADB Timeout ----
        timeout_card = self._make_card(scroll, "⏱️ ADB Command Timeout")

        timeout_row = ctk.CTkFrame(timeout_card, fg_color="transparent")
        timeout_row.pack(fill="x", padx=16, pady=(4, 12))

        self._timeout_label = ctk.CTkLabel(
            timeout_row, text="10 s",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ACCENT, width=50,
        )
        self._timeout_label.pack(side="right", padx=8)

        self._timeout_slider = ctk.CTkSlider(
            timeout_row, from_=5, to=60, number_of_steps=55,
            command=self._on_timeout_change,
            progress_color=ACCENT, button_color=ACCENT,
        )
        self._timeout_slider.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(timeout_card, text="Range: 5 – 60 seconds",
                     font=ctk.CTkFont(size=10), text_color="#555577").pack(anchor="w", padx=16, pady=(0, 8))

        # ---- Auto Refresh ----
        refresh_card = self._make_card(scroll, "🔄 Auto-Refresh Device Interval")
        refresh_row = ctk.CTkFrame(refresh_card, fg_color="transparent")
        refresh_row.pack(fill="x", padx=16, pady=(4, 12))

        ctk.CTkLabel(refresh_row, text="Interval:", font=ctk.CTkFont(weight="bold"),
                     text_color="#aaaacc", width=70).pack(side="left")
        self._refresh_var = ctk.StringVar(value="5")
        ctk.CTkOptionMenu(
            refresh_row, values=["3", "5", "10", "30"],
            variable=self._refresh_var,
            width=100, fg_color=SIDEBAR_BG, button_color=ACCENT,
        ).pack(side="left", padx=8)
        ctk.CTkLabel(refresh_row, text="seconds", text_color="#888899").pack(side="left")

        # ---- Theme ----
        theme_card = self._make_card(scroll, "🎨 Application Theme")
        theme_row = ctk.CTkFrame(theme_card, fg_color="transparent")
        theme_row.pack(fill="x", padx=16, pady=(4, 12))

        ctk.CTkLabel(theme_row, text="Theme Mode:", font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_PRIMARY, width=90).pack(side="left")
        self._theme_var = ctk.StringVar(value=self._settings.get("theme", THEME_DARK))
        self._theme_menu = ctk.CTkOptionMenu(
            theme_row,
            values=[THEME_DARK, THEME_LIGHT],
            variable=self._theme_var,
            width=230,
            fg_color=CARD_BG,
            button_color=ACCENT,
            button_hover_color=ACCENT_HOVER,
            command=self._on_theme_change,
        )
        self._theme_menu.pack(side="left", padx=8)

        ctk.CTkLabel(
            theme_row,
            text="(Instant Live Switch)",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED,
        ).pack(side="left", padx=8)

        # ---- Log Level ----
        log_card = self._make_card(scroll, "📋 Log Level")
        log_row = ctk.CTkFrame(log_card, fg_color="transparent")
        log_row.pack(fill="x", padx=16, pady=(4, 12))

        ctk.CTkLabel(log_row, text="Level:", font=ctk.CTkFont(weight="bold"),
                     text_color="#aaaacc", width=70).pack(side="left")
        self._log_level_var = ctk.StringVar(value="INFO")
        ctk.CTkOptionMenu(
            log_row, values=["DEBUG", "INFO", "WARNING"],
            variable=self._log_level_var,
            width=120, fg_color=SIDEBAR_BG, button_color=ACCENT,
        ).pack(side="left", padx=8)

        # ---- Developer & Credits Card ----
        about_card = self._make_card(scroll, "⚡ About & Developer Credits")
        about_content = ctk.CTkFrame(about_card, fg_color="transparent")
        about_content.pack(fill="x", padx=16, pady=(6, 14))

        ctk.CTkLabel(
            about_content,
            text="UniFlash Tool v1.0 — Black & Orange Edition",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=ACCENT,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            about_content,
            text=f"Developed & Maintained by: {DEV_NAME}",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w", pady=(4, 2))

        ctk.CTkLabel(
            about_content,
            text="Universal Android ADB & Fastboot Suite for all major smartphone manufacturers.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(0, 8))

        cred_btn_row = ctk.CTkFrame(about_content, fg_color="transparent")
        cred_btn_row.pack(anchor="w", pady=(4, 0))

        ctk.CTkButton(
            cred_btn_row,
            text=f"🐙 Visit GitHub Profile (@{DEV_GITHUB})",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            corner_radius=8,
            height=32,
            command=lambda: webbrowser.open(DEV_GITHUB_URL),
            cursor="hand2",
        ).pack(side="left")

        # ---- Action buttons ----
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(pady=16, anchor="w", padx=20)

        ctk.CTkButton(
            btn_row, text="💾 Save Settings", width=160,
            fg_color=SUCCESS, hover_color="#007733",
            font=ctk.CTkFont(weight="bold"),
            command=self._save,
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            btn_row, text="🔁 Reset to Defaults", width=170,
            fg_color=CARD_BG, hover_color="#1a3a60",
            font=ctk.CTkFont(weight="bold"),
            command=self._reset,
        ).pack(side="left")

        # Status label
        self._status_lbl = ctk.CTkLabel(
            scroll, text="",
            font=ctk.CTkFont(size=12), text_color=SUCCESS,
        )
        self._status_lbl.pack(pady=4)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _make_card(self, parent, title: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=CARD_BORDER)
        card.pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(card, text=title,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=ACCENT).pack(anchor="w", padx=16, pady=(14, 4))
        return card

    def _populate(self):
        """Fill widgets from loaded settings."""
        self._adb_path_entry.delete(0, "end")
        self._adb_path_entry.insert(0, self._settings.get("adb_path", DEFAULTS["adb_path"]))

        timeout = int(self._settings.get("adb_timeout", 10))
        self._timeout_slider.set(timeout)
        self._timeout_label.configure(text=f"{timeout} s")

        self._refresh_var.set(str(self._settings.get("auto_refresh", "5")))
        curr_theme = self._settings.get("theme", THEME_DARK)
        if curr_theme not in [THEME_DARK, THEME_LIGHT]:
            curr_theme = THEME_DARK
        self._theme_var.set(curr_theme)
        self._log_level_var.set(self._settings.get("log_level", "INFO"))

    def _collect(self) -> dict:
        return {
            "adb_path":     self._adb_path_entry.get().strip(),
            "adb_timeout":  int(self._timeout_slider.get()),
            "auto_refresh": self._refresh_var.get(),
            "theme":        self._theme_var.get(),
            "log_level":    self._log_level_var.get(),
        }

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _browse_adb(self):
        path = filedialog.askopenfilename(
            title="Select adb.exe",
            filetypes=[("ADB executable", "adb.exe"), ("All", "*.*")],
        )
        if path:
            self._adb_path_entry.delete(0, "end")
            self._adb_path_entry.insert(0, path)

    def _on_timeout_change(self, value: float):
        self._timeout_label.configure(text=f"{int(value)} s")

    def _on_theme_change(self, theme_choice: str):
        mode = "light" if "light" in theme_choice.lower() else "dark"
        self._main.set_app_theme(theme_choice, mode)
        self._settings["theme"] = theme_choice
        _save_settings(self._settings)
        self._main.log(f"Theme switched to: {theme_choice} ({mode.upper()} mode)")

    def _save(self):
        data = self._collect()
        self._settings = data
        try:
            _save_settings(data)
            self._status_lbl.configure(text="✅ Settings saved.", text_color=SUCCESS)
            self._main.log(f"Settings saved to {_config_path()}")
        except Exception as exc:
            self._status_lbl.configure(text=f"❌ Save failed: {exc}", text_color=DANGER)
            self._main.log(f"[Settings] Save error: {exc}")
        self.after(3000, lambda: self._status_lbl.configure(text=""))

    def _reset(self):
        self._settings = dict(DEFAULTS)
        self._populate()
        self._status_lbl.configure(text="🔁 Reset to defaults (not saved).", text_color=WARNING)
        self._main.log("Settings reset to defaults.")
        self.after(3000, lambda: self._status_lbl.configure(text=""))
