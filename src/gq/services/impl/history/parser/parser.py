from __future__ import annotations

from typing import List, Optional

from .parser_helper import ParserHelper
from .parser_model import Record, State, Segment, Reading, ParserResult, ParseIssue, Severity
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

        self._issues: List[ParseIssue] = []
        self._tail_annotated = False

    def _try_peek(self, n: int) -> bytes | None:
        if self._ptr + n > len(self._buf):
            return None
        return self._buf[self._ptr: self._ptr + n]

    def _try_read(self, n: int) -> bytes | None:
        if self._ptr + n > len(self._buf):
            return None
        out = self._buf[self._ptr: self._ptr + n]
        self._ptr += n
        return out

    def _annotate_eof_tail(self, *, message: str, expected: int | None = None) -> None:
        if self._tail_annotated:
            return

        tail = self._buf[self._ptr:]
        cap = 64
        raw_hex = tail[:cap].hex()

        ctx: dict[str, object] = {"remaining": len(tail)}
        if expected is not None:
            ctx["expected"] = expected
        if len(tail) > cap:
            ctx["truncated_to"] = cap

        self._issues.append(ParseIssue(
            severity=Severity.WARNING,
            message=message,
            offset=self._ptr,
            state=self._state.value,
            raw_hex=raw_hex,
            context=ctx,
        ))
        self._tail_annotated = True

    def _read_ascii_bytes(self) -> bytes:
        start = self._ptr
        while self._ptr + TOKEN_LEN <= len(self._buf):
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
        if self._try_read(TOKEN_LEN) == TIMESTAMP_MARKER:
            date6 = self._try_read(DATE_LEN)
            save3 = self._try_read(TOKEN_LEN)

            ts = ParserHelper.parse_date6(date6)
            save_type = SAVE_TYPE_TOKEN.get(save3, f"unknown({save3.hex()})")

            self._current_record = Record(ts, save_type_token=save3.hex(), save_type=save_type)
        else:
            # Should be unreachable because callers check _is_valid_header() first.
            self._issues.append(ParseIssue(
                severity=Severity.WARNING,
                message="Header mismatch while starting new record; attempting to continue.",
                offset=max(0, self._ptr - TOKEN_LEN),
                state=self._state.value,
            ))

    def parse_result(self) -> ParserResult:
        """
        Tolerant parse:
        - Keeps partial last record
        - Drops partial values
        - Annotates ONLY final tail/EOF as a WARNING with a hex dump
        """
        while self._ptr < len(self._buf):
            match self._state:
                case State.DATE:
                    while self._ptr < len(self._buf) and not self._is_valid_header():
                        self._ptr += 1
                    if self._ptr >= len(self._buf):
                        break

                    self._start_new_record_at_header()
                    if self._current_record is not None:
                        self._current_seg = None
                        self._reading = Reading.SINGLE
                        self._state = State.SPEC
                        self._records.append(self._current_record)
                    continue

                case State.SPEC:
                    lookup = self._try_peek(TOKEN_LEN)
                    if lookup is None:
                        self._annotate_eof_tail(message="EOF while looking for special token/header.")
                        break

                    if lookup in SPECIAL_BYTE_TOKEN:
                        tok = self._try_read(TOKEN_LEN)
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
                                tube_tok = self._try_read(TUBE_TOKEN_LEN)
                                if tube_tok is None:
                                    self._annotate_eof_tail(message="EOF while reading tube token.", expected=TUBE_TOKEN_LEN)
                                    break
                                if self._current_record is None:
                                    self._issues.append(ParseIssue(
                                        severity=Severity.WARNING,
                                        message="Got tube token but no current record; skipping.",
                                        offset=self._ptr,
                                        state=self._state.value,
                                    ))
                                    self._state = State.DATE
                                else:
                                    # Should be unreachable since the loop starts with date parsing.
                                    self._current_record.tube = TUBE_SELECTED_TOKEN.get(tube_tok, f"unknown({tube_tok.hex()})")
                                    self._last_record_tube = self._current_record.tube
                                    self._state = State.SPEC

                            case _:
                                # Should be unreachable since match-case is already exhaustive.
                                self._issues.append(ParseIssue(
                                    severity=Severity.WARNING,
                                    message=f"Unknown special token kind: {kind}",
                                    offset=max(0, self._ptr - TOKEN_LEN),
                                    state=self._state.value,
                                    context={"token_hex": tok.hex()},
                                ))
                                self._state = State.DATA
                    else:
                        self._state = State.DATA

                    if self._current_record is not None and self._current_record.tube is None:
                        self._current_record.tube = self._last_record_tube

                    continue

                case State.DATA:
                    if self._is_valid_header():
                        self._state = State.DATE
                        continue

                    lookup = self._try_peek(TOKEN_LEN)
                    if lookup is None:
                        self._annotate_eof_tail(message="EOF while reading data token.")
                        break

                    if any(key in lookup for key in SPECIAL_BYTE_TOKEN.keys()):
                        self._state = State.SPEC
                        continue

                    mode_name = self._reading.name.lower()
                    self._need_seg(mode_name)

                    end_marker = self._try_peek(TOKEN_LEN)
                    if end_marker is None:
                        self._annotate_eof_tail(message="EOF while checking end marker.")
                        break
                    if end_marker == b"\xff\xff\xff":
                        break

                    reading_bytes = int(self._reading)
                    raw = self._try_read(reading_bytes)
                    if raw is None:
                        self._annotate_eof_tail(
                            message=f"EOF mid-value while reading {mode_name}; dropped partial value.",
                            expected=reading_bytes,
                        )
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

        return ParserResult(records=self._records, issues=self._issues)
