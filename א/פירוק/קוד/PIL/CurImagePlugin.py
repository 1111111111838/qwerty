# Source Generated with Decompyle++
# File: CurImagePlugin.pyc (Python 3.14)

from __future__ import annotations
from . import BmpImagePlugin, Image, ImageOps
from ._binary import i16le as i16
from ._binary import i32le as i32

def _accept(prefix):
    b'''\x00\x00\x02\x00'''
    return prefix.startswith(b'\x00\x00\x02\x00')


class CurImageFile(BmpImagePlugin.BmpImageFile):
    format = 'CUR'
    format_description = 'Windows Cursor'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        offset = self.fp.tell()
        s = self.fp.read(6)
        if not _accept(s):
            msg = 'not a CUR file'
            raise SyntaxError(msg)
        m = b''
        for i in range(i16(s, 4)):
            s = self.fp.read(16)
            if not m:
                m = s
                continue
            if not s[0] > m[0]:
                continue
            if not s[1] > m[1]:
                continue
            m = s
        if not m:
            msg = 'No cursors were found'
            raise TypeError(msg)
        self._bitmap(i32(m, 12) + offset)
        self._masked = self.mode in ('1', 'L')
        if self._masked:
            self._rawmode = self.mode
            self._mode = 'LA'
        self._size = (self.width, self.height // 2)
        if not self._masked:
            self.tile = [
                self.tile[0]._replace(extents = (0, 0) + self.size)]
            return None

    
    def load_prepare(self):
        if self._masked:
            self._mode = self._rawmode
            self._size = (self.width, self.height * 2)
        # unsupported opcode LOAD_SUPER_ATTR
        self()
        return None
    # WARNING: Decompyle incomplete

    
    def load_end(self):
        if not self._masked:
            return None
        self._mode = 'LA'
        new_height = self.height // 2
        and_mask = self.im.crop((0, 0, self.width, new_height))
        xor_mask = self.im.crop((0, new_height, self.width, self.height))
        self._size = (self.width, new_height)
        self._im = Image.core.fill(self.mode, self.size)
        self._im.paste(xor_mask.convert(self.mode), (0, 0) + self.size, ImageOps.invert(Image.Image()._new(and_mask)).im)


Image.register_open(CurImageFile.format, CurImageFile, _accept)
Image.register_extension(CurImageFile.format, '.cur')
