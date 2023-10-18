import serial


with serial.Serial('/dev/ttyACM0', baudrate=115200, ) as ser:
