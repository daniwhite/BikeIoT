# IoT Bike System
Use this software to set up an IoT bike system with raspberry pis. The beacon raspberry pi, which taps into a bike traffic light, broadcasts to the receiver pi over bluetooth whether or not the traffic light has detected the bike. The beacon also sends information and sensor data back to a base station over cellular and LoRa.

Hardware used
------------
**Receiver**:
- Raspberry Pi 3

**Beacon**:
- Raspberry Pi 3
- MultiTech mDot X1P-SMA-1
- SparkFun XBee Explorer Dongle
- GrovePi
- Grove Loudness Sensor
- Grove Temperature and Humidity Sensor
- Rasberry Pi Camera Board, Rev 1.3
- Particle Electron 3G kit

**Other**:
- MultiTech MultiConnect AEP Conduit, with LoRa mCard

Setup
-----
**Beacon**
- Uses **Beacon.sh** and **Beacon.py** files
  - **Beacon.py** must either be in /home/pi, or else the filepath in the last line of **Beacon.sh** must be changed
- Disable getty on serial: `sudo systemctl disable serial-getty@ttyAMA0.service`
- Install [bluepy](https://github.com/IanHarvey/bluepy), [pyserial](https://github.com/pyserial/pyserial), [grovepi](https://github.com/DexterInd/GrovePi)
- Enable I2C with `sudo raspi-config`, under *Advanced Options* > *I2C*
- Enable serial with `sudo raspi-config`, under *Advanced Options* > *Serial*
- (Optional) Change hostname with`sudo raspi-config`, under *Advanced Options* > *Hostname*
- Create cronjob using `sudo crontab -e` (change `FILE_PATH` to path of Beacon.sh):
```
shell=bin/bash
@reboot sh FILE_PATH >/home/pi/cronlog 2>&1
```
- Enable camera through `raspi-config`
- To use wifi, you may need to edit `/etc/wpa_supplicant/wpa_supplicant.conf` and add the following:
```
network={
  ssid="YOUR_WIFI_NETWORK"
  psk="YOUR_PASSWORD"
}
```
Particle instructions:
- Install the [Particle CLI](https://github.com/spark/particle-cli)
  1. Make sure you are using the most recent node version, available [here](https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions)
  2. Make sure npm is updated using `sudo npm install npm -g`
  3. Install a different version of the serialport module that's compatible with the Raspberry Pi with this command: `sudo npm install --unsafe-perm serialport`
  4. Install dfu-utils: `sudo apt-get install dfu-utils`
  5. Follow instructions in the Particle CLI repository for ["Running from source (advanced)"](https://github.com/spark/particle-cli#running-from-source-advanced)
- To program the particle, put it in [DFU mode](https://docs.particle.io/guide/getting-started/modes/electron/#dfu-mode-device-firmware-upgrade-) and flash firmware [over USB](https://github.com/spark/particle-cli#compiling-remotely-and-flashing-locally) using the CLI (usually `particle flash --usb firmware.bin`)
    - If using the atom particle package, make sure that only the particle project folder (with nothing that won't be going on the particle) is open when you compilw
- To view the data, either run MQTT.py, or set up a webhook to work with [Zapier](zapier.com):
  - Create a new zap and select *Webhooks* as the trigger. Choose *Catch Hook.*
  - Copy the URL the *View Webhook* page and using the CLI, ussue the command `particle webhook create Brdcst URL`, where URL is your Zapier URL
  - Skip the *Edit options* page and start the Beacon program while it's hooked up to the particle, then test the Webhook. The test should be successful.
  - Add *Google Sheets* > *Create spreadsheet row* as an action. After logging in with your account, go to your Google Drive and create a new sheet. Add the headings "Time", "Devices", "Loudness", "Temperature", and "Humidity" to your sheet.
  - Go back to Zapier and for each of the headings, select the corresponding field (e.g., Published At for Time, Data Loudness for Loudness).
  - Test the step and start your zap!

**Receiver**
- Uses **Receiver.sh** and **Receiver.py** file
  - **Receiver.py** must either be in /home/pi, or else the filepath in the last line of **Receiver.sh** must be changed
- Install [bluepy](https://github.com/IanHarvey/bluepy)
- (Optional) Change hostname with`sudo raspi-config`, under *Advanced Options* > *Hostname*
- Create cronjob using `sudo crontab -e` (change `FILE_PATH` to path of Receiver.sh):
```
shell=bin/bash
@reboot bash FILE_PATH >/home/pi/cronlog 2>&1
```

**mDot and Gateway**
- Enable LoRa on Gateway through admin page (available at the IP address of the gateway). Go to *Setup* > *LoRa network server* and check *Enabled*
- Set up serial communication to mDot (baudrate = 115200) and send command `AT`. You should get back `OK`.
- Put both in public mode
  - mDot: Issue `AT+PN=1`
  - Gateway: Check *Public*
- Make sure they have the same Network ID, Network key, and Frequency Sub-Band
  - Gateway: Change in LoRa menu
  - mDot: Set `AT+NK`, `AT+NI`, and `AT+FSB` to the correct values  
- Check if the mDot's address is within the gateway's address range. If not, set it with `AT+NA`.
- Once all settings are correct, use `AT&W` to save them.

Additionally, the gateway will need the Node-RED flow imported. In Node-RED (*Apps* > *Node-RED*) go to *Import* > *Clipboard* and paste in **flow.JSON**.

**Server**
- Uses **Server.py**
- Install MySQL
  - Make sure you have a database named particle, a user named server, and a table named data
- Install [MySQLdb](https://pypi.python.org/pypi/MySQL-python/1.2.5) and [sseclient](https://github.com/mpetazzoni/sseclient)
