#Program for receiver RPi

import subprocess
import time
import grovepi
import grove_rgb_lcd as lcd

beacon_addr = 'B8:27:EB:38:A7:AE' #MAC address of beacon RPi
light_port = 3 #LED should be put in port D3

grovepi.pinMode(light_port, "OUTPUT")
lcd.setRGB(255,255,255)

approaching_rssi = -5 #rssi above this value says biker is approaching
arrived_rssi = -1 #rssi above this value says biker has approaching

def find_rssi():
    rssiProc = subprocess.Popen(['hcitool', 'rssi', beacon_addr],stdout=subprocess.PIPE)#creates process to find rssi
    rssi = rssiProc.stdout.readline()
    rssi = rssi[19:len(rssi) -1]
    return int(rssi)

while(True): #main loop of program
    try:
        rssi = find_rssi()
        if rssi > arrived_rssi:
            lcd.setText("Arrived!\n RSSI:%d" % rssi)
            lcd.setRGB(0,255,0)
            grovepi.digitalWrite(light_port,1)
            time.sleep(1) #makes reading lcd easier
        else:
            if rssi > approaching_rssi:
                lcd.setText("Approaching...\n RSSI:%d" % rssi)
                grovepi.digitalWrite(light_port,1)
                lcd.setRGB(0,255,0)
                time.sleep(1)
                grovepi.digitalWrite(light_port,0)
                lcd.setRGB(255,255,255)
                time.sleep(1)
            else:
                lcd.setText("Out of range\n RSSI:%d" % rssi)
                grovepi.digitalWrite(light_port,0)
                lcd.setRGB(255,255,255)
                time.sleep(1) #makes reading lcd easier
    except ValueError: #If beacon is not connected, find_rssi() throws this error when it tries to cast an empty string to int
        lcd.setText("Out of range\nNot connected" )
        grovepi.digitalWrite(light_port,0)
        lcd.setRGB(255,255,255)
        time.sleep(1) #makes reading lcd easier
        subprocess.Popen(['rfcomm', 'connect', 'rfcomm0', 'B8:27:EB:38:A7:AE'])#creates process to connect to beacon
