#Program for receiver RPi

import subprocess

beacon_addr = 'B8:27:EB:38:A7:AE' #MAC address of beacon RPi

def find_rssi():
    rssi = subprocess.check_output("hcitool rssi %s" % beacon_addr,shell=True)
    rssi = rssi[19:len(rssi) -1]
    return rssi

print find_rssi()
