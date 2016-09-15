"""Program for beacon RPi."""

from multiprocessing import Process, Queue
from Queue import Empty
import subprocess
import time
import os
import re

from bluepy import btle
import grovepi
import picamera
import serial

DEBUG = False
CELL = False  # Debugging other functions goes faster w/o cellular

LOOP_ON = '01'
LOOP_OFF = '00'

IMG_PATH = '/home/pi/Images/'

BROADCAST_PERIOD = 60*60  # At least ~540 to use 1 mb per month
if DEBUG:
    BROADCAST_PERIOD = 5
CAM_PERIOD = 12  # How often to take a picture
if DEBUG:
    CAM_PERIOD = 5
SCAN_LEN = 2  # How long to scan bluetooth at one time

# Initialize start time for periodic events
broadcast_time = time.time()
broadcast_time -= BROADCAST_PERIOD  # Makes particle broadcast immediately
cam_time = time.time()

# Set up grovepi
LOUDNESS_SENSOR = 0  # Connect to A0
TEMP_HUM_SENSOR = 6  # Connect to D6
LOOP = 3  # Connect to D5
LED = 2
grovepi.pinMode(LOUDNESS_SENSOR, 'INPUT')
grovepi.pinMode(TEMP_HUM_SENSOR, 'INPUT')
grovepi.pinMode(LOOP, 'INPUT')
grovepi.pinMode(TEMP_HUM_SENSOR, 'OUTPUT')
grove_queue = Queue()
grove_data = []

# Setup bluetooth
devices = []
sc = btle.Scanner(0)

# Initialize serial
cell_device = '/dev/ttyACM0'
cell_baudrate = 115200
cell_ser = serial.Serial(cell_device, cell_baudrate)

# Data to send to cell
broadcast_data = []
old_broadcast_data = []
prefixes = ['devs', 'ld', 'temp', 'hum', 'pics']

# Initialize camera
cam = picamera.PiCamera()


def bt_process():
    """Define bluetooth function that will be run as separate process."""
    try:
        while(True):
            data = get_data()
            set_queue_data(data)
            broadcast(data[0])
            # Diagnostic
            grovepi.digitalWrite(LED, data[0])
    except IOError:
        if DEBUG:
            print 'IOError detected and excepted'
        pass


def broadcast(loopstate):
    """Broadcast loopstate over bluetooth."""
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
    """Clean up at program end."""
    broadcast_proc.terminate()
    subprocess.call('sudo hciconfig hci0 noleadv', shell=True)
    if CELL:
        ser_command('Cell off', cell_ser)
        cell_ser.close()
    grovepi.digitalWrite(LED, 0)


def get_data():
    """
    Read sensor data right from grovepi.

    Don't call in more than one thread.
    """
    loopstate = get_loopstate()
    loudness = grovepi.analogRead(LOUDNESS_SENSOR)
    [temp, hum] = grovepi.dht(TEMP_HUM_SENSOR, module_type=0)
    return [loopstate, loudness, temp, hum]


def get_space():
    """Return what percent of space is left for images."""
    df = subprocess.Popen(['df', IMG_PATH], stdout=subprocess.PIPE)
    output = df.communicate()[0]
    output = output.split('\n')[1]
    output = re.sub(' +', ' ', output)  # Remove repeat spaces
    output = output.split(' ')[4]
    output = int(output[0])
    return output


def get_loopstate():
    """
    Get state of loop, with whatever the system ends up being.

    For now, since it's grovepi, don't call in multiple threads
    """
    return grovepi.digitalRead(LOOP)


def get_queue_data():
    """
    Get loopstate from queue.

    Safe for all theads.
    """
    global grove_data
    try:
        grove_data = grove_queue.get_nowait()
    except Empty:
        # Just use old loopstate if queue is empty
        pass
    return grove_data


def ser_command(str, ser, responses=['OK\r\n']):
    """Send command over serial, then returns its response."""
    ser.write(str)
    msg = ''
    while (msg not in responses):
        try:
            msg = ser.readline()
        except OSError, serial.SerialException:
            if DEBUG:
                print 'Unable to read. Is something else using the port?'
    return msg


def set_queue_data(data):
    """Set data in queue."""
    while(not grove_queue.empty):
        grove_queue.get()
    grove_queue.put(data)


def take_img(folder_path):
    """Take picture."""
    title = folder_path + time.ctime() + '.jpg'
    title = title.replace(' ', '_')
    title = title.replace(':', '-')
    cam.capture(title)


# Setup code for before running loop
broadcast_proc = Process(target=bt_process)
# Turn on cellular
if CELL:
    ser_command('Cell on', cell_ser)

# Main loop
while(True):
    try:
        # Start bluetooth broadcast in parallel
        if not broadcast_proc.is_alive():
            if DEBUG:
                print 'Starting new bluetooth process'
            del(broadcast_proc)
            broadcast_proc = Process(target=bt_process)
            broadcast_proc.start()

        # Get sensor data
        data = get_queue_data()
        # If there's no data, wait a bit
        if (len(data) == 0):
            if DEBUG:
                print 'Waiting for queue data' + '\r',
            continue

        if DEBUG:
            # Print sensor data
            print '\n** Sensor data **'
            print 'Loudness: ' + str(data[1])
            print 'Temperature: ' + str(data[2])
            print 'Humidity: ' + str(data[3])
            print '*****************\n'

        # Take picture
        if time.time() - cam_time > CAM_PERIOD:
            cam_time = time.time()
            if not (time.localtime().tm_hour > 21 or time.localtime().tm_hour < 5):
                if DEBUG:
                    print 'Space left: %d%%' % get_space()
                if get_space() < 95:
                    take_img(IMG_PATH)

        # Get number of images taken
        pics = len(os.listdir(IMG_PATH))
        if DEBUG:
            print 'Pics: %d' % pics

        # Check for new devices
        scan_devices = sc.scan(SCAN_LEN)
        for s_dev in scan_devices:
            for dev in devices:
                if dev.addr == s_dev.addr:
                    break
            else:
                devices.append(s_dev)
        if DEBUG:
            # Print device count
            print 'Devices found since ',
            print broadcast_time

        broadcast_data = data[1:4]
        broadcast_data.insert(0, len(devices))
        broadcast_data.insert(len(broadcast_data) - 1, pics)

        # Cell broadcast
        if (len(old_broadcast_data) != 0) and ((
                time.time() - broadcast_time) > BROADCAST_PERIOD):
            if CELL:
                # Create message to broadcast
                cell_msg = '{'
                for i, d in enumerate(broadcast_data):
                    cell_msg += '"' + prefixes[i] + '":' + str(d) + ','
                cell_msg = cell_msg[:len(cell_msg) - 1] + '}'
                if DEBUG:
                    print 'Old data: %s' % old_broadcast_data
                    print 'New data: %s' % broadcast_data
                    print 'Cell message: ' + cell_msg + '\n'
                # Send broadcast
                ser_command(cell_msg, cell_ser)
                broadcast_time = time.time()
            # Wipe bluetooth devices after sending cell message
            devices = []
        old_broadcast_data = broadcast_data

        if DEBUG:
            print 'Cycled'
    except:
        cleanup()
        raise
