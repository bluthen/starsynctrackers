import datetime
import csv
import sys
import numpy
import math


rows = []
with open(sys.argv[1], 'r') as f:
    sr = csv.reader(f, delimiter=",", quotechar='"')
    for row in sr:
        d = [float(sr[0]), float(row[1]), float(row[2]), float(row[3]), 0.0, 0.0, 0.0, 0.0]
        rows.append(row)

rows = numpy.asarray(rows)

pt = rows[0][0]
for row in rows:
    pt2 = row[0]
    row[0] = row[0] - pt
    pt = pt2
    pitch=math.atan(row[1]/math.sqrt(row[2]**2+row[3]**2))
    roll=math.atan(row[2]/math.sqrt(row[1]**2+row[3]**2))
    if row[3] == 0.0:
        theta = math.pi/2.0
    else:
        theta=math.atan(math.sqrt(row[1]**2+row[2]**2)/row[3])
    row[4] = pitch
    row[5] = roll
    row[6] = theta
    row[7] = math.sqrt(row[1]**2+row[2]**2+row[3]**2)

