from __future__ import annotations

from dataclasses import dataclass

from serial import Serial, SerialException
from serial.tools import list_ports


@dataclass(frozen=True)
class ConnConfig:
    port: str | None
    baud_rate: int = 115200
    stop_bits: int = 1

# TODO: check if connection is not None (state and error handling)
class SerialManager:
    """
    Manages serial communication with external devices.

    This class provides functionality for detecting available serial ports,
    connecting to a serial device, sending and receiving data, and closing
    the connection. It can handle default configurations and includes support
    for reading specific data formats.

    :ivar ACK: Acknowledgment byte used for communication validation.
    :type ACK: int
    """

    def __init__(self):
        self._conn: Serial | None = None
        self.ACK = 0xAA

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
        except (SerialException, OSError):
            self._conn = None
            return False

    def disconnect(self) -> None:
        if self._conn:
            try:
                self._conn.close()
            except (SerialException, OSError):
                pass
            finally:
                self._conn = None

    def write(self, data: bytes):
        self._conn.write(data)

    def read_exact(self, n: int) -> bytes:
        data = self._conn.read(n)
        if len(data) < n:
            raise OSError(f"Timeout: Expected {n} bytes, received {len(data)}")
        return data

    def read_u32_be(self) -> int:
        return int.from_bytes(self.read_exact(4), "big")

    def read_ack(self) -> bool:
        return self.read_exact(1)[0] == self.ACK
