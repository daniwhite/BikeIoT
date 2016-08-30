"""Program for receiver RPi."""
from __future__ import print_function
from bluepy import btle
import RPi.GPIO as GPIO
import sys
import signal
from datetime import datetime

# add pi python module dir to sys.path
sys.path.append("/home/pi/lib/python")
import rgb

LOOP_ON = '01'
LOOP_OFF = '00'
DEBUG = False
RSSI_THREASHOLD = -200
LOG_FILE = "/var/log/bike_loop.log"
LOG = False

# global led so can access it from signal handler
led = None
log_fh = None

def sig_handler(signum, frame):
    global led, LOG, log_fh
    led.close()
    if LOG:
        print('%s Stoped BleuTooth LE Traffic Light Loop Detection' % datetime.now(), file=log_fh)
        log_fh.flush()
        log_fh.close()
    exit()

def log_scan_entry(fh, se):
    log_entry = '%s, addr:%s rssi:%s msg:%s' % (datetime.now(), se.addr, se.rssi, se.getValueText(7))
    print(log_entry, file=fh)

def main(args):
    global led, DEBUG, RSSI_THREASHOLD, LOG, log_fh

    if len(args) >= 2:
        RSSI_THREASHOLD = int(args[1])
    if len(args) >= 3 and args[2] == "debug":
        DEBUG = True
    elif len(args) >= 3 and args[2] == "log":
        LOG = True
        log_fh = open(LOG_FILE, 'a')
        print('%s Started BlueTooth LE Traffic Light Loop Detection' % datetime.now(), file=log_fh)

    led = rgb.RGB_led(21,20,16)

    # Handle sigterm so we can exit gracefully
    signal.signal(signal.SIGTERM, sig_handler)

    # Initalize bluetooth
    SCAN_LEN = 0.5
    COMM_BUF_LEN = 6
    LOOP_BUF_LEN = 1
    key = '42696379636c65'  # Special header on bluetooth message sent by beacon
    sc = btle.Scanner(0)
    scanbuf = []
    databuf = []

    # Main loop of program
    try:
        while(True):
            # Update scan buffer
            scan = sc.scan(SCAN_LEN)
            scanbuf.insert(0, scan)
            if(len(scanbuf) > COMM_BUF_LEN):
                scanbuf.pop(len(scanbuf) - 1)

            # Set up loop
            data = ''
            beacon_detected = False
            new_scan = True
            for i, s in enumerate(scanbuf):
                if DEBUG:
                    print('=======Scan number %d=======' % i)
                if (new_scan) and DEBUG:
                    print('***NEW SCAN***')
                for d in s:
                    if d.rssi < RSSI_THREASHOLD:
                        continue
                    msg = d.getValueText(7)
                    if DEBUG:
                        print('address: %s, rssi: %d' % (d.addr,d.rssi))
                        for adtype, description, value in d.getScanData():
                            print('\t %s, %s, %s' % (adtype, description, value))
                    if msg is not None:
                        if msg[:len(msg) - 2] == key:
                            if new_scan and LOG:
                                log_scan_entry(log_fh, d)
                            beacon_detected = True
                            data = msg[len(msg) - 2:]
                            if new_scan and not (data == ''):
                                databuf.insert(0, data)
                if new_scan and DEBUG:
                    print('******')
                new_scan = False

            # Keep buffer at correct length
            if len(databuf) > LOOP_BUF_LEN:
                databuf.pop(len(databuf) - 1)
            loop_state = LOOP_ON in databuf

            # Set lights
            if beacon_detected:
                if DEBUG:
                    print('Comm light: %s' % beacon_detected)
                if loop_state:
                    if DEBUG:
                        print('Loop light: %s' % beacon_detected and loop_state)
                    led.blue()
                else:
                    led.red()
            else:
                led.green(True)
            if DEBUG:
                print()
    except btle.BTLEException:
        print('Must run as root user')
    except KeyboardInterrupt:
        led.close()
        exit()
    except:
        GPIO.cleanup()
        raise

if __name__ == "__main__":
    main(sys.argv)