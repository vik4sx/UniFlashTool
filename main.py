"""
UniFlash Tool v1.0 — by Tejas Jadhav
Universal ADB/Fastboot GUI for Android devices
"""
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from ui.main_window import MainWindow


def main():
    settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "settings.json")
    saved_theme = "Dark (Black & Orange)"
    try:
        if os.path.isfile(settings_file):
            with open(settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                saved_theme = data.get("theme", "Dark (Black & Orange)")
    except Exception:
        pass

    mode = "light" if "light" in saved_theme.lower() else "dark"
    ctk.set_appearance_mode(mode)
    ctk.set_default_color_theme("blue")

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
