from .manager import SerialManager
from .services.radiation import RadiationService
from .services.history.history import HistoryService

class GMCDevice:
    def __init__(self):
        self.manager = SerialManager()
        self.radiation = RadiationService(self.manager)
        self.history = HistoryService(self.manager)

    def auto_connect(self) -> bool:
        return self.manager.connect()