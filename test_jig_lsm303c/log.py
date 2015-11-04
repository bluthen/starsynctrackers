import datetime
import serial
import time

ser = serial.Serial("/dev/ttyUSB0", 115200)
print "Opened: "+ser.portstr

timestr = time.strftime("%Y%m%d-%H%M%S")
datestr = str(datetime.datetime.now())
with open(timestr+".csv", 'wb') as f:
    while(1):
        line=ser.readline()
        if (line):
            timestr = "%.12f" % time.time()
            f.write("\"%s\",%s" % (timestr, line))
