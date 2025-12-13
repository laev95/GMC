import serial

PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200
CONN = serial.Serial(port=PORT, baudrate=BAUD_RATE, stopbits=1)
FLASH_SIZE = 0x00100000