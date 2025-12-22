from __future__ import annotations

from struct import pack
from typing import Iterator

from src.gq.core_util.core import write, read_exact, FLASH_SIZE
from src.gq.history_reader.parser.parser import parse_gmc_history


def spir_read(addr: int, length: int) -> bytes:
    if not (0 <= addr <= 0xFFFFFF):
        raise ValueError("addr must be 0..0xFFFFFF")
    if not (1 <= length <= 4096):
        raise ValueError("length must be 1..4096")

    cmd = pack(">BBBH",
               (addr >> 16) & 0xFF,
               (addr >> 8) & 0xFF,
               addr & 0xFF,
               length)
    write(b"<SPIR" + cmd + b">>")
    return read_exact(length)


def iter_history_bytes(block_size: int = 4096, min_ff_tail: int = 512) -> Iterator[bytes]:
    addr = 0x000000
    bit_limit = FLASH_SIZE

    while True:
        block = spir_read(addr, block_size)

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
        if addr >= bit_limit:
            return


def get_history_bytes() -> bytes:
    return b"".join(iter_history_bytes())


def get_history():
    raw = get_history_bytes()
    return parse_gmc_history(raw)
