import serial

PORT = "COM3"
BAUDRATE = 115200
CONN = serial.Serial(port=PORT, baudrate=BAUDRATE, stopbits=1)
FLASH_SIZE = 0x00100000