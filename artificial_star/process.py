import cv2
import cv2.cv as cv
import numpy as np
import math
import getopt
import sys
import time
import exifread
import os
import datetime
from scipy import optimize
import getopt

debug = False

# TODO: Make this faster
def draw_circle_2(cimg, origin, radius, color, thickness=2.5):
    """
    Draws circle on image. Supports very large radius, unlike the opencv methods.
    :param cimg: The image to draw on.
    :param origin: Center of the circle
    :param radius: Radius of the circle
    :param color: Color to draw
    :param thickness: Thickness of the line.
    :return:
    """
    found = False
    # Find first x, y
    for x in xrange(cimg.shape[1]):
        for y in xrange(cimg.shape[0]):
            delta = abs(np.linalg.norm([x - origin[0], y - origin[1]]) - radius)
            if delta < thickness/2.0:
                found = True
                break
        if found:
            break
    print "Start %d, %d" % (x, y)
    # Now that we have a start we will go through rest of x, but limit how much y we do.
    for x2 in xrange(x, cimg.shape[1], ):
        y = draw_circle_2a(x2, y, cimg, origin, radius, color, thickness)


def draw_circle_2a(startx, starty, cimg, origin, radius, color, thickness=2.5):
    """
    Subfunction for draw_circle_2, goes through y-axis to draw
    :param startx: X coord to check draw on
    :param starty: Y coord to search to draw on
    :param cimg: Image to draw on
    :param origin: Center of circle
    :param radius: radius of circle
    :param color: color to draw
    :param thickness: thickness of line.
    :return: last y value it drew
    """
    last_good_y = starty
    x = startx
    for y in xrange(int(starty - 1.5 * thickness), int(starty + 1.5 * thickness)):
        delta = abs(np.linalg.norm([x - origin[0], y - origin[1]]) - radius)
        if delta < thickness/2.0:
            last_good_y = y
            cimg[y][x] = color
    return last_good_y


def circ_find_y(startx, maxy, origin, radius, thickness=1.5):
    """
    Find first y it would draw on.
    :param startx: X coord to start with.
    :param maxy: Maximum y to search for.
    :param origin: Center of circle
    :param radius: radius of circle
    :param thickness: thickness of line.
    :return: First y it would draw on.
    """
    x = startx
    for y in xrange(0, maxy):
        delta = abs(np.linalg.norm([x - origin[0], y - origin[1]]) - radius)
        if delta < thickness/2.0:
            return y


def calc_r(contour_t, xc, yc):
    """ calculate the distance of each 2D points from the center (xc, yc) """
    return np.sqrt((contour_t[0]-xc)**2 + (contour_t[1]-yc)**2)


def gen_f2(contour_t):
    """
    Function generator for arc lease squares.
    :param contour_t:
    :return:
    """
    def f2(c):
        """ calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc) """
        r_i = calc_r(contour_t, *c)
        return r_i - r_i.mean()
    return f2


def rad_to_arcsec(rad):
    """
    Radius to arcseconds
    :param rad: Radians
    :return: rad in arcseconds
    """
    return rad*(180.0/math.pi)*60.0*60.0


def calc_time_theta(t):
    """
    Given time t in seconds how much of a arc should have been made.
    :param t: Time in seconds
    :return: Angle in radians
    """
    t_sr = t*1.0027379
    theta = 0.25 * math.pi * t_sr / 10800.0
    return theta


def get_contours(img):
    """
    Get contours bright area in image, find one that is probably from our artificial star.
    :param img: Image tha analyize
    :return: [contours, countours_artificial_star_idx] The contours an index of which one is our artificial star
    """
    mean = np.mean(img)
    stddev = np.std(img)

    ret, thresh = cv2.threshold(img, mean+2*stddev, 255, 0)

    contours, hierarchy = cv2.findContours(thresh, 1, 2)

    # filter contours based on area.
    maxarea = -1
    contour_idx = -1
    for i in xrange(len(contours)):
        cnt = contours[i]
        carea = cv2.contourArea(cnt)
        if carea > maxarea:
            maxarea = carea
            contour_idx = i

    # print cv2.contourArea(contours[contourIdx])
    # cv2.drawContours(cimg, contours, contourIdx, (0, 255, 0), thickness=3)
    # cv2.imshow('test', cimg)
    # cv2.waitKey(0)

    return contours, contour_idx


