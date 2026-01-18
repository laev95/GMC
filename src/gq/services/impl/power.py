from __future__ import annotations

from typing import TYPE_CHECKING

from src.gq.services.service_base import ServiceBase

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class PowerService(ServiceBase):
    """
    Service for power-related commands of a GQ GMC Geiger counter.
    Encapsulates the commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        super().__init__(manager)

    def power_on(self) -> None:
        """
        RFC1801: <POWERON>> turns the device on (or wakes/activates it depending on the model).
        """
        def op() -> None:
            self._manager.write(b"<POWERON>>")
            return None
        self._call("power_on", op)

    def power_off(self) -> None:
        """
        RFC1801: <POWEROFF>> turns the device off.
        """
        def op() -> None:
            self._manager.write(b"<POWEROFF>>")
            return None
        self._call("power_off", op)

    def reboot(self) -> None:
        """
        RFC1801: <REBOOT>> performs a reboot.
        """
        def op() -> None:
            self._manager.write(b"<REBOOT>>")
            return None
        self._call("reboot", op)

    def factory_reset(self) -> bool:
        """
        RFC1801: <FACTORYRESET>> resets to factory settings.
        Returns: 0xAA (_ACK)
        """
        return self._cmd_ack("factory_reset", b"<FACTORYRESET>>")
