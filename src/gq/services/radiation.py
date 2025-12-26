from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class RadiationService:
    """
    Service für strahlungsbezogene Messwerte eines GQ GMC Geigerzählers.
    Kapselt die Befehle gemäß RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initialisiert den Service mit einem SerialManager.

        :param manager: Die zentrale Kommunikationsinstanz.
        """
        self._manager = manager

    def get_cpm(self) -> int:
        """
        RFC1801: <GETCPM>> liefert CPM als 4 Bytes (unsigned, big-endian).
        """
        self._manager.write(b"<GETCPM>>")
        return self._manager.read_u32_be()

    def get_cps(self) -> int:
        """
        RFC1801: <GETCPS>> liefert CPS als 4 Bytes (unsigned, big-endian).
        """
        self._manager.write(b"<GETCPS>>")
        return self._manager.read_u32_be()

    def get_max_cps(self) -> int:
        """
        RFC1801: <GETMAXCPS>> liefert den maximalen CPS seit Einschalten als 4 Bytes u32 (big-endian).
        """
        self._manager.write(b"<GETMAXCPS>>")
        return self._manager.read_u32_be()

    def get_cpm_high_tube(self) -> int:
        """
        RFC1801: <GETCPMH>> (GMC-500+ / Modelle mit High-Dose-Tube) liefert CPM High-Tube als 4 Bytes u32.
        """
        self._manager.write(b"<GETCPMH>>")
        return self._manager.read_u32_be()

    def get_cpm_low_tube(self) -> int:
        """
        RFC1801: <GETCPML>> (GMC-500+ / Modelle mit Low-Dose-Tube) liefert CPM Low-Tube als 4 Bytes u32.
        """
        self._manager.write(b"<GETCPML>>")
        return self._manager.read_u32_be()