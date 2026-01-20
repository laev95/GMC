from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from serial import Serial
from serial.tools import list_ports

from src.gq.errors import NotConnectedError, ConnectionLostError, ReadTimeoutError, AckError


@dataclass(frozen=True)
class ConnConfig:
    """
    Defaults for serial connection to GMC 500 and 600 series.
    """
    port: str | None
    baud_rate: int = 115200
    stop_bits: int = 1


class SerialManager:
    """
    Manages serial communication with GMC devices.
    """
    def __init__(self):
        self._conn: Serial | None = None
        self._ACK = 0xAA
        self._valid_ports: dict[str, str] = {}

    def _detect_ports(self) -> None:
        self._valid_ports.clear()
        for port in list_ports.comports():
            if "USB" in port.device or "COM" in port.device:
                self._valid_ports[port.name] = port.device

    def _get_auto_config(self) -> ConnConfig:
        self._detect_ports()
        if not self._valid_ports:
            return ConnConfig(port=None)

        first_port_device = next(iter(self._valid_ports.values()))
        return ConnConfig(port=first_port_device)

    def get_valid_ports(self) -> Dict[str, str]:
        self._detect_ports()
        return self._valid_ports

    def connect(self, port: str = "") -> bool:
        cfg: ConnConfig

        if self._conn and self._conn.is_open:
            return True

        if self._conn and not self._conn.is_open:
            self._conn.open()
            return True

        if port:
            cfg = ConnConfig(port=port)
        else:
            cfg = self._get_auto_config()
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
                self._valid_ports.clear()

    def write(self, data: bytes) -> None:
        if self._conn is None:
            raise NotConnectedError("write")
        try:
            self._conn.write(data)
        except OSError as e:
            raise ConnectionLostError("write", detail=str(e)) from e

    def read(self, bytes_len: int) -> bytes:
        if self._conn is None:
            raise NotConnectedError("read")

        try:
            data = self._conn.read(bytes_len)
        except OSError as e:
            raise ConnectionLostError("read", detail=str(e)) from e

        if len(data) < bytes_len:
            raise ReadTimeoutError(expected=bytes_len, received=len(data))
        return data

    def read_u32_be(self) -> int:
        return int.from_bytes(self.read(4), "big")

    def read_ack(self, b: bytes = None) -> bool:
        """
        Reads and validates an ACK byte from the device.
        :param b: Optional byte to validate instead of reading.
        :return: True if the byte is ACK byte.
        :raises AckError: If the byte is not ACK byte.
        """
        read_byte = self.read(1)[0] if not b else b
        if read_byte != self._ACK:
            raise AckError(expected=self._ACK, received=read_byte)
        return True