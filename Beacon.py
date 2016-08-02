# Program for beacon RPi

import subprocess
import serial
from bluepy import btle
import time
import picamera

LOOP_ON = '01'
LOOP_OFF = '00'

BT_PERIOD = 60  # How often to clear the bluetooth device list and start over
LORA_PERIOD = 5  # How many seconds between each Lora braodcast
SCAN_LEN = 2  # How long to scan bluetooth at one time

# Send bluetooth message
cmdstring = 'sudo hcitool -i hci0 cmd 0x08 0x0008 06 02 01 '
devices = []
sc = btle.Scanner(0)

# Initialize serial (to control mDot)
device = '/dev/ttyUSB0'
baudrate = 115200
ser = serial.Serial(device, baudrate)
# Join gateway
ser.write('AT+JOIN\n')

# Initialie camera
cam = picamera.PiCamera()

btTime = time.time()  # Start time (for bluetooth cycles)
loraTime = time.time()  # Start time (for LoRa cycles)

loop_state = input('Loop state: ')  # Temporary


def getLoopState():
    return loop_state  # Will eventually do something snazzier

while(True):
    imageTitle = 'Images/'
    if getLoopState():
            cmdstring = cmdstring + LOOP_ON
            imageTitle += 'bikes/'
    else:
        cmdstring = cmdstring + LOOP_OFF
    broadcastProc = subprocess.call(cmdstring, shell=True)

    # Take image
    imageTitle += time.ctime()
    imageTitle += '.jpg'
    # Get rid of bad characters, but keep text readable
    imageTitle = imageTitle.replace(' ', '_')
    imageTitle = imageTitle.replace(':', '-')
    cam.capture(imageTitle)

    # Check for new devices
    scanDevices = sc.scan(SCAN_LEN)
    for sDev in scanDevices:
        for dev in devices:
            if dev.addr == sDev.addr:
                break
        else:
            devices.append(sDev)
    # Print device count
    print 'Devices found since ',
    print time.ctime(btTime),
    print ' : %d' % len(devices)
    # Check if we need to refresh the list
    if(time.time() - btTime > BT_PERIOD):
        devices = []
        btTime = time.time()

    # Lora broadcast
    if(time.time() - loraTime > LORA_PERIOD):
        loraTime = time.time()
        msg = 'AT+SEND=' + \
            '{"aliveMsg":"Alive",' + \
            '"devCount":"' + str(len(devices)) + \
            '" }' + '\n'
        ser.write(msg)
    # Loop end code
    time.sleep(2)
