from enum import Enum
from collections.abc import Iterator

class Parser:    
    class State(Enum):
        DATE = 1
        DATA = 2
        ASCI = 3
        SPEC = 4
        FAIL = 5
    state: State = State.DATE

    pointer = 0

    reading_bytes = 2

    start_end_token = "55aa" 

    time_stamp_token = "55aa00"

    save_type_token = {
        "55aa00" : "off", 
        "55aa01" : "save every second", 
        "55aa02" : "save every minute", 
        "55aa03" : "save every hour (average)",
        "55aa04" : "save every second after threshold",
        "55aa05" : "save every minute after threshold"
    }

    special_byte_token = {
        "55aa01" : "double",
        "55aa02" : "ascii",
        "55aa03" : "triple",
        "55aa04" : "quadruple",
        "55aa05" : "tube"
    }

    tube_selected_token = {
        "55aa00" : "both",
        "55aa01" : "tube 1",
        "55aa02" : "tube 2",
    }

    @staticmethod
    def move_pointer(history: str, byte_amount) -> str:
        string: str = ""
        for i in range(byte_amount):
            string += history[Parser.pointer:Parser.pointer+i+1]
        Parser.pointer += byte_amount
        return string

    @staticmethod
    def check_bytes(buffer: str, *expected) -> bool:
        if buffer not in expected:
            print(f"Expected {expected}, got {buffer} instead")
            return False
        return True

    @staticmethod
    def get_date(buffer: str) -> None:
        year = int(buffer[:2], 16)
        month = int(buffer[:4], 16)
        day = int(buffer[:6], 16)
        hour = int(buffer[:8], 16)
        minute = int(buffer[:10], 16)
        second = int(buffer[:12], 16)

        print(f"{day}.{month}.{year} - {hour}:{minute}:{second}")

    @staticmethod
    def get_save_type(buffer: str) -> None:
        print(f"Save data type: {Parser.save_type_token[buffer]}")
    
    @staticmethod
    def get_special_byte_type(buffer: str) -> str:
        return Parser.special_byte_token[buffer]
    
    @staticmethod
    def read_measurement_data(buffer: str) -> int:
        return int(buffer, 16)
    
    @staticmethod
    def get_tube_type(buffer: str) -> None:
        print("Selected tube(s): " + Parser.tube_selected_token[buffer])
