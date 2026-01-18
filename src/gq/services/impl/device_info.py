from __future__ import annotations

from typing import TYPE_CHECKING

from src.gq.services.service_base import ServiceBase

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class DeviceInfoService(ServiceBase):
    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        super().__init__(manager)

    def get_hardware_model(self) -> str:
        """
        RFC1801: <GETVER>> returns the hardware/version as an ASCII string (typically 15 bytes).
        """
        def op() -> str:
            self._manager.write(b"<GETVER>>")
            response = self._manager.read(15)
            return response.decode()
        return self._call("get_hardware_model", op)

    def get_serial_number_bytes(self) -> bytes:
        """
        RFC1801: <GETSERIAL>> returns 7 bytes (serial number in device format).
        """
        def op() -> bytes:
            self._manager.write(b"<GETSERIAL>>")
            return self._manager.read(7)
        return self._call("get_serial_number_bytes", op)

    def get_voltage(self) -> str:
        """
        RFC1801: <GETVOLT>> returns the supply voltage as ASCII (typically 5 bytes).
        """
        def op() -> str:
            self._manager.write(b"<GETVOLT>>")
            return self._manager.read(5).decode()
        return self._call("get_voltage", op)
