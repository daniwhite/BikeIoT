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
CELL_PERIOD = 10  # At least ~540 should be the final to use 1 mb per month
SCAN_LEN = 2  # How long to scan bluetooth at one time

# Set up grovepi
LOUDNESS_SENSOR = 0  # Connect to A0
TEMP_HUM_SENSOR = 6  # Connect to D6
SWITCH = 5
grovepi.pinMode(LOUDNESS_SENSOR, "INPUT")
grovepi.pinMode(TEMP_HUM_SENSOR, "INPUT")
grovepi.pinMode(SWITCH, "INPUT")
grove_queue = Queue()
grove_data = []

# Setup bluetooth
devices = []
sc = btle.Scanner(0)

# Initialize serial
lora_device = '/dev/ttyUSB0'
lora_baudrate = 115200
lora_ser = serial.Serial(lora_device, lora_baudrate)
cell_device = '/dev/ttyACM0'
cell_baudrate = 115200
cell_ser = serial.Serial(cell_device, cell_baudrate)

# Data to send to cell
broadcast_data = []
old_broadcast_data = []
prefixes = ["devs", "ld", "temp", "hum"]

# Initialize camera
cam = picamera.PiCamera()

bt_time = time.time()  # Init time for bluetooth device count cycles
lora_time = time.time()  # Init time for LoRa cycles
cell_time = time.time()  # Init time for cell cycles
start_time = time.time()  # Init time for program run time

lora_network_status = False
lora_network_checked = False


# Defines bluetooth function that will be run as separate process
def bt_process():
    try:
        while(True):
            data = get_data()
            set_queue_data(data)
            broadcast(data[0])
    except IOError:
        print "IOError detected and excepted"
        pass


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
    ser_command('Cell off', cell_ser)
    lora_ser.close()
    cell_ser.close()
    # Print how long the program ran for
    now = time.time()
    print (now - start_time) // 60,
    print " min ",
    print now % 60,
    print "sec"


def get_loopstate():
    # Reads loopstate directly from grovepi
    # Should only be called in one thread
    return grovepi.digitalRead(SWITCH)


def get_data():
    # Reads assemble data directly from grovepi
    # Should only be called in one thread
    loopstate = get_loopstate()
    loudness = grovepi.analogRead(LOUDNESS_SENSOR)
    [temp, hum] = grovepi.dht(TEMP_HUM_SENSOR, module_type=0)
    return [loopstate, loudness, temp, hum]


def set_queue_data(data):
    # Sets loopstate in queue
    while(not grove_queue.empty):
        grove_queue.get()
    grove_queue.put(data)


def get_queue_data():
    # Gets loopstate from queue
    # Should be how alternate threads access the loopstate
    global grove_data
    try:
        grove_data = grove_queue.get_nowait()
    except Empty:
        # Just use old loopstate if queue is empty
        pass
    return grove_data


# Sends command over serial, then returns its response
def ser_command(str, ser, responses=['OK\r\n']):
    ser.write(str)
    if ser == lora_ser:
        ser.readline()
    msg = ''
    while (msg not in responses):
        try:
            msg = ser.readline()
            print msg
        except OSError, serial.SerialException:
            print 'Unable to read. Is something else using the serial port?'
    return msg


# Send AT command to join LoRa network
# Timout of -1 means wait for connection forever, 0 means don't wait at all
def lora_join_network(timeout=-1):
    str = ''
    start_time = time.time()
    while(not (str == 'Successfully joined network\r\n')):
        str = ser_command('AT+JOIN\n', lora_ser, [
            'Join Error - Failed to join network\r\n',
            'Successfully joined network\r\n'])
        if (timeout >= 0 and time.time() - start_time > timeout):
            return False
    return True


def take_img(folder_path='/home/pi/Images/'):
    title = folder_path + time.ctime() + '.jpg'
    title = title.replace(' ', '_')
    title = title.replace(':', '-')
    cam.capture(title)


# Prepare to broadcast
broadcast_proc = Process(target=bt_process)
# Main loop
while(True):
    try:
        # Start bluetooth broadcast in parallel
        if not broadcast_proc.is_alive():
            print 'Starting new bluetooth process'
            del(broadcast_proc)
            broadcast_proc = Process(target=bt_process)
            broadcast_proc.start()

        # Turn on cellular
        ser_command('Cell on', cell_ser)

        # Get sensor data
        data = get_queue_data()
        # If there's no data, wait a bit
        if (len(data) == 0):
            print 'Waiting'
            time.sleep(0.1)
            continue

        # Print sensor data
        print 'loudness: ' + str(data[1])
        print 'temperature: ' + str(data[2])
        print 'humidity: ' + str(data[3])

        # Check LoRa network status
        if(ser_command('AT+NJS\n', lora_ser, ['0\r\n', '1\r\n']) == '0\r\n'):
            if not lora_network_checked:
                lora_network_status = lora_join_network(5)
                lora_network_checked = True
                if lora_network_status:
                    print 'Network joined successfully!'
                else:
                    print 'Network join failed.'

        # Take picture if loop is triggered
        if data[0]:
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

        broadcast_data = data[1:4]
        broadcast_data.append(len(devices))

        # Lora broadcast
        lora_msg = ''
        for d in broadcast_data:
            lora_msg += str(d) + ','
        # Get rid of last comma, add newline
        lora_msg = lora_msg[:len(lora_msg) - 1] + '\n'
        if (time.time() - lora_time > LORA_PERIOD) and lora_network_status:
            lora_time = time.time()
            loraMsg = 'AT+SEND=' + lora_msg
            ser_command(lora_msg, lora_ser)

        # Cell broadcast
        if (len(old_broadcast_data) != 0) and (
                time.time() - cell_time) > CELL_PERIOD:
            cell_msg = ''
            for i, d in enumerate(broadcast_data):
                if not (d == old_broadcast_data[i]):
                    cell_msg += prefixes[i] + ':' + str(d) + ','
            cell_msg = cell_msg[:len(cell_msg) - 1] + '\n'
            print broadcast_data
            print old_broadcast_data
            print cell_msg
            ser_command(cell_msg, cell_ser)
            cell_time = time.time()
        old_broadcast_data = broadcast_data

        print 'Cycled'
    except:
        cleanup()
        raise
