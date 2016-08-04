# Program for beacon RPi

import subprocess
import serial
from bluepy import btle
import time
import picamera
import grovepi

LOOP_ON = '01'
LOOP_OFF = '00'

BT_PERIOD = 60  # How often to clear the bluetooth device list and start over
LORA_PERIOD = 5  # How many seconds between each Lora braodcast
SCAN_LEN = 2  # How long to scan bluetooth at one time

# Set up grovepi
LOUDNESS_SENSOR = 0  # Connect to A0
TEMP_HUM_SENSOR = 6  # Connect to D6

# Send bluetooth message
devices = []
sc = btle.Scanner(0)

# Initialize serial (to control mDot)
device = '/dev/ttyUSB0'
baudrate = 115200
ser = serial.Serial(device, baudrate)

# Initialize camera
cam = picamera.PiCamera()

btTime = time.time()  # Start time (for bluetooth cycles)
loraTime = time.time()  # Start time (for LoRa cycles)

loop_state = input('Loop state: ')  # Temporary


def bt_sendLoopState(loopState):
    cmdstring = 'sudo hcitool -i hci0 cmd 0x08 0x0008 06 02 01 '
    if loopState:
            cmdstring = cmdstring + LOOP_ON
    else:
        cmdstring = cmdstring + LOOP_OFF
    subprocess.call(cmdstring, shell=True)


def getLoopState():
    return loop_state  # Will eventually do something snazzier


# Sends an AT command, then returns its response
def lora_command(str, responses=['OK\r\n']):
    ser.write(str)
    ser.readline()
    msg = ''
    while (msg not in responses):
        try:
            msg = ser.readline()
        except OSError, serial.SerialException:
            print 'Unable to read. Is something else using the serial port?'
    return msg


# Send AT command to join LoRa network
def lora_joinNetwork():
    str = ''
    while(not (str == 'Successfully joined network\r\n')):
        str = lora_command('AT+JOIN\n', [
            'Join Error - Failed to join network\r\n',
            'Successfully joined network\r\n'])


def takeImg(folderPath='Images/'):
    imageTitle = folderPath + time.ctime() + '.jpg'
    imageTitle = imageTitle.replace(' ', '_')
    imageTitle = imageTitle.replace(':', '-')
    cam.capture(imageTitle)

while(True):
    # Check LoRa network status
    if(lora_command('AT+NJS\n', ['0\r\n', '1\r\n']) == '0\r\n'):
        lora_joinNetwork()

    # Bluetooth broadcast
    bt_sendLoopState(getLoopState())

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

    # Get sensor data
    loudness = grovepi.analogRead(LOUDNESS_SENSOR)
    [temp, hum] = grovepi.dht(TEMP_HUM_SENSOR, module_type=0)
    print 'loudness: ' + str(loudness)
    print 'temperature: ' + str(temp)
    print 'humidity: ' + str(hum)

    # Lora broadcast
    if(time.time() - loraTime > LORA_PERIOD):
        loraTime = time.time()
        msg = 'AT+SEND=' + \
            str(len(devices)) + ',' + \
            str(loudness) + ',' + \
            str(temp) + ',' + \
            str(hum) + '\n'
        lora_command(msg)

    # Loop end code
    time.sleep(2)
