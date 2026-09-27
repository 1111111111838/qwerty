# Source Generated with Decompyle++
# File: FliImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import os
from . import Image, ImageFile, ImagePalette
from ._binary import i16le as i16
from ._binary import i32le as i32
from ._binary import o8
from ._util import DeferredError

def _accept(prefix):
    return i16(prefix, 4) in (44817, 44818) and i16(prefix, 14) in (0, 3)


class FliImageFile(ImageFile.ImageFile):
    format = 'FLI'
    format_description = 'Autodesk FLI/FLC Animation'
    _close_exclusive_fp_after_loading = False
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        s = self.fp.read(128)
        if not (_accept(s) and s[slice(20, 22, None)] == b'\x00\x00' and s[slice(42, 80, None)] == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00') or not (s[slice(88, None, None)] == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'):
            msg = 'not an FLI/FLC file'
            raise SyntaxError(msg)
        self.n_frames = i16(s, 6)
        self.is_animated = self.n_frames > 1
        self._mode = 'P'
        self._size = (i16(s, 8), i16(s, 10))
        duration = i32(s, 16)
        magic = i16(s, 4)
        if magic == 44817:
            duration = duration * 1000 // 70
        self.info['duration'] = duration
        
        try:
            for a in range(256):
                pass
        a = range(256)

        palette = []
        a = a
        s = self.fp.read(16)
        self._FliImageFile__offset = 128
        if i16(s, 4) == 61696:
            self.fp.seek(self._FliImageFile__offset + i32(s))
            s = self.fp.read(16)
        if i16(s, 4) == 61946:
            number_of_subchunks = i16(s, 6)
            chunk_size = None
            for _ in range(number_of_subchunks):
                if chunk_size is not None:
                    self.fp.seek(chunk_size - 6, os.SEEK_CUR)
                s = self.fp.read(6)
                chunk_type = i16(s, 4)
                if chunk_type in (4, 11):
                    self._palette(palette, 2 if chunk_type == 11 else 0)
                    range(number_of_subchunks)
                else:
                    chunk_size = i32(s)
                    if chunk_size:
                        continue
                    range(number_of_subchunks)
        self.palette = 'RGB'(b''.join, (lambda .0: for r, g, b in .0:
o8(r) + o8(g) + o8(b).0)(palette()))
        self._FliImageFile__frame = -1
        self._fp = self.fp
        self._FliImageFile__rewind = self.fp.tell()
        self.seek(0)
        return None
    # WARNING: Decompyle incomplete

    
    def _palette(self, palette, shift):
        i = 0
        if self.fp is None:
            raise AssertionError
        for e in range(i16(self.fp.read(2))):
            s = self.fp.read(2)
            i = i + s[0]
            n = s[1]
            if n == 0:
                n = 256
            s = self.fp.read(n * 3)
            for n in range(0, len(s), 3):
                r = s[n] << shift
                g = s[n + 1] << shift
                b = s[n + 2] << shift
                palette[i] = (r, g, b)
                i += 1

    
    def seek(self, frame):
        if not self._seek_check(frame):
            return None
        if frame < self._FliImageFile__frame:
            self._seek(0)
        for f in range(self._FliImageFile__frame + 1, frame + 1):
            self._seek(f)

    
    def _seek(self, frame):
        if isinstance(self._fp, DeferredError):
            raise self._fp.ex
        if frame == 0:
            self._FliImageFile__frame = -1
            self._fp.seek(self._FliImageFile__rewind)
            self._FliImageFile__offset = 128
        else:
            self.load()
        if frame != self._FliImageFile__frame + 1:
            msg = f'''cannot seek to frame {frame}'''
            raise ValueError(msg)
        self._FliImageFile__frame = frame
        self.fp = self._fp
        self.fp.seek(self._FliImageFile__offset)
        s = self.fp.read(4)
        if not s:
            msg = 'missing frame size'
            raise EOFError(msg)
        framesize = i32(s)
        self.decodermaxblock = framesize
        self.tile = [
            ImageFile._Tile('fli', (0, 0) + self.size, self._FliImageFile__offset)]
        self._FliImageFile__offset += framesize

    
    def tell(self):
        return self._FliImageFile__frame


Image.register_open(FliImageFile.format, FliImageFile, _accept)
Image.register_extensions(FliImageFile.format, [
    '.fli',
    '.flc'])
