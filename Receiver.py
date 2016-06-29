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
approaching_light = 15
arrived_light = 14

GPIO.setmode(GPIO.BCM)  # GPIO will use Broadcom pin numbers
GPIO.setwarnings(False)

GPIO.setup(approaching_light, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(arrived_light, GPIO.OUT, initial=GPIO.LOW)

# Initalize bluetooth
sc = btle.Scanner(0)
beacon_addr = 'b8:27:eb:38:a7:ae'  # MAC address of beacon

# Main loop of program
while(True):
    devices = sc.scan(2)
    beacon_index = -1
    for i, d in enumerate(devices):
        if d.addr == beacon_addr:
            beacon_index = i
    if (beacon_index > -1):
        print "Beacon found!"
        GPIO.output(approaching_light, GPIO.HIGH)

        data = devices[beacon_index].getValueText(1)
        if data == LOOP_ON:
            GPIO.output(arrived_light, GPIO.HIGH)
            print "On"
        else:
            GPIO.output(arrived_light, GPIO.LOW)
            print "Off"
    else:
        print "Out of range."
        GPIO.output(approaching_light, GPIO.LOW)
