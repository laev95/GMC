from enum import Enum
from collections.abc import Iterator

class Parser:
    class State(Enum):
        DATE = 1
        DATA = 2
        SAVE = 3
        SPEC = 4
        FAIL = 5

    state: State = State.DATE
    current_save_type: str
    start_end_token = "55aa" 

    time_stamp_token = "00"
    save_type_token = {
        "00" : "off", 
        "01" : "save every second", 
        "02" : "save every minute", 
        "03" : "save every hour (average)",
        "04" : "save every second after threshold",
        "05" : "save every minute after threshold"
    }

    special_byte_token = {
        "01" : "double",
        "02" : "ascii",
        "03" : "triple",
        "04" : "quadruple",
        "05" : "tube"
    }

    tube_selected_token = {
        "00" : "both",
        "01" : "tube 1",
        "02" : "tube 2",
    }

    def get_two_bytes(iterable_data: Iterator[str]) -> str:
        return next(iterable_data) + next(iterable_data)

    @staticmethod
    def check_bytes(buffer: str, *expected) -> bool:
        if buffer not in expected:
            print(f"Expected {expected}, got {buffer} instead")
            return False
        return True

    def get_date(iterable_hist: Iterator[str]) -> None:
        year = int(Parser.get_two_bytes(iterable_hist), 16)
        month = int(Parser.get_two_bytes(iterable_hist), 16)
        day = int(Parser.get_two_bytes(iterable_hist), 16)
        hour = int(Parser.get_two_bytes(iterable_hist), 16)
        minute = int(Parser.get_two_bytes(iterable_hist), 16)
        second = int(Parser.get_two_bytes(iterable_hist), 16)

        print(f"{day}.{month}.{year} - {hour}:{minute}:{second}")

    @staticmethod
    def get_save_type(buffer: str) -> None:
        print(f"Save data type: {Parser.save_type_token[buffer]}")
