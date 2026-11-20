"""
UniFlash Tool — Brand Logo & Photo Manager
Loads or dynamically creates stylized brand logos and badges for Android manufacturers.
"""

import os
from typing import Optional

try:
    from PIL import Image, ImageDraw, ImageFont
    import customtkinter as ctk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Brand palette & characteristics
BRAND_DATA = {
    "samsung": {
        "name": "SAMSUNG",
        "bg": "#034EA2",
        "fg": "#FFFFFF",
        "sub": "Galaxy",
        "accent": "#0072D2",
    },
    "xiaomi": {
        "name": "MI",
        "bg": "#FF6900",
        "fg": "#FFFFFF",
        "sub": "Xiaomi / Redmi / POCO",
        "accent": "#FF8533",
    },
    "redmi": {
        "name": "Redmi",
        "bg": "#FF6900",
        "fg": "#FFFFFF",
        "sub": "By Xiaomi",
        "accent": "#FF8533",
    },
    "poco": {
        "name": "POCO",
        "bg": "#FFD700",
        "fg": "#000000",
        "sub": "Everything You Need",
        "accent": "#FFA500",
    },
    "oneplus": {
        "name": "1+",
        "bg": "#EB0028",
        "fg": "#FFFFFF",
        "sub": "ONEPLUS • Never Settle",
        "accent": "#FF2B4D",
    },
    "google": {
        "name": "Google",
        "bg": "#202124",
        "fg": "#4285F4",
        "sub": "Pixel",
        "accent": "#EA4335",
    },
    "pixel": {
        "name": "Pixel",
        "bg": "#202124",
        "fg": "#4285F4",
        "sub": "Google Phone",
        "accent": "#34A853",
    },
    "motorola": {
        "name": "MOTO",
        "bg": "#001428",
        "fg": "#0076CE",
        "sub": "Motorola",
        "accent": "#00A3E0",
    },
    "moto": {
        "name": "MOTO",
        "bg": "#001428",
        "fg": "#0076CE",
        "sub": "Motorola",
        "accent": "#00A3E0",
    },
    "oppo": {
        "name": "OPPO",
        "bg": "#006633",
        "fg": "#FFFFFF",
        "sub": "ColorOS",
        "accent": "#00994C",
    },
    "realme": {
        "name": "realme",
        "bg": "#FFC915",
        "fg": "#111111",
        "sub": "Dare to Leap",
        "accent": "#FFA000",
    },
    "vivo": {
        "name": "vivo",
        "bg": "#415FFF",
        "fg": "#FFFFFF",
        "sub": "FuntouchOS",
        "accent": "#667FFF",
    },
    "iqoo": {
        "name": "iQOO",
        "bg": "#111111",
        "fg": "#FF6B00",
        "sub": "Monster Performance",
        "accent": "#FF8533",
    },
    "sony": {
        "name": "SONY",
        "bg": "#000000",
        "fg": "#FFFFFF",
        "sub": "Xperia",
        "accent": "#FF6B00",
    },
    "asus": {
        "name": "ASUS",
        "bg": "#002B49",
        "fg": "#00A3E0",
        "sub": "ROG / Zenfone",
        "accent": "#FF0033",
    },
    "nothing": {
        "name": "( N )",
        "bg": "#0F0F0F",
        "fg": "#FFFFFF",
        "sub": "NOTHING Phone",
        "accent": "#FF334B",
    },
    "tecno": {
        "name": "TECNO",
        "bg": "#0055A5",
        "fg": "#FFFFFF",
        "sub": "HiOS Mobile",
        "accent": "#0088FF",
    },
    "infinix": {
        "name": "Infinix",
        "bg": "#009944",
        "fg": "#FFFFFF",
        "sub": "XOS Mobile",
        "accent": "#00CC55",
    },
    "itel": {
        "name": "itel",
        "bg": "#CC0000",
        "fg": "#FFFFFF",
        "sub": "itel Mobile",
        "accent": "#FF3333",
    },
    "huawei": {
        "name": "HUAWEI",
        "bg": "#CF0A2C",
        "fg": "#FFFFFF",
        "sub": "HarmonyOS",
        "accent": "#FF3355",
    },
    "generic": {
        "name": "ANDROID",
        "bg": "#1A1A22",
        "fg": "#FF6B00",
        "sub": "Universal Device",
        "accent": "#00E676",
    },
}

_CACHE = {}


def _icons_dir() -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bdir = os.path.join(root, "assets", "icons", "brands")
    os.makedirs(bdir, exist_ok=True)
    return bdir


def generate_brand_image(brand_key: str, width: int = 180, height: int = 80) -> Optional[str]:
    """Generate a clean stylized PNG badge for a brand if it does not exist."""
    if not HAS_PIL:
        return None

    bdir = _icons_dir()
    clean_key = brand_key.lower().strip()
    img_path = os.path.join(bdir, f"{clean_key}.png")

    if os.path.exists(img_path):
        return img_path

    data = BRAND_DATA.get(clean_key, BRAND_DATA["generic"])

    # Draw using PIL
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background
    bg_color = data["bg"]
    border_color = data["accent"]
    radius = 14

    # Background card
    draw.rounded_rectangle(
        [(2, 2), (width - 3, height - 3)],
        radius=radius,
        fill=bg_color,
        outline=border_color,
        width=2,
    )

    # Accent decorative bar on left
    draw.rounded_rectangle(
        [(5, 8), (11, height - 9)],
        radius=3,
        fill=data["accent"],
    )

    # Text rendering
    main_text = data["name"]
    sub_text = data["sub"]
    fg_color = data["fg"]

    # Try default font with fallback
    try:
        font_large = ImageFont.truetype("arialbd.ttf", 24)
        font_small = ImageFont.truetype("segoeui.ttf", 10)
    except Exception:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw main brand name
    draw.text((22, 14), main_text, fill=fg_color, font=font_large)

    # Draw subtext
    draw.text((22, 48), sub_text, fill="#CCCCCC", font=font_small)

    try:
        img.save(img_path, format="PNG")
        return img_path
    except Exception:
        return None


def get_brand_ctk_image(brand_key: str, width: int = 160, height: int = 70):
    """Return a CTkImage for the specified brand, or None if unavailable."""
    if not HAS_PIL:
        return None

    clean_key = (brand_key or "generic").lower().strip()
    cache_key = f"{clean_key}_{width}_{height}"
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    img_path = generate_brand_image(clean_key, width * 2, height * 2)
    if not img_path or not os.path.exists(img_path):
        return None

    try:
        pil_img = Image.open(img_path)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(width, height))
        _CACHE[cache_key] = ctk_img
        return ctk_img
    except Exception:
        return None
