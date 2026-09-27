# Source Generated with Decompyle++
# File: PcdImagePlugin.pyc (Python 3.14)

from __future__ import annotations
from . import Image, ImageFile

class PcdImageFile(ImageFile.ImageFile):
    format = 'PCD'
    format_description = 'Kodak PhotoCD'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        self.fp.seek(2048)
        s = self.fp.read(1539)
        if not s.startswith(b'PCD_'):
            msg = 'not a PCD file'
            raise SyntaxError(msg)
        orientation = s[1538] & 3
        self.tile_post_rotate = None
        if orientation == 1:
            self.tile_post_rotate = 90
        elif orientation == 3:
            self.tile_post_rotate = 270
        self._mode = 'RGB'
        self._size = (512, 768) if orientation in (1, 3) else (768, 512)
        self.tile = [
            ImageFile._Tile('pcd', (0, 0, 768, 512), 196608)]

    
    def load_prepare(self):
        if self._im is None and self.tile_post_rotate:
            self.im = Image.core.new(self.mode, (768, 512))
        ImageFile.ImageFile.load_prepare(self)

    
    def load_end(self):
        if self.tile_post_rotate:
            self.im = self.rotate(self.tile_post_rotate, expand = True).im
            return None


Image.register_open(PcdImageFile.format, PcdImageFile)
Image.register_extension(PcdImageFile.format, '.pcd')
