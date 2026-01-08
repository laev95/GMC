from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gq.manager import SerialManager

@dataclass(frozen=True)
class DeviceDateTime:
    """
    Data carrier for <GETDATETIME>>.
    year_since_2000: 0 corresponds to the year 2000.
    """
    year_since_2000: int
    month: int
    day: int
    hour: int
    minute: int
    second: int


class RTCService:
    """
    Service for real-time clock (RTC) related commands of a GQ GMC Geiger counter.
    Encapsulates the commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        self._manager = manager

    def get_datetime(self) -> DeviceDateTime:
        """
        RFC1801: <GETDATETIME>> returns 7 bytes:
          YY MM DD HH MM SS 0xAA
        """
        self._manager.write(b"<GETDATETIME>>")
        data = self._manager.read(7)
        if len(data) != 7:
            raise OSError(f"Expected 7 bytes, got {len(data)}")
        yy, mm, dd, hh, mi, ss, ack = data
        if ack != self._manager._ACK:
            raise OSError(f"Expected ack 0xAA as last byte, got 0x{ack:02X}")
        return DeviceDateTime(yy, mm, dd, hh, mi, ss)

    def set_date_year(self, year_since_2000: int) -> bool:
        """
        RFC1801: <SETDATEYY[D0]>> sets the year (since 2000 as 1 byte).
        Returns: 0xAA (_ACK)
        """
        if not (0 <= year_since_2000 <= 0xFF):
            raise ValueError("year_since_2000 must be 0..255 (0=2000)")
        self._manager.write(b"<SETDATEYY" + bytes([year_since_2000]) + b">>")
        return self._manager.read_ack()

    def set_date_month(self, month: int) -> bool:
        """
        RFC1801: <SETDATEMM[D0]>> sets the month (1..12).
        Returns: 0xAA (_ACK)
        """
        if not (1 <= month <= 12):
            raise ValueError("month must be 1..12")
        self._manager.write(b"<SETDATEMM" + bytes([month]) + b">>")
        return self._manager.read_ack()

    def set_date_day(self, day: int) -> bool:
        """
        RFC1801: <SETDATEDD[D0]>> sets the day (1..31).
        Returns: 0xAA (_ACK)
        """
        if not (1 <= day <= 31):
            raise ValueError("day must be 1..31")
        self._manager.write(b"<SETDATEDD" + bytes([day]) + b">>")
        return self._manager.read_ack()

    def set_time_hour(self, hour: int) -> bool:
        """
        RFC1801: <SETTIMEHH[D0]>> sets the hour (0..23).
        Returns: 0xAA (_ACK)
        """
        if not (0 <= hour <= 23):
            raise ValueError("hour must be 0..23")
        self._manager.write(b"<SETTIMEHH" + bytes([hour]) + b">>")
        return self._manager.read_ack()

    def set_time_minute(self, minute: int) -> bool:
        """
        RFC1801: <SETTIMEMM[D0]>> sets the minute (0..59).
        Returns: 0xAA (_ACK)
        """
        if not (0 <= minute <= 59):
            raise ValueError("minute must be 0..59")
        self._manager.write(b"<SETTIMEMM" + bytes([minute]) + b">>")
        return self._manager.read_ack()

    def set_time_second(self, second: int) -> bool:
        """
        RFC1801: <SETTIMESS[D0]>> sets the second (0..59).
        Returns: 0xAA (_ACK)
        """
        if not (0 <= second <= 59):
            raise ValueError("second must be 0..59")
        self._manager.write(b"<SETTIMESS" + bytes([second]) + b">>")
        return self._manager.read_ack()

    def set_datetime(
        self,
        year_since_2000: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
    ) -> bool:
        """
        RFC1801: <SETDATETIME[YYMMDDHHMMSS]>> sets date+time in one command.
        Returns: 0xAA (_ACK)

        All fields are transmitted as individual bytes:
          YY = years since 2000
          MM,DD,HH,MM,SS as usual
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
        self._manager.write(b"<SETDATETIME" + payload + b">>")
        return self._manager.read_ack()