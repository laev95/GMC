from .config import CONN
from .parse.parser import parse_gmc_history
import struct

def get_hardware_model() -> str:
    CONN.write(b"<GETVER>>")
    response = CONN.read(15)
    return response.decode()

def get_cpm() -> int:
    CONN.write(b"<GETCPM>>")
    response = CONN.read(4)
    return int.from_bytes(response)

def turn_on_heartbeat():
    beats = 0
    CONN.write("<HEARTBEAT1>>")
    while beats < 10:
        yield CONN.read(4)
        beats += 1
    turn_off_heartbeat()

def turn_off_heartbeat() -> None:
    CONN.write(b"<HEARTBEAT0>>")

def get_voltage() -> str:
    CONN.write(b"<GETVOLT>>")
    return CONN.read(5).decode()

def get_history_bytes() -> bytes:
    # TODO add logic for progressing address for next buffer.
    addr = 0x000000
    data_length = 4096

    cmd = struct.pack('>BBBH',
                (addr >> 16) & 0xff,
                (addr >> 8) & 0xff,
                addr & 0xff,
                data_length)

    CONN.write(b'<SPIR' + cmd + b'>>')
    return CONN.read(data_length)

def get_history():
    raw_hist = get_history_bytes()
    records = parse_gmc_history(raw_hist)

    preview = 20
    for r in records:
        print(f"{r.ts.isoformat(sep=" ", timespec="seconds")};", f"save_type={r.save_type};", f"tube={r.tube}")
        for segment in r.segments:
            print("  ", segment.mode, segment.values[:preview], f"... ({len(segment.values)} total)")