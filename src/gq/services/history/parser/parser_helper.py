from datetime import datetime

class ParserHelper:
    @staticmethod
    def bytes_to_uint(b: bytes) -> int:
        return int.from_bytes(b, signed=False)

    @staticmethod
    def parse_date6(b6: bytes) -> datetime:
        yy, mo, dd, hh, mi, ss = b6
        return datetime(2000 + yy, mo, dd, hh, mi, ss)

    @staticmethod
    def is_plausible_date6(b6: bytes) -> bool:
        if len(b6) != 6:
            return False
        yy, mo, dd, hh, mi, ss = b6
        return (
                0 <= yy <= 99 and
                1 <= mo <= 12 and
                1 <= dd <= 31 and
                0 <= hh <= 23 and
                0 <= mi <= 59 and
                0 <= ss <= 59
        )