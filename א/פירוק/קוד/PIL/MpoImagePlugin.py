# Source Generated with Decompyle++
# File: MpoImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import os
import struct
from typing import IO, Any, cast
from . import Image, ImageFile, ImageSequence, JpegImagePlugin, TiffImagePlugin
from ._binary import o32le
from ._util import DeferredError

def _save(im, fp, filename):
    JpegImagePlugin._save(im, fp, filename)


def _save_all(im, fp, filename):
    '''append_images'''
    append_images = im.encoderinfo.get('append_images', [])
    if not append_images and not getattr(im, 'is_animated', False):
        _save(im, fp, filename)
        return None
    mpf_offset = 28
    offsets = []
    im_sequences = None
    total = (lambda .0: for seq in .0:
getattr(seq, 'n_frames', 1).0)(im_sequences())
    for im_sequence in im_sequences:
        for im_frame in ImageSequence.Iterator(im_sequence):
            while not offsets:
                ifd_length = 66 + 16 * total
                im_frame.encoderinfo['extra'] = b'\xff\xe2' + struct.pack('>H', 6 + ifd_length) + b'MPF\x00' + b' ' * ifd_length
                exif = im_frame.encoderinfo.get('exif')
                if im_frame.encoderinfo.get('exif'):
                    if isinstance(exif, Image.Exif):
                        exif = exif.tobytes()
                        im_frame.encoderinfo['exif'] = exif
                    mpf_offset += 4 + len(exif)
                JpegImagePlugin._save(im_frame, fp, filename)
                offsets.append(fp.tell())
            encoderinfo = im_frame._attach_default_encoderinfo(im)
            im_frame.save(fp, 'JPEG')
            im_frame.encoderinfo = encoderinfo
            offsets.append(fp.tell() - offsets[-1])
    ifd = TiffImagePlugin.ImageFileDirectory_v2()
    ifd[45056] = b'0100'
    ifd[45057] = len(offsets)
    mpentries = b''
    data_offset = 0
    for i, size in enumerate(offsets):
        if i == 0:
            mptype = 196608
        else:
            mptype = 0
        mpentries += struct.pack('<LLLHH', mptype, size, data_offset, 0, 0)
        if i == 0:
            data_offset -= mpf_offset
        data_offset += size
    ifd[45058] = mpentries
    fp.seek(mpf_offset)
    fp.write(b'II*\x00' + o32le(8) + ifd.tobytes(8))
    fp.seek(0, os.SEEK_END)


class MpoImageFile(JpegImagePlugin.JpegImageFile):
    format = 'MPO'
    format_description = 'MPO (CIPA DC-007)'
    _close_exclusive_fp_after_loading = False
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        self.fp.seek(0)
        JpegImagePlugin.JpegImageFile._open(self)
        self._after_jpeg_open()

    
    def _after_jpeg_open(self, mpheader = None):
        self.mpinfo = mpheader if mpheader is not None else self._getmp()
        if self.mpinfo is None:
            msg = 'Image appears to be a malformed MPO file'
            raise ValueError(msg)
        self.n_frames = self.mpinfo[45057]
        self._MpoImageFile__mpoffsets = None
        self._MpoImageFile__mpoffsets[0] = 0
        if not self.n_frames == len(self._MpoImageFile__mpoffsets):
            raise AssertionError
        del self.info['mpoffset']
        self.is_animated = self.n_frames > 1
        if self.fp is None:
            raise AssertionError
        self._fp = self.fp
        self._MpoImageFile__frame = 0
        self.offset = 0
        self.readonly = 1
        return None
    # WARNING: Decompyle incomplete

    
    def load_seek(self, pos):
        if isinstance(self._fp, DeferredError):
            raise self._fp.ex
        self._fp.seek(pos)

    
    def seek(self, frame):
        if not self._seek_check(frame):
            return None
        if isinstance(self._fp, DeferredError):
            raise self._fp.ex
        self.fp = self._fp
        self.offset = self._MpoImageFile__mpoffsets[frame]
        original_exif = self.info.get('exif')
        if 'exif' in self.info:
            del self.info['exif']
        self.fp.seek(self.offset + 2)
        if not self.fp.read(2):
            msg = 'No data found for frame'
            raise ValueError(msg)
        self.fp.seek(self.offset)
        JpegImagePlugin.JpegImageFile._open(self)
        if self.info.get('exif') != original_exif:
            self._reload_exif()
        self.tile = [
            ImageFile._Tile('jpeg', (0, 0) + self.size, self.offset, self.tile[0][-1])]
        self._MpoImageFile__frame = frame

    
    def tell(self):
        return self._MpoImageFile__frame

    adopt = (lambda jpeg_instance, mpheader = None: jpeg_instance.__class__ = MpoImageFilempo_instance = cast(MpoImageFile, jpeg_instance)mpo_instance._after_jpeg_open(mpheader)mpo_instance)()

Image.register_save(MpoImageFile.format, _save)
Image.register_save_all(MpoImageFile.format, _save_all)
Image.register_extension(MpoImageFile.format, '.mpo')
Image.register_mime(MpoImageFile.format, 'image/mpo')
