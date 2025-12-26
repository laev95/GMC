from datetime import datetime
from .parser_token import TOKEN_LEN, DATE_LEN, TIMESTAMP_MARKER

__all__ = ["parse_date6", "is_valid_header"]


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


def parse_date6(b6: bytes) -> datetime:
    yy, mo, dd, hh, mi, ss = b6
    return datetime(2000 + yy, mo, dd, hh, mi, ss)


def is_valid_header(buf: bytes, pos: int) -> bool:
    """
    Determines if a given buffer contains a valid header starting at a specified
    position. The validity check involves verifying predefined markers, checking
    a plausible date format, and validating specific byte patterns.

    :param buf: The byte buffer to inspect.
    :type buf: bytes
    :param pos: The starting position within the buffer for header validation.
    :type pos: int
    :return: True if the header is valid, otherwise False.
    :rtype: bool
    """
    if pos + TOKEN_LEN + DATE_LEN + TOKEN_LEN > len(buf):
        return False
    if buf[pos:pos + TOKEN_LEN] != TIMESTAMP_MARKER:
        return False
    date6 = buf[pos + TOKEN_LEN:pos + TOKEN_LEN + DATE_LEN]
    save3 = buf[pos + TOKEN_LEN + DATE_LEN:pos + TOKEN_LEN + DATE_LEN + 3]
    return _is_plausible_date6(date6) and save3[:2] == b"\x55\xaa"


def _bytes_to_uint(b: bytes) -> int:
    return int.from_bytes(b, signed=False)
