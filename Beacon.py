# Program for beacon RPi

import subprocess

broadcastProc = subprocess.call('sudo hcitool -i hci0 cmd 0x08 0x0008 06 02 01 1a', shell=True)
print "NExt line reached"
