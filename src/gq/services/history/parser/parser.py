from __future__ import annotations

from typing import List, Optional

from .parser_helper import ParserHelper
from .parser_model import Record, State, Segment, Reading
from .parser_token import DATE_LEN, TOKEN_LEN, SPECIAL_BYTE_TOKEN, SAVE_TYPE_TOKEN, TUBE_SELECTED_TOKEN, TUBE_TOKEN_LEN, \
    TIMESTAMP_MARKER


class Parser:
    def __init__(self, raw_bytes: bytes):
        self._buf = raw_bytes
        self._ptr = 0
        self._state = State.DATE
        self._reading = Reading.SINGLE
        self._current_record: Optional[Record] = None
        self._last_record_tube: str = ""
        self._current_seg: Optional[Segment] = None
        self._records: List[Record] = []

    def _peek(self, n: int) -> bytes:
        if self._ptr + n > len(self._buf):
            raise EOFError("Unexpected end of stream.")
        return self._buf[self._ptr: self._ptr + n]

    def _read(self, n: int) -> bytes:
        if self._ptr + n > len(self._buf):
            raise EOFError("Unexpected end of stream.")
        out = self._buf[self._ptr: self._ptr + n]
        self._ptr += n
        return out

    def _read_ascii_bytes(self) -> bytes:
        start = self._ptr
        while self._ptr + TOKEN_LEN <= len(self._buf):
            # TODO error handling
            if self._buf[self._ptr:self._ptr + TOKEN_LEN] in SPECIAL_BYTE_TOKEN or self._is_valid_header():
                break
            if self._buf[self._ptr] == b"\xff":
                break
            self._ptr += 1

        return self._buf[start:self._ptr]

    def _need_seg(self, mode: str):
        assert self._current_record is not None
        if self._current_seg is None or self._current_seg.reading_mode != mode:
            self._current_seg = Segment(mode)
            self._current_record.segment = self._current_seg

    def _is_valid_header(self) -> bool:
        """
        Determines if a given buffer contains a valid header starting at a specified
        position. The validity check involves verifying predefined markers, checking
        a plausible date format, and validating specific byte patterns.

        :param buf: The byte buffer to inspect.
        :type buf: bytes
        :param pos: The starting position within the buffer for header validation.
        :type pos: int
        :return: True if the header is valid, otherwise False.
        :rtype: bool
        """
        if self._ptr + TOKEN_LEN + DATE_LEN + TOKEN_LEN > len(self._buf):
            return False
        if self._buf[self._ptr:self._ptr + TOKEN_LEN] != TIMESTAMP_MARKER:
            return False
        date6 = self._buf[self._ptr + TOKEN_LEN:self._ptr + TOKEN_LEN + DATE_LEN]
        save3 = self._buf[self._ptr + TOKEN_LEN + DATE_LEN:self._ptr + TOKEN_LEN + DATE_LEN + 3]
        return ParserHelper.is_plausible_date6(date6) and save3[:2] == b"\x55\xaa"

    def _start_new_record_at_header(self) -> None:
        if self._read(TOKEN_LEN) == TIMESTAMP_MARKER:
            date6 = self._read(DATE_LEN)
            save3 = self._read(TOKEN_LEN)

            ts = ParserHelper.parse_date6(date6)
            save_type = SAVE_TYPE_TOKEN.get(save3, f"unknown({save3.hex()})")

            self._current_record = Record(ts, save_type_token=save3.hex(), save_type=save_type)
            self._current_seg = None
            self._reading = Reading.SINGLE
            self._state = State.SPEC
        else:
            #TODO error handling
            pass

    def parse(self) -> List[Record]:
        """
        Parses a continuous history stream that may include "special byte" tokens
        changing the measurement width or ASCII reading_mode.
        """
        while self._ptr <= len(self._buf):
            match self._state:
                case State.DATE:
                    while self._ptr < len(self._buf) and not self._is_valid_header():
                        self._ptr += 1
                    if self._ptr >= len(self._buf):
                        break
                    self._start_new_record_at_header()
                    self._records.append(self._current_record)
                    continue

                case State.SPEC:
                    try:
                        lookup = self._peek(TOKEN_LEN)
                    except EOFError:
                        # TODO: Handle EOF gracefully, possibly by logging or raising a custom exception
                        break
                    if lookup in SPECIAL_BYTE_TOKEN:
                        tok = self._read(TOKEN_LEN)
                        kind = SPECIAL_BYTE_TOKEN[tok]

                        match kind:
                            case "ascii":
                                self._state = State.ASCI

                            case "double":
                                self._reading = Reading.DOUBLE
                                self._state = State.DATA

                            case "triple":
                                self._reading = Reading.TRIPLE
                                self._state = State.DATA

                            case "quadruple":
                                self._reading = Reading.QUADRUPLE
                                self._state = State.DATA

                            case "tube":
                                tube_tok = self._read(TUBE_TOKEN_LEN)
                                self._current_record.tube = TUBE_SELECTED_TOKEN.get(tube_tok, f"unknown({tube_tok.hex()})")
                                self._last_record_tube = self._current_record.tube
                                self._state = State.SPEC

                            case _:
                                print(f"Unknown special token: {tok.hex()}")
                                self._state = State.FAIL
                    else:
                        self._state = State.DATA

                    if self._current_record.tube is None:
                        self._current_record.tube = self._last_record_tube

                    continue

                case State.DATA:
                    if self._is_valid_header():
                        self._state = State.DATE
                        continue

                    try:
                        lookup = self._peek(TOKEN_LEN)
                    except EOFError:
                        # TODO
                        break
                    if any([key in lookup for key in SPECIAL_BYTE_TOKEN.keys()]):
                        self._state = State.SPEC
                        continue

                    mode_name = self._reading.name.lower()
                    self._need_seg(mode_name)

                    try:
                        if self._peek(TOKEN_LEN) == b"\xff\xff\xff":
                            raise EOFError("Reached end of recording.")
                        raw = self._read(int(self._reading))
                        if raw.hex() == "55":
                            print(lookup)
                    except EOFError as e:
                        print(f"EOF while reading {mode_name} data: {e}")
                        break

                    self._current_seg.values.append(ParserHelper.bytes_to_uint(raw))
                    continue

                case State.ASCI:
                    ascii_bytes = self._read_ascii_bytes()
                    self._need_seg("ascii")

                    if ascii_bytes:
                        try:
                            self._current_seg.values.append(ascii_bytes.decode(encoding="ascii", errors="strict"))
                        except UnicodeDecodeError:
                            self._current_seg.values.append(ascii_bytes.hex())

                    if self._ptr >= len(self._buf):
                        break
                    if self._is_valid_header():
                        self._state = State.DATE
                    else:
                        self._state = State.SPEC
                    continue

        return self._records