def get_contour_center(contour):
    """
    Find center of contour.
    :param contour: Contour to find center of.
    :return: Tuple of center of contour.
    """
    # Center of contour
    movement = cv2.moments(contour)
    ccenter = (movement['m10']/movement['m00'], movement['m01']/movement['m00'])
    print ccenter
    return ccenter


def circle_least_squares(contour):
    """
    Does least squares to find circle function from a contour.
    :param contour: The contour to get circle function for.
    :return: (radius, center) The radius and center of the circle
    """
    # http://scipy-cookbook.readthedocs.io/items/Least_Squares_Circle.html

    #If concave
    contour_shape = contour.shape
    contour_r = np.reshape(contour, [contour_shape[0], contour_shape[2]]).T
    center, ier = optimize.leastsq(gen_f2(contour_r), (3888, 3888))
    r_i2 = calc_r(contour_r, center[0], center[1])
    r_2 = np.mean(r_i2)
    r_residu2 = np.sum((r_i2 - r_2)**2.0)

    #If convex
    contour_shape = contour.shape
    contour_r = np.reshape(contour, [contour_shape[0], contour_shape[2]]).T
    center_b, ier = optimize.leastsq(gen_f2(contour_r), (0, 0))
    r_i2 = calc_r(contour_r, center_b[0], center_b[1])
    r_2_b = np.mean(r_i2)
    r_residu2 = np.sum((r_i2 - r_2)**2.0)

    if r_2_b < r_2:
        return r_2_b, center_b
    else:
        return r_2, center


def line_thickness(rows, cols, contours, contour_idx, contour_center):
    """
    Gets the thinkness of the artificial star if using line mode. Uses fit line and perpendicular line.
    :param rows:
    :param cols:
    :param contours:
    :param contour_idx:
    :param contour_center:
    :return:
    """
    # fit line
    mask0 = np.zeros((rows, cols))
    [vx, vy, x, y] = cv2.fitLine(contours[contour_idx], cv.CV_DIST_L2, 0, 0.01, 0.01)
    lefty = int((-x * vy / vx) + y)
    righty = int(((cols - 1 - x) * vy / vx) + y)
    fit_line = ((cols - 1, righty), (0, lefty))
    cv2.line(mask0, (cols - 1, righty), (0, lefty), 1, 2)

    # perpendicular line
    m_perp = -vx/vy
    print "Perp slope: ",
    print m_perp
    b_perp = contour_center[1]-m_perp*contour_center[0]
    leftx = 0
    lefty = m_perp*leftx + b_perp
    if lefty < 0 or lefty > rows-1:
        if lefty < 0:
            lefty = 0
        else:
            lefty = rows-1
        leftx = (lefty-b_perp)/m_perp

    rightx = cols-1
    righty = m_perp*rightx + b_perp
    if righty < 0 or righty > rows-1:
        if righty < 0:
            righty = 0
        else:
            righty = rows-1
        rightx = (righty-b_perp)/m_perp

    leftx = int(leftx)
    lefty = int(lefty)
    rightx = int(rightx)
    righty = int(righty)

    print "Perp line: ",
    print ([leftx, lefty], [rightx, righty])

    cv2.line(mask0, (rightx, righty), (leftx, lefty), 1, 2)

    mask1 = np.zeros((rows, cols))
    mask2 = np.zeros((rows, cols))
    mask3 = np.zeros((rows, cols))
    cv2.drawContours(mask1, contours, contour_idx, 1, thickness=cv.CV_FILLED)
    cv2.line(mask2, (rightx, righty), (leftx, lefty), 1, 1)
    np.logical_and(mask1, mask2, mask3)
    thickness = np.sum(mask3)
    print "Thickness: " + str(thickness)
    #cv2.imshow('test', mask0)
    #cv2.waitKey(0)
    #cv2.imshow('test', mask1)
    #cv2.waitKey(0)
    #cv2.imshow('test', mask2)
    #cv2.waitKey(0)
    #cv2.imshow('test', mask3)
    #cv2.waitKey(0)
    return thickness, fit_line, ((leftx, lefty), (rightx, righty))

def get_contour_box(contour):
    """
    Gets boxed contour.
    :param contour: The contour find box.
    :return: box coords, box coords as integers.
    """
    rect = cv2.minAreaRect(contour)
    print rect
    box = cv2.cv.BoxPoints(rect)
    print box
    box2 = np.int0(box)
    return box, box2

