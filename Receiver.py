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
beacon_addr = 'b8:27:eb:38:a7:ae'  # MAC address of beacon


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
        '''
        connectionState = beacon_index > -1
        if  or last_connectionState:
            print "Beacon found!"
            data = devices[beacon_index].getValueText(1)
            if beacon_index == -1:

                if last_loop_state:
                    print "Caught by last_loop_state"
                    data = LOOP_ON
                    print "On"
            GPIO.output(connection_light, GPIO.HIGH)
            print data
            if data == LOOP_ON:
                GPIO.output(loop_light, GPIO.HIGH)
                last_loop_state = True
                print "On"
            else:
                GPIO.output(loop_light, GPIO.LOW)
                last_loop_state = False
                print "Off"
        else:
        last_connectionState = beacon_index > -1
        '''
except btle.BTLEException:
    print "Must run as root user"
