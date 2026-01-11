from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from typing import List, Optional, Union


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
    reading_mode: str # "single"/"double"/"triple"/"quadruple"/"ascii"
    values: List[Union[int, str]] = field(default_factory=list)


@dataclass
class Record:
    ts: datetime
    save_type_token: str
    save_type: str
    tube: Optional[str] = None
    segment: Segment = field(default_factory=lambda: Segment(reading_mode="no readings"))


class Severity(Enum):
    WARNING = "warning"


@dataclass(frozen=True)
class ParseIssue:
    severity: Severity
    message: str
    offset: int
    state: str
    raw_hex: Optional[str] = None
    context: Optional[dict[str, object]] = None


@dataclass(frozen=True)
class ParserResult:
    records: List[Record]
    issues: List[ParseIssue]
