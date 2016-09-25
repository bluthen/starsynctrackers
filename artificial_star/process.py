import cv2
import cv2.cv as cv
import numpy as np
import math
import getopt
import sys
import time
import exifread
import os
from scipy import optimize


def drawCircle1(cimg, origin, radius, color, thickness=2.5):
    for x in xrange(cimg.shape[1]):
        for y in xrange(cimg.shape[0]):
            delta = abs(np.linalg.norm([x - origin[0], y - origin[1]]) - radius)
            if delta < thickness:
                cimg[y][x] = color


def drawCircle2(cimg, origin, radius, color, thickness=2.5):
    found = False
    for x in xrange(cimg.shape[1]):
        for y in xrange(cimg.shape[0]):
            delta = abs(np.linalg.norm([x - origin[0], y - origin[1]]) - radius)
            if delta < thickness:
                cimg[y][x] = color



def calc_R(contour_t, xc, yc):
    """ calculate the distance of each 2D points from the center (xc, yc) """
    return np.sqrt((contour_t[0]-xc)**2 + (contour_t[1]-yc)**2)

def gen_f2(contour_t):

    def f2(c):
        """ calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc) """
        Ri = calc_R(contour_t, *c)
        return Ri - Ri.mean()
    return f2


def rad_to_arcsec(rad):
    return rad*(180.0/(math.pi))*60.0*60.0

def calc_time_theta(t):
    t_sr = t*1.0027379
    theta = 0.25 * math.pi * t_sr / 10800.0
    return theta

def threshold(img, mthres):
    mthresh = 127
    bigmask = img >= mthresh
    smallmask = img < mthresh

    img[bigmask] = 255
    img[smallmask] = 0


if __name__ == "__main__":
    filename = sys.argv[1]
    name, ext = os.path.splitext(filename)
    cimg = cv2.imread(filename)
    img = cv2.imread(filename, 0)
    with open(filename, 'rb') as f:
        tags = exifread.process_file(f)
        exposure_time = float(tags['EXIF ExposureTime'].printable)
        print exposure_time

    cv2.namedWindow('test', cv2.WINDOW_NORMAL)
    #cv2.imshow('test', img)
    #cv2.waitKey(0)

    #threshold(img, 127)
    mean = np.mean(img)
    stddev = np.std(img)

    ret, thresh = cv2.threshold(img, mean+2*stddev, 255, 0)

    #cv2.imshow('test', thresh)
    #cv2.waitKey(0)

    contours, hierarchy = cv2.findContours(thresh, 1, 2)

    #filter contours based on area.
    maxarea = -1
    foundcontour = None
    contourIdx = -1
    for i in xrange(len(contours)):
        cnt = contours[i]
        carea = cv2.contourArea(cnt)
        if carea > maxarea:
            foundcontour=cnt
            maxarea = carea
            contourIdx = i

    print cv2.contourArea(contours[contourIdx])
    #cv2.drawContours(cimg, contours, contourIdx, (0, 255, 0), thickness=3)
    #cv2.imshow('test', cimg)
    #cv2.waitKey(0)

    #Center of contour
    M = cv2.moments(contours[contourIdx])
    ccenter = (M['m10']/M['m00'], M['m01']/M['m00'])
    print ccenter

    #http://scipy-cookbook.readthedocs.io/items/Least_Squares_Circle.html
    contour = contours[contourIdx]
    contShape = contour.shape
    contourR = np.reshape(contour, [contShape[0], contShape[2]]).T
    circ, ier = optimize.leastsq(gen_f2(contourR), (3888, 3888))
    Ri_2 = calc_R(contourR, circ[0], circ[1])
    R_2 = np.mean(Ri_2)
    R_residu2 = np.sum((Ri_2 - R_2)**2.0)

    print R_2
    print "Artificial Dec: %f" % (90.0 - R_2*3.92/(60.*60),)




    # fit line
    rows, cols = img.shape[:2]
    [vx, vy, x, y] = cv2.fitLine(contours[contourIdx], cv.CV_DIST_L2, 0, 0.01, 0.01)
    lefty = int((-x * vy / vx) + y)
    righty = int(((cols - 1 - x) * vy / vx) + y)
    #cv2.line(cimg, (cols - 1, righty), (0, lefty), (0, 255, 0), 2)

    #parallel line
    mp = -vx/vy
    leftx = 0
    rightx = cols-1
    lefty = ((leftx-ccenter[0] * mp) + ccenter[1])
    righty = (((righty - ccenter[0]) * mp) + ccenter[1])
    if lefty >= rows:
        lefty=rows-1
        leftx = (lefty-ccenter[1])/mp + ccenter[0]
    elif lefty < 0:
        lefty = 0
        leftx = (lefty-ccenter[1])/mp + ccenter[0]

    if righty >= rows:
        righty=rows-1
        rightx = (righty-ccenter[1])/mp + ccenter[0]
    elif righty < 0:
        righty = 0
        rightx = (righty-ccenter[1])/mp + ccenter[0]

    print (lefty, righty)

