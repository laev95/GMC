from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class PowerService:
    """
    Service for power-related commands of a GQ GMC Geiger counter.
    Encapsulates the commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        self._manager = manager

    def power_on(self) -> None:
        """
        RFC1801: <POWERON>> turns the device on (or wakes/activates it depending on the model).
        """
        self._manager.write(b"<POWERON>>")

    def power_off(self) -> None:
        """
        RFC1801: <POWEROFF>> turns the device off.
        """
        self._manager.write(b"<POWEROFF>>")

    def reboot(self) -> None:
        """
        RFC1801: <REBOOT>> performs a reboot.
        """
        self._manager.write(b"<REBOOT>>")

    def factory_reset(self) -> bool:
        """
        RFC1801: <FACTORYRESET>> resets to factory settings.
        Returns: 0xAA (ACK)
        """
        self._manager.write(b"<FACTORYRESET>>")
        return self._manager.read_ack()