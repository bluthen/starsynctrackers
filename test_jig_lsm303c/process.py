import datetime
import csv
import sys
import numpy
import math
import matplotlib.pyplot as pyplot


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

data = zip(*rows)

def rollAvg(col):
    N=200
    return numpy.convolve(col, numpy.ones((N,))/N, mode='valid')
    return col

def calc_theta(theta_initial, t):
    t_sr = t*1.0027379
    theta = theta_initial + (180.0/math.pi) * (0.25 * math.pi * t_sr / 10800.0)
    return theta
skip = 80000 

data[0] = data[0][skip:]
data[0] = data[0] - data[0][0]
data[1] = data[1][skip:]
data[2] = data[2][skip:]
data[3] = data[3][skip:]
data[4] = data[4][skip:]
data[5] = numpy.abs(data[5][skip:]) - numpy.abs(data[5][skip:][0])
data[6] = data[6][skip:]
data[7] = data[7][skip:]

data[0] = rollAvg(data[0])
data[1] = rollAvg(data[1])
data[2] = rollAvg(data[2])
data[3] = rollAvg(data[3])
data[4] = rollAvg(data[4])
data[5] = rollAvg(data[5])
data[6] = rollAvg(data[6])
data[7] = calc_theta(data[5][0], numpy.asarray(data[0]))

fig, ax1 = pyplot.subplots()
ax2 = ax1.twinx()

#ax1.plot(data[0], data[1])
#ax1.plot(data[0], data[2])
#ax1.plot(data[0], data[3])
ax1.plot(data[0], (numpy.abs(data[5]) - data[7])*60*60)

#ax2.plot(data[0], data[4], 'c-')
ax2.plot(data[0], data[5], 'm-')
#ax2.plot(data[0], data[6], 'g-')
ax2.plot(data[0], data[7], 'k-')

ax1.set_xlabel('Time (s)')
#ax1.set_ylabel('Gs')
ax1.set_ylabel('Error (arcsec)')
ax2.set_ylabel('Degrees')
#ax1.legend(['X', 'Y', 'Z'], loc=2)
ax1.legend(['delta'], loc=2)
#ax2.legend(['pitch', 'roll', 'yaw', r'$\theta_{true}$'], loc=1)
ax2.legend([r'$\theta$', r'$\theta_{true}$'], loc=1)

pyplot.show()
