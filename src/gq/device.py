from __future__ import annotations

from .manager import SerialManager, ConnConfig
from src.gq.services.impl.audio import AudioService
from src.gq.services.impl.config import ConfigService
from src.gq.services.impl.device_info import DeviceInfoService
from src.gq.services.impl.heartbeat import HeartbeatService
from src.gq.services.impl.history.history import HistoryService
from src.gq.services.impl.input_keys import InputKeysService
from src.gq.services.impl.power import PowerService
from src.gq.services.impl.radiation import RadiationService
from src.gq.services.impl.rtc import RTCService
from src.gq.services.impl.sensors import SensorsService
from src.gq.services.impl.wifi import WiFiService

AUTO_CONNECT = ""

class GMCDevice:
    def __init__(self):
        self._manager = SerialManager()
        self.connection_status = False

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

    def connect(self, port: str = AUTO_CONNECT) -> None:
        self.connection_status = self._manager.connect(port)

    def disconnect(self) -> None:
        self._manager.disconnect()