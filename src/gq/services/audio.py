from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class AudioService:
    """
    Service for audio-related settings of a GQ GMC Geiger counter.
    Encapsulates the commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        self._manager = manager

    def echo_on(self) -> bool:
        """
        RFC1801: <EchoON>> activates echo.
        Returns: 0xAA (_ACK)
        """
        self._manager.write(b"<EchoON>>")
        return self._manager.read_ack()

    def echo_off(self) -> bool:
        """
        RFC1801: <EchoOFF>> deactivates echo.
        Returns: 0xAA (_ACK)
        """
        self._manager.write(b"<EchoOFF>>")
        return self._manager.read_ack()

    def alarm_on(self) -> bool:
        """
        RFC1801: <ALARM1>> activates alarm.
        Returns: 0xAA (_ACK)
        """
        self._manager.write(b"<ALARM1>>")
        return self._manager.read_ack()

    def alarm_off(self) -> bool:
        """
        RFC1801: <ALARM0>> deactivates alarm.
        Returns: 0xAA (_ACK)
        """
        self._manager.write(b"<ALARM0>>")
        return self._manager.read_ack()

    def speaker_on(self) -> bool:
        """
        RFC1801: <SPEAKER1>> activates speaker.
        Returns: 0xAA (_ACK)
        """
        self._manager.write(b"<SPEAKER1>>")
        return self._manager.read_ack()

    def speaker_off(self) -> bool:
        """
        RFC1801: <SPEAKER0>> deactivates speaker.
        Returns: 0xAA (_ACK)
        """
        self._manager.write(b"<SPEAKER0>>")
        return self._manager.read_ack()