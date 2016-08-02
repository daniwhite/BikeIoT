# bike-project
Setup
=====
Beacon
------
- Install [bluepy](https://github.com/IanHarvey/bluepy) and [pyserial](https://github.com/pyserial/pyserial)
- Create cronjob using `sudo crontab -e` (change `FILE_PATH` to path of Beacon.sh):
```
shell=bin/bash
@reboot sh FILE_PATH >/home/pi/cronlog 2>&1
```
- Enable camera through raspi-config

Receiver
--------
- Install [bluepy](https://github.com/IanHarvey/bluepy)
- Create cronjob using `sudo crontab -e` (change `FILE_PATH` to path of Receiver.py):
```
shell=bin/bash
@reboot python FILE_PATH >/home/pi/cronlog 2>&1
```
