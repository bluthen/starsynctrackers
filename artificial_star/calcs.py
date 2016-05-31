import math

def rad_to_arcsec(rad):
    return rad*(180.0/(math.pi))*60.0*60.0

def calc_time_theta(t):
    t_sr = t*1.0027379
    theta = 0.25 * math.pi * t_sr / 10800.0
    return theta

exposure_time = 913.0
asec = rad_to_arcsec(calc_time_theta(exposure_time))
print asec
linepxs=3448.0
arcsperpx=3.92
actual = linepxs*arcsperpx
period_pxs=364.0
amp_pxs=27.0

period = period_pxs/(linepxs/exposure_time)
amp = amp_pxs * arcsperpx

print "Expected: %f " % (asec,)
print "Actual: %f" % (actual,)
print "Error \"/m: %f " % (60*(actual-asec)/exposure_time,)
print "Periodic error: "
print "Period: %f s" % (period,)
print "Amplitude: %f \"" % (amp,)
