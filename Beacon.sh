#!/usr/bin/bash

sudo hciconfig hci0 up
sudo hciconfig hcio noscanc
sudo python Beacon.py
