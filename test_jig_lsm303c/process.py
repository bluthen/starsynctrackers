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


data = zip(*rows)

def rollAvg(col, N):
    return numpy.convolve(col, numpy.ones((N,))/N, mode='valid')

def calc_theta(theta_initial, t):
    t_sr = t*1.0027379
    theta = theta_initial + (180.0/math.pi) * (0.25 * math.pi * t_sr / 10800.0)
    return theta

data[0] = data[0] - data[0][0]
data[7] = numpy.sqrt(numpy.power(data[1], 2)+ numpy.power(data[2], 2) + numpy.power(data[3], 2))


pyplot.plot(data[0], data[1])
pyplot.plot(data[0], data[2])
pyplot.plot(data[0], data[3])
pyplot.plot(data[0], data[7])
pyplot.xlabel('Time (s)')
pyplot.ylabel('G')
pyplot.legend(['X', 'Y', 'Z', '$\\rho$'])
pyplot.title('Raw Accelerometer Data')
pyplot.show()

N=200
data[0] = rollAvg(data[0], N)
data[1] = rollAvg(data[1], N)
data[2] = rollAvg(data[2], N)
data[3] = rollAvg(data[3], N)
data[7] = numpy.sqrt(numpy.power(data[1], 2)+ numpy.power(data[2], 2) + numpy.power(data[3], 2))
s = 2*numpy.arcsin( numpy.sqrt(numpy.power(data[1] - data[1][0], 2)+ numpy.power(data[2]-data[2][0], 2) + numpy.power(data[3]-data[3][0], 2))/2.0)


pyplot.plot(data[0], data[1])
pyplot.plot(data[0], data[2])
pyplot.plot(data[0], data[3])
pyplot.plot(data[0], data[7])
pyplot.plot(data[0], s)
pyplot.xlabel('Time (s)')
pyplot.ylabel('G')
pyplot.legend(['X', 'Y', 'Z', '$\\rho$', r'$\Delta\sigma$'])
pyplot.title('Raw Accelerometer Data (Rolling)')
pyplot.show()

data[4] = numpy.arctan2(data[1], numpy.sqrt(numpy.power(data[2], 2)+numpy.power(data[3], 2)))
data[5] = numpy.arctan2(data[2], numpy.sqrt(numpy.power(data[1], 2)+numpy.power(data[3], 2)))
data[6] = numpy.arctan2(numpy.sqrt(numpy.power(data[1], 2)+numpy.power(data[2], 2)), data[3])

pyplot.plot(data[0], numpy.asarray(data[4]) * 180.0/math.pi)
pyplot.plot(data[0], numpy.asarray(data[5]) * 180.0/math.pi)
pyplot.plot(data[0], numpy.asarray(data[6]) * 180.0/math.pi)
pyplot.xlabel('Time (s)')
pyplot.ylabel('Degrees')
pyplot.legend([r'$\theta$', r'$\psi$', r'$\phi$'])
pyplot.title('Euler Angles')
pyplot.show()

#Spherical

def d_sigma(p1, p2):
#    return numpy.arccos(numpy.sin(p1[0])*numpy.sin(p2[0]) + numpy.cos(p1[0])*numpy.cos(p2[0])*numpy.cos(numpy.fabs(p1[1] - p2[1])))
    return 2.0*numpy.arcsin(  numpy.sin(numpy.fabs(p1[0] - p2[0])/2.0) * numpy.sin(numpy.fabs(p1[0] - p2[0])/2.0) + numpy.cos(p1[0]) * numpy.cos(p2[0]) * numpy.sin(numpy.fabs(p1[1] - p2[1]) / 2.0) * numpy.sin(numpy.fabs(p1[1] - p2[1]) / 2.0))


spherical = [data[7], numpy.arctan2(data[2], data[1]), data[6]]

dS = d_sigma([spherical[2], spherical[1]], [spherical[2][0], spherical[1][0]])

fig, ax1 = pyplot.subplots()
ax2 = ax1.twinx()

ax1.plot(data[0], spherical[0])
ax2.plot(data[0], spherical[1] * 180.0/math.pi, 'r-')
ax2.plot(data[0], spherical[2] * 180.0/math.pi, 'g-')
ax2.plot(data[0], dS * 180.0/math.pi, 'm-')

ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Magnitude')
ax2.set_ylabel('Degrees')
ax1.legend(['$\\rho$'], loc=2)
ax2.legend([r'$\theta$', r'$\phi$', r'$\Delta\sigma$'], loc=1)
pyplot.title('Spherical')
pyplot.show()




estart = [data[4][0], data[5][0], data[6][0]]

def d(a, b):
    return min(abs(a-b), 2*math.pi - abs(a - b))

edist=[]
for i in xrange(len(data[4])):
    edist.append(math.sqrt( d(estart[0], data[4][i])**2.0 + d(estart[1], data[5][i])**2.0 + d(estart[2], data[6][i])**2.0 ))
edist = numpy.asarray(edist)
edist = edist * 180.0/math.pi
edist = s * 180.0/math.pi
data[7] = calc_theta(edist[0], numpy.asarray(data[0]))

fig, ax1 = pyplot.subplots()
ax2 = ax1.twinx()

ax1.plot(data[0], (edist - data[7])*60*60)
ax2.plot(data[0], edist, 'm-')
ax2.plot(data[0], data[7], 'k-')

ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Error (arcsec)')
ax2.set_ylabel('Degrees')
ax1.legend(['delta'], loc=2)
ax2.legend([r'$\theta$', r'$\theta_{true}$'], loc=1)

pyplot.show()
