# Source Generated with Decompyle++
# File: ImageQt.pyc (Python 3.14)

__conditional_annotations__ = {}
from __future__ import annotations
import sys
from io import BytesIO
from . import Image
from ._util import is_path
TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any
    from . import ImageFile
    QBuffer: 'type'
qt_version: 'str | None'
qt_versions = [
    [
        '6',
        'PyQt6'],
    [
        'side6',
        'PySide6']]
qt_versions.sort(key = (lambda version: version[1] in sys.modules), reverse = True)
for version, qt_module in qt_versions:
    
    try:
        qRgba: 'Callable[[int, int, int, int], int]'
        if qt_module == 'PyQt6':
            from PyQt6.QtCore import QBuffer, QByteArray, QIODevice
            from PyQt6.QtGui import QImage, QPixmap, qRgba
        elif qt_module == 'PySide6':
            from PySide6.QtCore import QBuffer, QByteArray, QIODevice
            from PySide6.QtGui import QImage, QPixmap, qRgba
    except (ImportError, RuntimeError):
        pass

    qt_is_installed = True
    qt_version = version
    qt_versions
qt_is_installed = False
qt_version = None

def rgb(r, g, b, a = 255):
    '''(Internal) Turns an RGB color into a Qt compatible color integer.'''
    return qRgba(r, g, b, a) & 0xFFFFFFFF


def fromqimage(im):
    '''
:param im: QImage or PIL ImageQt object
'''
    buffer = QBuffer()
    if qt_version == '6':
        
        try:
            qt_openmode = getattr(QIODevice, 'OpenModeFlag')
        except AttributeError:
            qt_openmode = getattr(QIODevice, 'OpenMode')

    else:
        qt_openmode = QIODevice
    buffer.open(getattr(qt_openmode, 'ReadWrite'))
    if im.hasAlphaChannel():
        im.save(buffer, 'png')
    else:
        im.save(buffer, 'ppm')
    b = BytesIO()
    b.write(buffer.data())
    buffer.close()
    b.seek(0)
    return Image.open(b)


def fromqpixmap(im):
    return fromqimage(im)


def align8to32(bytes, width, mode):
    '''
converts each scanline of data from 8 bit to 32 bit aligned
'''
    bits_per_pixel = {
        'I;16': 16,
        'P': 8,
        'L': 8,
        '1': 1 }[mode]
    bits_per_line = bits_per_pixel * width
    full_bytes_per_line, remaining_bits_per_line = divmod(bits_per_line, 8)
    bytes_per_line = full_bytes_per_line + 1 if remaining_bits_per_line else 0
    extra_padding = -bytes_per_line % 4
    if not extra_padding:
        return bytes
    
    try:
        for i in range(len(bytes) // bytes_per_line):
            pass
    i = range(len(bytes) // bytes_per_line)

    new_data = []
    i = i
    return b''.join(new_data)
# WARNING: Decompyle incomplete


def _toqclass_helper(im):
    data = None
    colortable = None
    exclusive_fp = False
    if hasattr(im, 'toUtf8'):
        im = str(im.toUtf8(), 'utf-8')
    if is_path(im):
        im = Image.open(im)
        exclusive_fp = True
    if not isinstance(im, Image.Image):
        raise AssertionError
    qt_format = getattr(QImage, 'Format') if qt_version == '6' else QImage
    if im.mode == '1':
        format = getattr(qt_format, 'Format_Mono')
    elif im.mode == 'L':
        format = getattr(qt_format, 'Format_Indexed8')
        
        try:
            for i in range(256):
                pass
        i = range(256)
        
        try:
            for i in range(0, len(palette), 3):
                pass
        i = None


        colortable = []
        i = i
    elif im.mode == 'P':
        format = getattr(qt_format, 'Format_Indexed8')
        palette = im.getpalette()
        if palette is None:
            raise AssertionError
        
        try:
            for i in range(0, len(palette), 3):
                pass
        i = None

        colortable = None
        i = range(0, len(palette), 3)
    elif im.mode == 'RGB':
        im = im.convert('RGBA')
        data = im.tobytes('raw', 'BGRA')
        format = getattr(qt_format, 'Format_RGB32')
    elif im.mode == 'RGBA':
        data = im.tobytes('raw', 'BGRA')
        format = getattr(qt_format, 'Format_ARGB32')
    elif im.mode == 'I;16':
        im = im.point((lambda i: i * 256))
        format = getattr(qt_format, 'Format_Grayscale16')
    elif exclusive_fp:
        im.close()
    msg = f'''unsupported image mode {repr(im.mode)}'''
    raise ValueError(msg)
    size = im.size
    __data = data or align8to32(im.tobytes(), size[0], im.mode)
    if exclusive_fp:
        im.close()
    return {
        'colortable': colortable,
        'format': format,
        'size': size,
        'data': __data }
# WARNING: Decompyle incomplete

if qt_is_installed:
    
    class ImageQt(QImage):
        
        def __init__(self, im):
            """
An PIL image wrapper for Qt.  This is a subclass of PyQt's QImage
class.

:param im: A PIL Image object, or a file name (given either as
    Python string or a PyQt string object).
"""
            im_data = _toqclass_helper(im)
            self._ImageQt__data = im_data['data']
            # unsupported opcode LOAD_SUPER_ATTR
            self(self._ImageQt__data, im_data['size'][0], im_data['size'][1], im_data['format'])
            if im_data['colortable']:
                self.setColorTable(im_data['colortable'])
                return None
            return None
        # WARNING: Decompyle incomplete



def toqimage(im):
    return ImageQt(im)


def toqpixmap(im):
    '''fromImage'''
    qimage = toqimage(im)
    pixmap = getattr(QPixmap, 'fromImage')(qimage)
    if qt_version == '6':
        pixmap.detach()
    return pixmap