def box_length_width(box):
    """
    Calculates the width and length of the box, length is the longer side.
    :param box: The box used to calulate
    :return: box_width, box_length
    """
    dist1 = np.linalg.norm([box[0][0] - box[1][0], box[0][1] - box[1][1]])
    dist2 = np.linalg.norm([box[1][0] - box[2][0], box[1][1] - box[2][1]])
    if dist1 < dist2:
        return dist1, dist2
    else:
        return dist2, dist1

def circle_arclength(rows, cols, box_int, circ_center, circ_radius, thickness):
    """
    Calculates arclength from circle and artificial star box.
    :param rows: rows in image
    :param cols: Columsn in image
    :param box_int: Box containing contour.
    :return: arclength in radians
    """
    mask_circ_box1 = np.zeros((rows, cols))
    cv2.drawContours(mask_circ_box1, [box_int], 0, 1, 1)
    mask_circ_box2 = np.zeros((rows, cols))
    draw_circle_2(mask_circ_box2, circ_center, circ_radius, 1, thickness=1.5)
    mask_circ_box3 = np.zeros((rows, cols))
    np.logical_and(mask_circ_box1, mask_circ_box2, mask_circ_box3)
    arcindex = np.nonzero(mask_circ_box3)
    # Find points farthest apart in the arcindex
    end_points=[None, None, -1]
    for i in range(len(arcindex[0])):
        point1 = [arcindex[0][i], arcindex[1][i]]
        for j in range(len(arcindex[0])):
            point2 = [arcindex[0][j], arcindex[1][j]]
            dist = np.linalg.norm([point1[0] - point2[0], point1[1] - point2[1]])
            #dist = math.sqrt((point1[0]-point2[0])**2.0 + (point1[1]-point2[1])**2.0)
            if dist > end_points[2]:
                end_points = [point1, point2, dist]
    print "Ends: "+str(end_points)
    # Find arclength https://math.stackexchange.com/questions/830413/calculating-the-arc-length-of-a-circle-segment
    #d = math.sqrt((end_points[0][0] - end_points[1][0])**2.0 + (end_points[0][1] - end_points[1][1])**2.0)
    d = end_points[2]
    arclength = math.acos(1.0 - ((d**2.0)/(2.0*(circ_radius**2.0))))
    arclength_thick = math.acos(1.0 - (thickness**2.0)/(2.0*(circ_radius**2.0)))
    arclength = arclength - arclength_thick
    return arclength, end_points

def arc_period_thickness(rows, cols, contours, contour_idx, circ_center, circ_radius, queue=None):
    mask1 = np.zeros((rows, cols))
    cv2.drawContours(mask1, contours, contour_idx, 1, thickness=cv.CV_FILLED)

    thickness = 1.5
    last_sum = -1
    # TODO: Thickness by bysection
    trange = [1.5, 100]
    while True:
        if last_sum == -1:
            thickness = trange[1]
        else:
            thickness = trange[0]+(trange[1] - trange[0])/2.0
        mask2 = np.zeros((rows, cols))
        mask3 = np.zeros((rows, cols))
        queue.put({'status': 'update', 'message': 'Trying arc-thickness %d...' % (int(thickness),)})
        draw_circle_2(mask2, circ_center, circ_radius, 1, thickness=thickness)
        np.logical_and(mask1, mask2, mask3)

        this_sum = np.sum(mask3)
        print "In arc thick:",
        print thickness, this_sum, last_sum
        #cv2.imshow('test', mask3)
        #cv2.waitKey(0)

        if last_sum == -1:
            pass
        elif this_sum == last_sum:
            trange = [trange[0], thickness]
        else:
            trange = [thickness, trange[1]]
        if last_sum != -1 and abs(trange[0] - trange[1]) < 1:
            return thickness
        last_sum = this_sum

