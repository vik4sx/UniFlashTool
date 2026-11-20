"""
UniFlash Tool — Brand Handlers Package

Exports all brand-specific flash handler classes and provides
a convenience factory function ``get_handler()`` that maps a brand
key string to the appropriate handler instance.

Brand key → Handler class mapping:
  samsung   → SamsungHandler
  xiaomi    → XiaomiHandler
  redmi     → XiaomiHandler
  poco      → XiaomiHandler
  oneplus   → OnePlusHandler
  google    → GoogleHandler
  motorola  → MotorolaHandler
  moto      → MotorolaHandler
  oppo      → OppoHandler
  realme    → RealmeHandler
  vivo      → VivoHandler
  iqoo      → VivoHandler
  sony      → SonyHandler
  asus      → AsusHandler
  nothing   → NothingHandler
  <other>   → GenericHandler  (fallback)
"""

from .samsung import SamsungHandler
from .xiaomi import XiaomiHandler
from .oneplus import OnePlusHandler
from .google import GoogleHandler
from .motorola import MotorolaHandler
from .oppo_realme import OppoHandler, RealmeHandler
from .vivo import VivoHandler
from .sony import SonyHandler
from .asus import AsusHandler
from .nothing import NothingHandler
from .generic import GenericHandler

__all__ = [
    "SamsungHandler",
    "XiaomiHandler",
    "OnePlusHandler",
    "GoogleHandler",
    "MotorolaHandler",
    "OppoHandler",
    "RealmeHandler",
    "VivoHandler",
    "SonyHandler",
    "AsusHandler",
    "NothingHandler",
    "GenericHandler",
    "BRAND_MAP",
    "get_handler",
]

# ------------------------------------------------------------------ #
# Brand → Handler class mapping                                        #
# ------------------------------------------------------------------ #

BRAND_MAP: dict = {
    "samsung": SamsungHandler,
    "xiaomi": XiaomiHandler,
    "redmi": XiaomiHandler,
    "poco": XiaomiHandler,
    "oneplus": OnePlusHandler,
    "google": GoogleHandler,
    "pixel": GoogleHandler,
    "motorola": MotorolaHandler,
    "moto": MotorolaHandler,
    "oppo": OppoHandler,
    "realme": RealmeHandler,
    "vivo": VivoHandler,
    "iqoo": VivoHandler,
    "sony": SonyHandler,
    "asus": AsusHandler,
    "nothing": NothingHandler,
}


def get_handler(brand_key: str, serial: str, model: str, adb, fastboot):
    """
    Return an instantiated brand handler for the given brand key.

    If ``brand_key`` is not recognised, falls back to ``GenericHandler``.

    Args:
        brand_key: Brand identifier string (case-insensitive), e.g. "samsung".
        serial:    Device serial number.
        model:     Device model string (e.g. "SM-G991B").
        adb:       ADBManager instance.
        fastboot:  FastbootManager instance.

    Returns:
        An instance of the appropriate BaseBrandHandler subclass.

    Example::

        handler = get_handler("xiaomi", "ABC123", "Redmi Note 11", adb, fb)
        success = handler.flash("/path/to/firmware.zip", {}, print)
    """
    cls = BRAND_MAP.get(brand_key.lower(), GenericHandler)
    return cls(serial, model, adb, fastboot)
