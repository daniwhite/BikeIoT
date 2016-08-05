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
sc = btle.Scanner(0)
SCAN_LEN = 2  # Shortest length that consistantly picks up signal
key = '42696379636c65'  # Special header on bluetooth message sent by beacon

# Main loop of program
try:
    while(True):
        devices = sc.scan(SCAN_LEN)
        data = ''
        for d in (devices):
            msg = d.getValueText(7)
            if (not (msg is None)):
                if msg[:len(msg) - 2] == key:
                    data = msg[len(msg) - 2:]
                    break
        # Set lights
        beaconDetected = not (data == '')
        print 'Connection light: %s' % beaconDetected
        GPIO.output(connection_light, beaconDetected)

        print data
        loop_state = data == LOOP_ON
        print 'Loop light: %s' % loop_state
        GPIO.output(loop_light, loop_state)
        print
except btle.BTLEException:
    print 'Must run as root user'
except:
    GPIO.cleanup()
    raise
