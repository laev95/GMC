from config import CONN

def get_hardware_model() -> str|None:
    CONN.write("<GETVER>>")
    response = CONN.read(15)
    return response.decode()

def get_CPM() -> int:
    CONN.write("<GETCPM>>")
    response = CONN.read(4)
    return int.from_bytes(response)

def turn_on_heartbeat():
    counter = 0
    CONN.write("<HEARTBEAT1>>")
    while counter < 10:
        yield CONN.read(4)
        counter += 1
    turn_off_hearbeat()

def turn_off_hearbeat() -> None:
    CONN.write(b"<HEARTBEAT0>>")

def get_voltage() -> str:
    CONN.write(b"<GETVOLT>>")
    return CONN.read(5).decode()
