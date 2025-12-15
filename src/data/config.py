import serial

PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200
try:
    CONN = serial.Serial(port=PORT, baudrate=BAUD_RATE, stopbits=1)
except serial.SerialException:
    CONN = serial.Serial()
    print("Failed to connect to device!")

FLASH_SIZE = 0x00100000