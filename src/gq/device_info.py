from src.gq.core_util.core import write, read_exact

def get_hardware_model() -> str:
    """
    RFC1801: <GETVER>> liefert die Hardware/Version als ASCII-String (typ. 15 Bytes).
    """
    write(b"<GETVER>>")
    response = read_exact(15)
    return response.decode()


def get_serial_number_bytes() -> bytes:
    """
    RFC1801: <GETSERIAL>> liefert 7 Bytes (Seriennummer im Geräteformat).
    """
    write(b"<GETSERIAL>>")
    return read_exact(7)


def get_voltage() -> str:
    """
    RFC1801: <GETVOLT>> liefert die Versorgungsspannung als ASCII (typ. 5 Bytes).
    """
    write(b"<GETVOLT>>")
    return read_exact(5).decode()