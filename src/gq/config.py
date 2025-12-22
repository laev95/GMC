from __future__ import annotations

from struct import pack
from .core import write, read_exact, read_ack

"""
Configuration commands for the GQ device. Sensitive settings, not well documented!
"""


def get_config_bytes() -> bytes:
    write(b"<GETCFG>>")
    return read_exact(512)


def erase_config() -> bool:
    write(b"<ECFG>>")
    return read_ack()


def write_config_byte(addr: int, value: int) -> bool:
    if not (0 <= addr <= 0x1FF):
        raise ValueError("addr must be 0..511")
    if not (0 <= value <= 0xFF):
        raise ValueError("value must be 0..255")

    a1 = (addr >> 8) & 0x01
    a0 = addr & 0xFF
    cmd = pack(">BBB", a1, a0, value)
    write(b"<WCFG" + cmd + b">>")
    return read_ack()


def cfg_update() -> bool:
    write(b"<CFGUPDATE>>")
    return read_ack()


def write_config_block(cfg512: bytes, *, do_erase: bool = True, do_update: bool = True) -> bool:
    if len(cfg512) != 512:
        raise ValueError("cfg512 must be exactly 512 bytes")

    ok = True
    if do_erase:
        ok = ok and erase_config()

    for i, b in enumerate(cfg512):
        ok = ok and write_config_byte(i, b)

    if do_update:
        ok = ok and cfg_update()

    return ok
