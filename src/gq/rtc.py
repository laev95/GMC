from dataclasses import dataclass
from .core import write, read_ack, read_exact, ACK

@dataclass(frozen=True)
class DeviceDateTime:
    """
    Datenträger für <GETDATETIME>>.
    year_since_2000: 0 entspricht Jahr 2000.
    """
    year_since_2000: int
    month: int
    day: int
    hour: int
    minute: int
    second: int


def get_datetime() -> DeviceDateTime:
    """
    RFC1801: <GETDATETIME>> liefert 7 Bytes:
      YY MM DD HH MM SS 0xAA
    """
    write(b"<GETDATETIME>>")
    data = read_exact(7)
    if len(data) != 7:
        raise IOError(f"Expected 7 bytes, got {len(data)}")
    yy, mm, dd, hh, mi, ss, ack = data
    if ack != ACK:
        raise IOError(f"Expected ack 0xAA as last byte, got 0x{ack:02X}")
    return DeviceDateTime(yy, mm, dd, hh, mi, ss)


def set_date_year(year_since_2000: int) -> bool:
    """
    RFC1801: <SETDATEYY[D0]>> setzt Jahr (seit 2000 als 1 Byte).
    Rückgabe: 0xAA (ACK)
    """
    if not (0 <= year_since_2000 <= 0xFF):
        raise ValueError("year_since_2000 must be 0..255 (0=2000)")
    write(b"<SETDATEYY" + bytes([year_since_2000]) + b">>")
    return read_ack()


def set_date_month(month: int) -> bool:
    """
    RFC1801: <SETDATEMM[D0]>> setzt Monat (1..12).
    Rückgabe: 0xAA (ACK)
    """
    if not (1 <= month <= 12):
        raise ValueError("month must be 1..12")
    write(b"<SETDATEMM" + bytes([month]) + b">>")
    return read_ack()


def set_date_day(day: int) -> bool:
    """
    RFC1801: <SETDATEDD[D0]>> setzt Tag (1..31).
    Rückgabe: 0xAA (ACK)
    """
    if not (1 <= day <= 31):
        raise ValueError("day must be 1..31")
    write(b"<SETDATEDD" + bytes([day]) + b">>")
    return read_ack()


def set_time_hour(hour: int) -> bool:
    """
    RFC1801: <SETTIMEHH[D0]>> setzt Stunde (0..23).
    Rückgabe: 0xAA (ACK)
    """
    if not (0 <= hour <= 23):
        raise ValueError("hour must be 0..23")
    write(b"<SETTIMEHH" + bytes([hour]) + b">>")
    return read_ack()


def set_time_minute(minute: int) -> bool:
    """
    RFC1801: <SETTIMEMM[D0]>> setzt Minute (0..59).
    Rückgabe: 0xAA (ACK)
    """
    if not (0 <= minute <= 59):
        raise ValueError("minute must be 0..59")
    write(b"<SETTIMEMM" + bytes([minute]) + b">>")
    return read_ack()


def set_time_second(second: int) -> bool:
    """
    RFC1801: <SETTIMESS[D0]>> setzt Sekunde (0..59).
    Rückgabe: 0xAA (ACK)
    """
    if not (0 <= second <= 59):
        raise ValueError("second must be 0..59")
    write(b"<SETTIMESS" + bytes([second]) + b">>")
    return read_ack()


def set_datetime(
    year_since_2000: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
) -> bool:
    """
    RFC1801: <SETDATETIME[YYMMDDHHMMSS]>> setzt Datum+Zeit in einem Kommando.
    Rückgabe: 0xAA (ACK)

    Alle Felder werden als einzelne Bytes übertragen:
      YY = Jahre seit 2000
      MM,DD,HH,MM,SS wie üblich
    """
    if not (0 <= year_since_2000 <= 0xFF):
        raise ValueError("year_since_2000 must be 0..255")
    if not (1 <= month <= 12):
        raise ValueError("month must be 1..12")
    if not (1 <= day <= 31):
        raise ValueError("day must be 1..31")
    if not (0 <= hour <= 23):
        raise ValueError("hour must be 0..23")
    if not (0 <= minute <= 59):
        raise ValueError("minute must be 0..59")
    if not (0 <= second <= 59):
        raise ValueError("second must be 0..59")

    payload = bytes([year_since_2000, month, day, hour, minute, second])
    write(b"<SETDATETIME" + payload + b">>")
    return read_ack()