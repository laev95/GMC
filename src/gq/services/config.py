from __future__ import annotations

from struct import pack
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gq.manager import SerialManager

"""
Configuration commands for the GQ device. Sensitive settings, not well documented!
"""


class ConfigService:
    """
    Service for configuration-related commands of a GQ GMC Geiger counter.
    Encapsulates the commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        self._manager = manager

    def get_config_bytes(self) -> bytes:
        """
        RFC1801: <GETCFG>> returns the configuration bytes (512 bytes).
        """
        self._manager.write(b"<GETCFG>>")
        return self._manager.read_exact(512)

    def erase_config(self) -> bool:
        """
        RFC1801: <ECFG>> erases the configuration.
        """
        self._manager.write(b"<ECFG>>")
        return self._manager.read_ack()

    def write_config_byte(self, addr: int, value: int) -> bool:
        """
        RFC1801: <WCFG[A1][A0][V0]>> writes a single configuration byte.
        """
        if not (0 <= addr <= 0x1FF):
            raise ValueError("addr must be 0..511")
        if not (0 <= value <= 0xFF):
            raise ValueError("value must be 0..255")

        a1 = (addr >> 8) & 0x01
        a0 = addr & 0xFF
        cmd = pack(">BBB", a1, a0, value)
        self._manager.write(b"<WCFG" + cmd + b">>")
        return self._manager.read_ack()

    def cfg_update(self) -> bool:
        """
        RFC1801: <CFGUPDATE>> updates the configuration.
        """
        self._manager.write(b"<CFGUPDATE>>")
        return self._manager.read_ack()

    def write_config_block(self, cfg512: bytes, *, do_erase: bool = True, do_update: bool = True) -> bool:
        """
        Writes a full 512-byte configuration block.
        """
        if len(cfg512) != 512:
            raise ValueError("cfg512 must be exactly 512 bytes")

        ok = True
        if do_erase:
            ok = ok and self.erase_config()

        for i, b in enumerate(cfg512):
            ok = ok and self.write_config_byte(i, b)

        if do_update:
            ok = ok and self.cfg_update()

        return ok
