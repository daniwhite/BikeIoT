# Program for beacon RPi

import subprocess
import serial
from bluepy import btle
import time
import picamera
import grovepi
from multiprocessing import Process, Queue
from Queue import Empty

LOOP_ON = '01'
LOOP_OFF = '00'

BT_PERIOD = 60  # How often to clear the bluetooth device list and start over
LORA_PERIOD = 5  # How many seconds between each Lora braodcast
SCAN_LEN = 2  # How long to scan bluetooth at one time

# Set up grovepi
LOUDNESS_SENSOR = 0  # Connect to A0
TEMP_HUM_SENSOR = 6  # Connect to D6
SWITCH = 5
grovepi.pinMode(LOUDNESS_SENSOR, "INPUT")
grovepi.pinMode(TEMP_HUM_SENSOR, "INPUT")
grovepi.pinMode(SWITCH, "INPUT")

# Setup bluetooth
devices = []
sc = btle.Scanner(0)
switchQ = Queue()
qloopstate = 0

# Initialize serial (to control mDot)
device = '/dev/ttyUSB0'
baudrate = 115200
ser = serial.Serial(device, baudrate)

# Initialize camera
cam = picamera.PiCamera()

bt_time = time.time()  # Init time for bluetooth device count cycles
lora_time = time.time()  # Init time for LoRa cycles
start_time = time.time()  # Init time for program run time


# Defines bluetooth function that will be run as separate process
def bt_process():
    while(True):
        loopstate = get_queue_loopstate()
        broadcast(loopstate)
broadcast_proc = Process(target=bt_process)


def broadcast(loopstate):
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
    if loopstate:
            cmdstring = cmdstring + LOOP_ON
    else:
        cmdstring = cmdstring + LOOP_OFF + ' >/dev/null 2>&1'
    subprocess.call(cmdstring, shell=True)
    subprocess.call('sudo hciconfig hci0 leadv 3 >/dev/null 2>&1', shell=True)


def cleanup():
    broadcast_proc.terminate()
    subprocess.call('sudo hciconfig hci0 down', shell=True)
    ser.close()
    now = time.time()
    print now - start_time
    print (now - start_time) // 60,
    print " min ",
    print now % 60,
    print "sec"


def get_loopstate():
    # Reads loopstate directly from grovepi
    # Should only be called in main thread
    return grovepi.digitalRead(SWITCH)


def set_queue_loopstate(state):
    # Sets loopstate in queue
    while(not switchQ.empty):
        switchQ.get()
    switchQ.put(state)


def get_queue_loopstate():
    # Gets loopstate from queue
    # Should be how alternate threads access the loopstate
    global qloopstate
    try:
        qloopstate = switchQ.get_nowait()
    except Empty:
        # Just use old loopstate if queue is empty
        pass
    return qloopstate


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
def lora_join_network():
    str = ''
    while(not (str == 'Successfully joined network\r\n')):
        str = lora_command('AT+JOIN\n', [
            'Join Error - Failed to join network\r\n',
            'Successfully joined network\r\n'])


def take_img(folder_path='Images/'):
    title = folder_path + time.ctime() + '.jpg'
    title = title.replace(' ', '_')
    title = title.replace(':', '-')
    cam.capture(title)

# Start bluetooth broadcast in parallel
broadcast_proc.start()
# Main loop
while(True):
    try:
        set_queue_loopstate(get_loopstate())
        # Check LoRa network status
        if(lora_command('AT+NJS\n', ['0\r\n', '1\r\n']) == '0\r\n'):
            lora_join_network()

        if get_loopstate():
            take_img()

        # Check for new devices
        scan_devices = sc.scan(SCAN_LEN)
        for s_dev in scan_devices:
            for dev in devices:
                if dev.addr == s_dev.addr:
                    break
            else:
                devices.append(s_dev)
        # Print device count
        print 'Devices found since ',
        print time.ctime(bt_time),
        print ' : %d' % len(devices)
        # Check if we need to refresh the list
        if(time.time() - bt_time > BT_PERIOD):
            devices = []
            bt_time = time.time()

        # Get sensor data
        loudness = grovepi.analogRead(LOUDNESS_SENSOR)
        [temp, hum] = grovepi.dht(TEMP_HUM_SENSOR, module_type=0)
        print 'loudness: ' + str(loudness)
        print 'temperature: ' + str(temp)
        print 'humidity: ' + str(hum)

        # Lora broadcast
        if(time.time() - lora_time > LORA_PERIOD):
            lora_time = time.time()
            msg = 'AT+SEND=' + \
                str(len(devices)) + ',' + \
                str(loudness) + ',' + \
                str(temp) + ',' + \
                str(hum) + '\n'
            lora_command(msg)
    except IOError:
        print "IOError detected and excepted"
        pass
    except:
        cleanup()
        raise
