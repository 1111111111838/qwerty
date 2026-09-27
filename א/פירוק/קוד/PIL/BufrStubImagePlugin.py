# Source Generated with Decompyle++
# File: BufrStubImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import os
from typing import IO
from . import Image, ImageFile
_handler = None

def register_handler(handler):
    '''
Install application-specific BUFR image handler.

:param handler: Handler object.
'''
    global _handler
    _handler = handler


def _accept(prefix):
    b'''BUFR'''
    return prefix.startswith((b'BUFR', b'ZCZC'))


class BufrStubImageFile(ImageFile.StubImageFile):
    format = 'BUFR'
    format_description = 'BUFR'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        if not _accept(self.fp.read(4)):
            msg = 'Not a BUFR file'
            raise SyntaxError(msg)
        self.fp.seek(-4, os.SEEK_CUR)
        self._mode = 'F'
        self._size = (1, 1)

    
    def _load(self):
        return _handler



def _save(im, fp, filename):
    if not (_handler is not None) or not hasattr(_handler, 'save'):
        msg = 'BUFR save handler not installed'
        raise OSError(msg)
    _handler.save(im, fp, filename)

Image.register_open(BufrStubImageFile.format, BufrStubImageFile, _accept)
Image.register_save(BufrStubImageFile.format, _save)
Image.register_extension(BufrStubImageFile.format, '.bufr')
