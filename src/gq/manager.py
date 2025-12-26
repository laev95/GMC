from __future__ import annotations
from serial import Serial, SerialException
from serial.tools import list_ports
from dataclasses import dataclass

@dataclass(frozen=True)
class ConnConfig:
    port: str
    baud_rate: int = 115200
    stop_bits: int = 1

class SerialManager:
    def __init__(self):
        self._conn: Serial | None = None
        self.ACK = 0xAA

    @staticmethod
    def discover_ports() -> dict[str, str]:
        possible: dict[str, str] = {}
        for port in list_ports.comports():
            if "USB" in port.device or "COM" in port.device:
                possible[port.name] = port.device
        return possible

    def _get_default_config(self) -> ConnConfig:
        ports = self.discover_ports()
        if not ports:
            return ConnConfig(port="")

        first_port_device = next(iter(ports.values()))
        return ConnConfig(port=first_port_device)

    def connect(self, cfg: ConnConfig | None = None) -> bool:
        if self._conn and self._conn.is_open:
            return True

        if cfg is None or cfg.port == "":
            cfg = self._get_default_config()
            if cfg.port == "":
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

    def write(self, data: bytes):
        if not self._conn: raise ConnectionError("Nicht verbunden")
        self._conn.write(data)

    def read_exact(self, n: int) -> bytes:
        if not self._conn: raise ConnectionError("Nicht verbunden")
        data = self._conn.read(n)
        if len(data) < n:
            raise IOError(f"Timeout: Erwartet {n} Bytes, erhalten {len(data)}")
        return data

    def read_u32_be(self) -> int:
        return int.from_bytes(self.read_exact(4), "big")

    def read_ack(self) -> bool:
        return self.read_exact(1)[0] == self.ACK