from config import CONN
from parser.parser import parse
import struct

def get_hardware_model() -> str:
    CONN.write(b"<GETVER>>")
    response = CONN.read(15)
    return response.decode()

def get_CPM() -> int:
    CONN.write(b"<GETCPM>>")
    response = CONN.read(4)
    return int.from_bytes(response)

def turn_on_heartbeat():
    beats = 0
    CONN.write("<HEARTBEAT1>>")
    while beats < 10:
        yield CONN.read(4)
        beats += 1
    turn_off_hearbeat()

def turn_off_hearbeat() -> None:
    CONN.write(b"<HEARTBEAT0>>")

def get_voltage() -> str:
    CONN.write(b"<GETVOLT>>")
    return CONN.read(5).decode()

def get_history_bytes() -> str:
    addr = 0x000000
    data_length = 4096

    cmd = struct.pack('>BBBH',
                (addr >> 16) & 0xff,
                (addr >> 8) & 0xff,
                addr & 0xff,
                data_length)

    CONN.write(b'<SPIR' + cmd + b'>>')
    raw_dump = CONN.read(data_length)

    #TODO check if next four values are xff before rstrip!
    #z = custom end character
    return parse(raw_dump.rstrip(b"\xff"))