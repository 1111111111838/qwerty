# Source Generated with Decompyle++
# File: GribStubImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import os
from typing import IO
from . import Image, ImageFile
_handler = None

def register_handler(handler):
    '''
Install application-specific GRIB image handler.

:param handler: Handler object.
'''
    global _handler
    _handler = handler


def _accept(prefix):
    return prefix.startswith(b'GRIB') and prefix[7] == 1


class GribStubImageFile(ImageFile.StubImageFile):
    format = 'GRIB'
    format_description = 'GRIB'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        if not _accept(self.fp.read(8)):
            msg = 'Not a GRIB file'
            raise SyntaxError(msg)
        self.fp.seek(-8, os.SEEK_CUR)
        self._mode = 'F'
        self._size = (1, 1)

    
    def _load(self):
        return _handler



def _save(im, fp, filename):
    if not (_handler is not None) or not hasattr(_handler, 'save'):
        msg = 'GRIB save handler not installed'
        raise OSError(msg)
    _handler.save(im, fp, filename)

Image.register_open(GribStubImageFile.format, GribStubImageFile, _accept)
Image.register_save(GribStubImageFile.format, _save)
Image.register_extension(GribStubImageFile.format, '.grib')
