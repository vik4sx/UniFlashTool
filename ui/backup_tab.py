"""
UniFlash Tool — Backup Tab
Full-device backup/restore, partition pull, and TWRP backup operations.
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

PARTITIONS = ["boot", "recovery", "system", "vendor", "dtbo", "userdata"]


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _adb_path() -> str:
    return os.path.join(_project_root(), "tools", "platform-tools", "adb.exe")


class BackupTab(ctk.CTkFrame):
    """Tab for backup, restore, and partition pull operations."""

    def __init__(self, parent, main_window):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self._main = main_window
        self._running = False
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(
            scroll,
            text="📦 Backup & Restore",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ACCENT,
        ).pack(anchor="w", padx=20, pady=(16, 4))

        self._build_full_backup_card(scroll)
        self._build_partition_pull_card(scroll)
        self._build_twrp_card(scroll)
        self._build_progress_area(scroll)

    def _build_full_backup_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12)
        card.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(card, text="💾 Full Device Backup (ADB)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=ACCENT).pack(anchor="w", padx=16, pady=(14, 4))

        # Save path row
        path_row = ctk.CTkFrame(card, fg_color="transparent")
        path_row.pack(fill="x", padx=16, pady=4)

        self._backup_path = ctk.CTkEntry(
            path_row, placeholder_text="Backup save path (e.g. D:\\backup.ab) …",
            font=ctk.CTkFont(size=12), height=34,
        )
        self._backup_path.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            path_row, text="📂 Browse", width=90, height=34,
            fg_color=ACCENT, hover_color="#0077cc",
            command=self._browse_backup_path,
        ).pack(side="left")

        # Buttons
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(padx=16, pady=(4, 14), anchor="w")

        ctk.CTkButton(
            btn_row, text="💾 Backup Full Device", width=180,
            fg_color=SUCCESS, hover_color="#007733",
            font=ctk.CTkFont(weight="bold"),
            command=self._backup_full,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="📂 Restore Backup", width=160,
            fg_color=CARD_BG, hover_color="#1a3a60",
            font=ctk.CTkFont(weight="bold"),
            command=self._restore_backup,
        ).pack(side="left")

    def _build_partition_pull_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12)
        card.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(card, text="⬇️ Pull Partition Image",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=ACCENT).pack(anchor="w", padx=16, pady=(14, 4))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(row, text="Partition:", font=ctk.CTkFont(weight="bold"),
                     text_color="#aaaacc", width=80).pack(side="left")
        self._part_var = ctk.StringVar(value="boot")
        ctk.CTkOptionMenu(
            row, values=PARTITIONS, variable=self._part_var,
            width=140, fg_color=SIDEBAR_BG, button_color=ACCENT,
        ).pack(side="left", padx=8)

        self._pull_path = ctk.CTkEntry(
            row, placeholder_text="Save location …",
            font=ctk.CTkFont(size=12), height=32,
        )
        self._pull_path.pack(side="left", fill="x", expand=True, padx=8)

        ctk.CTkButton(
            row, text="📂", width=36, height=32,
            fg_color=SIDEBAR_BG, hover_color=CARD_BG,
            command=self._browse_pull_path,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            card, text="⬇️ Pull Partition Image", width=200,
            fg_color=ACCENT, hover_color="#0077cc",
            font=ctk.CTkFont(weight="bold"),
            command=self._pull_partition,
        ).pack(anchor="w", padx=16, pady=(4, 14))

    def _build_twrp_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12)
        card.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(card, text="🛡️ TWRP Backup via ADB",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=ACCENT).pack(anchor="w", padx=16, pady=(14, 4))

        ctk.CTkLabel(
            card,
            text="Automates TWRP backup sequence via ADB shell commands.\n"
                 "Device must be booted into TWRP recovery.",
            font=ctk.CTkFont(size=11),
            text_color="#888899",
        ).pack(anchor="w", padx=16)

        self._twrp_path = ctk.CTkEntry(
            card, placeholder_text="TWRP backup save directory …",
            font=ctk.CTkFont(size=12), height=32,
        )
        self._twrp_path.pack(fill="x", padx=16, pady=6)

        ctk.CTkButton(
            card, text="🛡️ TWRP Backup via ADB", width=220,
            fg_color=WARNING, hover_color="#aa7700", text_color="#000000",
            font=ctk.CTkFont(weight="bold"),
            command=self._twrp_backup,
        ).pack(anchor="w", padx=16, pady=(0, 14))

    def _build_progress_area(self, parent):
        prog_card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12)
        prog_card.pack(fill="x", padx=20, pady=8)

        self._prog_bar = ctk.CTkProgressBar(prog_card, progress_color=ACCENT, mode="indeterminate")
        self._prog_bar.pack(fill="x", padx=16, pady=(14, 4))

        self._prog_label = ctk.CTkLabel(prog_card, text="Idle",
                                         text_color="#888899",
                                         font=ctk.CTkFont(size=11))
        self._prog_label.pack(anchor="w", padx=16)

        self._log_box = ctk.CTkTextbox(
            prog_card,
            font=ctk.CTkFont(family="Courier New", size=10),
            fg_color="#0a0a1a", text_color="#88cc88",
            height=100, state="disabled",
        )
        self._log_box.pack(fill="x", padx=16, pady=(4, 14))

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------
    def _browse_backup_path(self):
        path = filedialog.asksaveasfilename(
            title="Save Backup As",
            defaultextension=".ab",
            filetypes=[("ADB Backup", "*.ab"), ("All", "*.*")],
        )
        if path:
            self._backup_path.delete(0, "end")
            self._backup_path.insert(0, path)

    def _browse_pull_path(self):
        path = filedialog.asksaveasfilename(
            title="Save Partition Image As",
            defaultextension=".img",
            filetypes=[("Image", "*.img"), ("All", "*.*")],
        )
        if path:
            self._pull_path.delete(0, "end")
            self._pull_path.insert(0, path)

    def _log(self, msg: str):
        self.after(0, lambda: self._main.log(msg))
        def _ui():
            self._log_box.configure(state="normal")
            self._log_box.insert("end", msg + "\n")
            self._log_box.configure(state="disabled")
            self._log_box.see("end")
        self.after(0, _ui)

    def _set_progress(self, msg: str, running: bool = True):
        def _ui():
            self._prog_label.configure(text=msg)
            if running:
                self._prog_bar.start()
            else:
                self._prog_bar.stop()
        self.after(0, _ui)

    def _run_adb_cmd(self, args: list[str], label: str):
        """Run adb command in background thread and stream output."""
        adb = _adb_path()
        self._set_progress(f"{label} …", running=True)

        def _worker():
            try:
                proc = subprocess.Popen(
                    [adb, *args],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True,
                )
                for line in proc.stdout:
                    self._log(line.rstrip())
                proc.wait()
                ok = proc.returncode == 0
                self._set_progress(
                    f"✅ {label} done." if ok else f"❌ {label} failed (code {proc.returncode}).",
                    running=False,
                )
                self._log(f"[{label}] Exit code: {proc.returncode}")
            except FileNotFoundError:
                self._set_progress("❌ adb.exe not found!", running=False)
                self._log("[Error] adb.exe not found. Check Settings → ADB Path.")
            except Exception as exc:
                self._set_progress(f"❌ Error: {exc}", running=False)
                self._log(f"[Error] {exc}")

        threading.Thread(target=_worker, daemon=True).start()

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------
    def _backup_full(self):
        path = self._backup_path.get().strip()
        if not path:
            self._log("Please specify a backup file path.")
            return
        self._main.log(f"Starting full device backup → {path}")
        self._run_adb_cmd(["backup", "-apk", "-shared", "-all", "-f", path], "Full Backup")

    def _restore_backup(self):
        path = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("ADB Backup", "*.ab"), ("All", "*.*")],
        )
        if not path:
            return
        self._main.log(f"Restoring backup from: {path}")
        self._run_adb_cmd(["restore", path], "Restore Backup")

    def _pull_partition(self):
        part = self._part_var.get()
        save_path = self._pull_path.get().strip()
        if not save_path:
            self._log("Please specify a save location.")
            return
        self._main.log(f"Pulling partition [{part}] → {save_path}")

        adb = _adb_path()
        # Map partition to block device path (common paths)
        block_paths = {
            "boot":     "/dev/block/by-name/boot",
            "recovery": "/dev/block/by-name/recovery",
            "system":   "/dev/block/by-name/system",
            "vendor":   "/dev/block/by-name/vendor",
            "dtbo":     "/dev/block/by-name/dtbo",
            "userdata": "/dev/block/by-name/userdata",
        }
        block = block_paths.get(part, f"/dev/block/by-name/{part}")

        def _worker():
            try:
                self._set_progress(f"Pulling {part} …", running=True)
                tmp_remote = f"/sdcard/{part}.img"
                # Pull via dd
                proc = subprocess.run(
                    [adb, "shell", f"su -c 'dd if={block} of={tmp_remote}'"],
                    capture_output=True, text=True, timeout=120,
                )
                self._log(proc.stdout or proc.stderr)
                # ADB pull to local
                proc2 = subprocess.run(
                    [adb, "pull", tmp_remote, save_path],
                    capture_output=True, text=True, timeout=120,
                )
                self._log(proc2.stdout or proc2.stderr)
                # Cleanup
                subprocess.run([adb, "shell", f"rm {tmp_remote}"], timeout=10)
                self._set_progress(f"✅ {part} pulled to {save_path}", running=False)
                self._main.log(f"Partition [{part}] pulled successfully.")
            except Exception as exc:
                self._set_progress(f"❌ Error: {exc}", running=False)
                self._log(f"[Pull Error] {exc}")

        threading.Thread(target=_worker, daemon=True).start()

    def _twrp_backup(self):
        save_dir = self._twrp_path.get().strip() or "/sdcard/TWRP/BACKUPS"
        self._main.log(f"Starting TWRP backup via ADB → {save_dir}")
        adb = _adb_path()

        def _worker():
            cmds = [
                f"mkdir -p {save_dir}",
                "twrp backup SYSTEM BOOT RECOVERY DATA",
            ]
            try:
                self._set_progress("TWRP Backup …", running=True)
                for cmd in cmds:
                    proc = subprocess.run(
                        [adb, "shell", cmd],
                        capture_output=True, text=True, timeout=180,
                    )
                    self._log(proc.stdout or proc.stderr)
                self._set_progress("✅ TWRP Backup sequence sent.", running=False)
                self._main.log("TWRP Backup commands executed. Monitor TWRP screen for progress.")
            except Exception as exc:
                self._set_progress(f"❌ Error: {exc}", running=False)
                self._log(f"[TWRP Error] {exc}")

        threading.Thread(target=_worker, daemon=True).start()
