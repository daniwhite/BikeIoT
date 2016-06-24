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
import grovepi
import grove_rgb_lcd as lcd

beacon_addr = 'B8:27:EB:38:A7:AE' # MAC address of beacon RPi
light_port = 3
ledbar_port = 2

grovepi.pinMode(light_port, "OUTPUT")
grovepi.pinMode(ledbar_port, "OUTPUT")
lcd.setRGB(255,255,255)
grovepi.ledBar_init(ledbar_port, 0)

approaching_rssi = -5 # rssi above this value says biker is approaching
arrived_rssi = -1 # rssi above this value says biker has approaching

def find_rssi():
    # Create process to find rssi
    rssiProc = subprocess.Popen(['hcitool', 'rssi', beacon_addr],
        stdout=subprocess.PIPE)

    rssi = rssiProc.stdout.readline()
    rssi = rssi[19:len(rssi) -1]
    return int(rssi)

# Still being fine tuned
def set_LEDBar(rssi):
    rssi_range = 10
    rssi = rssi + rssi_range
    if rssi < 0:
        rssi = 0
    rssi /= rssi_range
    rssi *= 10
    rssi = int(rssi)
    rssi += 20
    grovepi.ledBar_setLevel(ledbar_port, rssi)
    return rssi

# Main loop of program
while(True):
    try:
        rssi = find_rssi()
        adj_rssi = set_LEDBar(rssi)
        if rssi > arrived_rssi:
            lcd.setText("Arrived!\n RSSI:%d    %d" % (rssi, adj_rssi))
            lcd.setRGB(0,255,0)
            grovepi.digitalWrite(light_port,1)
        else:
            if rssi > approaching_rssi:
                lcd.setText("Approaching...\n RSSI:%d    %d" % (rssi, adj_rssi))
                grovepi.digitalWrite(light_port,1)
                lcd.setRGB(0,255,0)
                time.sleep(1)
                grovepi.digitalWrite(light_port,0)
                lcd.setRGB(255,255,255)
                time.sleep(1)
            else:
                lcd.setText("Out of range\n RSSI:%d    %d" % (rssi, adj_rssi))
                grovepi.digitalWrite(light_port,0)
                lcd.setRGB(255,255,255)

    #If beacon is not connected, find_rssi() throws ValueError when it tries to
    #cast an empty string to int
    except ValueError:
        lcd.setText("Out of range\nNot connected" )
        grovepi.digitalWrite(light_port,0)
        lcd.setRGB(255,255,255)

        #Creates process to connect to beacon
        subprocess.Popen(['rfcomm', 'connect', 'rfcomm0', 'B8:27:EB:38:A7:AE'])
