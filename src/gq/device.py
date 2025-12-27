from .manager import SerialManager, ConnConfig
from .services.device_info import DeviceInfoService
from .services.history.history import HistoryService
from .services.radiation import RadiationService


class GMCDevice:
    def __init__(self):
        self._manager = SerialManager()
        self.radiation = RadiationService(self._manager)
        self.history = HistoryService(self._manager)
        self.device_info = DeviceInfoService(self._manager)

    def connect(self, port: str) -> bool:
        return self._manager.connect(ConnConfig(port=port))

    def auto_connect(self) -> bool:
        return self._manager.connect()

    def disconnect(self) -> None:
        self._manager.disconnect()