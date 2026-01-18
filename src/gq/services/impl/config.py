from __future__ import annotations

from struct import pack
from typing import TYPE_CHECKING

from src.gq.services.service_base import ServiceBase

if TYPE_CHECKING:
    from src.gq.manager import SerialManager

"""
Configuration commands for the GQ device. Sensitive settings, not well documented!
"""


class ConfigService(ServiceBase):
    """
    Service for configuration-related commands of a GQ GMC Geiger counter.
    Encapsulates the commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        super().__init__(manager)

    def get_config_bytes(self) -> bytes:
        """
        RFC1801: <GETCFG>> returns the configuration bytes (512 bytes).
        """
        def op() -> bytes:
            self._manager.write(b"<GETCFG>>")
            return self._manager.read(512)
        return self._call("get_config_bytes", op)

    def erase_config(self) -> bool:
        """
        RFC1801: <ECFG>> erases the configuration.
        """
        return self._cmd_ack("erase_config", b"<ECFG>>")

    def write_config_byte(self, addr: int, value: int) -> bool:
        """
        RFC1801: <WCFG[A1][A0][V0]>> writes a single configuration byte.
        """
        self._validate_range("write_config_byte", "addr", addr, 0, 0x1FF)
        self._validate_range("write_config_byte", "value", value, 0, 0xFF)

        a1 = (addr >> 8) & 0x01
        a0 = addr & 0xFF
        cmd = pack(">BBB", a1, a0, value)
        return self._cmd_ack("write_config_byte", b"<WCFG" + cmd + b">>")

    def cfg_update(self) -> bool:
        """
        RFC1801: <CFGUPDATE>> updates the configuration.
        """
        return self._cmd_ack("cfg_update", b"<CFGUPDATE>>")

    def write_config_block(self, cfg512: bytes, *, do_erase: bool = True, do_update: bool = True) -> bool:
        """
        Writes a full 512-byte configuration block.
        """
        self._validate_byte_length("write_config_block", "cfg512", cfg512, 512)

        ok = True
        if do_erase:
            ok = ok and self.erase_config()

        for i, b in enumerate(cfg512):
            ok = ok and self.write_config_byte(i, b)

        if do_update:
            ok = ok and self.cfg_update()

        return ok
