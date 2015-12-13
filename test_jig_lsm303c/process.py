import datetime
import csv
import sys
import numpy
import math


rows = []
with open(sys.argv[1], 'r') as f:
    sr = csv.reader(f, delimiter=",", quotechar='"')
    for row in sr:
        d = [float(row[0]), float(row[1])/1000.0, float(row[2])/1000.0, float(row[3])/1000.0, 0.0, 0.0, 0.0, 0.0]
        rows.append(d)

rows = numpy.asarray(rows)

pt = rows[0][0]
for row in rows:
    #pt2 = row[0]
    row[0] = row[0] - pt
    #pt = pt2
    pitch=math.atan(row[1]/math.sqrt(row[2]**2+row[3]**2))
    roll=math.atan(row[2]/math.sqrt(row[1]**2+row[3]**2))
    if row[3] == 0.0:
        theta = math.pi/2.0
    else:
        theta=math.atan(math.sqrt(row[1]**2+row[2]**2)/row[3])
    row[4] = pitch * 180.0/math.pi
    row[5] = roll * 180.0/math.pi
    row[6] = theta * 180.0/math.pi
    row[7] = math.sqrt(row[1]**2+row[2]**2+row[3]**2)
    print row
