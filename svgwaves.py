#!/usr/bin/env python3
import re
import sys
import argparse

from decimal import Decimal

import numpy as np
import scipy.misc


# http://stackoverflow.com/a/12644499/1570972
def bernstein_poly(i, n, t):
    """
     The Bernstein polynomial of n, i as a function of t
    """

    # Note that i and (n-i) are swapped when compared to the SO post
    return scipy.misc.comb(n, i) * (t**i) * (1 - t)**(n-i)


def bezier_curve(points, nTimes=1000):
    """
       Given a set of control points, return the
       bezier curve defined by the control points.

       points should be a list of lists, or list of tuples
       such as [ [1,1],
                 [2,3],
                 [4,5], ..[Xn, Yn] ]
        nTimes is the number of time steps, defaults to 1000

        See http://processingjs.nihongoresources.com/bezierinfo/
    """

    nPoints = len(points)
    xPoints = np.array([p[0] for p in points])
    yPoints = np.array([p[1] for p in points])

    # print("Evaluate bezier from %s,%s to %s,%s" %
    #       (xPoints[0], yPoints[0], xPoints[-1], yPoints[-1]))

    t = np.linspace(0.0, 1.0, nTimes)

    polynomial_array = np.array(
        [bernstein_poly(i, nPoints-1, t) for i in range(0, nPoints)])

    xvals = np.dot(xPoints, polynomial_array)
    yvals = np.dot(yPoints, polynomial_array)

    return xvals, yvals


# http://stackoverflow.com/a/8405756/1570972
def bezier(points, t):
    x1, y1 = points[0]
    x2, y2 = points[1]
    x3, y3 = points[2]
    x4, y4 = points[3]

    x12 = (x2-x1)*t+x1
    y12 = (y2-y1)*t+y1

    x23 = (x3-x2)*t+x2
    y23 = (y3-y2)*t+y2

    x34 = (x4-x3)*t+x3
    y34 = (y4-y3)*t+y3

    x123 = (x23-x12)*t+x12
    y123 = (y23-y12)*t+y12

    x234 = (x34-x23)*t+x23
    y234 = (y34-y23)*t+y23

    x1234 = (x234-x123)*t+x123
    y1234 = (y234-y123)*t+y123

    return [(x1, y1), (x12, y12), (x123, y123), (x1234, y1234)]


