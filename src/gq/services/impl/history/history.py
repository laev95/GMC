from __future__ import annotations

from struct import pack
from typing import Iterator, TYPE_CHECKING

from src.gq.services.impl.history.parser.parser import Parser
from src.gq.services.service_base import ServiceBase

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class HistoryService(ServiceBase):
    """
    Service for reading the internal flash memory (history) of the GQ GMC.
    Encapsulates the <SPIR>> commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager, flash_size: int = 0x1000000):
        """
        :param manager: The central communication instance.
        :param flash_size: The size of the flash memory (Default GMC-500+: 16MB).
        """
        super().__init__(manager)
        self._flash_size = flash_size
        self._addr = 0x000000

    def _spir_read(self, addr: int, length: int) -> bytes:
        """
        Reads a specific block from the flash memory.

        RFC1801: <SPIR[A2][A1][A0][L1][L0]>>

        A2-A0 are 3 bytes address, L1-L0 are 2 bytes length.
        """
        if not (0 <= addr <= 0xFFFFFF):
            raise ValueError("addr must be 0..0xFFFFFF")
        if not (1 <= length <= 4096):
            raise ValueError("length must be 1..4096")

        cmd = pack(">BBBH",
                   (addr >> 16) & 0xFF,
                   (addr >> 8) & 0xFF,
                   addr & 0xFF,
                   length)

        def op() -> bytes:
            self._manager.write(b"<SPIR" + cmd + b">>")
            return self._manager.read(length)
        return self._call("spir_read", op)

    def _iter_history_bytes(self, block_size: int = 4096, min_ff_tail: int = 512) -> Iterator[bytes]:
        """
        Iterates over the flash memory until no more data is present.
        """
        while True:
            block = self._spir_read(self._addr, block_size)

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
            self._addr += block_size
            if self._addr >= self._flash_size:
                return

    def _get_history_bytes(self) -> bytes:
        """Collects all history bytes in a stream."""
        return b"".join(self._iter_history_bytes())

    def get_history(self):
        """
        Reads the entire history and formats it for display.
        Returns a formatted string showing datetime, save_type, and tube for each segment.
        """
        def op() -> str:
            result = Parser(self._get_history_bytes()).parse_result()
            records = result.records
            issues = result.issues

            if not records:
                return "No history data found."

            output_lines = []
            for record in records:
                if record.segment.values:
                    tube_info = f" | Tube: {record.tube}" if record.tube else ""
                    line = (
                        f"{record.ts.strftime('%Y-%m-%d %H:%M:%S')} | {record.save_type}"
                        f"{tube_info} | Reading bytes: {record.segment.reading_mode}"
                    )
                    output_lines.append(line)
                    output_lines.append(f"Values: {', '.join(str(value) for value in record.segment.values)}\n")

            if issues:
                output_lines.append("\nWarnings:")
                for i, issue in enumerate(issues, start=1):
                    msg = f"{i}. {issue.message} (offset={issue.offset}, state={issue.state})"
                    output_lines.append(msg)
                    if issue.raw_hex:
                        output_lines.append(f"   tail_hex: {issue.raw_hex}")
                    if issue.context:
                        output_lines.append(f"   context: {issue.context}")

            return "\n".join(output_lines)

        return self._call("get_history", op)