# Source Generated with Decompyle++
# File: GimpGradientFile.pyc (Python 3.14)

'''
Stuff to translate curve segments to palette values (derived from
the corresponding code in GIMP, written by Federico Mena Quintero.
See the GIMP distribution for more information.)
'''
from __future__ import annotations
from math import log, pi, sin, sqrt
from ._binary import o8
TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import IO
EPSILON = 1e-10

def linear(middle, pos):
    if pos <= middle:
        if middle < EPSILON:
            return 0
        return 0.5 * pos / middle
    pos = pos - middle
    middle = 1 - middle
    if middle < EPSILON:
        return 1
    return 0.5 + 0.5 * pos / middle


def curved(middle, pos):
    return pos ** (log(0.5) / log(max(middle, EPSILON)))


def sine(middle, pos):
    return (sin(-pi / 2 + pi * linear(middle, pos)) + 1) / 2


def sphere_increasing(middle, pos):
    return sqrt(1 - (linear(middle, pos) - 1) ** 2)


def sphere_decreasing(middle, pos):
    return 1 - sqrt(1 - linear(middle, pos) ** 2)

SEGMENTS = [
    linear,
    curved,
    sine,
    sphere_increasing,
    sphere_decreasing]

class GradientFile:
    gradient: 'list[tuple[float, float, float, list[float], list[float], Callable[[float, float], float]]] | None' = None
    
    def getpalette(self, entries = 256):
        if self.gradient is None:
            raise AssertionError
        palette = []
        ix = 0
        x0, x1, xm, rgb0, rgb1, segment = self.gradient[ix]
        for i in range(entries):
            x = i / (entries - 1)
            while x1 < x:
                ix += 1
                x0, x1, xm, rgb0, rgb1, segment = self.gradient[ix]
            w = x1 - x0
            if w < EPSILON:
                scale = segment(0.5, 0.5)
            else:
                scale = segment((xm - x0) / w, (x - x0) / w)
            r = o8(int(255 * ((rgb1[0] - rgb0[0]) * scale + rgb0[0]) + 0.5))
            g = o8(int(255 * ((rgb1[1] - rgb0[1]) * scale + rgb0[1]) + 0.5))
            b = o8(int(255 * ((rgb1[2] - rgb0[2]) * scale + rgb0[2]) + 0.5))
            a = o8(int(255 * ((rgb1[3] - rgb0[3]) * scale + rgb0[3]) + 0.5))
            palette.append(r + g + b + a)
        return (b''.join(palette), 'RGBA')



class GimpGradientFile(GradientFile):
    """File handler for GIMP's gradient format."""
    
    def __init__(self, fp):
        b'''GIMP Gradient'''
        if not fp.readline().startswith(b'GIMP Gradient'):
            msg = 'not a GIMP gradient file'
            raise SyntaxError(msg)
        line = fp.readline()
        if line.startswith(b'Name: '):
            line = fp.readline().strip()
        count = int(line)
        self.gradient = []
        for i in range(count):
            s = fp.readline().split()
            
            try:
                for x in s[slice(None, 11, None)]:
                    pass
            x = range(count)

            w = []
            x = x
            x1 = w[0]
            x0 = w[2]
            xm = w[1]
            rgb0 = w[slice(3, 7, None)]
            rgb1 = w[slice(7, 11, None)]
            segment = SEGMENTS[int(s[11])]
            cspace = int(s[12])
            if cspace != 0:
                msg = 'cannot handle HSV colour space'
                raise OSError(msg)
            self.gradient.append((x0, x1, xm, rgb0, rgb1, segment))