#    cv2.line(cimg, (rightx, righty), (leftx, lefty), (0, 255, 0), 2)

    mask1 = np.zeros((rows, cols))
    mask2 = np.zeros((rows, cols))
    mask3 = np.zeros((rows, cols))
    cv2.drawContours(mask1, contours, contourIdx, 1, thickness=cv.CV_FILLED)
    cv2.line(mask2, (rightx, righty), (leftx, lefty), 1, 1)
    np.logical_and(mask1, mask2, mask3)
    thickness = np.sum(mask3)
    print thickness
    #cv2.imshow('test', mask3)
    #cv2.waitKey(0)

    #Contour bound rectangle
    rect = cv2.minAreaRect(contours[contourIdx])
    print rect
    box = cv2.cv.BoxPoints(rect)
    print box
    box2 = np.int0(box)
#    cv2.drawContours(cimg, [box2], 0, (0, 0, 255), 2)

    smallest = 999999.0
    biggest = -1.0
    for cord1 in box:
        for cord2 in box:
            if cord1 == cord2:
                continue
            dist = np.linalg.norm([cord1[0] - cord2[0], cord1[1] - cord2[1]])
            if dist < smallest:
                smallest = dist
            if dist > biggest:
                biggest = dist


    #cv2.circle(cimg, (int(circ[0]), int(circ[1])), int(R_2), (0, 0, 255), 2)
    #cv2.circle(cimg, (-26600, 600), 27000, (0, 0, 255), 2)
    #TODO: Draw circle array of x,y coordinates that represent the image
    # for each pixel find distance between the coordinate and circ
    #
    for x in xrange(cimg.shape[1]):
        for y in xrange(cimg.shape[0]):
            delta = abs(np.linalg.norm([x - circ[0], y - circ[1]]) - R_2)
            if delta < 2.5:
                cimg[y][x] = [0, 0, 255]



    arcsecs_per_pixel = 3.92
    A = (smallest - thickness)*arcsecs_per_pixel

    lengthasec = rad_to_arcsec(calc_time_theta(exposure_time))
    actuallengthasec = biggest*arcsecs_per_pixel
    linearerror = 60.0*(actuallengthasec-lengthasec)/exposure_time

    text = ""
    text += "Assuming %f\"/px\n" % (arcsecs_per_pixel,)
    text += "Exposure time: %fs\n" % (exposure_time,)
    text += "Line Thickness %fpx\n" % (thickness,)
    text += "Periodic Pk-Pk Amplitude %f\"\n" % (A,)
    text += "Arc length: %f\"\n" % (biggest*arcsecs_per_pixel)
    text += "Expected Arc Length: %f\"\n" % (lengthasec,)
    text += "Arc Length error per minute: %f\"/min\n" % (linearerror,)
    print text

    font = cv2.FONT_HERSHEY_SIMPLEX
    y0, dy = 50, 40
    for i, line in enumerate(text.split('\n')):
        y = y0 + i*dy
        #cv2.putText(cimg, line, (50, y), font, 1.2, (0, 255, 0), 2)

    cv2.imwrite(name+".analyzed"+ext, cimg)
    csvfilename = os.path.join(os.path.dirname(filename), "sst_astar.csv")
    csvexists = False
    if os.path.isfile(csvfilename):
        csvexists = True

    with open(csvfilename, 'ab') as f:
        if not csvexists:
            print >> f, "\"filename\",\"Exposure(s)\",\"Line Thickness(px)\",\"Pk-Pk Error\",\"arc length\",\"expected arclength\", \"linear error\""
        print >> f, "\"%s\",%f,%f,%f,%f,%f,%f" % (os.path.basename(filename), exposure_time, thickness, A, biggest*arcsecs_per_pixel, lengthasec, linearerror)

    cv2.imshow('test', cimg)
    cv2.waitKey(0)

