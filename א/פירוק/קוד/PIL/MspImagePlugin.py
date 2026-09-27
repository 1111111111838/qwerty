# Source Generated with Decompyle++
# File: MspImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import io
import struct
from typing import IO
from . import Image, ImageFile
from ._binary import i16le as i16
from ._binary import o16le as o16

def _accept(prefix):
    b'''DanM'''
    return prefix.startswith((b'DanM', b'LinS'))


class MspImageFile(ImageFile.ImageFile):
    format = 'MSP'
    format_description = 'Windows Paint'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        s = self.fp.read(32)
        if not _accept(s):
            msg = 'not an MSP file'
            raise SyntaxError(msg)
        checksum = 0
        for i in range(0, 32, 2):
            checksum = checksum ^ i16(s, i)
        if checksum != 0:
            msg = 'bad MSP checksum'
            raise SyntaxError(msg)
        self._mode = '1'
        self._size = (i16(s, 4), i16(s, 6))
        if s.startswith(b'DanM'):
            self.tile = [
                ImageFile._Tile('raw', (0, 0) + self.size, 32, '1')]
            return None
        self.tile = [
            ImageFile._Tile('MSP', (0, 0) + self.size, 32)]



class MspDecoder(ImageFile.PyDecoder):
    _pulls_fd = True
    
    def decode(self, buffer):
        if self.fd is None:
            raise AssertionError
        img = io.BytesIO()
        blank_line = bytearray((255,) * ((self.state.xsize + 7) // 8))
        
        try:
            self.fd.seek(32)
            rowmap = struct.unpack_from(f'''<{self.state.ysize}H''', self.fd.read(self.state.ysize * 2))
        except struct.error as e:
            msg = 'Truncated MSP file in row map'
            raise OSError(msg) from e

        for x, rowlen in enumerate(rowmap):
            
            try:
                while rowlen == 0:
                    img.write(blank_line)
                row = self.fd.read(rowlen)
                if len(row) != rowlen:
                    msg = f'''Truncated MSP file, expected {rowlen} bytes on row {x}'''
                    raise OSError(msg)
                idx = 0
                while idx < rowlen:
                    runtype = row[idx]
                    idx += 1
                    if runtype == 0:
                        runcount, runval = struct.unpack_from('Bc', row, idx)
                        img.write(runval * runcount)
                        idx += 2
                        continue
                    runcount = runtype
                    img.write(row[idx:idx + runcount])
                    idx += runcount
            except struct.error as e:
                msg = f'''Corrupted MSP file in row {x}'''
                raise OSError(msg) from e

        self.set_as_raw(img.getvalue(), '1')
        return (-1, 0)


Image.register_decoder('MSP', MspDecoder)

def _save(im, fp, filename):
    '''1'''
    if im.mode != '1':
        msg = f'''cannot write mode {im.mode} as MSP'''
        raise OSError(msg)
    header = [
        0] * 16
    header[0] = i16(b'Da')
    header[1] = i16(b'nM')
    (header[2], header[3]) = im.size
    header[4] = 1
    header[5] = 1
    header[6] = 1
    header[7] = 1
    (header[8], header[9]) = im.size
    checksum = 0
    for h in header:
        checksum = checksum ^ h
    header[12] = checksum
    for h in header:
        fp.write(o16(h))
    ImageFile._save(im, fp, [
        ImageFile._Tile('raw', (0, 0) + im.size, 32, '1')])

Image.register_open(MspImageFile.format, MspImageFile, _accept)
Image.register_save(MspImageFile.format, _save)
Image.register_extension(MspImageFile.format, '.msp')
