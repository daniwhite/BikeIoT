# Program for beacon RPi

import subprocess
import serial
from bluepy import btle
import time
import picamera
import grovepi
from multiprocessing import Process

LOOP_ON = '01'
LOOP_OFF = '00'

BT_PERIOD = 60  # How often to clear the bluetooth device list and start over
LORA_PERIOD = 5  # How many seconds between each Lora braodcast
SCAN_LEN = 2  # How long to scan bluetooth at one time

# Set up grovepi
LOUDNESS_SENSOR = 0  # Connect to A0
TEMP_HUM_SENSOR = 6  # Connect to D6
SWITCH = 5

# Setup bluetooth
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


# Defines bluetooth function that will be run as separate process
def bt_process():
    while(True):
        loopState = getLoopState()
        bt_sendLoopState(loopState)
broadcastProc = Process(target=bt_process)


def bt_sendLoopState(loopState):
    cmdstring = 'sudo hcitool -i hci0 cmd '  # Send cmd to hci0
    cmdstring += '0x08 '  # Set group to BLE
    cmdstring += '0x0008 '  # Set command to HCI_LE_Set_Advertising_Data
    cmdstring += '0D '  # Length of entire following data, in bytes
    cmdstring += '02 '  # Length of flag info
    cmdstring += '01 '  # Use AD flags
    cmdstring += '02 '  # Flag value:
    # bit 0 (OFF) LE Limited Discoverable Mode
    # bit 1 (ON) LE General Discoverable Mode
    # bit 2 (OFF) BR/EDR Not Supported
    # bit 3 (ON) Simultaneous LE and BR/EDR to Same Device Capable (controller)
    # bit 4 (ON) Simultaneous LE and BR/EDR to Same Device Capable (Host)
    cmdstring += '09 '  # Length of following message, in bytes
    cmdstring += '07 '  # GAP value (07 = 128 Bit Complete Service UUID List)
    cmdstring += '42 69 63 79 63 6c 65 '  # Header to identify beacon message-
    # - and it's also is Bicycle in ASCII!
    if loopState:
            cmdstring = cmdstring + LOOP_ON
    else:
        cmdstring = cmdstring + LOOP_OFF
    subprocess.call(cmdstring, shell=True)
    subprocess.call('sudo hciconfig hci0 leadv 3', shell=True)


def getLoopState():
    return grovepi.digitalRead(SWITCH)  # Stand-in


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

# Start bluetooth broadcast in parallel
broadcastProc.start()
# Main loop
while(True):
    try:
        # Check LoRa network status
        if(lora_command('AT+NJS\n', ['0\r\n', '1\r\n']) == '0\r\n'):
            lora_joinNetwork()

        if getLoopState():
            takeImg()

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
    except:
        # Cleanup code
        broadcastProc.terminate()
        subprocess.call('sudo hciconfig hci0 down', shell=True)
        ser.close()
        raise