class Artist(object):
    def __init__(self):
        self.x = self.y = None

    def move_to(self, x, y):
        if x != self.x or y != self.y:
            print('%g %g m' % (x, y))
            self.x = x
            self.y = y

    def line_to(self, x, y):
        if x != self.x or y != self.y:
            print('%g %g l' % (x, y))
            self.x = x
            self.y = y

    def spline_to(self, xc, yc, x, y):
        print('%g %g\n%g %g s' % (xc, yc, x, y))
        self.x = x
        self.y = y

    def spline_wave_to(self, x, y):
        dx = x - self.x
        xc = self.x + dx / 2
        yc = self.y - dx / 2
        self.spline_to(xc, yc, x, self.y)
        self.line_to(x, y)

    def curve_to(self, x1, y1, x2, y2, x3, y3):
        print('%g %g %g %g %g %g c' % (x1, y1, x2, y2, x3, y3))
        self.x = x3
        self.y = y3

    def partial_curve_to(self, x1, y1, x2, y2, x3, y3, xcut):
        points = [(float(self.x), float(self.y)), (float(x1), float(y1)),
                  (float(x2), float(y2)), (float(x3), float(y3))]
        nTimes = 1000
        xs, ys = bezier_curve(points, nTimes)
        t = next(t for t, x in enumerate(xs) if x >= xcut)
        partial_points = bezier(points, t / (nTimes - 1))
        (x12, y12), (x123, y123), (x1234, y1234) = partial_points[1:]
        self.curve_to(x12, y12, x123, y123, Decimal(x1234), Decimal(y1234))

    def curve_wave_to(self, x, y):
        dx = x - self.x
        x0 = self.x + dx / 12
        y0 = self.y - dx / 12
        x1 = self.x + dx / 6
        y1 = self.y - dx / 6
        x2 = self.x + dx / 3
        y2 = self.y - dx / 3
        x3 = self.x + dx / 2
        y3 = y2
        self.line_to(x0, y0)
        self.curve_to(x1, y1, x2, y2, x3, y3)
        x1 = self.x + dx / 6
        y1 = self.y
        x2 = self.x + dx / 3
        y2 = self.y + dx / 6
        x3 = self.x + 5 * dx / 12
        y3 = self.y + dx / 4
        self.curve_to(x1, y1, x2, y2, x3, y3)
        self.line_to(self.x + dx / 12, self.y + dx / 12)

    def partial_curve_wave_to(self, x, xcut, y):
        dx = x - self.x
        x0 = self.x + dx / 12
        y0 = self.y - dx / 12
        if xcut < x0:
            # print('partial_curve_wave_to: partial first line',
            #       file=sys.stderr)
            self.line_to(xcut, self.y - (xcut - self.x))
            return
        x1 = self.x + dx / 6
        y1 = self.y - dx / 6
        x2 = self.x + dx / 3
        y2 = self.y - dx / 3
        x3 = self.x + dx / 2
        y3 = y2
        self.line_to(x0, y0)
        if xcut <= x0:
            # print('partial_curve_wave_to: complete first line',
            #       file=sys.stderr)
            return
        if xcut < x3:
            # print('partial_curve_wave_to: partial first curve %s/%s/%s' %
            #       (self.x, xcut, x3),
            #       file=sys.stderr)
            self.partial_curve_to(x1, y1, x2, y2, x3, y3, xcut)
            return
        self.curve_to(x1, y1, x2, y2, x3, y3)
        if xcut <= x3:
            # print('partial_curve_wave_to: complete first curve',
            #       file=sys.stderr)
            return
        x1 = self.x + dx / 6
        y1 = self.y
        x2 = self.x + dx / 3
        y2 = self.y + dx / 6
        x3 = self.x + 5 * dx / 12
        y3 = self.y + dx / 4
        if xcut < x3:
            # print('partial_curve_wave_to: partial second curve',
            #       file=sys.stderr)
            self.partial_curve_to(x1, y1, x2, y2, x3, y3, xcut)
            return
        self.curve_to(x1, y1, x2, y2, x3, y3)
        if xcut <= x3:
            # print('partial_curve_wave_to: complete second curve',
            #       file=sys.stderr)
            return
        if xcut < self.x + dx / 12:
            # print('partial_curve_wave_to: partial second line',
            #       file=sys.stderr)
            self.line_to(xcut, self.y + (xcut - self.x))
            return
        self.line_to(self.x + dx / 12, self.y + dx / 12)

    def spline_waves_to(self, x, y, dx):
        while self.x < x:
            self.spline_wave_to(self.x + dx, self.y)
        self.line_to(x, y)

    def curve_waves_to(self, x, y, dx):
        while self.x + dx <= x:
            self.curve_wave_to(self.x + dx, self.y)
        if self.x < x:
            self.partial_curve_wave_to(self.x + dx, x, self.y)
        self.line_to(x, y)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--scale', type=Decimal, default=Decimal('2'))
    parser.add_argument('-p', '--use-splines', action='store_true')
    parser.add_argument('-t', '--test', action='store_true')
    args = parser.parse_args()

    if args.test:
        x1 = 0
        y1 = args.scale
        x2 = args.scale * 27 / 20
        y2 = args.scale
        m1 = 'm'
    else:
        s = sys.stdin.read()
        o = re.fullmatch(
            r'(?P<x1>\d+\.?\d*) (?P<y1>\d+\.?\d*) (?P<m1>[ml])\n' +
            r'(?P<x2>\d+\.?\d*) (?P<y2>\d+\.?\d*) l\n',
            s)
        if o is None:
            sys.stdout.write(s)
            raise SystemExit("Unrecognized input")
        x1 = Decimal(o.group('x1'))
        y1 = Decimal(o.group('y1'))
        x2 = Decimal(o.group('x2'))
        y2 = Decimal(o.group('y2'))
        m1 = o.group('m1')

    a = Artist()
    if m1 == 'm':
        a.move_to(x1, y1)
    else:
        a.line_to(x1, y1)
    if args.use_splines:
        a.spline_waves_to(x2, y2, args.scale)
    else:
        a.curve_waves_to(x2, y2, args.scale)


if __name__ == "__main__":
    main()
