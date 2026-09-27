# Source Generated with Decompyle++
# File: ImagePalette.pyc (Python 3.14)

from __future__ import annotations
import array
from collections.abc import Sequence
from typing import IO
from . import GimpGradientFile, GimpPaletteFile, ImageColor, PaletteFile
TYPE_CHECKING = False
if TYPE_CHECKING:
    from . import Image

class ImagePalette:
    '''
Color palette for palette mapped images

:param mode: The mode to use for the palette. See:
    :ref:`concept-modes`. Defaults to "RGB"
:param palette: An optional palette. If given, it must be a bytearray,
    an array or a list of ints between 0-255. The list must consist of
    all channels for one color followed by the next color (e.g. RGBRGBRGB).
    Defaults to an empty palette.
'''
    
    def __init__(self, mode = 'RGB', palette = None):
        self.mode = mode
        self.rawmode = None
        self.palette = palette or bytearray()
        self.dirty = None

    palette = (lambda self: self._palette)()
    palette = (lambda self, palette: self._colors = Noneself._palette = palette)()
    colors = (lambda self: if self._colors is None:
mode_len = len(self.mode)self._colors = { }for i in range(0, len(self.palette), mode_len):
color = tuple(self.palette[i:i + mode_len])if color in self._colors:
continueself._colors[color] = i // mode_lenself._colors)()
    colors = (lambda self, colors: self._colors = colors)()
    
    def copy(self):
        new = ImagePalette()
        new.mode = self.mode
        new.rawmode = self.rawmode
        if self.palette is not None:
            new.palette = self.palette[slice(None, None, None)]
        new.dirty = self.dirty
        return new

    
    def getdata(self):
        '''
Get palette contents in format suitable for the low-level
``im.putpalette`` primitive.

.. warning:: This method is experimental.
'''
        if self.rawmode:
            return (self.rawmode, self.palette)
        return (self.mode, self.tobytes())

    
    def tobytes(self):
        '''Convert palette to bytes.

.. warning:: This method is experimental.
'''
        if self.rawmode:
            msg = 'palette contains raw palette data'
            raise ValueError(msg)
        if isinstance(self.palette, bytes):
            return self.palette
        arr = array.array('B', self.palette)
        return arr.tobytes()

    tostring = tobytes
    
    def _new_color_index(self, image = None, e = None):
        '''background'''
        if not isinstance(self.palette, bytearray):
            self._palette = bytearray(self.palette)
        index = len(self.palette) // len(self.mode)
        special_colors = ()
        if image:
            special_colors = (image.info.get('background'), image.info.get('transparency'))
            while index in special_colors:
                index += 1
        if index >= 256:
            if image:
                for i, count in reversed(list(enumerate(image.histogram()))):
                    while not count == 0:
                        pass
                    while not i not in special_colors:
                        pass
                    index = i
                    reversed(list(enumerate(image.histogram())))
            if index >= 256:
                msg = 'cannot allocate more than 256 colors'
                raise ValueError(msg) from e
        return index

    
    def getcolor(self, color, image = None):
        '''Given an rgb tuple, allocate palette entry.

.. warning:: This method is experimental.
'''
        if self.rawmode:
            msg = 'palette contains raw palette data'
            raise ValueError(msg)
        if isinstance(color, tuple):
            if self.mode == 'RGB':
                if len(color) == 4:
                    if color[3] != 255:
                        msg = 'cannot add non-opaque RGBA color to RGB palette'
                        raise ValueError(msg)
                    color = color[slice(None, 3, None)]
            elif self.mode == 'RGBA' and len(color) == 3:
                color += (255,)
            
            try:
                return self.colors[color]
            except KeyError as e:
                index = self._new_color_index(image, e)
                if not isinstance(self._palette, bytearray):
                    raise AssertionError
                self.colors[color] = index
                mode_len = len(self.mode)
                if index * mode_len < len(self.palette):
                    self._palette = self._palette[:index * mode_len] + bytes(color) + self._palette[index * mode_len + mode_len:]
                else:
                    self._palette += bytes(color)
                self.dirty = 1
                return index

        msg = f'''unknown color specifier: {repr(color)}'''
        raise ValueError(msg)
    # WARNING: Decompyle incomplete

    
    def save(self, fp):
        '''Save palette to text file.

.. warning:: This method is experimental.
'''
        if self.rawmode:
            msg = 'palette contains raw palette data'
            raise ValueError(msg)
        open_fp = False
        if isinstance(fp, str):
            fp = open(fp, 'w')
            open_fp = True
        
        try:
            fp.write('# Palette\n')
            fp.write(f'''# Mode: {self.mode}\n''')
            palette_len = len(self.palette)
            for i in range(256):
                fp.write(f'''{i}''')
                for j in range(i * len(self.mode), (i + 1) * len(self.mode)):
                    fp.write(f''' {self.palette[j] if j < palette_len else 0}''')
                fp.write('\n')
            return None
        finally:
            if open_fp:
                fp.close()
                return None




def raw(rawmode, data):
    palette = ImagePalette()
    palette.rawmode = rawmode
    palette.palette = data
    palette.dirty = 1
    return palette


def make_linear_lut(black, white):
    if black == 0:
        return None
    msg = 'unavailable when black is non-zero'
    raise NotImplementedError(msg)
# WARNING: Decompyle incomplete


def make_gamma_lut(exp):
    return None
# WARNING: Decompyle incomplete


def negative(mode = 'RGB'):
    palette = list(range(256 * len(mode)))
    palette.reverse()
    return None(ImagePalette, i)


def random(mode = 'RGB'):
    from random import randint
    
    try:
        for _ in range(256 * len(mode)):
            pass
    _ = range(256 * len(mode))

    palette = []
    _ = _
    return ImagePalette(mode, palette)
# WARNING: Decompyle incomplete


def sepia(white = '#fff0c0'):
    
    try:
        for band in ImageColor.getrgb(white):
            pass
    band = ImageColor.getrgb(white)

    bands = []
    band = band
    return None(ImagePalette, i)


def wedge(mode = 'RGB'):
    palette = list(range(256 * len(mode)))
    return None(ImagePalette, i)


def load(filename):
    '''rb'''
    fp = open(filename, 'rb').__enter__()
    paletteHandlers = [
        GimpPaletteFile.GimpPaletteFile,
        GimpGradientFile.GimpGradientFile,
        PaletteFile.PaletteFile]
    for paletteHandler in paletteHandlers:
        
        try:
            fp.seek(0)
            lut = paletteHandler(fp).getpalette()
            if lut:
                paletteHandlers
            
        except (SyntaxError, ValueError):
            pass

    msg = 'cannot load palette'
    raise OSError(msg)
    None(None, None, None)
    return lut

