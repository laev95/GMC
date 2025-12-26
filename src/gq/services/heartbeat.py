from typing import Iterator

from src.gq.core_util.core import write, read_exact


heartbeat_stopped = False


def turn_on_heartbeat() -> Iterator[bytes]:
    """
    RFC1801: <HEARTBEAT1>> startet einen periodischen 4-Byte-Heartbeat-Stream.
    """
    write(b"<HEARTBEAT1>>")
    while not heartbeat_stopped:
        yield read_exact(4)


def turn_off_heartbeat() -> None:
    """
    RFC1801: <HEARTBEAT0>> stoppt den Heartbeat-Stream.
    """
    global heartbeat_stopped

    heartbeat_stopped = True
    write(b"<HEARTBEAT0>>")