from .parser_model import Record, State, Segment, Reading
from .parser_token import DATE_LEN, TOKEN_LEN, SPECIAL_BYTE_TOKEN, SAVE_TYPE_TOKEN, TUBE_SELECTED_TOKEN, TUBE_TOKEN_LEN
from .parser_helper import _parse_date6, _is_valid_header, _bytes_to_uint
from typing import List, Optional


def parse_gmc_history(raw_bytes: bytes) -> List[Record]:
    """
    Parses a continuous history stream that may include "special byte" tokens
    changing the measurement width or ASCII mode.
    """
    def read_ascii_bytes() -> bytes:
        nonlocal ptr
        start = ptr
        local_ptr = ptr
        while local_ptr + TOKEN_LEN <= len(buf):
            if buf[local_ptr:local_ptr+TOKEN_LEN] in SPECIAL_BYTE_TOKEN or _is_valid_header(buf, local_ptr):
                break
            if buf[local_ptr] == b"\xff":
                break
            local_ptr += 1
        ptr = local_ptr

        return buf[start:local_ptr]

    def need_seg(mode: str) -> Segment:
        nonlocal current_seg
        assert current_record is not None
        if current_seg is None or current_seg.mode != mode:
            current_seg = Segment(mode)
            current_record.segments.append(current_seg)
        return current_seg

    def read(n: int) -> bytes:
        nonlocal ptr
        if ptr + n > len(buf):
            raise EOFError("Unexpected end of stream.")
        out = buf[ptr : ptr+n]
        ptr += n
        return out

    def peek(n: int) -> bytes:
        if ptr + n > len(buf):
            raise EOFError("Unexpected end of stream.")
        return buf[ptr : ptr+n]

    def start_new_record_at_header() -> None:
        nonlocal current_record, current_seg, reading, state
        _ = read(TOKEN_LEN)
        date6 = read(DATE_LEN)
        save3 = read(TOKEN_LEN)

        ts = _parse_date6(date6)
        save_type = SAVE_TYPE_TOKEN.get(save3, f"unknown({save3.hex()})")

        current_record = Record(ts, save_type_token=save3.hex(), save_type=save_type)
        current_seg = None
        reading = Reading.SINGLE
        state = State.SPEC

    buf = raw_bytes
    ptr = 0
    state = State.DATE
    reading = Reading.SINGLE
    current_record: Optional[Record] = None
    last_record_tube: str = ""
    current_seg: Optional[Segment] = None
    records: List[Record] = []

    while ptr <= len(buf):
        if state == State.DATE:
            # Scan forward until we find a *valid* header
            # (so we don’t get fooled by 55aa00 inside data)
            while ptr < len(buf) and not _is_valid_header(buf, ptr):
                ptr += 1
            if ptr >= len(buf):
                break
            start_new_record_at_header()
            records.append(current_record)
            continue

        if state == State.SPEC:
            try:
                lookup = peek(TOKEN_LEN)
            except EOFError:
                break

            if lookup in SPECIAL_BYTE_TOKEN:
                tok = read(TOKEN_LEN)
                kind = SPECIAL_BYTE_TOKEN[tok]

                if kind == "ascii":
                    state = State.ASCI

                elif kind == "double":
                    reading = Reading.DOUBLE
                    state = State.DATA

                elif kind == "triple":
                    reading = Reading.TRIPLE
                    state = State.DATA

                elif kind == "quadruple":
                    reading = Reading.QUADRUPLE
                    state = State.DATA

                elif kind == "tube":
                    tube_tok = read(TUBE_TOKEN_LEN)
                    current_record.tube = TUBE_SELECTED_TOKEN.get(tube_tok, f"unknown({tube_tok.hex()})")
                    last_record_tube = current_record.tube
                    state = State.SPEC

                else:
                    print(f"Unknown special token: {tok.hex()}")
                    state = State.FAIL
            else:
                state = State.DATA

            if current_record.tube is None:
                current_record.tube = last_record_tube

            continue

        if state == State.ASCI:
            ascii_bytes = read_ascii_bytes()
            seg = need_seg("ascii")

            if ascii_bytes:
                try:
                    seg.values.append(ascii_bytes.decode(encoding="ascii", errors="strict"))
                except UnicodeDecodeError:
                    seg.values.append(ascii_bytes.hex())

            if ptr >= len(buf):
                break
            if _is_valid_header(buf, ptr):
                state = State.DATE
            else:
                state = State.SPEC
            continue

        if state == State.DATA:
            if _is_valid_header(buf, ptr):
                state = State.DATE
                continue

            try:
                lookup = peek(DATE_LEN)
            except EOFError:
                break
            if lookup in SPECIAL_BYTE_TOKEN:
                state = State.SPEC
                continue

            mode_name = reading.name.lower()
            seg = need_seg(mode_name)
            try:
                if peek(TOKEN_LEN) == b"\xff\xff\xff":
                    raise EOFError("Reached end of recording.")
                raw = read(int(reading))
            except EOFError as e:
                print(f"EOF while reading {mode_name} data: {e}")
                break
            seg.values.append(_bytes_to_uint(raw))
            continue

        break

    return records
