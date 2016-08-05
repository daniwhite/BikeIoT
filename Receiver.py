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
SCAN_LEN = 1.5
PERSIST_LEN = 10
key = '42696379636c65'  # Special header on bluetooth message sent by beacon
sc = btle.Scanner(0)
sc.start()
PERSIST_BUFFER_LEN = 3
cycles = 0
lastBeaconState = False

# Main loop of program
try:
    while(True):
        print 'Cycles: %d' % cycles
        print lastBeaconState
        sc.process(SCAN_LEN)
        devices = sc.getDevices()
        data = ''
        print "Device count: %d" % len(devices)
        for d in (devices):
            print d.getValueText(7)
            msg = d.getValueText(7)
            if (not (msg is None)):
                if msg[:len(msg) - 2] == key:
                    data = msg[len(msg) - 2:]
                    break
        # Set lights
        beaconDetected = not (data == '')
        print 'Connection light: %s' % beaconDetected
        if(cycles > PERSIST_BUFFER_LEN):
            GPIO.output(connection_light, beaconDetected)
        elif lastBeaconState:
            GPIO.output(connection_light, True)
        print data
        loop_state = data == LOOP_ON
        print 'Loop light: %s' % loop_state
        GPIO.output(loop_light, loop_state)
        print
        if (cycles > PERSIST_LEN):
            lastBeaconState = beaconDetected
            sc.clear()
            cycles = -1
        cycles += 1
except btle.BTLEException:
    print 'Must run as root user'
except:
    GPIO.cleanup()
    raise
