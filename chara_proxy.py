import serial
from serial import Serial


class CharaProxy:
    def __init__(self, dev_name: str, ser: Serial = None) -> None:
        if ser is None:
            self.ser = Serial(dev_name)
            self.owned = True
        else:
            self.ser = ser
            self.owned = False

    def __del__(self):
        if self.owned:
            self.ser.close()
