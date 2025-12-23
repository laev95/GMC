from __future__ import annotations

from serial import Serial

from src.startup.startup import connect

__all__ = ["ACK", "FLASH_SIZE", "read_exact", "read_ack", "read_u32_be", "write"]

ACK = 0xAA
FLASH_SIZE = 0x1000000 #GMC 500+


def _ensure_conn() -> Serial:
    return connect()


def read_exact(n: int) -> bytes:
    serial_con = _ensure_conn()
    buf = bytearray()
    while len(buf) < n:
        chunk = serial_con.read(n - len(buf))
        if not chunk:
            raise OSError(f"Timeout/EOF while reading {n} bytes (got {len(buf)})")
        buf += chunk
    return bytes(buf)


def read_ack() -> bool:
    b = read_exact(1)
    return len(b) == 1 and b[0] == ACK


def read_u32_be() -> int:
    data = read_exact(4)
    return int.from_bytes(data, "big", signed=False)


def write(data: bytes) -> None:
    ser = _ensure_conn()
    ser.write(data)
