#!/usr/bin/bash

# Waits for bluetooth to start
while true
do
  DEVICES=$(hcitool dev)
  DEVICES=${DEVICES:10}
  if [ -z "$DEVICES" ]
  then
    printf "Waiting for bluetooth to start\r"
    continue
  else
    echo "Bluetooth device available!\n"
    break
  fi
done

sudo hciconfig hci0 up
sudo hciconfig hcio noscanc
sudo python /home/pi/Beacon.py
