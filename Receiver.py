# Program for receiver RPi

from bluepy import btle
import RPi.GPIO as GPIO

LOOP_ON = '01'
LOOP_OFF = '00'

# Initalize GPIO
connection_light = 15
loop_light = 14

GPIO.setmode(GPIO.BCM)  # GPIO will use Broadcom pin numbers
GPIO.setwarnings(False)

GPIO.setup(connection_light, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(loop_light, GPIO.OUT, initial=GPIO.LOW)

# Initalize bluetooth
SCAN_LEN = 0.5
CONNECTION_PERSIST_LEN = 6
LOOP_PERSIST_LEN = 1
key = '42696379636c65'  # Special header on bluetooth message sent by beacon
sc = btle.Scanner(0)
scanBuf = []
dataBuf = []

# Main loop of program
try:
    while(True):
        # Update scan buffer
        scan = sc.scan(SCAN_LEN)
        scanBuf.append(scan)
        if(len(scanBuf) > CONNECTION_PERSIST_LEN):
            scanBuf.pop(0)

        # Set up loop
        data = ''
        beaconDetected = False
        newScan = True
        for s in scanBuf:
            for d in s:
                msg = d.getValueText(7)
                print msg
                if (not (msg is None)):
                    if msg[:len(msg) - 2] == key:
                        beaconDetected = True
                        data = msg[len(msg) - 2:]
                        if newScan and not (data == ''):
                            dataBuf.insert(0, data)
            newScan = False

        # Keep buffer at correct length
        if len(dataBuf) > LOOP_PERSIST_LEN:
            dataBuf.pop(len(dataBuf) - 1)
        loop_state = LOOP_ON in dataBuf

        # Set lights
        print 'Connection light: %s' % beaconDetected
        GPIO.output(connection_light, beaconDetected)

        print 'Loop light: %s' % loop_state
        GPIO.output(loop_light, loop_state)
        print
except btle.BTLEException:
    print 'Must run as root user'
except:
    GPIO.cleanup()
    raise
