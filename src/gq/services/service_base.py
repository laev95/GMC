from __future__ import annotations

import time
from typing import Callable, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from src.gq.manager import SerialManager

from src.gq.errors import (
    NotConnectedError,
    ConnectionLostError,
    ReadTimeoutError,
    DeviceUnavailableError,
    DeviceProtocolError,
    DeviceConfigurationError,
    AckError,
)


T = TypeVar("T")


class ServiceBase:
    """
    Common service behavior:

    - retries transient transport errors

    - attempts reconnect using SerialManager.connect() (default config)
    """

    def __init__(self, manager: SerialManager, *, max_attempts: int = 2, backoff_s: float = 0.15):
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if backoff_s <= 0:
            raise ValueError("backoff_s must be > 0")

        self._manager = manager
        self._max_attempts = max_attempts
        self._backoff_s = backoff_s

    def _cmd_ack(self, operation: str, cmd: bytes) -> bool:
        def op() -> bool:
            self._manager.write(cmd)
            return self._manager.read_ack()

        return self._call(operation, op)

    def _call(self, operation: str, fn: Callable[[], T]) -> T:
        """
        Calls a function with retry logic for transient errors.
        :param operation: Name of the function.
        :param fn: Function to call.
        :return: Result of the function call.
        :raises DeviceUnavailableError: If the device is unreachable after retries.
        :raises DeviceProtocolError: If a communication error occurs.
        """
        for attempt in range(1, self._max_attempts + 1):
            try:
                return fn()
            except (NotConnectedError, ConnectionLostError, ReadTimeoutError) as e:
                self._manager.disconnect()
                ok = self._manager.connect()

                if not ok or attempt >= self._max_attempts:
                    raise DeviceUnavailableError(operation, detail=str(e)) from e

                time.sleep(self._backoff_s)

            except AckError as e:
                raise DeviceProtocolError(operation, detail=str(e)) from e

        raise AssertionError("Unreachable: max_attempts >= 1, loop must return or raise.")

    @staticmethod
    def _validate_range(operation: str, param_name: str, value: int, min_val: int, max_val: int) -> None:
        if not (min_val <= value <= max_val):
            raise DeviceConfigurationError(operation, f"{param_name} must be {min_val}..{max_val}")

    @staticmethod
    def _validate_byte_length(operation: str, param_name: str, data: bytes, expected_length: int) -> None:
        if len(data) != expected_length:
            raise DeviceConfigurationError(operation, f"{param_name} must be exactly {expected_length} bytes")

