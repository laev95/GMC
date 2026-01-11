from __future__ import annotations

from dataclasses import dataclass

from serial import Serial, SerialException
from serial.tools import list_ports

from src.gq.errors import NotConnectedError, ConnectionLostError, ReadTimeoutError, AckError


@dataclass(frozen=True)
class ConnConfig:
    port: str | None
    baud_rate: int = 115200
    stop_bits: int = 1

class SerialManager:
    """
    Manages serial communication with external devices.

    This class provides functionality for detecting available serial ports,
    connecting to a serial device, sending and receiving data, and closing
    the connection. It can handle default configurations and includes support
    for reading specific data formats.

    :ivar _ACK: Acknowledgment byte used for communication validation.
    :type _ACK: int
    """

    def __init__(self):
        self._conn: Serial | None = None
        self._ACK = 0xAA

    @staticmethod
    def _discover_ports() -> dict[str, str]:
        possible: dict[str, str] = {}
        for port in list_ports.comports():
            if "USB" in port.device or "COM" in port.device:
                possible[port.name] = port.device
        return possible

    def _get_default_config(self) -> ConnConfig:
        ports = self._discover_ports()
        if not ports:
            return ConnConfig(port=None)

        first_port_device = next(iter(ports.values()))
        return ConnConfig(port=first_port_device)

    def connect(self, cfg: ConnConfig = None) -> bool:
        if self._conn and self._conn.is_open:
            return True

        if self._conn and not self._conn.is_open:
            self._conn.open()
            return True

        if not cfg:
            cfg = self._get_default_config()
            if not cfg.port:
                return False

        try:
            self._conn = Serial(
                port=cfg.port,
                baudrate=cfg.baud_rate,
                stopbits=cfg.stop_bits,
                timeout=2
            )
            return True
        except OSError:
            self._conn = None
            return False

    def disconnect(self) -> None:
        if self._conn:
            try:
                self._conn.close()
            except OSError:
                pass
            finally:
                self._conn = None

    def write(self, data: bytes) -> None:
        if self._conn is None:
            raise NotConnectedError("write")
        try:
            self._conn.write(data)
        except (SerialException, OSError) as e:
            self.disconnect()
            raise ConnectionLostError("write", detail=str(e)) from e

    def read(self, n: int) -> bytes:
        if self._conn is None:
            raise NotConnectedError("read")

        try:
            data = self._conn.read(n)
        except OSError as e:
            raise ConnectionLostError("read", detail=str(e)) from e

        if len(data) < n:
            raise ReadTimeoutError(expected=n, received=len(data))
        return data

    def read_u32_be(self) -> int:
        return int.from_bytes(self.read(4), "big")

    def read_ack(self, b: bytes = None) -> bool:
        read_byte = self.read(1)[0] if not b else b
        if read_byte != self._ACK:
            raise AckError(expected=self._ACK, received=read_byte)
        return True
