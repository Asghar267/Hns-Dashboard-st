"""
Central business toggles for QR/Blinkco reporting.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class QRBusinessToggles:
    include_unassigned_default: bool = os.getenv("QR_INCLUDE_UNASSIGNED_DEFAULT", "true").lower() in ("1", "true", "yes", "on")
    default_commission_rate: float = float(os.getenv("QR_DEFAULT_COMMISSION_RATE", "2.0"))
    blocked_mode_default: str = os.getenv("QR_BLOCKED_MODE_DEFAULT", "Filtered")


QR_TOGGLES = QRBusinessToggles()

