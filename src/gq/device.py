from __future__ import annotations

from .manager import SerialManager, ConnConfig
from .services.audio import AudioService
from .services.config import ConfigService
from .services.device_info import DeviceInfoService
from .services.heartbeat import HeartbeatService
from .services.history.history import HistoryService
from .services.input_keys import InputKeysService
from .services.power import PowerService
from .services.radiation import RadiationService
from .services.rtc import RTCService
from .services.sensors import SensorsService
from .services.wifi import WiFiService


class GMCDevice:
    def __init__(self):
        self._manager = SerialManager()
        self.connection_status = self.auto_connect()

        self.audio = AudioService(self._manager)
        self.config = ConfigService(self._manager)
        self.device_info = DeviceInfoService(self._manager)
        self.heartbeat = HeartbeatService(self._manager)
        self.history = HistoryService(self._manager)
        self.input_keys = InputKeysService(self._manager)
        self.power = PowerService(self._manager)
        self.radiation = RadiationService(self._manager)
        self.rtc = RTCService(self._manager)
        self.sensors = SensorsService(self._manager)
        self.wifi = WiFiService(self._manager)

    def connect(self, port: str) -> bool:
        return self._manager.connect(ConnConfig(port=port))

    def auto_connect(self) -> bool:
        return self._manager.connect()

    def disconnect(self) -> None:
        self._manager.disconnect()