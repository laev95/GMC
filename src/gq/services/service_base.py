from __future__ import annotations

import time
from typing import Callable, TypeVar

from src.gq.errors import (
    NotConnectedError,
    ConnectionLostError,
    ReadTimeoutError,
    DeviceUnavailableError,
    DeviceProtocolError,
    AckError,
)

T = TypeVar("T")


class ServiceBase:
    """
    Common service behavior:
    - retries transient transport errors
    - attempts reconnect using SerialManager.connect() (default config)
    """

    def __init__(self, manager, *, max_attempts: int = 2, backoff_s: float = 0.15):
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")

        self._manager = manager
        self._max_attempts = max_attempts
        self._backoff_s = backoff_s

    def _cmd_ack(self, operation: str, cmd: bytes) -> bool:
        def op() -> bool:
            self._manager.write(cmd)
            return self._manager.read_ack()

        return self._call(operation, op)

    def _call(self, operation: str, fn: Callable[[], T]) -> T:
        for attempt in range(1, self._max_attempts + 1):
            try:
                return fn()
            except (NotConnectedError, ConnectionLostError, ReadTimeoutError) as e:
                self._manager.disconnect()
                ok = self._manager.connect()

                if not ok or attempt == self._max_attempts:
                    raise DeviceUnavailableError(operation, detail=str(e)) from e

                time.sleep(self._backoff_s)

            except AckError as e:
                raise DeviceProtocolError(operation, detail=str(e)) from e

        raise AssertionError("Unreachable: max_attempts >= 1, loop must return or raise.")