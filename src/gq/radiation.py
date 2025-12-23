from src.gq.core_util.core import write, read_u32_be


def get_cpm() -> int:
    """
    RFC1801: <GETCPM>> liefert CPM als 4 Bytes (unsigned, big-endian).
    """
    write(b"<GETCPM>>")
    return read_u32_be()


def get_cps() -> int:
    """
    RFC1801: <GETCPS>> liefert CPS als 4 Bytes (unsigned, big-endian).
    """
    write(b"<GETCPS>>")
    return read_u32_be()


def get_max_cps() -> int:
    """
    RFC1801: <GETMAXCPS>> liefert den maximalen CPS seit Einschalten als 4 Bytes u32 (big-endian).
    """
    write(b"<GETMAXCPS>>")
    return read_u32_be()


def get_cpm_high_tube() -> int:
    """
    RFC1801: <GETCPMH>> (GMC-500+ / Modelle mit High-Dose-Tube) liefert CPM High-Tube als 4 Bytes u32.
    """
    write(b"<GETCPMH>>")
    return read_u32_be()


def get_cpm_low_tube() -> int:
    """
    RFC1801: <GETCPML>> (GMC-500+ / Modelle mit Low-Dose-Tube) liefert CPM Low-Tube als 4 Bytes u32.
    """
    write(b"<GETCPML>>")
    return read_u32_be()