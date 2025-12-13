from datetime import datetime, timezone
from .parser_token import TOKEN_LEN, DATE_LEN, TIMESTAMP_MARKER

def _is_plausible_date6(b6: bytes) -> bool:
    if len(b6) != 6:
        return False
    yy, mo, dd, hh, mi, ss = b6
    return (
        0 <= yy <= 99 and
        1 <= mo <= 12 and
        1 <= dd <= 31 and
        0 <= hh <= 23 and
        0 <= mi <= 59 and
        0 <= ss <= 59
    )


def _parse_date6(b6: bytes, tz=timezone.utc) -> datetime:
    yy, mo, dd, hh, mi, ss = b6
    return datetime(2000 + yy, mo, dd, hh, mi, ss, tzinfo=tz)


def _is_valid_header(buf: bytes, pos: int) -> bool:
    """
    Treat 55aa00 as a *real* date/header only if:
      55aa00 + 6 plausible date bytes + 55aa?? (any 55aaXX)
    This avoids accidentally splitting when 55aa00 occurs in measurement bytes.
    """
    if pos + TOKEN_LEN + DATE_LEN + TOKEN_LEN > len(buf):
        return False
    if buf[pos:pos + 3] != TIMESTAMP_MARKER:
        return False
    date6 = buf[pos + 3:pos + 3 + DATE_LEN]
    save3 = buf[pos + 3 + DATE_LEN:pos + 3 + DATE_LEN + 3]
    return _is_plausible_date6(date6) and save3[:2] == b"\x55\xaa"


def _bytes_to_uint(b: bytes, endian: str) -> int:
    return int.from_bytes(b, byteorder=endian, signed=False)