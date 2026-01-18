from __future__ import annotations

from typing import TYPE_CHECKING

from src.gq.services.service_base import ServiceBase

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class AudioService(ServiceBase):
    """
    Service for audio-related settings of a GQ GMC Geiger counter.
    Encapsulates the commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        super().__init__(manager)

    def echo_on(self) -> bool:
        """
        RFC1801: <EchoON>> activates echo.
        Returns: 0xAA (_ACK)
        """
        return self._cmd_ack("echo_on", b"<EchoON>>")

    def echo_off(self) -> bool:
        """
        RFC1801: <EchoOFF>> deactivates echo.
        Returns: 0xAA (_ACK)
        """
        return self._cmd_ack("echo_off", b"<EchoOFF>>")

    def alarm_on(self) -> bool:
        """
        RFC1801: <ALARM1>> activates alarm.
        Returns: 0xAA (_ACK)
        """
        return self._cmd_ack("alarm_on", b"<ALARM1>>")

    def alarm_off(self) -> bool:
        """
        RFC1801: <ALARM0>> deactivates alarm.
        Returns: 0xAA (_ACK)
        """
        return self._cmd_ack("alarm_off", b"<ALARM0>>")

    def speaker_on(self) -> bool:
        """
        RFC1801: <SPEAKER1>> activates speaker.
        Returns: 0xAA (_ACK)
        """
        return self._cmd_ack("speaker_on", b"<SPEAKER1>>")

    def speaker_off(self) -> bool:
        """
        RFC1801: <SPEAKER0>> deactivates speaker.
        Returns: 0xAA (_ACK)
        """
        return self._cmd_ack("speaker_off", b"<SPEAKER0>>")
