from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class DeviceInfoService:
    def __init__(self, manager: SerialManager):
        """
        Initialisiert den Service mit einem SerialManager.

        :param manager: Die zentrale Kommunikationsinstanz.
        """
        self._manager = manager
    def get_hardware_model(self) -> str:
        """
        RFC1801: <GETVER>> liefert die Hardware/Version als ASCII-String (typ. 15 Bytes).
        """
        self._manager.write(b"<GETVER>>")
        response = self._manager.read_exact(15)
        return response.decode()


    def get_serial_number_bytes(self) -> bytes:
        """
        RFC1801: <GETSERIAL>> liefert 7 Bytes (Seriennummer im Geräteformat).
        """
        self._manager.write(b"<GETSERIAL>>")
        return self._manager.read_exact(7)


    def get_voltage(self) -> str:
        """
        RFC1801: <GETVOLT>> liefert die Versorgungsspannung als ASCII (typ. 5 Bytes).
        """
        self._manager.write(b"<GETVOLT>>")
        return self._manager.read_exact(5).decode()