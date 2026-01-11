from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gq.manager import SerialManager


class InputKeysService:
    """
    Service for sending key presses to a GQ GMC Geiger counter.
    Encapsulates the commands according to RFC1801.
    """

    def __init__(self, manager: SerialManager):
        """
        Initializes the service with a SerialManager.

        :param manager: The central communication instance.
        """
        self._manager = manager

    def send_key(self, key: int) -> None:
        """
        RFC1801: Sends a key press.
        Allowed forms:
          - <KEY[D0]>>
          - or explicitly: <KEY0>> .. <KEY3>>
        """
        if not (0 <= key <= 3):
            raise ValueError("key must be 0..3")
        self._manager.write(f"<KEY{key}>>".encode("ascii"))