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
print "StartTime = "+str(pt)
for row in rows:
    #pt2 = row[0]
    row[0] = row[0] - pt
    #pt = pt2
    rho=math.atan(row[1]/math.sqrt(row[2]**2+row[3]**2))
    phi=math.atan(row[2]/math.sqrt(row[1]**2+row[3]**2))
    if row[3] == 0.0:
        theta = math.pi/2.0
    else:
        theta=math.atan(math.sqrt(row[1]**2+row[2]**2)/row[3])
    row[4] = rho * 180.0/math.pi
    row[5] = phi * 180.0/math.pi
    row[6] = theta * 180.0/math.pi
    row[7] = math.sqrt(row[1]**2+row[2]**2+row[3]**2)

data = zip(*rows)

def rollAvg(col, N):
    return numpy.convolve(col, numpy.ones((N,))/N, mode='valid')

def calc_theta(theta_initial, t):
    t_sr = t*1.0027379
    theta = theta_initial + (180.0/math.pi) * (0.25 * math.pi * t_sr / 10800.0)
    return theta

skip = 80000

data[0] = data[0] - data[0][0]

pyplot.plot(data[0], data[1])
pyplot.plot(data[0], data[2])
pyplot.plot(data[0], data[3])
pyplot.xlabel('Time (s)')
pyplot.ylabel('G')
pyplot.legend(['X', 'Y', 'Z'])
pyplot.title('Raw Accelerometer Data')
pyplot.show()

pyplot.plot(data[0], data[4])
pyplot.plot(data[0], data[5])
pyplot.plot(data[0], data[6])
pyplot.xlabel('Time (s)')
pyplot.ylabel('Degrees')
pyplot.legend([r'$\rho$', r'$\phi$', r'$\theta$'])
pyplot.title('Converted Raw')
pyplot.show()

N=200

data[0] = rollAvg(data[0], N)
print "=========="
print data[0][0]
print data[0][N]
data[5] = rollAvg(numpy.abs(data[5]), N)
data[7] = calc_theta(data[5][0], numpy.asarray(data[0]))

fig, ax1 = pyplot.subplots()
ax2 = ax1.twinx()

ax1.plot(data[0], numpy.abs((numpy.abs(data[5]) - data[7])*60*60))
ax2.plot(data[0], data[5], 'm-')
ax2.plot(data[0], data[7], 'k-')

ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Error (arcsec)')
ax2.set_ylabel('Degrees')
ax1.legend(['delta'], loc=2)
ax2.legend([r'$\theta$', r'$\theta_{true}$'], loc=1)

pyplot.show()
