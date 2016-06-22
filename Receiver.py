#Program for receiver RPi

import subprocess
import time
import grovepi
import grove_rgb_lcd as lcd

beacon_addr = 'B8:27:EB:38:A7:AE' #MAC address of beacon RPi
light_port = 3 #LED should be put in port D3

grovepi.pinMode(light_port, "OUTPUT")

approaching_rssi = -5 #rssi above this value says biker is approaching
arrived_rssi = -1 #rssi above this value says biker has approaching

def find_rssi():
    rssi = subprocess.check_output("hcitool rssi %s" % beacon_addr,shell=True)
    rssi = rssi[19:len(rssi) -1]
    return int(rssi)

while(True): #main loop of program
    rssi = find_rssi()
    if rssi > arrived_rssi:
        lcd.setText("Arrived!\n RSSI:%d" % rssi)
        grovepi.digitalWrite(light_port,1)
    else:
        if rssi > approaching_rssi:
            lcd.setText("Approaching...\n RSSI:%d" % rssi)
            grovepi.digitalWrite(light_port,1)
            time.sleep(1)
            grovepi.digitalWrite(light_port,0)
        else:
            lcd.setText("Out of range\n RSSI:%d" % rssi)
            grovepi.digitalWrite(light_port,0)
#    print rssi
    #time.sleep(1) #Not necessary, just makes reading input easier
