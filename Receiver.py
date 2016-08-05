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
        scan = sc.scan(SCAN_LEN)
        scanBuf.append(scan)
        if(len(scanBuf) > CONNECTION_PERSIST_LEN):
            scanBuf.pop(0)
        data = ''
        for d in scan:
            print d.getValueText(7)
            msg = d.getValueText(7)
            if (not (msg is None)):
                if msg[:len(msg) - 2] == key:
                    data = msg[len(msg) - 2:]
                    if not (data == ''):
                        dataBuf.append(data)
                    break

        beaconDetected = False
        for s in scanBuf:
            print 'For loop endered'
            for d in s:
                print 'Inner loop entered'
                msg = d.getValueText(7)
                print 'Value text retreived'
                print msg
                if (not (msg is None)):
                    print 'Confirmed it is not none'
                    if msg[:len(msg) - 2] == key:
                        print 'Checked for key'
                        beaconDetected = True

        print beaconDetected
        # Keep buffer at correct length
        if len(dataBuf) > LOOP_PERSIST_LEN:
            dataBuf.pop(0)
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
