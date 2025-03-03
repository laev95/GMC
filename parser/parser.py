import re
from parser_config import State, DATE_LENGTH, TOKEN_LENGTH, time_stamp_token, special_byte_token, Reading
from parser_helper import get_date, get_save_type, get_special_byte_type, get_tube_type, parse_measurement, move_pointer, get_substring

buffer: bytes
remaining_hist: int
reading_bytes: Reading = Reading.NORMAL
pointer = 0
state: State = State.FAIL


def parse(hist: bytes) -> None:
    buffer = get_substring(TOKEN_LENGTH, hist, pointer)
    move_pointer(pointer, TOKEN_LENGTH)
    if buffer == time_stamp_token:
        state == State.DATE

    while pointer < len(hist):
        if state == State.DATE:
            buffer = get_substring(DATE_LENGTH, hist)
            move_pointer(pointer, DATE_LENGTH)
            get_date(buffer)
            buffer = get_substring(TOKEN_LENGTH, hist)
            move_pointer(pointer, TOKEN_LENGTH)
            if buffer in special_byte_token:
                get_save_type(buffer)
                state = State.SPEC

        elif state == State.SPEC:

            type = get_special_byte_type(buffer)
            if type == "ascii":
                state = State.ASCI
            elif type == "double":
                reading_bytes = Reading.DOUBLE
                state = State.DATA
            elif type == "triple":
                reading_bytes = Reading.TRIPLE
                state = State.DATA
            elif type == "quadruple":
                reading_bytes = Reading.QUADRUPLE
                state = State.DATA
            elif type == "tube":
                get_tube_type(buffer)
                state = State.DATE
            buffer = get_substring(TOKEN_LENGTH, hist)
            move_pointer(pointer, TOKEN_LENGTH)

        elif state == State.DATA:
            read_data: list[str] = []
            if reading_bytes.value < Reading.DOUBLE.value:
                while pointer < len(hist):
                    buffer = get_substring(reading_bytes, hist)
                    move_pointer(pointer, reading_bytes)
                    supplement_buffer = get_substring(reading_bytes, hist)
                    move_pointer(pointer, reading_bytes)
                    check_which_token_buffer = get_substring(reading_bytes, hist)
                    move_pointer(pointer, reading_bytes)

                    check_buffer = buffer + supplement_buffer + check_which_token_buffer

                    if re.search("^55aa00$", check_buffer):
                        state = State.DATE
                        buffer = check_buffer
                        break
                    if re.search("^55aa0[1-5]$", check_buffer):
                        state = State.SPEC
                        buffer = check_buffer
                        break
                    if "ff" in check_buffer:
                        #TODO
                        break
                            
                    read_data.append(parse_measurement(buffer))
                    if supplement_buffer:
                        read_data.append(parse_measurement(supplement_buffer))
                    if check_which_token_buffer:
                        read_data.append(parse_measurement(check_which_token_buffer))
            else:
                buffer = get_substring(reading_bytes, hist)
                move_pointer(pointer, reading_bytes)
                read_data.append(parse_measurement(buffer))

                buffer = get_substring(reading_bytes, hist)
                move_pointer(pointer, reading_bytes)
                if re.search("^55aa00$", buffer):
                    state = State.DATE
                elif re.search("^55aa0[1-5]$", buffer):
                    state = State.SPEC
                else:
                    state = State.FAIL

            with open("parsed_output.txt", "w") as file:
                for data in read_data:
                    file.write(data + "\n")
        
        elif state == State.ASCI:
            pass

        else:
            #TODO
            pass

