"""Save HTTP data from particle to MySQL database."""

import json
import time
import MySQLdb

from sseclient import SSEClient

PI_ALIVE_PERIOD = 60  # Timeout for alive signal
COREID = '3f001d000351353337353037'  # ID of particle
PSWD = 'password'  # Change to be MySQL password
# Came from Particle console
ADDR = "https://api.particle.io/v1/devices/events?access_token=222dbfc46f58a5a4cbfc8ec454360c44aa3947ed"

db = MySQLdb.connect('localhost','root', PSWD,'particle')
cursor = db.cursor()

last_time = time.time()

messages = SSEClient(ADDR)
# Iterates through ever object in the stream and waits for new objects
for msg in messages:
    if len(msg.data) > 0:
        print "Message received at %s" % time.ctime()
        print msg.data
        jMsg = json.loads(msg.data)

        # Data is JSON with some overhead removed, which we need to add back
        if jMsg['coreid'] != COREID:
            continue
        raw_data = jMsg['data']
        print raw_data
        data = json.loads(raw_data)
        exec_str = 'INSERT INTO data values(CURRENT_DATE(), NOW(), '
        for key in data:
            print "Key: %s -- Data: %d" % (key, data[key])
            exec_str += '%s, ' % data[key]
        exec_str = exec_str[:len(exec_str) - 2]
        exec_str += ');'
        print exec_str
        cursor.execute(exec_str)
        db.commit()
        last_time = time.time()
    else:
        print "No message at %s" % time.ctime()
    if time.time() - last_time > PI_ALIVE_PERIOD:
        print 'Pi down!'
