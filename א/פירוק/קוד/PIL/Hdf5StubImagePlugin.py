# Source Generated with Decompyle++
# File: Hdf5StubImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import os
from typing import IO
from . import Image, ImageFile
_handler = None

def register_handler(handler):
    '''
Install application-specific HDF5 image handler.

:param handler: Handler object.
'''
    global _handler
    _handler = handler


def _accept(prefix):
    b'''\x89HDF\r
\x1a
'''
    return prefix.startswith(b'\x89HDF\r\n\x1a\n')


class HDF5StubImageFile(ImageFile.StubImageFile):
    format = 'HDF5'
    format_description = 'HDF5'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        if not _accept(self.fp.read(8)):
            msg = 'Not an HDF file'
            raise SyntaxError(msg)
        self.fp.seek(-8, os.SEEK_CUR)
        self._mode = 'F'
        self._size = (1, 1)

    
    def _load(self):
        return _handler



def _save(im, fp, filename):
    if not (_handler is not None) or not hasattr(_handler, 'save'):
        msg = 'HDF5 save handler not installed'
        raise OSError(msg)
    _handler.save(im, fp, filename)

Image.register_open(HDF5StubImageFile.format, HDF5StubImageFile, _accept)
Image.register_save(HDF5StubImageFile.format, _save)
Image.register_extensions(HDF5StubImageFile.format, [
    '.h5',
    '.hdf'])
