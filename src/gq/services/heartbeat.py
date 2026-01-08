from __future__ import annotations
from typing import Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class HeartbeatService:
    """
    Service for heartbeat-related commands of a GQ GMC Geiger counter.
    Encapsulates the commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        self._manager = manager
        self._heartbeat_stopped = False

    def turn_on_heartbeat(self) -> Iterator[bytes]:
        """
        RFC1801: <HEARTBEAT1>> starts a periodic 4-byte heartbeat stream.
        """
        self._heartbeat_stopped = False
        self._manager.write(b"<HEARTBEAT1>>")
        while not self._heartbeat_stopped:
            yield self._manager.read(4)

    def turn_off_heartbeat(self) -> None:
        """
        RFC1801: <HEARTBEAT0>> stops the heartbeat stream.
        """
        self._heartbeat_stopped = True
        self._manager.write(b"<HEARTBEAT0>>")