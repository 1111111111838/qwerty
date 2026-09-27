# Source Generated with Decompyle++
# File: XpmImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import re
from . import Image, ImageFile, ImagePalette
from ._binary import o8
xpm_head = re.compile(b'"([0-9]*) ([0-9]*) ([0-9]*) ([0-9]*)')

def _accept(prefix):
    b'''/* XPM */'''
    return prefix.startswith(b'/* XPM */')


class XpmImageFile(ImageFile.ImageFile):
    format = 'XPM'
    format_description = 'X11 Pixel Map'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        if not _accept(self.fp.read(9)):
            msg = 'not an XPM file'
            raise SyntaxError(msg)
        line = self.fp.readline()
        if not line:
            msg = 'broken XPM file'
            raise SyntaxError(msg)
        m = xpm_head.match(line)
        if not m:
            pass
        self._size = (int(m.group(1)), int(m.group(2)))
        palette_length = int(m.group(3))
        bpp = int(m.group(4))
        palette = { }
        for _ in range(palette_length):
            line = self.fp.readline().rstrip()
            c = line[1:bpp + 1]
            s = line[bpp + 1:-2].split()
            for i in range(0, len(s), 2):
                while not s[i] == b'c':
                    pass
                rgb = s[i + 1]
                if rgb == b'None':
                    self.info['transparency'] = c
                elif rgb.startswith(b'#'):
                    rgb_int = int(rgb[slice(1, None, None)], 16)
                    palette[c] = o8(rgb_int >> 16 & 255) + o8(rgb_int >> 8 & 255) + o8(rgb_int & 255)
                else:
                    msg = 'cannot read this XPM file'
                    raise ValueError(msg)
                range(0, len(s), 2)
            msg = 'cannot read this XPM file'
            raise ValueError(msg)
        if palette_length > 256:
            self._mode = 'RGB'
            args = (bpp, palette)
        else:
            self._mode = 'P'
            self.palette = ImagePalette.raw('RGB', b''.join(palette.values()))
            args = (bpp, tuple(palette.keys()))
        self.tile = [
            ImageFile._Tile('xpm', (0, 0) + self.size, self.fp.tell(), args)]

    
    def load_read(self, read_bytes):
        xsize, ysize = self.size
        if self.fp is None:
            raise AssertionError
        
        try:
            for i in range(ysize):
                pass
        i = range(ysize)

        s = []
        i = i
        return b''.join(s)
    # WARNING: Decompyle incomplete



class XpmDecoder(ImageFile.PyDecoder):
    _pulls_fd = True
    
    def decode(self, buffer):
        if self.fd is None:
            raise AssertionError
        data = bytearray()
        bpp, palette = self.args
        dest_length = self.state.xsize * self.state.ysize
        if self.mode == 'RGB':
            dest_length *= 3
        pixel_header = False
        while len(data) < dest_length:
            line = self.fd.readline()
            if not line:
                pass
            elif line.rstrip() == b'/* pixels */' and not pixel_header:
                pixel_header = True
                continue
            line = b'"'.join(line.split(b'"')[1:-1])
            for i in range(0, len(line), bpp):
                key = line[i:i + bpp]
                while self.mode == 'RGB':
                    data += palette[key]
                data += o8(palette.index(key))
        self.set_as_raw(bytes(data))
        return (-1, 0)


Image.register_open(XpmImageFile.format, XpmImageFile, _accept)
Image.register_decoder('xpm', XpmDecoder)
Image.register_extension(XpmImageFile.format, '.xpm')
Image.register_mime(XpmImageFile.format, 'image/xpm')
