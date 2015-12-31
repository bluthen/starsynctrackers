import datetime
import serial
import time
import sys

ser = serial.Serial("/dev/ttyUSB0", 115200)
print "Opened: "+ser.portstr

timestr = time.strftime("%Y%m%d-%H%M%S")
fn = timestr
if len(sys.argv) > 1:
    fn = sys.argv[1]
with open(fn+".csv", 'wb') as f:
    while(1):
        line=ser.readline()
        if (line):
            timestr = "%.12f" % time.time()
            f.write("\"%s\",%s" % (timestr, line))
