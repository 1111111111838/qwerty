# Source Generated with Decompyle++
# File: MicImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import olefile
from . import Image, TiffImagePlugin

def _accept(prefix):
    return prefix.startswith(olefile.MAGIC)


class MicImageFile(TiffImagePlugin.TiffImageFile):
    format = 'MIC'
    format_description = 'Microsoft Image Composer'
    _close_exclusive_fp_after_loading = False
    
    def _open(self):
        '''not an MIC file; invalid OLE file'''
        
        try:
            self.ole = olefile.OleFileIO(self.fp)
        except OSError as e:
            msg = 'not an MIC file; invalid OLE file'
            raise SyntaxError(msg) from e

        self.images = None
        if not self.images:
            msg = 'not an MIC file; no image entries'
            raise SyntaxError(msg)
        self.frame = -1
        self._n_frames = len(self.images)
        self.is_animated = self._n_frames > 1
        if self.fp is None:
            raise AssertionError
        self._MicImageFile__fp = self.fp
        return None
    # WARNING: Decompyle incomplete

    
    def seek(self, frame):
        if not self._seek_check(frame):
            return None
        filename = self.images[frame]
        self.fp = self.ole.openstream(filename)
        TiffImagePlugin.TiffImageFile._open(self)
        self.frame = frame

    
    def tell(self):
        return self.frame

    
    def close(self):
        self._MicImageFile__fp.close()
        self.ole.close()
        # unsupported opcode LOAD_SUPER_ATTR
        self()
        return None
    # WARNING: Decompyle incomplete

    
    def __exit__(self, *args):
        self._MicImageFile__fp.close()
        self.ole.close()
        # unsupported opcode LOAD_SUPER_ATTR
        self()
        return None
    # WARNING: Decompyle incomplete


Image.register_open(MicImageFile.format, MicImageFile, _accept)
Image.register_extension(MicImageFile.format, '.mic')
