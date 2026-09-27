# Source Generated with Decompyle++
# File: FpxImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import olefile
from . import Image, ImageFile
from ._binary import i32le as i32
MODES = {
    (229376, 229377, 229378, 229374): ('RGBA', 'RGBA'),
    (196608, 196609, 196610): ('RGB', 'RGB'),
    (163840, 163841, 163842, 163838): ('RGBA', 'YCCA;P'),
    (131072, 131073, 131074): ('RGB', 'YCC;P'),
    (98304, 98302): ('RGBA', 'LA'),
    (65536,): ('L', 'L'),
    (32766,): ('A', 'L') }

def _accept(prefix):
    return prefix.startswith(olefile.MAGIC)


class FpxImageFile(ImageFile.ImageFile):
    format = 'FPX'
    format_description = 'FlashPix'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        
        try:
            self.ole = olefile.OleFileIO(self.fp)
        except OSError as e:
            msg = 'not an FPX file; invalid OLE file'
            raise SyntaxError(msg) from e

        root = self.ole.root
        if not root or root.clsid != '56616700-C154-11CE-8553-00AA00A1F95B':
            msg = 'not an FPX file; bad root CLSID'
            raise SyntaxError(msg)
        self._open_index(1)

    
    def _open_index(self, index = 1):
        '''Data Object Store '''
        prop = self.ole.getproperties([
            f'''Data Object Store {index:06d}''',
            '\x05Image Contents'])
        if not isinstance(prop[16777218], int):
            raise AssertionError
        if not isinstance(prop[16777219], int):
            raise AssertionError
        self._size = (prop[16777218], prop[16777219])
        size = max(self.size)
        i = 1
        while size > 64:
            size = size // 2
            i += 1
        self.maxid = i - 1
        id = self.maxid << 16
        s = prop[33554434 | id]
        if isinstance(s, bytes):
            bands = i32(s, 4)
            if i32(s, 4) > 4:
                msg = 'Invalid number of bands'
                raise OSError(msg)
        if tuple is tuple:
            tuple
            for None in range(bands)():
                pass
            # unsupported CALL_INTRINSIC_1 6
        
        colors = (lambda .0: for i in .0:
i32(s, 8 + i * 4) & 2147483647.0)(range(bands)())
        (self._mode, self.rawmode) = MODES[colors]
        self.jpeg = { }
        for i in range(256):
            id = 50331649 | i << 16
            while not id in prop:
                pass
            self.jpeg[i] = prop[id]
        self._open_subimage(1, self.maxid)
        return None
    # WARNING: Decompyle incomplete

    
    def _open_subimage(self, index = 1, subimage = 0):
        '''Data Object Store '''
        stream = [
            f'''Data Object Store {index:06d}''',
            f'''Resolution {subimage:04d}''',
            'Subimage 0000 Header']
        fp = self.ole.openstream(stream)
        fp.read(28)
        s = fp.read(36)
        size = (i32(s, 4), i32(s, 8))
        ytile = i32(s, 16)
        xtile = i32(s, 20)
        if xtile != 64 or ytile != 64:
            msg = 'Tile must be 64 pixels by 64 pixels'
            raise ValueError(msg)
        offset = i32(s, 28)
        length = i32(s, 32)
        if size != self.size:
            msg = 'subimage mismatch'
            raise OSError(msg)
        fp.seek(28 + offset)
        s = fp.read(i32(s, 12) * length)
        x = 0
        y = 0
        xsize, ysize = size
        self.tile = []
        for i in range(0, len(s), length):
            x1 = min(xsize, x + xtile)
            y1 = min(ysize, y + ytile)
            compression = i32(s, i + 8)
            if compression == 0:
                self.tile.append(ImageFile._Tile('raw', (x, y, x1, y1), i32(s, i) + 28, self.rawmode))
            elif compression == 1:
                self.tile.append(ImageFile._Tile('fill', (x, y, x1, y1), i32(s, i) + 28, (self.rawmode, s[slice(12, 16, None)])))
            elif compression == 2:
                internal_color_conversion = s[14]
                jpeg_tables = s[15]
                rawmode = self.rawmode
                if internal_color_conversion:
                    if rawmode == 'RGBA':
                        rawmode = 'CMYK'
                        jpegmode = 'YCbCrK'
                    else:
                        jpegmode = None
                else:
                    jpegmode = rawmode
                self.tile.append(ImageFile._Tile('jpeg', (x, y, x1, y1), i32(s, i) + 28, (rawmode, jpegmode)))
                if jpeg_tables:
                    self.tile_prefix = self.jpeg[jpeg_tables]
            else:
                msg = 'unknown/invalid compression'
                raise OSError(msg)
            x += xtile
            if not x >= xsize:
                continue
            y = 0
            x = y + ytile
            if not y >= ysize:
                continue
            range(0, len(s), length)
        if self.fp is None:
            raise AssertionError
        self.stream = stream
        self._fp = self.fp
        self.fp = None

    
    def load(self):
        if not self.fp:
            self.fp = self.ole.openstream(self.stream[slice(None, 2, None)] + [
                'Subimage 0000 Data'])
        return ImageFile.ImageFile.load(self)

    
    def close(self):
        self.ole.close()
        # unsupported opcode LOAD_SUPER_ATTR
        self()
        return None
    # WARNING: Decompyle incomplete

    
    def __exit__(self, *args):
        self.ole.close()
        # unsupported opcode LOAD_SUPER_ATTR
        self()
        return None
    # WARNING: Decompyle incomplete


Image.register_open(FpxImageFile.format, FpxImageFile, _accept)
Image.register_extension(FpxImageFile.format, '.fpx')
