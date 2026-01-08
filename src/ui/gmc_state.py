from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class GlobalState:
    radiation: Dict[str, int] = field(default_factory=lambda: {
        'cpm': 0, 'cps': 0, 'max_cps': 0, 'cpm_high': 0, 'cpm_low': 0
    })
    is_connected: bool = True
    device_name: str = ""
    is_active: bool = False
    error_message: str = ''
    history_data: str = ''