import struct
from enum import Enum
from serial import Serial

class Parser:
    class State(Enum):
        BEGIN = 1
        DATE = 2
        DATA = 3
        NEXT = 4

    parser_state = State.BEGIN

    start_end_token = "55aa" 
    time_stamp_token = "00"
    time_stamp_save_token = {
        "00" : "off", 
        "01" : "save every second", 
        "02" : "save every minute", 
        "03" : "save every hour (average)",
        "04" : "save every second after threshold",
        "05" : "save every minute after threshold"
    }
    byte_type_token = {
        "01" : "double",
        "02" : "ascii",
        "03" : "triple",
        "04" : "quadruple"
    }
    
def get_history_data(conn: Serial):
    addr = 0x000000
    data_length = 4096

    cmd = struct.pack('>BBBH',
                (addr >> 16) & 0xff,
                (addr >> 8) & 0xff,
                addr & 0xff,
                data_length)

    conn.write(b'<SPIR' + cmd + b'>>')

    raw_dump = conn.read(data_length)

    #TODO check if next four values are xff before rstrip!

    raw_hist = raw_dump.rstrip(b"\xff")
    string_hist = raw_hist.hex(" ")
    

def parse_history_data(hist: str):
    curret_index = 0
    buffer: str
    formatted_text: list[str]

    while curret_index < len(hist):
        if Parser.State == Parser.State.BEGIN:
            curret_index = hist.find(Parser.start_end_token) 
            buffer = hist[curret_index : curret_index+2]

            if buffer == Parser.time_stamp_token:
                Parser.State = Parser.State.DATE
            elif buffer in Parser.byte_type_token:
                Parser.State = Parser.State.DATA
            else:
                print("Error")
                break

        if Parser.State == Parser.State.DATE:
            pass
    
    Parser.State == Parser.State.BEGIN