def help(stream):
    print >> stream, "Usage: %s [OPTION]... IMAGE_FILE.JPG" % (sys.argv[0],)
    print >> stream, "  -h, --help                   show this screen"
    print >> stream, "  --arcsecs-per-pixel=value    Use value for \"/pixel [required]"
    print >> stream, "  --tracker-rate=1.0           Overwrite default tracker rate of 1.0"
    print >> stream, "  --exposure-overwrite=seconds Overwrite exposure time than what is in header"
    print >> stream, "  --gui                        Force gui"
    print >> stream
    print >> stream, "  --debug                      Show debugging images"
    print >> stream
    print >> stream, "If any options are missing that is needed to run, it will launch GUI."
    print >> stream
    print >> stream, "Example Usage:"
    print >> stream, "%s --arcseconds-per-pixel=3.92 IMG_4863.JPG" % (sys.argv[0],)
    print >> stream

def parse_args():
    ret = {'arcsecs-per-pixel': 3.92, 'tracker-rate': 1.0, 'exposure-overwrite': None, 'filename': None, 'gui': False, 'debug': False}
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['help', 'arcsecs-per-pixel=', 'tracker-rate=', 'exposure-overwrite=', 'gui', 'debug'])
    except getopt.GetoptError, err:
        print >> sys.stderr, str(err)
        help(sys.stderr)
        sys.exit(1)
    for o, a in opts:
        if o in ('-h', '--help'):
            help(sys.stdout)
            sys.exit(0)
        if o in ('--gui',):
            ret['gui'] = True
        elif o in ('--debug',):
            ret['debug'] = True
        else:
            if o[2:] in ret:
                ret[o[2:]] = float(a)
    if len(args) >= 1:
        print args
        ret['filename'] = args[0]
    return ret

