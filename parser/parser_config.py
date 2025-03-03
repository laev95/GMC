from enum import Enum
class State(Enum):
    DATE = 1
    DATA = 2
    ASCI = 3
    SPEC = 4
    FAIL = 5

class Reading(Enum):
    NORMAL = 1
    DOUBLE = 2
    TRIPLE = 3
    QUADRUPLE = 4

TOKEN_LENGTH = 6
DATE_LENGTH = 12

time_stamp_token = b"\x55\xaa\x00"
save_type_token = {
    b"\x55\xaa\x00" : "off", 
    b"\x55\xaa\x01" : "save every second", 
    b"\x55\xaa\x02" : "save every minute", 
    b"\x55\xaa\x03" : "save every hour (average)",
    b"\x55\xaa\x04" : "save every second after threshold",
    b"\x55\xaa\x05" : "save every minute after threshold"
}
special_byte_token = {
    b"\x55\xaa\x01" : "double",
    b"\x55\xaa\x02" : "ascii",
    b"\x55\xaa\x03" : "triple",
    b"\x55\xaa\x04" : "quadruple",
    b"\x55\xaa\x05" : "tube"
}
tube_selected_token = {
    b"\x55\xaa\x00" : "both",
    b"\x55\xaa\x01" : "tube 1",
    b"\x55\xaa\x02" : "tube 2",
}