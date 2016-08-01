# Program for beacon RPi

import subprocess
import serial
from bluepy import btle
import time

LOOP_ON = '01'
LOOP_OFF = '00'

PERIOD = 60  # How often to clear the list and start over
SCAN_LEN = 2  # How long to scan at one time

# Send bluetooth message
cmdstring = 'sudo hcitool -i hci0 cmd 0x08 0x0008 06 02 01 '
devices = []
sc = btle.Scanner(0)

# Initialize serial (to control mDot)
device = '/dev/ttyUSB0'
baudrate = 115200
ser = serial.Serial(device, baudrate)
ser.write('AT+JOIN\n')

aliveCntr = 0  # Counter to broadcast alive signal only every 30 seconds
startTime = time.time()


loop_state = input("Loop state: ")  # Temporary


def getLoopState():
    return loop_state  # Will eventually do something snazzier

while(True):
    if getLoopState():
            cmdstring = cmdstring + LOOP_ON
    else:
        cmdstring = cmdstring + LOOP_OFF
    broadcastProc = subprocess.call(cmdstring, shell=True)

    # Send "I'm alive" signal over LoRa
    if aliveCntr % 15 == 0:  # Broadcast only every 30 (15*2) seconds
        ser.write("AT+SEND=I'm alive\n")

    # Check for new devices
    scanDevices = sc.scan(SCAN_LEN)
    for sDev in scanDevices:
        for dev in devices:
            if dev.addr == sDev.addr:
                break
        else:
            devices.append(sDev)
    print "Devices found since ",
    print time.ctime(startTime),
    print " : %d" % len(devices)
    if(time.time() - startTime > PERIOD):
        devices = []
        startTime = time.time()

    time.sleep(2)
    aliveCntr += 1
