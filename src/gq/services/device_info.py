from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class DeviceInfoService:
    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        self._manager = manager

    def get_hardware_model(self) -> str:
        """
        RFC1801: <GETVER>> returns the hardware/version as an ASCII string (typically 15 bytes).
        """
        self._manager.write(b"<GETVER>>")
        response = self._manager.read(15)
        return response.decode()

    def get_serial_number_bytes(self) -> bytes:
        """
        RFC1801: <GETSERIAL>> returns 7 bytes (serial number in device format).
        """
        self._manager.write(b"<GETSERIAL>>")
        return self._manager.read(7)

    def get_voltage(self) -> str:
        """
        RFC1801: <GETVOLT>> returns the supply voltage as ASCII (typically 5 bytes).
        """
        self._manager.write(b"<GETVOLT>>")
        return self._manager.read(5).decode()