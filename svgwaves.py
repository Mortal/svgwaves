#!/usr/bin/env python3
import re
import sys
import argparse

from decimal import Decimal


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

    def wave_to(self, x, y):
        dx = x - self.x
        xc = self.x + dx / 2
        yc = self.y - dx / 2
        self.spline_to(xc, yc, x, self.y)
        self.line_to(x, y)

    def curve_to(self, x1, y1, x2, y2, x3, y3):
        print('%g %g %g %g %g %g c' % (x1, y1, x2, y2, x3, y3))
        self.x = x3
        self.y = y3

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

    def waves_to(self, x, y, dx):
        while self.x < x:
            self.wave_to(self.x + dx, self.y)
        self.line_to(x, y)

    def curve_waves_to(self, x, y, dx):
        while self.x < x:
            self.curve_wave_to(self.x + dx, self.y)
        self.line_to(x, y)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--scale', type=Decimal, default=Decimal('2'))
    parser.add_argument('-c', '--use-curves', action='store_true')
    args = parser.parse_args()

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
    a = Artist()
    if o.group('m1') == 'm':
        a.move_to(x1, y1)
    else:
        a.line_to(x1, y1)
    if args.use_curves:
        a.curve_waves_to(x2, y2, args.scale)
    else:
        a.waves_to(x2, y2, args.scale)


if __name__ == "__main__":
    main()