def analyize(args, queue):
    global debug
    if 'debug' in args and args['debug']:
        debug = True
    arcsecs_per_pixel = args['arcsecs-per-pixel']
    tracker_rate = args['tracker-rate']
    filename = args['filename']
    name, ext = os.path.splitext(filename)
    #cimg = cv2.imread(filename)
    img = cv2.imread(filename, 0)
    cimg = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
    if args['exposure-overwrite']:
        print "Using overwrite exposure time."
        exposure_time = args['exposure-overwrite']
    else:
        with open(filename, 'rb') as f:
            tags = exifread.process_file(f)
            exposure_time = float(tags['EXIF ExposureTime'].printable)
            print "EXIF ExposureTime: "+str(exposure_time)

    if debug:
        cv2.namedWindow('test', cv2.WINDOW_NORMAL)
    # cv2.imshow('test', img)
    # cv2.waitKey(0)
    queue.put({'status': 'update', 'message': 'Getting Contours...'})
    img = cv2.GaussianBlur(img, (15,15), 0)
    contours, contour_idx = get_contours(img)

    contour_center = get_contour_center(contours[contour_idx])
    print "Contour Center: "+str(contour_center)

    queue.put({'status': 'update', 'message': 'Doing Circle Least Squares...'})
    circ_radius, circ_center = circle_least_squares(contours[contour_idx])

    print "Circle:", circ_radius, circ_center
    #artificial_dec_old = 90.0 - circ_radius*arcsecs_per_pixel/(60.*60)
    artificial_dec = (180.0/math.pi)*math.acos(circ_radius*arcsecs_per_pixel/(90.0*60.0*60.0))
    arc_mode = False
    if artificial_dec < 0:
        print "Invalid Artificial dec %f degrees, settings to zero dec." % (artificial_dec,)
        artificial_dec = 0
    else:
        arc_mode = True
        print "Artificial Dec: %f" % (artificial_dec,)

    # If dec is zero can use line mode, otherwise do arc mode.
    queue.put({'status': 'update', 'message': 'Doing Line Thickness...'})
    rows, cols = img.shape[:2]
    thickness, fit_line, perp_line = line_thickness(rows, cols, contours, contour_idx, contour_center)
    # TODO: Do arc thickness, perpendicular arch.

    # Bound rectangle is used by both arc and line modes.
    # Contour bound rectangle
    box, box_int = get_contour_box(contours[contour_idx])

    box_width, box_length = box_length_width(box)
    # print box_width, box_length

    # TODO: Draw circle array of x,y coordinates that represent the image
    # Open
    #print "Drawing circle."
    #start_ts = datetime.datetime.now()
    #print "Drawing Circle time = %d" % ((datetime.datetime.now() - start_ts).total_seconds())

    if arc_mode:
        # Arclength
        # TODO: Remove thickness from arclength
        arclength, arclength_endpoints = circle_arclength(rows, cols, box_int, circ_center, circ_radius, thickness)
        # Compression from dec
        #arclength = arclength*(1.0/math.cos(artificial_dec))
        arclength = rad_to_arcsec(arclength)
        periodic_error_thickness = arc_period_thickness(rows, cols, contours, contour_idx, circ_center, circ_radius, queue)
        periodic_error = (periodic_error_thickness-thickness)*arcsecs_per_pixel
    else:
        arclength = (box_length - thickness) * arcsecs_per_pixel
        periodic_error = (box_width - thickness)*arcsecs_per_pixel

    expected_arclength = rad_to_arcsec(calc_time_theta(tracker_rate*exposure_time))
    error_asec_per_min = 60.0*(arclength-expected_arclength)/(tracker_rate*exposure_time)

    if arc_mode:
        draw_circle_2(cimg, circ_center, circ_radius, (255, 128, 0), thickness=periodic_error_thickness)
    cv2.drawContours(cimg, contours, contour_idx, (0, 255, 0), thickness=cv.CV_FILLED)

    cv2.line(cimg, perp_line[0], perp_line[1], (255, 0, 0), 2)
    if arc_mode:
        draw_circle_2(cimg, circ_center, circ_radius, (255, 0, 255), thickness=2.0)
        cv2.circle(cimg, (arclength_endpoints[0][1], arclength_endpoints[0][0]), 5, (255, 0, 255), thickness=-1)
        cv2.circle(cimg, (arclength_endpoints[1][1], arclength_endpoints[1][0]), 5, (255, 0, 255), thickness=-1)
    else:
        cv2.drawContours(cimg, [box_int], 0, (0, 0, 255), 1)
        cv2.line(cimg, fit_line[0], fit_line[1], (255, 0, 0), 2)

    text = ""
    text += "Arcsec/Pixel: %f\"/px\n" % (arcsecs_per_pixel,)
    text += "Artificial Dec: %fdeg\n" % (artificial_dec,)
    text += "Exposure time: %fs\n" % (exposure_time,)
    text += "Tracker Rate: %.4fX\n" % (tracker_rate,)
    text += "Star Thickness %fpx\n" % (thickness,)
    text += "Star Thickness %f\"\n" % (thickness*arcsecs_per_pixel,)
    text += "Periodic Pk-Pk Error %f\"\n" % (periodic_error,)
    text += "Arc length: %f\"\n" % (arclength,)
    text += "Expected Arc Length: %f\"\n" % (expected_arclength,)
    text += "Arc Length error per minute: %f\"/min\n" % (error_asec_per_min,)
    text += "Correction Time Multiplier: %f\n" % (expected_arclength/arclength)
    print text

    font = cv2.FONT_HERSHEY_SIMPLEX
    y0, dy = 50, 40
    for i, line in enumerate(text.split('\n')):
        y = y0 + i*dy
        cv2.putText(cimg, line, (50, y), font, 1.2, (0, 255, 0), 2)

    analyzed = name+".analyzed"+".png"
    cv2.imwrite(analyzed, cimg)
    return analyzed

    #csvfilename = os.path.join(os.path.dirname(filename), "sst_astar.csv")
    # csvexists = False
    #if os.path.isfile(csvfilename):
    #    csvexists = True

    #TODO: Fix this.
    #with open(csvfilename, 'ab') as f:
    #    if not csvexists:
    #        print >> f, "\"filename\",\"Exposure(s)\",\"Line Thickness(px)\",\"Pk-Pk Error\",\"arc length\",\"expected arclength\", \"linear error\""
    #    print >> f, "\"%s\",%f,%f,%f,%f,%f,%f" % (os.path.basename(filename), exposure_time, thickness, A, biggest*arcsecs_per_pixel, lengthasec, linearerror)

    #cv2.imshow('test', cimg)
    #cv2.waitKey(0)


class DummyQueue():
    def put(self, item, block=False, timeout=-1):
        if 'status' in item and item['status'] == 'update':
            print item


def main():
    args = parse_args()
    #Do we have what we need to not need the gui?
    if args['gui'] or (not args['filename'] or not args['arcsecs-per-pixel']):
        import process_gui
        process_gui.show(args)
    else:
        queue = DummyQueue()
        fn = analyize(args, queue)
        print "Wrote: %s" % (fn,)


if __name__ == "__main__":
    main()
