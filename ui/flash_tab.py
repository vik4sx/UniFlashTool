"""
UniFlash Tool — Flash Tab
Main flashing interface: file picker, brand selection, options, partition flash, special ops.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import sys

from assets.styles.theme import (
    ACCENT, ACCENT_HOVER, DANGER, DANGER_HOVER, SUCCESS, WARNING,
    BG, SIDEBAR_BG, CARD_BG, CARD_HOVER, CARD_BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
)
from core.brand_logos import get_brand_ctk_image

BRANDS = [
    "Samsung", "Xiaomi", "OnePlus", "Google", "Motorola",
    "Realme", "OPPO", "Vivo", "Sony", "Asus",
    "Nothing", "Tecno", "Infinix", "itel", "Generic",
]

BRAND_METHODS = {
    "samsung":  "ADB Sideload",
    "xiaomi":   "Fastboot",
    "oneplus":  "Fastboot / Sideload",
    "google":   "Fastboot Update",
    "motorola": "Fastboot",
    "realme":   "ADB Sideload",
    "oppo":     "ADB Sideload",
    "vivo":     "Fastboot",
    "sony":     "Fastboot",
    "asus":     "Fastboot",
    "nothing":  "Fastboot",
    "tecno":    "Fastboot",
    "infinix":  "Fastboot",
    "itel":     "Fastboot",
    "generic":  "Auto-Detect",
}

PARTITIONS = ["boot", "recovery", "system", "vendor", "vbmeta", "dtbo", "userdata"]


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ConfirmDialog(ctk.CTkToplevel):
    """Modal confirmation dialog for destructive flash operations."""

    def __init__(self, parent, title: str, message: str):
        super().__init__(parent)
        self.title(title)
        self.geometry("420x200")
        self.resizable(False, False)
        self.configure(fg_color=SIDEBAR_BG)
        self.grab_set()

        self.result = False

        ctk.CTkLabel(
            self, text=f"⚠️  {title}",
            font=ctk.CTkFont(size=15, weight="bold"), text_color=WARNING,
        ).pack(pady=(20, 8), padx=20)
        ctk.CTkLabel(
            self, text=message, wraplength=380,
            font=ctk.CTkFont(size=12), text_color="#ccccdd",
        ).pack(padx=20)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=20)
        ctk.CTkButton(
            btn_row, text="✅ Proceed", width=120,
            fg_color=DANGER, hover_color="#aa2222",
            command=self._ok,
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            btn_row, text="❌ Cancel", width=120,
            fg_color=CARD_BG, hover_color="#1a3a60",
            command=self._cancel,
        ).pack(side="left", padx=8)

        self.wait_window()

    def _ok(self):
        self.result = True
        self.destroy()

    def _cancel(self):
        self.result = False
        self.destroy()


class FlashTab(ctk.CTkFrame):
    """Main flash UI tab."""

    def __init__(self, parent, main_window):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self._main = main_window
        self._cancel_flag = threading.Event()
        self._flash_thread: threading.Thread | None = None
        self._partition_entries: dict[str, ctk.CTkEntry] = {}
        self._adv_visible = False
        self._build_ui()

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Scrollable container
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        self._scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Header
        ctk.CTkLabel(
            self._scroll,
            text="⚡ Flash Firmware",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ACCENT,
        ).pack(anchor="w", padx=20, pady=(16, 4))

        self._build_file_row()
        self._build_brand_row()
        self._build_options_row()
        self._build_flash_button()
        self._build_progress_section()
        self._build_advanced_partitions()
        self._build_special_ops()

    def _build_file_row(self):
        card = ctk.CTkFrame(self._scroll, fg_color=CARD_BG, corner_radius=10)
        card.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(card, text="Firmware File", font=ctk.CTkFont(weight="bold"),
                     text_color="#aaaacc").pack(anchor="w", padx=12, pady=(10, 2))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(0, 10))

        self._file_entry = ctk.CTkEntry(
            row, placeholder_text="Select firmware file (.zip / .img / .tar.md5 / .ozip) …",
            font=ctk.CTkFont(size=12), height=36,
        )
        self._file_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._partition_var = ctk.StringVar(value="boot")
        ctk.CTkOptionMenu(row, values=PARTITIONS, variable=self._partition_var,
                          width=115, fg_color=SIDEBAR_BG, button_color=ACCENT,
                          button_hover_color=ACCENT_HOVER).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            row, text="📂 Browse", width=100, height=36,
            fg_color=ACCENT, hover_color="#0077cc",
            command=self._browse_firmware,
        ).pack(side="left")

    def _build_brand_row(self):
        card = ctk.CTkFrame(self._scroll, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=CARD_BORDER)
        card.pack(fill="x", padx=20, pady=6)

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(row, text="Brand:", font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_SECONDARY, width=50).pack(side="left")

        self._brand_var = ctk.StringVar(value="Generic")
        self._brand_menu = ctk.CTkOptionMenu(
            row, values=BRANDS, variable=self._brand_var,
            width=150, fg_color=SIDEBAR_BG, button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            command=self._on_brand_change,
        )
        self._brand_menu.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(row, text="Method:", font=ctk.CTkFont(weight="bold"),
                     text_color=TEXT_MUTED).pack(side="left")
        self._method_label = ctk.CTkLabel(row, text="Auto-Detect",
                                          text_color=ACCENT,
                                          font=ctk.CTkFont(weight="bold"))
        self._method_label.pack(side="left", padx=8)

        # Dynamic Brand Logo Preview Badge
        self._brand_logo_label = ctk.CTkLabel(row, text="")
        self._brand_logo_label.pack(side="right", padx=12)
        self._update_brand_logo("Generic")

    def _update_brand_logo(self, brand: str):
        img = get_brand_ctk_image(brand, width=130, height=52)
        if img:
            self._brand_logo_label.configure(image=img, text="")
        else:
            self._brand_logo_label.configure(image=None, text=f"🏷️ {brand.upper()}", font=ctk.CTkFont(weight="bold"))

    def _build_options_row(self):
        card = ctk.CTkFrame(self._scroll, fg_color=CARD_BG, corner_radius=10)
        card.pack(fill="x", padx=20, pady=6)
        ctk.CTkLabel(card, text="Flash Options", font=ctk.CTkFont(weight="bold"),
                     text_color="#aaaacc").pack(anchor="w", padx=12, pady=(10, 4))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(0, 10))

        self._wipe_data   = ctk.CTkCheckBox(row, text="Wipe Data",   text_color="#ccccdd")
        self._wipe_cache  = ctk.CTkCheckBox(row, text="Wipe Cache",  text_color="#ccccdd")
        self._wipe_dalvik = ctk.CTkCheckBox(row, text="Wipe Dalvik", text_color="#ccccdd")
        self._sideload    = ctk.CTkCheckBox(row, text="Flash as Sideload", text_color="#ccccdd")

        for cb in (self._wipe_data, self._wipe_cache, self._wipe_dalvik, self._sideload):
            cb.pack(side="left", padx=12)

    def _build_flash_button(self):
        self._flash_btn = ctk.CTkButton(
            self._scroll,
            text="🚀   START FLASH OPERATION   (1-CLICK)",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=58,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            corner_radius=12,
            border_width=1,
            border_color="#FFA04D",
            cursor="hand2",
            command=self._on_flash_now,
        )
        self._flash_btn.pack(fill="x", padx=20, pady=12)

    def _build_progress_section(self):
        self._prog_frame = ctk.CTkFrame(self._scroll, fg_color=CARD_BG, corner_radius=10)
        # Initially hidden — shown during flash
        self._prog_bar = ctk.CTkProgressBar(self._prog_frame, mode="indeterminate",
                                             progress_color=ACCENT)
        self._prog_bar.pack(fill="x", padx=16, pady=(14, 4))

        status_row = ctk.CTkFrame(self._prog_frame, fg_color="transparent")
        status_row.pack(fill="x", padx=16, pady=(0, 10))

        self._prog_status = ctk.CTkLabel(status_row, text="Flashing …",
                                          text_color="#ccccdd",
                                          font=ctk.CTkFont(size=12))
        self._prog_status.pack(side="left")

        self._cancel_btn = ctk.CTkButton(
            status_row, text="✖ Cancel", width=90,
            fg_color=DANGER, hover_color="#aa2222",
            command=self._on_cancel,
        )
        self._cancel_btn.pack(side="right")

    def _build_advanced_partitions(self):
        # Toggle header
        self._adv_toggle = ctk.CTkButton(
            self._scroll,
            text="▶  Advanced Partitions",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=SIDEBAR_BG, hover_color=CARD_BG,
            anchor="w",
            command=self._toggle_advanced,
        )
        self._adv_toggle.pack(fill="x", padx=20, pady=(10, 0))

        self._adv_frame = ctk.CTkFrame(self._scroll, fg_color=CARD_BG, corner_radius=10)
        # (Initially hidden)

        for part in PARTITIONS:
            row = ctk.CTkFrame(self._adv_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=4)

            ctk.CTkLabel(row, text=part, font=ctk.CTkFont(weight="bold"),
                         text_color="#aaaacc", width=80, anchor="w").pack(side="left")

            entry = ctk.CTkEntry(row, placeholder_text=f"Path to {part}.img …",
                                  font=ctk.CTkFont(size=11), height=30)
            entry.pack(side="left", fill="x", expand=True, padx=4)
            self._partition_entries[part] = entry

            ctk.CTkButton(
                row, text="📂", width=36, height=30,
                fg_color=SIDEBAR_BG, hover_color=CARD_BG,
                command=lambda p=part: self._browse_partition(p),
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                row, text="⚡ Flash", width=70, height=30,
                fg_color=ACCENT, hover_color="#0077cc",
                command=lambda p=part: self._flash_partition(p),
            ).pack(side="left", padx=2)

    def _build_special_ops(self):
        ctk.CTkLabel(
            self._scroll, text="Special Operations",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#888899",
        ).pack(anchor="w", padx=20, pady=(14, 4))

        ops_frame = ctk.CTkFrame(self._scroll, fg_color=CARD_BG, corner_radius=10)
        ops_frame.pack(fill="x", padx=20, pady=(0, 20))

        ops = [
            ("🛡️ Flash TWRP",    self._op_twrp),
            ("🧲 Flash Magisk",  self._op_magisk),
            ("📡 ADB Sideload",  self._op_sideload),
            ("🌐 Flash GSI",     self._op_gsi),
            ("⚡ Fastbootd",     self._op_fastbootd),
        ]
        row = ctk.CTkFrame(ops_frame, fg_color="transparent")
        row.pack(padx=12, pady=12)
        for label, cmd in ops:
            ctk.CTkButton(
                row, text=label, width=130, height=38,
                fg_color=SIDEBAR_BG, hover_color=CARD_BG,
                font=ctk.CTkFont(size=11),
                command=cmd,
            ).pack(side="left", padx=4)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _browse_firmware(self):
        path = filedialog.askopenfilename(
            title="Select Firmware",
            filetypes=[
                ("Firmware files", "*.zip *.img *.tar.md5 *.ozip"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self._file_entry.delete(0, "end")
            self._file_entry.insert(0, path)
            self._main.log(f"Firmware selected: {path}")

    def _browse_partition(self, part: str):
        path = filedialog.askopenfilename(
            title=f"Select {part}.img",
            filetypes=[("Image files", "*.img"), ("All files", "*.*")],
        )
        if path:
            entry = self._partition_entries[part]
            entry.delete(0, "end")
            entry.insert(0, path)

    def _on_brand_change(self, brand: str):
        key = brand.lower()
        method = BRAND_METHODS.get(key, "Auto-Detect")
        self._method_label.configure(text=method)
        self._update_brand_logo(brand)
        self._main.log(f"Brand set to {brand} → method: {method}")

    def _toggle_advanced(self):
        self._adv_visible = not self._adv_visible
        if self._adv_visible:
            self._adv_frame.pack(fill="x", padx=20, pady=(0, 4))
            self._adv_toggle.configure(text="▼  Advanced Partitions")
        else:
            self._adv_frame.pack_forget()
            self._adv_toggle.configure(text="▶  Advanced Partitions")

    def _on_flash_now(self):
        fw_path = self._file_entry.get().strip()
        if not fw_path:
            messagebox.showwarning("No File", "Please select a firmware file first.")
            return
        if not os.path.isfile(fw_path):
            messagebox.showerror("File Not Found", f"Cannot find:\n{fw_path}")
            return

        brand  = self._brand_var.get()
        file_type = os.path.splitext(fw_path)[1].lower()
        if file_type == ".img":
            target = self._partition_var.get()
        else:
            target = "ADB sideload" if self._sideload.get() else "Fastboot update"
        opts   = []
        if self._wipe_data.get():   opts.append("Wipe Data")
        if self._wipe_cache.get():  opts.append("Wipe Cache")
        if self._wipe_dalvik.get(): opts.append("Wipe Dalvik")
        if self._sideload.get():    opts.append("Sideload Mode")

        warn_msg = (
            f"You are about to flash:\n{os.path.basename(fw_path)}\n\n"
            f"Brand: {brand}\nTarget: {target}\n"
            f"Options: {', '.join(opts) or 'None'}\n\n"
            "⚠️  This may erase device data. Proceed?"
        )
        dlg = ConfirmDialog(self, "Confirm Flash", warn_msg)
        if not dlg.result:
            self._main.log("Flash cancelled by user.")
            return

        self._start_flash(fw_path, brand)

    def _start_flash(self, fw_path: str, brand: str):
        self._cancel_flag.clear()
        self._prog_frame.pack(fill="x", padx=20, pady=4)
        self._prog_bar.start()
        self._flash_btn.configure(state="disabled")
        self._main.log(f"Starting flash: {os.path.basename(fw_path)} [{brand}]")

        def _worker():
            try:
                root = _project_root()
                if root not in sys.path:
                    sys.path.insert(0, root)
                from core.flash_engine import FlashEngine
                from core.adb_manager import ADBManager
                from core.fastboot_manager import FastbootManager

                adb  = ADBManager()
                fb   = FastbootManager()
                eng  = FlashEngine(adb, fb)

                device = self._main.get_device()
                if not device or device.state not in ("adb", "recovery", "fastboot"):
                    raise RuntimeError("Connect one authorized device and wait for it to appear before flashing.")
                serial = device.serial

                file_type = eng.detect_file_type(fw_path)
                self._update_status(f"Detected file type: {file_type}")

                if file_type == "unknown":
                    raise RuntimeError("Unsupported file type. Choose a supported firmware file.")
                if file_type == "zip" and (self._sideload.get() or device.state in ("recovery",)):
                    if device.state not in ("recovery",):
                        raise RuntimeError("ADB sideload requires the device to be in recovery/sideload mode.")
                    command = eng.flash_zip_sideload(serial, fw_path, callback=self._log_cb)
                elif file_type == "img":
                    if device.state != "fastboot":
                        raise RuntimeError("Partition images can only be flashed while the device is in fastboot mode.")
                    command = eng.flash_partition(serial, self._partition_var.get(), fw_path, callback=self._log_cb)
                elif file_type == "zip":
                    if device.state != "fastboot":
                        raise RuntimeError("Factory ZIP update requires fastboot mode, or select sideload while in recovery.")
                    command = eng.flash_fastboot_update(serial, fw_path, callback=self._log_cb)
                else:
                    raise RuntimeError(f"{file_type} packages are not supported by the selected flashing workflow.")

                self._flash_thread = command
                command.join()
                if self._cancel_flag.is_set():
                    self._flash_done(success=False, message="Flash cancelled; check device state before retrying.")
                elif getattr(command, "returncode", 1) == 0:
                    self._flash_done(success=True)
                else:
                    self._flash_done(success=False, message=f"Flash command failed (exit code {getattr(command, 'returncode', 'unknown')}).")
            except Exception as exc:
                self._update_status(f"Error: {exc}")
                self._flash_done(success=False)

        self._flash_thread = threading.Thread(target=_worker, daemon=True)
        self._flash_thread.start()

    def _flash_done(self, success: bool, message: str | None = None):
        def _ui():
            self._prog_bar.stop()
            self._prog_bar.set(1.0 if success else 0.0)
            self._flash_btn.configure(state="normal")
            msg = message or ("✅ Flash complete!" if success else "❌ Flash failed — check log.")
            self._prog_status.configure(text=msg,
                                         text_color=SUCCESS if success else DANGER)
            self._main.log(msg)
        self.after(0, _ui)

    def _update_status(self, msg: str):
        def _ui():
            self._prog_status.configure(text=msg)
            self._main.log(msg)
        self.after(0, _ui)

    def _log_cb(self, line: str):
        self.after(0, lambda: self._main.log(line))

    def _on_cancel(self):
        self._cancel_flag.set()
        command = self._flash_thread
        if command and hasattr(command, "cancel"):
            command.cancel()
        self._main.log("Flash operation cancelled.")

    def _flash_partition(self, part: str):
        path = self._partition_entries[part].get().strip()
        if not path:
            messagebox.showwarning("No File", f"Select a file for partition: {part}")
            return
        dlg = ConfirmDialog(self, f"Flash {part}",
                             f"Flash {os.path.basename(path)} to partition '{part}'?\n\nThis cannot be undone.")
        if not dlg.result:
            return
        self._main.log(f"Flashing partition [{part}]: {path}")

        def _worker():
            try:
                root = _project_root()
                if root not in sys.path:
                    sys.path.insert(0, root)
                from core.flash_engine import FlashEngine
                from core.adb_manager import ADBManager
                from core.fastboot_manager import FastbootManager
                eng = FlashEngine(ADBManager(), FastbootManager())
                device = self._main.get_device()
                serial = device.serial if device else None
                eng.flash_partition(serial, part, path, callback=self._log_cb)
                self.after(0, lambda: self._main.log(f"[{part}] Flash complete."))
            except Exception as exc:
                self.after(0, lambda: self._main.log(f"[{part}] Error: {exc}"))

        threading.Thread(target=_worker, daemon=True).start()

    # Special ops
    def _op_twrp(self):
        self._main.log("Flash TWRP: select TWRP .img file …")
        path = filedialog.askopenfilename(
            title="Select TWRP Image",
            filetypes=[("TWRP image", "*.img"), ("All", "*.*")],
        )
        if path:
            self._partition_entries["recovery"].delete(0, "end")
            self._partition_entries["recovery"].insert(0, path)
            if not self._adv_visible:
                self._toggle_advanced()
            self._main.log(f"TWRP image loaded: {path}")

    def _op_magisk(self):
        self._main.log("Flash Magisk: select patched boot.img …")
        path = filedialog.askopenfilename(
            title="Select Magisk-patched boot.img",
            filetypes=[("Boot image", "*.img"), ("All", "*.*")],
        )
        if path:
            self._partition_entries["boot"].delete(0, "end")
            self._partition_entries["boot"].insert(0, path)
            if not self._adv_visible:
                self._toggle_advanced()
            self._main.log(f"Magisk boot image loaded: {path}")

    def _op_sideload(self):
        path = filedialog.askopenfilename(
            title="Select ZIP for ADB Sideload",
            filetypes=[("ZIP", "*.zip"), ("All", "*.*")],
        )
        if not path:
            return
        self._main.log(f"ADB Sideload: {os.path.basename(path)}")

        def _worker():
            try:
                root = _project_root()
                if root not in sys.path:
                    sys.path.insert(0, root)
                from core.adb_manager import ADBManager
                adb = ADBManager()
                device = self._main.get_device()
                serial = device.serial if device else None
                adb.sideload(serial, path, callback=self._log_cb)
            except Exception as exc:
                self.after(0, lambda: self._main.log(f"Sideload error: {exc}"))

        threading.Thread(target=_worker, daemon=True).start()

    def _op_gsi(self):
        self._main.log("Flash GSI: select GSI system.img …")
        path = filedialog.askopenfilename(
            title="Select GSI system.img",
            filetypes=[("Image", "*.img"), ("All", "*.*")],
        )
        if path:
            self._partition_entries["system"].delete(0, "end")
            self._partition_entries["system"].insert(0, path)
            if not self._adv_visible:
                self._toggle_advanced()

    def _op_fastbootd(self):
        self._main.log("Rebooting to Fastbootd …")
        def _worker():
            try:
                root = _project_root()
                if root not in sys.path:
                    sys.path.insert(0, root)
                from core.fastboot_manager import FastbootManager
                fb = FastbootManager()
                device = self._main.get_device()
                serial = device.serial if device else None
                fb.reboot(serial, "fastboot", callback=self._log_cb)
            except Exception as exc:
                self.after(0, lambda: self._main.log(f"Fastbootd error: {exc}"))
        threading.Thread(target=_worker, daemon=True).start()
