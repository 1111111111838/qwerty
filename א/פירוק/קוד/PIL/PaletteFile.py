# Source Generated with Decompyle++
# File: PaletteFile.pyc (Python 3.14)

from __future__ import annotations
from typing import IO
from ._binary import o8

class PaletteFile:
    '''File handler for Teragon-style palette files.'''
    rawmode = 'RGB'
    
    def __init__(self, fp):
        
        try:
            for i in range(256):
                pass
        i = None
        
        try:
            for x in s.split():
                pass
        x = s.split()


        palette = []
        i = i
        s = fp.readline()
        if not s:
            pass
        elif s.startswith(b'#'):
            pass
        if len(s) > 100:
            msg = 'bad palette file'
            raise SyntaxError(msg)
        
        try:
            for x in s.split():
                pass
        x = s.split()

        v = []
        x = x
        
        try:
            i, r, g, b = v
        except ValueError:
            i, r = v
            g = r
            b = r

        if 0 <= i:
            if not i <= 255:
                pass
        else:
            i
        palette[i] = o8(r) + o8(g) + o8(b)
        self.palette = b''.join(palette)
        return None
    # WARNING: Decompyle incomplete

    
    def getpalette(self):
        return (self.palette, self.rawmode)


