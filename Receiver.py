"""Program for receiver RPi."""

from bluepy import btle
import RPi.GPIO as GPIO
import sys

# add pi python module dir to sys.path
sys.path.append("/home/pi/lib/python")
import rgb

LOOP_ON = '01'
LOOP_OFF = '00'


def main(args):
    DEBUG = False
    if len(args) >= 2 and args[1] == "debug":
        DEBUG = True

    led = rgb.RGB_led(21,20,16)

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
                    print '=======Scan number %d=======' % i
                if (new_scan) and DEBUG:
                    print '***NEW SCAN***'
                for d in s:
                    msg = d.getValueText(7)
                    if DEBUG:
                        print('address: %s' % d.addr)
                        for adtype, description, value in d.getScanData():
                            print(adtype, description, value)
                    if msg is not None:
                        if msg[:len(msg) - 2] == key:
                            beacon_detected = True
                            data = msg[len(msg) - 2:]
                            if new_scan and not (data == ''):
                                databuf.insert(0, data)
                if new_scan and DEBUG:
                    print '******'
                new_scan = False

            # Keep buffer at correct length
            if len(databuf) > LOOP_BUF_LEN:
                databuf.pop(len(databuf) - 1)
            loop_state = LOOP_ON in databuf

            # Set lights
            if beacon_detected:
                if DEBUG:
                    print 'Comm light: %s' % beacon_detected
                if loop_state:
                    if DEBUG:
                        print 'Loop light: %s' % beacon_detected and loop_state
                    led.blue()
                else:
                    led.red()
            else:
                led.green(True)
            if DEBUG:
                print
    except btle.BTLEException:
        print 'Must run as root user'
    except:
        GPIO.cleanup()
        raise

if __name__ == "__main__":
    main(sys.argv)