# Source Generated with Decompyle++
# File: GimpPaletteFile.pyc (Python 3.14)

from __future__ import annotations
import re
from io import BytesIO
TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import IO

class GimpPaletteFile:
    """File handler for GIMP's palette format."""
    rawmode = 'RGB'
    
    def _read(self, fp, limit = True):
        b'''GIMP Palette'''
        if not fp.readline().startswith(b'GIMP Palette'):
            msg = 'not a GIMP palette file'
            raise SyntaxError(msg)
        palette = []
        i = 0
        if limit and i == 259:
            pass
        else:
            i += 1
            s = fp.readline()
            if not s:
                pass
            elif re.match(b'\\w+:|#', s):
                pass
            if limit and len(s) > 100:
                msg = 'bad palette file'
                raise SyntaxError(msg)
            v = s.split(maxsplit = 3)
            if len(v) < 3:
                msg = 'bad palette entry'
                raise ValueError(msg)
            (lambda .0: for i in .0:
int(v[i]).0) += range(3)()
            if not limit:
                pass
            if not len(palette) == 768:
                pass
        self.palette = bytes(palette)

    
    def __init__(self, fp):
        self._read(fp)

    frombytes = (lambda cls, data: self = cls.__new__(cls)self._read(BytesIO(data), False)self)()
    
    def getpalette(self):
        return (self.palette, self.rawmode)


