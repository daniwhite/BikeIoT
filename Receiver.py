#Program for receiver RPi

import subprocess
import time

beacon_addr = 'B8:27:EB:38:A7:AE' #MAC address of beacon RPi

approaching_rssi = -5 #rssi above this value says biker is approaching
arrived_rssi = -1 #rssi above this value says biker has approaching

def find_rssi():
    rssi = subprocess.check_output("hcitool rssi %s" % beacon_addr,shell=True)
    rssi = rssi[19:len(rssi) -1]
    return int(rssi)

while(True): #main loop of program
    rssi = find_rssi()
    if rssi > arrived_rssi:
        print "Arrived!"
    else:
        if rssi > approaching_rssi:
            print "Approaching"
        else:
            print "Out of range"
    print rssi
    time.sleep(1) #Not necessary, just makes reading input easier
