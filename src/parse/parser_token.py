SAVE_TYPE_TOKEN = {
    b"\x55\xaa\x00": "off",
    b"\x55\xaa\x01": "save every second",
    b"\x55\xaa\x02": "save every minute",
    b"\x55\xaa\x03": "save every hour (average)",
    b"\x55\xaa\x04": "save every second after threshold",
    b"\x55\xaa\x05": "save every minute after threshold",
}

SPECIAL_BYTE_TOKEN = {
    b"\x55\xaa\x01": "double",
    b"\x55\xaa\x02": "ascii",
    b"\x55\xaa\x03": "triple",
    b"\x55\xaa\x04": "quadruple",
    b"\x55\xaa\x05": "tube",
}

TUBE_SELECTED_TOKEN = {
    b"\x00": "both",
    b"\x01": "tube 1",
    b"\x02": "tube 2",
}

TIMESTAMP_MARKER = b"\x55\xaa\x00"  # date token/header marker
TOKEN_LEN = 3
TUBE_TOKEN_LEN = 1
DATE_LEN = 6  # YY MM DD HH mm ss (raw bytes)