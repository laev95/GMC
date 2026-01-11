from __future__ import annotations


class GMCError(Exception):
    """Base class for all project-specific errors."""


class TransportError(GMCError):
    """Serial/transport-layer failures (port, USB disconnects, timeouts)."""


class NotConnectedError(TransportError):
    def __init__(self, operation: str):
        super().__init__(f"Not connected: cannot {operation}.")


class ConnectionLostError(TransportError):
    def __init__(self, operation: str, detail: str | None = None):
        msg = f"Connection lost during {operation}."
        if detail:
            msg = f"{msg} {detail}"
        super().__init__(msg)


class ReadTimeoutError(TransportError):
    def __init__(self, expected: int, received: int):
        super().__init__(f"Read timeout: expected {expected} bytes, received {received}.")
        self.expected = expected
        self.received = received


class ProtocolError(GMCError):
    """Device responded, but content/shape is invalid."""


class AckError(ProtocolError):
    def __init__(self, expected: int, received: int):
        super().__init__(f"Bad ACK: expected 0x{expected:02X}, got 0x{received:02X}.")
        self.expected = expected
        self.received = received


class ServiceError(GMCError):
    """Service-layer error (operation-level failures)."""
    def __init__(self, msg: str, operation: str = ""):
        self.operation = operation
        super().__init__(msg)

class DeviceUnavailableError(ServiceError):
    def __init__(self, operation: str, detail: str | None = None):
        msg = f"Device unavailable while performing {operation}."
        if detail:
            msg = f"{msg} {detail}"
        super().__init__(msg, operation)

class DeviceProtocolError(ServiceError):
    def __init__(self, operation: str, detail: str | None = None):
        msg = f"Device protocol error while performing {operation}."
        if detail:
            msg = f"{msg} {detail}"
        super().__init__(msg, operation)