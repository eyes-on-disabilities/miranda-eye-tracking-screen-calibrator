import serial

ser = serial.Serial("/dev/ttyUSB0", 115200)
ser.write(b"a")
