from parser_config import save_type_token, special_byte_token, tube_selected_token


def get_substring(len_bytes: int, hist: bytes, pointer: int) -> str:
    string: str = ""

    for i in range(len_bytes):
        string += hist[pointer:pointer+i+1]

    return string

def move_pointer(len_bytes: int) -> None:
    pointer += len_bytes

def get_date(buffer: bytes) -> None:
    year = int(buffer[:2], 16)
    month = int(buffer[:4], 16)
    day = int(buffer[:6], 16)
    hour = int(buffer[:8], 16)
    minute = int(buffer[:10], 16)
    second = int(buffer[:12], 16)

    print(f"{day}.{month}.{year} - {hour}:{minute}:{second}")

def get_save_type(buffer: bytes) -> None:
    print(f"Save data type: {save_type_token[buffer]}")

def get_special_byte_type(buffer: bytes) -> str:
    return special_byte_token[buffer]

def get_tube_type(buffer: bytes) -> None:
    print("Selected tube(s): " + tube_selected_token[buffer])

def parse_measurement(buffer: bytes) -> str:
    return str(int(buffer))