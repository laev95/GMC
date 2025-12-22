from dataclasses import dataclass
from src.gq.core_util.core import write, read_exact, ACK

@dataclass(frozen=True)
class GyroData:
    """
    RFC1801: Gyro liefert rohe X/Y/Z-Werte (je 2 Byte, unsigned) + ACK.
    """
    x: int
    y: int
    z: int


def get_gyro() -> GyroData:
    """
    RFC1801: <GETGYRO>> → 7 Bytes:
      X_MSB X_LSB Y_MSB Y_LSB Z_MSB Z_LSB 0xAA
    """
    write(b"<GETGYRO>>")
    data = read_exact(7)
    if len(data) != 7:
        raise IOError(f"Expected 7 bytes, got {len(data)}")
    x = int.from_bytes(data[0:2], "big", signed=False)
    y = int.from_bytes(data[2:4], "big", signed=False)
    z = int.from_bytes(data[4:6], "big", signed=False)
    if data[6] != ACK:
        raise IOError(f"Expected ack 0xAA as last byte, got 0x{data[6]:02X}")
    return GyroData(x=x, y=y, z=z)


def get_temperature_raw() -> bytes:
    """
    RFC1801: <GETTEMP>> ist laut Dokumentation bei mehreren Modellen nicht unterstützt.
    Daher als Raw-Read belassen (Länge nicht normiert).
    """
    write(b"<GETTEMP>>")
    return read_exact(32)