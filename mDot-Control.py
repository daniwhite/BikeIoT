import serial
device = "/dev/ttyUSB0"
baudrate = 115200
ser = serial.Serial(device, baudrate)
ser.write("AT+JOIN\n")
ser.write("AT+SEND=Hello\n")
