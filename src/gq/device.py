from .manager import SerialManager
from .services.radiation import RadiationService
from .services.history.history import HistoryService

class GMCDevice:
    def __init__(self):
        self._manager = SerialManager()
        self.radiation = RadiationService(self._manager)
        self.history = HistoryService(self._manager)

    def auto_connect(self) -> bool:
        return self._manager.connect()

    def disconnect(self) -> None:
        self._manager.disconnect()