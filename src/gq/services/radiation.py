from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class RadiationService:
    """
    Service for radiation-related measured values of a GQ GMC Geiger counter.
    Encapsulates the commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        self._manager = manager

    def get_cpm(self) -> int:
        """
        RFC1801: <GETCPM>> returns CPM as 4 bytes (unsigned, big-endian).
        """
        self._manager.write(b"<GETCPM>>")
        return self._manager.read_u32_be()

    def get_cps(self) -> int:
        """
        RFC1801: <GETCPS>> returns CPS as 4 bytes (unsigned, big-endian).
        """
        self._manager.write(b"<GETCPS>>")
        return self._manager.read_u32_be()

    def get_max_cps(self) -> int:
        """
        RFC1801: <GETMAXCPS>> returns the maximum CPS since power-on as 4 bytes u32 (big-endian).
        """
        self._manager.write(b"<GETMAXCPS>>")
        return self._manager.read_u32_be()

    def get_cpm_high_tube(self) -> int:
        """
        RFC1801: <GETCPMH>> (GMC-500+ / models with high-dose tube) returns CPM high-tube as 4 bytes u32.
        """
        self._manager.write(b"<GETCPMH>>")
        return self._manager.read_u32_be()

    def get_cpm_low_tube(self) -> int:
        """
        RFC1801: <GETCPML>> (GMC-500+ / models with low-dose tube) returns CPM low-tube as 4 bytes u32.
        """
        self._manager.write(b"<GETCPML>>")
        return self._manager.read_u32_be()