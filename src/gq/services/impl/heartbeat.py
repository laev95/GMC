from __future__ import annotations

from typing import Iterator, TYPE_CHECKING

from src.gq.services.service_base import ServiceBase

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class HeartbeatService(ServiceBase):
    """
    Service for heartbeat-related commands of a GQ GMC Geiger counter.
    Encapsulates the commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        super().__init__(manager)
        self._heartbeat_stopped = False

    def turn_on_heartbeat(self) -> Iterator[bytes]:
        """
        RFC1801: <HEARTBEAT1>> starts a periodic 4-byte heartbeat stream.
        """
        def start() -> None:
            self._heartbeat_stopped = False
            self._manager.write(b"<HEARTBEAT1>>")
            return None
        self._call("turn_on_heartbeat", start)

        while not self._heartbeat_stopped:  # TODO rework as async
            def read_op() -> bytes:
                return self._manager.read(4)
            yield self._call("heartbeat_read", read_op)

    def turn_off_heartbeat(self) -> None:
        """
        RFC1801: <HEARTBEAT0>> stops the heartbeat stream.
        """
        def op() -> None:
            self._heartbeat_stopped = True
            self._manager.write(b"<HEARTBEAT0>>")
            return None
        self._call("turn_off_heartbeat", op)
