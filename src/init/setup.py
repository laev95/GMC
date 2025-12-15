from serial.tools import list_ports
from src.data import util

def check_ports():
    for port in list_ports.comports():
        if port.product == "USB Serial":
            try:
                model = util.get_hardware_model()
                if "GMC" in model:
                    print(f"Found {model} on {port.device}")
                else:
                    print(f"Found unknown device {model} on {port.device}")
            except Exception as e:
                print(f"Failed to get hardware model: {e}")
                quit()

if __name__ == "__main__":
    check_ports()