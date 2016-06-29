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
import time
import RPi.GPIO as GPIO

# Initalize GPIO
approaching_light = 15
arrived_light = 14

GPIO.setmode(GPIO.BCM)  # GPIO will use Broadcom pin numbers
GPIO.setwarnings(False)

GPIO.setup(approaching_light, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(arrived_light, GPIO.OUT, initial=GPIO.LOW)

connected = False

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
    else:
        print "Out of range."
