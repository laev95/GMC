from parser_model import Record, State, Segment, Reading
from parser_token import DATE_LEN, TOKEN_LEN, SPECIAL_BYTE_TOKEN, SAVE_TYPE_TOKEN, TUBE_SELECTED_TOKEN
from parser_helper import _parse_date6, _is_valid_header, _bytes_to_uint
from datetime import timezone
from typing import List, Optional


def parse_gmc_history(
    hex_string: str,
    *,
    tz=timezone.utc,
    endian: str = "big",   # try "little" if values look wrong
) -> List[Record]:
    """
    Parses a continuous history stream that may include "special byte" tokens
    changing the measurement width or ASCII mode.

    Assumptions (matching your state machine):
      - A new record begins at a valid header: 55aa00 + date6 + save_type_token
      - Inside data, the 3-byte sequences 55aa01..55aa05 can appear as *special* tokens
        (double/ascii/triple/quadruple/tube), changing how subsequent measurements decode.
      - Tube token (55aa05 in SPECIAL_BYTE_TOKEN) is followed by another 3-byte token
        selecting tube (55aa00/01/02), then continues.
    """
    s = "".join(hex_string.split()).lower()
    if len(s) % 2:
        raise ValueError("Odd-length hex string.")
    buf = bytes.fromhex(s)

    ptr = 0
    state = State.DATE
    reading = Reading.SINGLE
    current_record: Optional[Record] = None
    current_seg: Optional[Segment] = None

    def need_seg(mode: str) -> Segment:
        nonlocal current_seg
        assert current_record is not None
        if current_seg is None or current_seg.mode != mode:
            current_seg = Segment(mode=mode)
            current_record.segments.append(current_seg)
        return current_seg

    def read(n: int) -> bytes:
        nonlocal ptr
        if ptr + n > len(buf):
            raise EOFError("Unexpected end of stream.")
        out = buf[ptr:ptr + n]
        ptr += n
        return out

    def peek(n: int) -> bytes:
        return buf[ptr:ptr + n]

    def start_new_record_at_header() -> None:
        nonlocal current_record, current_seg, reading, state
        # we are positioned at 55aa00
        _ = read(3)                 # 55aa00
        date6 = read(DATE_LEN)
        save3 = read(3)

        ts = _parse_date6(date6, tz=tz)
        save_type = SAVE_TYPE_TOKEN.get(save3, f"unknown({save3.hex()})")

        current_record = Record(ts=ts, save_type_token=save3, save_type=save_type)
        current_seg = None
        reading = Reading.SINGLE
        state = State.SPEC  # next tokens inside the record might immediately set mode

    records: List[Record] = []

    while ptr < len(buf):
        if state == State.DATE:
            # Scan forward until we find a *valid* header
            # (so we don’t get fooled by 55aa00 inside data)
            while ptr < len(buf) and not _is_valid_header(buf, ptr):
                ptr += 1
            if ptr >= len(buf):
                break
            start_new_record_at_header()
            records.append(current_record)  # type: ignore[arg-type]
            continue

        if current_record is None:
            state = State.FAIL
            break

        if state == State.SPEC:
            # In your naive loop you keep consuming TOKEN_LEN chunks and react if special.
            tok = read(TOKEN_LEN)

            if tok in SPECIAL_BYTE_TOKEN:
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
                    # Next 3 bytes select tube
                    tube_tok = read(TOKEN_LEN)
                    current_record.tube = TUBE_SELECTED_TOKEN.get(tube_tok, f"unknown({tube_tok.hex()})")
                    # After tube selection, continue in SPEC (mode may follow) or DATA;
                    # your naive code jumps to DATE, but in real streams tube selection
                    # often just changes metadata. Adjust here if you confirm otherwise.
                    state = State.SPEC
                else:
                    state = State.FAIL

            else:
                # Not a special token; most streams will go into DATA with current reading.
                # If you *require* a special token before data, remove this.
                state = State.DATA
                # "unread" the token by stepping back, so DATA can treat it as data/tokens
                ptr -= TOKEN_LEN

            continue

        if state == State.ASCI:
            seg = need_seg("ascii")
            # Read bytes until we hit a token prefix 55aa?? that is either:
            #   - a valid header (55aa00 + date + 55aa??)
            #   - a special token (55aa01..05)
            # We stop *before* that token so the main loop can process it.
            start = ptr
            i = ptr
            while i + 3 <= len(buf):
                if buf[i:i + 2] == b"\x55\xaa":
                    cand = buf[i:i + 3]
                    if cand in SPECIAL_BYTE_TOKEN or _is_valid_header(buf, i):
                        break
                i += 1
            ascii_bytes = buf[start:i]
            ptr = i

            # decode best-effort; keep raw hex on failure
            if ascii_bytes:
                try:
                    seg.values.append(ascii_bytes.decode("ascii", errors="strict"))
                except UnicodeDecodeError:
                    seg.values.append(ascii_bytes.hex())

            # Next thing is a token (special or header) or EOF
            if ptr >= len(buf):
                break
            if _is_valid_header(buf, ptr):
                state = State.DATE
            else:
                state = State.SPEC  # likely 55aa01..05
            continue

        if state == State.DATA:
            # Before consuming a measurement, check if we're at a token.
            if _is_valid_header(buf, ptr):
                state = State.DATE
                continue

            if peek(2) == b"\x55\xaa" and peek(3) in SPECIAL_BYTE_TOKEN:
                state = State.SPEC
                continue

            # Otherwise consume one measurement of current width.
            mode_name = {
                Reading.SINGLE: "single",
                Reading.DOUBLE: "double",
                Reading.TRIPLE: "triple",
                Reading.QUADRUPLE: "quadruple",
            }[reading]
            seg = need_seg(mode_name)
            try:
                raw = read(int(reading))
            except EOFError:
                break
            seg.values.append(_bytes_to_uint(raw, endian=endian))
            continue

        # FAIL or unknown
        break

    return records


# ---------------- example use ----------------
if __name__ == "__main__":
    example = """
    55aa00 180901111d34 55aa02 1a1610100c0b140f0b
    55aa00 180901112c07 55aa02
    55aa00 180901112c08 55aa03
    55aa00 180901112c08 55aa04
    55aa00 180901112c09 55aa05
    55aa00 180901112c09 55aa00
    """
    recs = parse_gmc_history(example, endian="big")
    for r in recs:
        print(r.ts.isoformat(), r.save_type, "tube=", r.tube)
        for seg in r.segments:
            print("  ", seg.mode, seg.values[:20])
