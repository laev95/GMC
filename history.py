from config import CONN, FLASH_SIZE
from parser import Parser
from util import get_raw_data

def parse_history(raw_hist: str) -> None:
    buffer: str

    start_index = raw_hist.find(Parser.start_end_token) 
    if start_index == -1:
        print("Error no start sequence found!")
        return

    hist = raw_hist[start_index:]
    read_data : list[int] = []
    buffer = Parser.move_pointer(hist, 6)

    #TODO actually check before hand
    while Parser.pointer < len(hist):
        if buffer[:5] == Parser.start_end_token:
            if buffer == Parser.time_stamp_token and Parser.state == Parser.State.DATE:
                Parser.state = Parser.State.DATE
                buffer = Parser.move_pointer(hist[Parser.pointer:], 12)
                Parser.get_date(buffer)
                buffer = Parser.move_pointer(hist[Parser.pointer:], 6)
                Parser.get_save_type(buffer)
                Parser.state = Parser.State.SPEC
            elif buffer in Parser.special_byte_token and Parser.state == Parser.State.SPEC:
                type = Parser.get_special_byte_type(buffer)
                if type == "ascii":
                    Parser.state = Parser.State.ASCI
                elif type == "double":
                    Parser.reading_bytes = 4
                    Parser.state = Parser.State.DATA
                elif type == "triple":
                    Parser.reading_bytes = 6
                    Parser.state = Parser.State.DATA
                elif type == "quadruple":
                    Parser.reading_bytes = 8
                    Parser.state = Parser.State.DATA
                elif type == "tube":
                    buffer = Parser.move_pointer(hist, 6)
                    Parser.get_tube_type(buffer)
                    Parser.state = Parser.State.DATE
            else:
                # TODO check if valid data -> check previous state
                pass

        elif Parser.state == Parser.State.DATA:
            buffer = Parser.move_pointer(hist[Parser.pointer:], Parser.reading_bytes)

            if Parser.reading_bytes >= 4:
                while Parser.start_end_token not in buffer:
                    read_data.append(Parser.read_measurement_data(buffer))
                    buffer = Parser.move_pointer(hist, Parser.reading_bytes)
            else: 
                look_ahead = Parser.move_pointer(hist, 2)
                while Parser.start_end_token not in buffer+look_ahead:
                    read_data.append(Parser.read_measurement_data(buffer))
                    read_data.append(Parser.read_measurement_data(look_ahead))
                    buffer = Parser.move_pointer(hist, Parser.reading_bytes)
                    look_ahead = Parser.move_pointer(hist, 2)

parse_history(get_raw_data())