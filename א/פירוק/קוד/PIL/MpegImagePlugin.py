# Source Generated with Decompyle++
# File: MpegImagePlugin.pyc (Python 3.14)

from __future__ import annotations
from . import Image, ImageFile
from ._binary import i8
from ._typing import SupportsRead

class BitStream:
    
    def __init__(self, fp):
        self.fp = fp
        self.bits = 0
        self.bitbuffer = 0

    
    def next(self):
        return i8(self.fp.read(1))

    
    def peek(self, bits):
        while self.bits < bits:
            self.bitbuffer = (self.bitbuffer << 8) + self.next()
            self.bits += 8
        return self.bitbuffer >> self.bits - bits & (1 << bits) - 1

    
    def skip(self, bits):
        while self.bits < bits:
            self.bitbuffer = (self.bitbuffer << 8) + i8(self.fp.read(1))
            self.bits += 8
        self.bits = self.bits - bits

    
    def read(self, bits):
        v = self.peek(bits)
        self.bits = self.bits - bits
        return v



def _accept(prefix):
    b'''\x00\x00\x01\xb3'''
    return prefix.startswith(b'\x00\x00\x01\xb3')


class MpegImageFile(ImageFile.ImageFile):
    format = 'MPEG'
    format_description = 'MPEG'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        s = BitStream(self.fp)
        if s.read(32) != 435:
            msg = 'not an MPEG file'
            raise SyntaxError(msg)
        self._mode = 'RGB'
        self._size = (s.read(12), s.read(12))


Image.register_open(MpegImageFile.format, MpegImageFile, _accept)
Image.register_extensions(MpegImageFile.format, [
    '.mpg',
    '.mpeg'])
Image.register_mime(MpegImageFile.format, 'video/mpeg')
