import struct
from enum import Enum
from serial import Serial
from collections.abc import Iterable
from config import CONN, FLASH_SIZE

class Parser:
    class State(Enum):
        DATE = 1
        DATA = 2

    def __init__(self) -> None:
        
        self.parser_state = None
        self.start_end_token = "55aa" 
        self.time_stamp_token = "00"
        self.time_stamp_save_type_token = {
            "00" : "off", 
            "01" : "save every second", 
            "02" : "save every minute", 
            "03" : "save every hour (average)",
            "04" : "save every second after threshold",
            "05" : "save every minute after threshold"
        }
        self.current_save_type = None
        self.byte_type_token = {
            "01" : "double",
            "02" : "ascii",
            "03" : "triple",
            "04" : "quadruple"
        }
        self.tube_selection_token = "05"

    @staticmethod
    def get_two_bytes(iterable_data: Iterable[str]) -> str:
        return next(iterable_data) + next(iterable_data)

    def parse_history_data(self, raw_hist: str) -> None:
        formatted_text: list[str]
        buffer: str
        start_index = raw_hist.find(self.start_end_token) 

        if start_index == -1:
            print("Error no start sequence found!")
            return

        hist = raw_hist[start_index + 4:]
        print(hist)
        iterable_hist = iter(hist)

        for byte in iterable_hist:
            if byte == "z":
                print("End of data!")
                break
            
            buffer = byte + next(iterable_hist)
            if buffer == self.time_stamp_token:
                self.parser_state = self.State.DATE
            elif buffer in self.byte_type_token:
                self.parser_state = self.State.DATA
            else:
                print(f"Expected byte value between 00-05 got {buffer} instead!")
                break

            if self.parser_state == self.State.DATE:
                year = int(self.get_two_bytes(iterable_hist), 16)
                month = int(self.get_two_bytes(iterable_hist), 16)
                day = int(self.get_two_bytes(iterable_hist), 16)
                hour = int(self.get_two_bytes(iterable_hist), 16)
                minute = int(self.get_two_bytes(iterable_hist), 16)
                second = int(self.get_two_bytes(iterable_hist), 16)

                print(f"{day}.{month}.{year} - {hour}:{minute}:{second}")

                buffer = self.get_two_bytes(iterable_hist) + self.get_two_bytes(iterable_hist)
                if buffer != self.start_end_token:
                    print(f"Expected end of sequence marker, got {buffer} instead")
                    break

                buffer = self.get_two_bytes(iterable_hist)

                if buffer not in self.time_stamp_save_token:
                    print(f"Expected indicator of save data type, got {buffer} instead")
                    break
                
                print(f"Save data type: {self.time_stamp_save_token[buffer]}")

                buffer = self.get_two_bytes(iterable_hist) + self.get_two_bytes(iterable_hist)
                if buffer != self.start_end_token:
                    self.parser_state == self.State.DATA

            if self.parser_state == self.State.DATA:
                pass


def get_raw_data(conn: Serial) -> str:
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

    return raw_dump.rstrip(b"\xff").hex()+"z"

hist = get_raw_data(CONN)
parser = Parser()
parser.parse_history_data(hist)