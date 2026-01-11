from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gq.manager import SerialManager

@dataclass(frozen=True)
class GyroData:
    """
    RFC1801: Gyro returns raw X/Y/Z values (2 bytes each, unsigned) + _ACK.
    """
    x: int
    y: int
    z: int


class SensorsService:
    """
    Service for sensors (Gyro, Temperature) of a GQ GMC Geiger counter.
    Encapsulates the commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        self._manager = manager

    def get_gyro(self) -> GyroData:
        """
        RFC1801: <GETGYRO>> → 7 bytes:
          X_MSB X_LSB Y_MSB Y_LSB Z_MSB Z_LSB 0xAA
        """
        self._manager.write(b"<GETGYRO>>")
        data = self._manager.read(7)
        if len(data) != 7:
            raise IOError(f"Expected 7 bytes, got {len(data)}")
        x = int.from_bytes(data[0:2], "big", signed=False)
        y = int.from_bytes(data[2:4], "big", signed=False)
        z = int.from_bytes(data[4:6], "big", signed=False)
        self._manager.read_ack(bytes(data[6]))
        return GyroData(x=x, y=y, z=z)

    def get_temperature_raw(self) -> bytes:
        """
        RFC1801: <GETTEMP>> is, according to documentation, not supported on several models.
        Therefore left as a raw read (length not normalized).
        """
        self._manager.write(b"<GETTEMP>>")
        return self._manager.read(32)