# Program for beacon RPi

import subprocess

LOOP_ON = '01'
LOOP_OFF = '00'
cmdstring = 'sudo hcitool -i hci0 cmd 0x08 0x0008 06 02 01 '

loop_state = input("Loop state: ")  # Temporary

if loop_state:
        cmdstring = cmdstring + LOOP_ON
else:
    cmdstring = cmdstring + LOOP_OFF

broadcastProc = subprocess.call(cmdstring, shell=True)
