#!/usr/bin/bash

sudo hciconfig hci0 up
sudo hciconfig hcio noscanc
sudo hciconfig hci0 leadv 3
sudo python ~/Beacon.py
