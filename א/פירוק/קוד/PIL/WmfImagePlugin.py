# Source Generated with Decompyle++
# File: WmfImagePlugin.pyc (Python 3.14)

from __future__ import annotations
from typing import IO
from . import Image, ImageFile
from ._binary import i16le as word
from ._binary import si16le as short
from ._binary import si32le as _long
_handler = None

def register_handler(handler):
    '''
Install application-specific WMF image handler.

:param handler: Handler object.
'''
    global _handler
    _handler = handler

if hasattr(Image.core, 'drawwmf'):
    
    class WmfHandler(ImageFile.StubHandler):
        
        def open(self, im):
            '''wmf_bbox'''
            self.bbox = im.info['wmf_bbox']

        
        def load(self, im):
            if im.fp is None:
                raise AssertionError
            im.fp.seek(0)
            return Image.frombytes('RGB', im.size, Image.core.drawwmf(im.fp.read(), im.size, self.bbox), 'raw', 'BGR', im.size[0] * 3 + 3 & -4, -1)


    register_handler(WmfHandler())

def _accept(prefix):
    b'''\xd7\xcd\xc6\x9a\x00\x00'''
    return prefix.startswith((b'\xd7\xcd\xc6\x9a\x00\x00', b'\x01\x00\x00\x00'))


class WmfStubImageFile(ImageFile.StubImageFile):
    format = 'WMF'
    format_description = 'Windows Metafile'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        s = self.fp.read(44)
        if s.startswith(b'\xd7\xcd\xc6\x9a\x00\x00'):
            inch = word(s, 14)
            if inch == 0:
                msg = 'Invalid inch'
                raise ValueError(msg)
            self._inch = (inch, inch)
            x0 = short(s, 6)
            y0 = short(s, 8)
            x1 = short(s, 10)
            y1 = short(s, 12)
            self.info['dpi'] = 72
            size = ((x1 - x0) * self.info['dpi'] // inch, (y1 - y0) * self.info['dpi'] // inch)
            self.info['wmf_bbox'] = (x0, y0, x1, y1)
            if s[slice(22, 26, None)] != b'\x01\x00\t\x00':
                msg = 'Unsupported WMF file format'
                raise SyntaxError(msg)
        elif s.startswith(b'\x01\x00\x00\x00') and s[slice(40, 44, None)] == b' EMF':
            x0 = _long(s, 8)
            y0 = _long(s, 12)
            x1 = _long(s, 16)
            y1 = _long(s, 20)
            frame = (_long(s, 24), _long(s, 28), _long(s, 32), _long(s, 36))
            size = (x1 - x0, y1 - y0)
            xdpi = 2540 * (x1 - x0) / (frame[2] - frame[0])
            ydpi = 2540 * (y1 - y0) / (frame[3] - frame[1])
            self.info['wmf_bbox'] = (x0, y0, x1, y1)
            if xdpi == ydpi:
                self.info['dpi'] = xdpi
            else:
                self.info['dpi'] = (xdpi, ydpi)
            self._inch = (xdpi, ydpi)
        else:
            msg = 'Unsupported file format'
            raise SyntaxError(msg)
        self._mode = 'RGB'
        self._size = size

    
    def _load(self):
        return _handler

    
    def load(self, dpi = None):
        if dpi is not None:
            self.info['dpi'] = dpi
            x0, y0, x1, y1 = self.info['wmf_bbox']
            if not isinstance(dpi, tuple):
                dpi = (dpi, dpi)
            self._size = (int((x1 - x0) * dpi[0] / self._inch[0]), int((y1 - y0) * dpi[1] / self._inch[1]))
        # unsupported opcode LOAD_SUPER_ATTR
        return self()
    # WARNING: Decompyle incomplete



def _save(im, fp, filename):
    if not (_handler is not None) or not hasattr(_handler, 'save'):
        msg = 'WMF save handler not installed'
        raise OSError(msg)
    _handler.save(im, fp, filename)

Image.register_open(WmfStubImageFile.format, WmfStubImageFile, _accept)
Image.register_save(WmfStubImageFile.format, _save)
Image.register_extensions(WmfStubImageFile.format, [
    '.wmf',
    '.emf'])
