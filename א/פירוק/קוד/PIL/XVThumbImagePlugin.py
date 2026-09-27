# Source Generated with Decompyle++
# File: XVThumbImagePlugin.pyc (Python 3.14)

from __future__ import annotations
from . import Image, ImageFile, ImagePalette
from ._binary import o8
_MAGIC = b'P7 332'
PALETTE = b''
for r in range(8):
    for g in range(8):
        for b in range(4):
            PALETTE = PALETTE + o8(r * 255 // 7) + o8(g * 255 // 7) + o8(b * 255 // 3)

def _accept(prefix):
    return prefix.startswith(_MAGIC)


class XVThumbImageFile(ImageFile.ImageFile):
    format = 'XVThumb'
    format_description = 'XV thumbnail image'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        if not _accept(self.fp.read(6)):
            msg = 'not an XV thumbnail file'
            raise SyntaxError(msg)
        self.fp.readline()
        s = self.fp.readline()
        if not s:
            msg = 'Unexpected EOF reading XV thumbnail file'
            raise SyntaxError(msg)
        if not s[0] != 35:
            pass
        w, h = s.strip().split(maxsplit = 2)[slice(None, 2, None)]
        self._mode = 'P'
        self._size = (int(w), int(h))
        self.palette = ImagePalette.raw('RGB', PALETTE)
        self.tile = [
            ImageFile._Tile('raw', (0, 0) + self.size, self.fp.tell(), self.mode)]


Image.register_open(XVThumbImageFile.format, XVThumbImageFile, _accept)
