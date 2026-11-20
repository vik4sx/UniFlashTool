"""
UniFlash Tool — Info Tab
Scrollable 2-column table of device properties fetched via getprop.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import threading
import subprocess
import os
import sys

from assets.styles.theme import (
    ACCENT, ACCENT_HOVER, DANGER, DANGER_HOVER, SUCCESS, WARNING,
    BG, SIDEBAR_BG, CARD_BG, CARD_HOVER, CARD_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
)

PROP_KEYS = [
    "ro.product.brand",
    "ro.product.manufacturer",
    "ro.product.model",
    "ro.product.device",
    "ro.product.name",
    "ro.build.version.release",
    "ro.build.version.sdk",
    "ro.build.fingerprint",
    "ro.build.date",
    "ro.build.type",
    "ro.build.tags",
    "ro.bootloader",
    "ro.serialno",
    "ro.product.cpu.abi",
    "ro.product.cpu.abilist",
    "ro.board.platform",
    "ro.hardware",
    "sys.usb.state",
    "ro.boot.verifiedbootstate",
    "ro.boot.veritymode",
    "ro.crypto.state",
    "ro.secure",
    "ro.debuggable",
    "gsm.operator.alpha",
    "gsm.network.type",
    "ro.build.display.id",
    "ro.build.version.incremental",
    "dalvik.vm.heapsize",
    "ro.sf.lcd_density",
]


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _adb_path() -> str:
    return os.path.join(_project_root(), "tools", "platform-tools", "adb.exe")


class InfoTab(ctk.CTkFrame):
    """Tab showing full device property table."""

    def __init__(self, parent, main_window):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self._main = main_window
        self._props: dict[str, str] = {}
        self._row_widgets: list[tuple] = []
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 4))

        ctk.CTkLabel(
            header,
            text="📊 Device Properties",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ACCENT,
        ).pack(side="left")

        btn_row = ctk.CTkFrame(header, fg_color="transparent")
        btn_row.pack(side="right")

        ctk.CTkButton(
            btn_row, text="🔄 Refresh", width=100,
            fg_color=ACCENT, hover_color="#0077cc",
            command=self._refresh,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            btn_row, text="📋 Copy All", width=110,
            fg_color=CARD_BG, hover_color="#1a3a60",
            command=self._copy_all,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            btn_row, text="💾 Export TXT", width=120,
            fg_color=CARD_BG, hover_color="#1a3a60",
            command=self._export_txt,
        ).pack(side="left", padx=4)

        # Table column headers
        col_header = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, corner_radius=0, height=28)
        col_header.pack(fill="x", padx=20)
        col_header.pack_propagate(False)

        ctk.CTkLabel(col_header, text="Property", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#8899bb", width=240, anchor="w").pack(side="left", padx=12)
        ctk.CTkLabel(col_header, text="Value", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#8899bb", anchor="w").pack(side="left", padx=4)

        # Scrollable table
        self._table_scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        self._table_scroll.pack(fill="both", expand=True, padx=20, pady=4)

        # Build empty rows
        for idx, key in enumerate(PROP_KEYS):
            row_bg = "#0d2d50" if idx % 2 == 0 else CARD_BG
            row = ctk.CTkFrame(self._table_scroll, fg_color=row_bg, corner_radius=6)
            row.pack(fill="x", pady=1)

            key_lbl = ctk.CTkLabel(
                row, text=key,
                font=ctk.CTkFont(family="Courier New", size=11),
                text_color="#7799bb", width=240, anchor="w",
            )
            key_lbl.pack(side="left", padx=(12, 4), pady=5)

            val_lbl = ctk.CTkLabel(
                row, text="—",
                font=ctk.CTkFont(family="Courier New", size=11),
                text_color="#ddddee", anchor="w",
            )
            val_lbl.pack(side="left", padx=4)

            self._row_widgets.append((key, val_lbl))

        # Status label
        self._status = ctk.CTkLabel(
            self, text="Press 🔄 Refresh to load device properties.",
            font=ctk.CTkFont(size=11), text_color="#555577",
        )
        self._status.pack(pady=4)

    # ------------------------------------------------------------------
    def _refresh(self):
        self._status.configure(text="Fetching properties …", text_color=ACCENT)
        self._main.log("Fetching device properties …")
        adb = _adb_path()

        def _worker():
            props: dict[str, str] = {}
            try:
                # Try to get all props at once
                result = subprocess.run(
                    [adb, "shell", "getprop"],
                    capture_output=True, text=True, timeout=15,
                )
                for line in result.stdout.splitlines():
                    line = line.strip()
                    if line.startswith("[") and "]: [" in line:
                        key_part, _, val_part = line.partition("]: [")
                        key = key_part.lstrip("[")
                        val = val_part.rstrip("]")
                        props[key] = val

                self._props = props
                self.after(0, self._update_table)
                self.after(0, lambda: self._status.configure(
                    text=f"✅ {len(props)} properties loaded.", text_color=SUCCESS))
                self.after(0, lambda: self._main.log(f"Loaded {len(props)} device properties."))
            except FileNotFoundError:
                self.after(0, lambda: self._status.configure(
                    text="❌ adb.exe not found.", text_color=DANGER))
            except Exception as exc:
                self.after(0, lambda: self._status.configure(
                    text=f"❌ Error: {exc}", text_color=DANGER))

        threading.Thread(target=_worker, daemon=True).start()

    def _update_table(self):
        for key, val_lbl in self._row_widgets:
            value = self._props.get(key, "—")
            val_lbl.configure(text=value or "—")

            # Highlight bootloader state
            if key == "ro.boot.verifiedbootstate":
                if "unlocked" in value.lower():
                    val_lbl.configure(text_color=SUCCESS)
                elif "locked" in value.lower():
                    val_lbl.configure(text_color=DANGER)
                else:
                    val_lbl.configure(text_color="#ddddee")
            elif key == "ro.bootloader":
                # Some devices put "UNLOCKED" in ro.bootloader
                if "UNLOCKED" in value.upper():
                    val_lbl.configure(text_color=SUCCESS)
                elif "LOCKED" in value.upper():
                    val_lbl.configure(text_color=DANGER)
                else:
                    val_lbl.configure(text_color="#ddddee")
            else:
                val_lbl.configure(text_color="#ddddee")

    def _build_prop_text(self) -> str:
        lines = []
        for key, _ in self._row_widgets:
            val = self._props.get(key, "N/A")
            lines.append(f"{key:<45} = {val}")
        return "\n".join(lines)

    def _copy_all(self):
        if not self._props:
            self._main.log("No properties loaded — press Refresh first.")
            return
        text = self._build_prop_text()
        self.clipboard_clear()
        self.clipboard_append(text)
        self._main.log("Device properties copied to clipboard.")

    def _export_txt(self):
        if not self._props:
            self._main.log("No properties loaded — press Refresh first.")
            return
        path = filedialog.asksaveasfilename(
            title="Export Device Properties",
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._build_prop_text())
            self._main.log(f"Properties exported to: {path}")
        except Exception as exc:
            self._main.log(f"[Export Error] {exc}")
