from src.gq.core_util.core import write, read_ack


def echo_on() -> bool:
    """
    RFC1801: <EchoON>> aktiviert Echo.
    Rückgabe: 0xAA (ACK)
    """
    write(b"<EchoON>>")
    return read_ack()


def echo_off() -> bool:
    """
    RFC1801: <EchoOFF>> deaktiviert Echo.
    Rückgabe: 0xAA (ACK)
    """
    write(b"<EchoOFF>>")
    return read_ack()


def alarm_on() -> bool:
    """
    RFC1801: <ALARM1>> aktiviert Alarm.
    Rückgabe: 0xAA (ACK)
    """
    write(b"<ALARM1>>")
    return read_ack()


def alarm_off() -> bool:
    """
    RFC1801: <ALARM0>> deaktiviert Alarm.
    Rückgabe: 0xAA (ACK)
    """
    write(b"<ALARM0>>")
    return read_ack()


def speaker_on() -> bool:
    """
    RFC1801: <SPEAKER1>> aktiviert Lautsprecher.
    Rückgabe: 0xAA (ACK)
    """
    write(b"<SPEAKER1>>")
    return read_ack()


def speaker_off() -> bool:
    """
    RFC1801: <SPEAKER0>> deaktiviert Lautsprecher.
    Rückgabe: 0xAA (ACK)
    """
    write(b"<SPEAKER0>>")
    return read_ack()