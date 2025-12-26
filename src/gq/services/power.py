from src.gq.core_util.core import write, read_ack

def power_on() -> None:
    """
    RFC1801: <POWERON>> schaltet das Gerät ein (bzw. weckt/aktiviert je nach Modell).
    """
    write(b"<POWERON>>")


def power_off() -> None:
    """
    RFC1801: <POWEROFF>> schaltet das Gerät aus.
    """
    write(b"<POWEROFF>>")


def reboot() -> None:
    """
    RFC1801: <REBOOT>> führt einen Neustart aus.
    """
    write(b"<REBOOT>>")

def factory_reset() -> bool:
    """
    RFC1801: <FACTORYRESET>> setzt auf Werkseinstellungen zurück.
    Rückgabe: 0xAA (ACK)
    """
    write(b"<FACTORYRESET>>")
    return read_ack()