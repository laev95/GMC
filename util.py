from config import CONN
import struct

def get_hardware_model() -> str|None:
    CONN.write(b"<GETVER>>")
    response = CONN.read(15)
    return response.decode()

def get_CPM() -> int:
    CONN.write(b"<GETCPM>>")
    response = CONN.read(4)
    return int.from_bytes(response)

def turn_on_heartbeat():
    counter = 0
    CONN.write("<HEARTBEAT1>>")
    while counter < 10:
        yield CONN.read(4)
        counter += 1
    turn_off_hearbeat()

def turn_off_hearbeat() -> None:
    CONN.write(b"<HEARTBEAT0>>")

def get_voltage() -> str:
    CONN.write(b"<GETVOLT>>")
    return CONN.read(5).decode()

def get_raw_data() -> str:
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
    return raw_dump.rstrip(b"\xff").hex()+"z"