from enum import Enum
from util import get_history_bytes
import re

class Parser:    
    class State(Enum):
        DATE = 1
        DATA = 2
        ASCI = 3
        SPEC = 4
        FAIL = 5

    state: State = State.FAIL

    buffer: str
    remaining_hist: int

    token_length = 6
    date_length = 12
    pointer = 0
    reading_chars = 2

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

    @classmethod
    def parse_history(cls, hist: str) -> None:
        cls.buffer = cls.get_substring(cls.token_length, hist)
        if cls.buffer == Parser.time_stamp_token:
            cls.state == cls.State.DATE

        while cls.pointer < len(hist):

            if cls.state == cls.State.DATE:

                cls.buffer = cls.get_substring(cls.date_length, hist)
                cls.get_date(cls.buffer)
                cls.buffer = cls.get_substring(cls.token_length, hist)
                if cls.buffer in cls.special_byte_token:
                    cls.get_save_type(cls.buffer)
                    cls.state = cls.State.SPEC

            elif cls.state == cls.State.SPEC:

                type = cls.get_special_byte_type(cls.buffer)
                if type == "ascii":
                    cls.state = cls.State.ASCI
                elif type == "double":
                    cls.reading_chars = 4
                    cls.state = cls.State.DATA
                elif type == "triple":
                    cls.reading_chars = 6
                    cls.state = cls.State.DATA
                elif type == "quadruple":
                    cls.reading_chars = 8
                    cls.state = cls.State.DATA
                elif type == "tube":
                    cls.get_tube_type(cls.buffer)
                    cls.state = cls.State.DATE
                cls.buffer = cls.get_substring(cls.token_length, hist)

            elif cls.state == cls.State.DATA:

                read_data : list[str] = []
                if cls.reading_chars < 4:
                    while cls.pointer < len(hist):
                        cls.buffer = cls.get_substring(cls.reading_chars, hist)
                        supplement_buffer = cls.get_substring(cls.reading_chars, hist)
                        check_which_token_buffer = cls.get_substring(cls.reading_chars, hist)

                        check_buffer = cls.buffer + supplement_buffer + check_which_token_buffer

                        if re.search("^55aa00$", check_buffer):
                            cls.state = cls.State.DATE
                            cls.buffer = check_buffer
                            break
                        if re.search("^55aa0[1-5]$", check_buffer):
                            cls.state = cls.State.SPEC
                            cls.buffer = check_buffer
                            break
                        if "ff" in check_buffer:
                            #TODO
                            break
                                
                        read_data.append(cls.parse_measurement(cls.buffer))
                        if supplement_buffer:
                            read_data.append(cls.parse_measurement(supplement_buffer))
                        if check_which_token_buffer:
                            read_data.append(cls.parse_measurement(check_which_token_buffer))
                else:
                    cls.buffer = cls.get_substring(cls.reading_chars, hist)
                    read_data.append(cls.parse_measurement(cls.buffer))

                    cls.buffer = cls.get_substring(cls.token_length, hist)
                    if re.search("^55aa00$", cls.buffer):
                        cls.state = cls.State.DATE
                    elif re.search("^55aa0[1-5]$", cls.buffer):
                        cls.state = cls.State.SPEC
                    else:
                        cls.state = cls.State.FAIL

                with open("parsed_output.txt", "w") as file:
                    for data in read_data:
                        file.write(data + "\n")
            
            elif cls.state == cls.State.ASCI:
                pass

            else:
                #TODO
                pass

    
    @classmethod
    def get_substring(cls, positions: int, hist: str) -> str:
        string: str = ""

        for i in range(positions):
            string += hist[cls.pointer:cls.pointer+i+1]

        cls.move_pointer(positions)
        return string
    
    @classmethod
    def move_pointer(cls, positions: int) -> None:
        cls.pointer += positions

    @classmethod
    def get_date(cls, buffer: str) -> None:
        year = int(buffer[:2], 16)
        month = int(buffer[:4], 16)
        day = int(buffer[:6], 16)
        hour = int(buffer[:8], 16)
        minute = int(buffer[:10], 16)
        second = int(buffer[:12], 16)

        print(f"{day}.{month}.{year} - {hour}:{minute}:{second}")

    @classmethod
    def get_save_type(cls, buffer: str) -> None:
        print(f"Save data type: {cls.save_type_token[buffer]}")
    
    @classmethod
    def get_special_byte_type(cls, buffer: str) -> str:
        return cls.special_byte_token[buffer]
    
    @classmethod
    def get_tube_type(cls, buffer: str) -> None:
        print("Selected tube(s): " + cls.tube_selected_token[buffer])
    
    @staticmethod
    def parse_measurement(buffer: str) -> str:
        return str(int(buffer, 16))
