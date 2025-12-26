# src/gq/history_reader/history.py
from __future__ import annotations

from struct import pack
from typing import Iterator, TYPE_CHECKING

from src.gq.services.history.parser.parser import parse_gmc_history

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class HistoryService:
    """
    Service zum Auslesen des internen Flash-Speichers (History) des GQ GMC.
    Kapselt die <SPIR>> Befehle gemäß RFC1801.
    """

    def __init__(self, manager: SerialManager, flash_size: int = 0x1000000):
        """
        :param manager: Die zentrale Kommunikationsinstanz.
        :param flash_size: Die Größe des Flash-Speichers (Standard GMC-500+: 16MB).
        """
        self._manager = manager
        self._flash_size = flash_size

    def _spir_read(self, addr: int, length: int) -> bytes:
        """
        Liest einen spezifischen Block aus dem Flash-Speicher.
        """
        if not (0 <= addr <= 0xFFFFFF):
            raise ValueError("addr must be 0..0xFFFFFF")
        if not (1 <= length <= 4096):
            raise ValueError("length must be 1..4096")

        # RFC1801: <SPIR[A2][A1][A0][L1][L0]>>
        # A2-A0 sind 3 Bytes Adresse, L1-L0 sind 2 Bytes Länge.
        cmd = pack(">BBBH",
                   (addr >> 16) & 0xFF,
                   (addr >> 8) & 0xFF,
                   addr & 0xFF,
                   length)

        self._manager.write(b"<SPIR" + cmd + b">>")
        return self._manager.read_exact(length)

    def _iter_history_bytes(self, block_size: int = 4096, min_ff_tail: int = 512) -> Iterator[bytes]:
        """
        Iteriert über den Flash-Speicher, bis keine Daten mehr vorhanden sind.
        """
        addr = 0x000000

        while True:
            block = self._spir_read(addr, block_size)

            if all(b == 0xFF for b in block):
                return

            non_ff_len = len(block)
            while non_ff_len > 0 and block[non_ff_len - 1] == 0xFF:
                non_ff_len -= 1
            ff_tail = len(block) - non_ff_len

            if ff_tail >= min_ff_tail:
                if non_ff_len:
                    yield block[:non_ff_len]
                return

            yield block
            addr += block_size
            if addr >= self._flash_size:
                return

    def _get_history_bytes(self) -> bytes:
        """Sammelt alle History-Bytes in einem Stream."""
        return b"".join(self._iter_history_bytes())

    def get_history(self):
        """
        Liest den gesamten Verlauf aus und nutzt den bestehenden Parser.
        """
        raw = self._get_history_bytes()
        return parse_gmc_history(raw)