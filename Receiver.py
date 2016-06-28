#Program for receiver RPi

# SETUP (TO RUN ON BOOT):
#
# Create a bash script to run this command:
# sudo python /home/pi/Receiver.py
#
# Then create crontab job for root user with the following:
# shell=bin/bash
# @reboot sh FILE_PATH >/home/pi/cronlog 2>&1
# where FILE_PATH is the name of the script

import subprocess
import time
import RPi.GPIO as GPIO

approaching_rssi = -11 # RSSI above this value says biker is approaching
arrived_rssi = -1 # RSSI above this value says biker has approaching
rssi_range = 10 # Lowest RSSI that registers on LED bar

rssi_buffer = [-40,-40,-40]

connected = False

beacon_addr = 'B8:27:EB:38:A7:AE' # MAC address of beacon RPi
approaching_light = 15
arrived_light = 14

GPIO.setmode(GPIO.BCM) # GPIO will use Broadcom pin numbers
GPIO.setwarnings(False)

GPIO.setup(approaching_light, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(arrived_light, GPIO.OUT, initial = GPIO.LOW)

def checkConnection():
    connectProc = subprocess.Popen(['hcitool', 'con'],
        stdout=subprocess.PIPE)
    connectProc.stdout.readline() # Moves down one line
    connections = connectProc.stdout.readline()
    if connections != "":
        GPIO.output(approaching_light, GPIO.HIGH)
    else:
        GPIO.output(approaching_light, GPIO.LOW)
        #Creates process to connect to beacon
        subprocess.Popen(['rfcomm', 'connect', 'rfcomm0', 'B8:27:EB:38:A7:AE'])

def find_raw_rssi():
    # Create process to find RSSI
    rssiProc = subprocess.Popen(['hcitool', 'rssi', beacon_addr],
        stdout=subprocess.PIPE)

    rssi = rssiProc.stdout.readline()
    rssi = rssi[19:len(rssi) -1]
    return float(rssi)

def find_avg_rssi():
    rssi_buffer[2] = rssi_buffer[1]
    rssi_buffer[1] = rssi_buffer[0]
    rssi_buffer[0] = find_raw_rssi()
    avg = 0
    for i in rssi_buffer:
        avg += i
    avg /= 3
    return avg

# Main loop of program
while(True):
    checkConnection()
    time.sleep(1)
