# Source Generated with Decompyle++
# File: ImtImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import re
from . import Image, ImageFile
field = re.compile(b'([a-z]*) ([^ \\r\\n]*)')

class ImtImageFile(ImageFile.ImageFile):
    format = 'IMT'
    format_description = 'IM Tools'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        buffer = self.fp.read(100)
        if b'\n' not in buffer:
            msg = 'not an IM file'
            raise SyntaxError(msg)
        xsize = 0
        ysize = 0
        if buffer:
            s = buffer[slice(None, 1, None)]
            buffer = buffer[slice(1, None, None)]
        else:
            s = self.fp.read(1)
        if not s:
            return None
        if s == b'\x0c':
            self.tile = [
                ImageFile._Tile('raw', (0, 0) + self.size, self.fp.tell() - len(buffer), self.mode)]
            return None
        if b'\n' not in buffer:
            buffer += self.fp.read(100)
        lines = buffer.split(b'\n')
        s += lines.pop(0)
        buffer = b'\n'.join(lines)
        if len(s) == 1 or len(s) > 100:
            return None
        if s[0] == ord(b'*'):
            pass
        m = field.match(s)
        if not m:
            return None
        k, v = m.group(1, 2)
        if k == b'width':
            xsize = int(v)
            self._size = (xsize, ysize)
        if k == b'height':
            ysize = int(v)
            self._size = (xsize, ysize)
        if not k == b'pixel':
            pass
        if not v == b'n8':
            pass
        self._mode = 'L'


Image.register_open(ImtImageFile.format, ImtImageFile)
