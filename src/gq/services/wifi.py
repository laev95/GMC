from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class WiFiService:
    """
    Service for WiFi-related commands of a GQ GMC Geiger counter.
    Encapsulates the commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        self._manager = manager

    def set_wifi_ssid(self, ssid: str) -> bool:
        """
        RFC1801: <SETSSID...>> sets SSID (ASCII string).
        Returns: 0xAA (ACK)
        """
        self._manager.write(b"<SETSSID" + ssid.encode("ascii", errors="strict") + b">>")
        return self._manager.read_ack()

    def set_wifi_password(self, password: str) -> bool:
        """
        RFC1801: <SETWIFIPW...>> sets WiFi password (ASCII string).
        Returns: 0xAA (ACK)
        """
        self._manager.write(b"<SETWIFIPW" + password.encode("ascii", errors="strict") + b">>")
        return self._manager.read_ack()

    def set_website(self, website: str) -> bool:
        """
        RFC1801: <SETWEBSITE...>> sets website parameter (ASCII string).
        Returns: 0xAA (ACK)
        """
        self._manager.write(b"<SETWEBSITE" + website.encode("ascii", errors="strict") + b">>")
        return self._manager.read_ack()

    def set_url(self, url: str) -> bool:
        """
        RFC1801: <SETURL...>> sets URL (ASCII string).
        Returns: 0xAA (ACK)
        """
        self._manager.write(b"<SETURL" + url.encode("ascii", errors="strict") + b">>")
        return self._manager.read_ack()

    def set_user_id(self, user_id: str) -> bool:
        """
        RFC1801: <SETUSERID...>> sets UserID (ASCII string).
        Returns: 0xAA (ACK)
        """
        self._manager.write(b"<SETUSERID" + user_id.encode("ascii", errors="strict") + b">>")
        return self._manager.read_ack()

    def set_counter_id(self, counter_id: str) -> bool:
        """
        RFC1801: <SETCOUNTERID...>> sets CounterID (ASCII string).
        Returns: 0xAA (ACK)
        """
        self._manager.write(b"<SETCOUNTERID" + counter_id.encode("ascii", errors="strict") + b">>")
        return self._manager.read_ack()

    def set_period_hex(self, period: int) -> bool:
        """
        RFC1801: <SETPERIOD[Param in hex]>> sets the transmission interval/period parameter.
        Returns: 0xAA (ACK)

        Implementation note:
        The RFC describes "Param in hex". In practice, it is usually a 1-byte raw value (0..255),
        analogous to other [D0] parameters.
        """
        if not (0 <= period <= 0xFF):
            raise ValueError("period must be 0..255")
        self._manager.write(b"<SETPERIOD" + bytes([period]) + b">>")
        return self._manager.read_ack()

    def wifi_on(self) -> bool:
        """
        RFC1801: <WiFiON>> activates WiFi.
        Returns: 0xAA (ACK)
        """
        self._manager.write(b"<WiFiON>>")
        return self._manager.read_ack()

    def wifi_off(self) -> bool:
        """
        RFC1801: <WiFiOFF>> deactivates WiFi.
        Returns: 0xAA (ACK)
        """
        self._manager.write(b"<WiFiOFF>>")
        return self._manager.read_ack()

    def at_command(self, command: str = "") -> bytes:
        """
        RFC1801: <AT>> or <AT+...>> passes AT commands through to the WiFi module.

        Returns:
          - typically ASCII ("OK", or more detailed)
          - length not fixed in RFC → implemented here as raw read with a fixed upper limit.
        """
        if command:
            self._manager.write(b"<AT" + command.encode("ascii", errors="strict") + b">>")
        else:
            self._manager.write(b"<AT>>")
        return self._manager.read_exact(256)

    def wifi_level(self) -> bytes:
        """
        RFC1801: <WiFiLevel>> returns signal/status from the WiFi module.
        Length not fixed in RFC → raw read.
        """
        self._manager.write(b"<WiFiLevel>>")
        return self._manager.read_exact(256)