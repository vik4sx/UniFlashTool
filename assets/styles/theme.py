"""
UniFlash Tool — Theme & Palette Constants
Supports:
  1. Dark Theme: Black & Orange
  2. Light Theme: White & Orange
CustomTkinter tuples format: (light_color, dark_color)
"""

# Theme Mode Identifier
THEME_DARK = "Dark (Black & Orange)"
THEME_LIGHT = "Light (White & Orange)"

THEME_OPTIONS = [THEME_DARK, THEME_LIGHT]

# Primary Accent (Orange in both themes)
ACCENT          = "#FF6B00"                     # Vibrant Cyber Orange
ACCENT_HOVER    = "#FF8533"                     # Bright Orange Hover
ACCENT_MUTED    = "#CC5500"                     # Deep Tone Orange
ACCENT_GLOW     = "#FFA04D"                     # Light Orange Highlight

# Core Surfaces: (Light Mode, Dark Mode)
BG              = ("#F0F2F6", "#0A0A0D")        # Clean Light Surface / Pitch Obsidian Black
SIDEBAR_BG      = ("#FFFFFF", "#121217")        # Pure White Sidebar / Stealth Charcoal
CARD_BG         = ("#FFFFFF", "#18181F")        # Crisp White Card / Deep Graphite Surface
CARD_HOVER      = ("#F2F4F8", "#22222B")        # Light Surface Hover / Dark Elevated Hover
CARD_BORDER     = ("#DDE1EA", "#2A2A36")        # Crisp Light Border / Dark Component Border

# Hero / Special Highlight Cards
HERO_BG         = ("#FFF5EB", "#181822")        # Warm White Orange Tint / Dark Obsidian Orange Tint
HERO_BADGE_BG   = ("#EAECEF", "#121217")        # Light Badge / Dark Badge

# Console Surfaces
CONSOLE_BG      = ("#E8ECF2", "#060608")        # Light Console Surface / Deep Black Terminal
CONSOLE_HEADER  = ("#DDE2EC", "#0F0F14")        # Light Header / Dark Header
CONSOLE_TEXT    = ("#007722", "#33FF88")        # Dark Emerald / Neon Green Terminal Output

# Status & Alert Colors
DANGER          = "#FF334B"                     # Crimson Red
DANGER_HOVER    = "#E02038"                     # Deep Red Hover
SUCCESS         = ("#009944", "#00E676")        # Forest Emerald / Neon Emerald
WARNING         = ("#E68A00", "#FFB300")        # Amber Orange
INFO            = "#FF6B00"                     # Orange Info

# Text Hierarchies: (Light Mode, Dark Mode)
TEXT_PRIMARY    = ("#14141C", "#FFFFFF")        # Deep Charcoal Black / Pure White
TEXT_SECONDARY  = ("#484B59", "#A0A0B0")        # Slate Grey / Slate Silver
TEXT_MUTED      = ("#767A8A", "#5A5A6A")        # Dimmed Grey / Muted Dark Gray
BUTTON_HOVER    = "#FF8533"

# Credits
DEV_NAME        = "Tejas Jadhav"
DEV_GITHUB      = "vik4sx"
DEV_GITHUB_URL  = "https://github.com/vik4sx"
