from __future__ import annotations
from typing import List, Optional, Union
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from datetime import datetime


class State(Enum):
    DATE = "DATE"
    SPEC = "SPEC"
    DATA = "DATA"
    ASCI = "ASCI"
    FAIL = "FAIL"


class Reading(IntEnum):
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3
    QUADRUPLE = 4


@dataclass
class Segment:
    """A contiguous run with a certain decoding mode."""
    mode: str  # "single"/"double"/"triple"/"quadruple"/"ascii"
    values: List[Union[int, str]] = field(default_factory=list)


@dataclass
class Record:
    ts: datetime
    save_type_token: str
    save_type: str
    tube: Optional[str] = None
    segments: List[Segment] = field(default_factory=list)
