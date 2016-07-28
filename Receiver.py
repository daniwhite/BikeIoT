# Program for receiver RPi

# SETUP (TO RUN ON BOOT):
#
# Create a bash script to run this command:
# sudo python /home/pi/Receiver.py
#
# Then create crontab job for root user with the following:
# shell=bin/bash
# @reboot sh FILE_PATH >/home/pi/cronlog 2>&1
# where FILE_PATH is the name of the script

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
beacon_addr = 'b8:27:eb:97:3c:f1'  # MAC address of beacon


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
        devices = sc.scan(2)
        beacon_index = -1
        for i, d in enumerate(devices):
            if d.addr == beacon_addr:
                beacon_index = i
        data = devices[beacon_index].getValueText(1)
        if setLight(beacon_index > -1, last_connectionState, connection_light):
            print data
            setLight(data == LOOP_ON, last_loop_state, loop_light)
        last_connectionState = beacon_index > -1
        last_loop_state = data == LOOP_ON
except btle.BTLEException:
    print "Must run as root user"
