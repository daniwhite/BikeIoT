#Program for receiver RPi

#SETUP (TO RUN ON BOOT):
#Create a bash script to run this command:
#sudo python /home/pi/Receiver.py
#Then create crontab job for root user with the following:
#shell=bin/bash
#@reboot sh FILE_PATH >/home/pi/cronlog 2>&1
#where FILE_PATH is the name of the script

import subprocess
import time
import grovepi
import grove_rgb_lcd as lcd

beacon_addr = 'B8:27:EB:38:A7:AE' #MAC address of beacon RPi
light_port = 3 #LED should be put in port D3
ledbar_port = 2 #LED bar should be in port D2

grovepi.pinMode(light_port, "OUTPUT")
grovepi.pinMode(ledbar_port, "OUTPUT")
lcd.setRGB(255,255,255)
grovepi.ledBar_init(ledbar_port, 0)

approaching_rssi = -5 #rssi above this value says biker is approaching
arrived_rssi = -1 #rssi above this value says biker has approaching

def find_rssi():
    rssiProc = subprocess.Popen(['hcitool', 'rssi', beacon_addr],stdout=subprocess.PIPE)#creates process to find rssi
    rssi = rssiProc.stdout.readline()
    rssi = rssi[19:len(rssi) -1]
    return int(rssi)

def set_LEDBar(rssi):
    rssi_range = 10 # True because rssi maxes out at about 0

    rssi = rssi + rssi_range # Should now be positive

    # Takes care of far away cases
    if rssi < 0:
        rssi = 0
    rssi /= rssi_range
    rssi *= 10
    rssi = int(rssi)

    rssi += 20
    grovepi.ledBar_setLevel(ledbar_port, rssi)
    return rssi


while(True): #main loop of program
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
    except ValueError: #If beacon is not connected, find_rssi() throws this error when it tries to cast an empty string to int
        lcd.setText("Out of range\nNot connected" )
        grovepi.digitalWrite(light_port,0)
        lcd.setRGB(255,255,255)
        subprocess.Popen(['rfcomm', 'connect', 'rfcomm0', 'B8:27:EB:38:A7:AE'])#creates process to connect to beacon
