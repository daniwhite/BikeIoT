# Program for receiver RPi

from bluepy import btle
import RPi.GPIO as GPIO

LOOP_ON = '01'
LOOP_OFF = '00'

# Initalize GPIO
connection_light = 15
loop_light = 14

last_connectionState = False
last_loop_state = False

GPIO.setmode(GPIO.BCM)  # GPIO will use Broadcom pin numbers
GPIO.setwarnings(False)

GPIO.setup(connection_light, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(loop_light, GPIO.OUT, initial=GPIO.LOW)

# Initalize bluetooth
sc = btle.Scanner(0)
SCAN_LEN = 10
key = '42696379636c65'  # Special header on bluetooth message sent by beacon


# Function that accounts for past light states, returns true if light is on
def setLight(currentState, lastState, light):
    if currentState:
        print "Light %d currently true" % light
        GPIO.output(light, GPIO.HIGH)
        return True
    elif lastState:
        print "Light %d caught by last state" % light
        GPIO.output(light, GPIO.HIGH)
        return True
    else:
        print "Light %d off" % light
        GPIO.output(light, GPIO.LOW)
        return False

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
        if setLight(not (data == ''), last_connectionState, connection_light):
            print data
            setLight(data == LOOP_ON, last_loop_state, loop_light)
        last_connectionState = not (data == '')
        last_loop_state = data == LOOP_ON
except btle.BTLEException:
    print "Must run as root user"
