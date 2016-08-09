# Program for receiver RPi

from bluepy import btle
import RPi.GPIO as GPIO

LOOP_ON = '01'
LOOP_OFF = '00'

# Initalize GPIO
comm_light = 15
loop_light = 14

GPIO.setmode(GPIO.BCM)  # GPIO will use Broadcom pin numbers
GPIO.setwarnings(False)

GPIO.setup(comm_light, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(loop_light, GPIO.OUT, initial=GPIO.LOW)

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
            print '=======Scan number %d=======' % i
            if (new_scan):
                print '***NEW SCAN***'
            for d in s:
                msg = d.getValueText(7)
                print msg
                if (not (msg is None)):
                    if msg[:len(msg) - 2] == key:
                        beacon_detected = True
                        data = msg[len(msg) - 2:]
                        print data
                        if new_scan and not (data == ''):
                            databuf.insert(0, data)
                            print databuf
            if new_scan:
                print '******'
            new_scan = False

        # Keep buffer at correct length
        if len(databuf) > LOOP_BUF_LEN:
            databuf.pop(len(databuf) - 1)
        loop_state = LOOP_ON in databuf
        # Set lights
        print 'Comm light: %s' % beacon_detected
        GPIO.output(comm_light, beacon_detected)
        print 'Loop light: %s' % beacon_detected and loop_state
        GPIO.output(loop_light, beacon_detected and loop_state)
        print
except btle.BTLEException:
    print 'Must run as root user'
except:
    GPIO.cleanup()
    raise
