from config import CONN, FLASH_SIZE
from parser import Parser
from util import get_raw_data


def parse_history_data(raw_hist: str) -> None:
    buffer: str
    start_index = raw_hist.find(Parser.start_end_token) 

    if start_index == -1:
        print("Error no start sequence found!")
        return

    hist = raw_hist[start_index + 4:]
    with open("output_hourly", "w") as file:
        file.write(hist)

    iterable_hist = iter(hist)

    for byte in iterable_hist:
        if byte == "z":
            print("End of data!")
            break

        buffer = byte + next(iterable_hist)
        if Parser.check_bytes(buffer, Parser.time_stamp_token, Parser.special_byte_token):
            if buffer == Parser.time_stamp_token:
                Parser.state = Parser.State.DATE
            elif buffer in Parser.special_byte_token:
                Parser.state = Parser.State.SPEC
        else:
            Parser.state = Parser.State.FAIL

        if Parser.state == Parser.State.FAIL:
            break

        if Parser.state == Parser.State.DATE:
            Parser.get_date(iterable_hist)
            buffer = Parser.get_two_bytes(iterable_hist) + Parser.get_two_bytes(iterable_hist)
            if Parser.check_bytes(buffer, Parser.start_end_token):
                Parser.state = Parser.State.SAVE
            else:
                Parser.state = Parser.State.FAIL

        if Parser.state == Parser.State.SAVE:
            buffer = Parser.get_two_bytes(iterable_hist)
            if Parser.check_bytes(buffer, *(Parser.save_type_token.keys())):
                Parser.get_save_type(buffer)
                Parser.current_save_type = buffer
            else:
                Parser.state = Parser.State.FAIL

            buffer = Parser.get_two_bytes(iterable_hist) + Parser.get_two_bytes(iterable_hist)
            if Parser.check_bytes(buffer, Parser.start_end_token):
                Parser.state = Parser.State.DATA
            else:
                Parser.state = Parser.State.FAIL

        if Parser.state == Parser.State.DATA:
            if Parser.current_save_type == "03":
                buffer += Parser.get_two_bytes(iterable_hist) 
                print(f"Average cpm: {int(buffer[:2], 16)}")

                if buffer[2:] != Parser.start_end_token:
                    print(f"Error. Expected end of sequence marker, got {buffer} instead.")
                    break

        if Parser.state == Parser.State.SPEC:
            if buffer == "05":
                print(f"Tube mdode: {Parser.tube_selected_token[Parser.get_two_bytes(iterable_hist)]}")

parse_history_data(get_raw_data())