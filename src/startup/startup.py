from __future__ import annotations

from dataclasses import dataclass
from serial import Serial, SerialException
from serial.tools import list_ports

__all__ = ["connect"]

_CONN: Serial | None = None
_PORTS: dict[str, str] = {}


@dataclass(frozen=True)
class ConnConfig:
    port: str
    baud_rate: int = 115200
    stop_bits: int = 1


def _check_ports() -> dict[str, str]:
    possible: dict[str, str] = {}
    for port in list_ports.comports():
        if port.product == "USB Serial":
            model = port.device
            print(f"Found candidate on {port.device}")
            possible[model] = port.device
    return possible


def _get_connection_config() -> ConnConfig:
    global _PORTS
    if not _PORTS:
        _PORTS = _check_ports()
        if not _PORTS:
            return ConnConfig("")

    possible_port = next(iter(_PORTS.values()))
    return ConnConfig(port=possible_port)


def connect() -> Serial | None:
    global _CONN

    if _CONN is not None:
        return _CONN

    cfg = _get_connection_config()
    if cfg.port == "":
        return None

    _CONN = Serial(port=cfg.port, baudrate=cfg.baud_rate, stopbits=cfg.stop_bits)
    return _CONN


def invalidate_connection():
    global _CONN
    _CONN = None
