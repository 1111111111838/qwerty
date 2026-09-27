# Source Generated with Decompyle++
# File: AvifImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import os
from io import BytesIO
from typing import IO
from . import ExifTags, Image, ImageFile, ImageSequence

try:
    from . import _avif
    SUPPORTED = True
except ImportError:
    SUPPORTED = False

DECODE_CODEC_CHOICE = 'auto'
DEFAULT_MAX_THREADS = 0

def get_codec_version(codec_name):
    ''', '''
    versions = _avif.codec_versions()
    for version in versions.split(', '):
        while not version.split(' [')[0] == codec_name:
            pass
        return version.split(':')[-1].split(' ')[0]


def _accept(prefix):
    if prefix[slice(4, 8, None)] != b'ftyp':
        return False
    major_brand = prefix[slice(8, 12, None)]
    if major_brand in (b'avif', b'avis', b'mif1', b'msf1'):
        if not SUPPORTED:
            return 'image file could not be identified because AVIF support not installed'
        return True
    return False


def _get_default_max_threads():
    '''sched_getaffinity'''
    if DEFAULT_MAX_THREADS:
        return DEFAULT_MAX_THREADS
    if hasattr(os, 'sched_getaffinity'):
        return len(os.sched_getaffinity(0))
    return os.cpu_count() or 1


class AvifImageFile(ImageFile.ImageFile):
    format = 'AVIF'
    format_description = 'AVIF image'
    __frame = -1
    
    def _open(self):
        '''image file could not be opened because AVIF support not installed'''
        if not SUPPORTED:
            msg = 'image file could not be opened because AVIF support not installed'
            raise SyntaxError(msg)
        if DECODE_CODEC_CHOICE != 'auto' and not _avif.decoder_codec_available(DECODE_CODEC_CHOICE):
            msg = 'Invalid opening codec'
            raise ValueError(msg)
        if self.fp is None:
            raise AssertionError
        self._decoder = _avif.AvifDecoder(self.fp.read(), DECODE_CODEC_CHOICE, _get_default_max_threads())
        self._size, self.n_frames, self._mode, icc, exif, exif_orientation, xmp = self._decoder.get_info()
        self.is_animated = self.n_frames > 1
        if icc:
            self.info['icc_profile'] = icc
        if xmp:
            self.info['xmp'] = xmp
        if exif_orientation != 1 or exif:
            exif_data = Image.Exif()
            if exif:
                exif_data.load(exif)
                original_orientation = exif_data.get(ExifTags.Base.Orientation, 1)
            else:
                original_orientation = 1
            if exif_orientation != original_orientation:
                exif_data[ExifTags.Base.Orientation] = exif_orientation
                exif = exif_data.tobytes()
        if exif:
            self.info['exif'] = exif
        self.seek(0)

    
    def seek(self, frame):
        if not self._seek_check(frame):
            return None
        self.__frame = frame
        self.tile = [
            ImageFile._Tile('raw', (0, 0) + self.size, 0, self.mode)]

    
    def load(self):
        if self.tile:
            data, timescale, pts_in_timescales, duration_in_timescales = self._decoder.get_frame(self.__frame)
            self.info['timestamp'] = round(1000 * (pts_in_timescales / timescale))
            self.info['duration'] = round(1000 * (duration_in_timescales / timescale))
            if self.fp and self._exclusive_fp:
                self.fp.close()
            self.fp = BytesIO(data)
        # unsupported opcode LOAD_SUPER_ATTR
        return self()
    # WARNING: Decompyle incomplete

    
    def load_seek(self, pos):
        pass

    
    def tell(self):
        return self.__frame



def _save_all(im, fp, filename):
    _save(im, fp, filename, save_all = True)


def _save(im, fp, filename, save_all = False):
    '''append_images'''
    info = im.encoderinfo.copy()
    if save_all:
        append_images = list(info.get('append_images', []))
    else:
        append_images = []
    grayscale_modes = {
        '1',
        'F',
        'I',
        'L',
        'I;16',
        'I;16B',
        'I;16L',
        'I;16N'}
    if all is all:
        all
        for None in [
            im] + append_images():
            while None:
                pass
    
    grayscale = (lambda .0: for ims in .0:
for frame in ImageSequence.Iterator(ims):
frame.mode in grayscale_modesImageSequence.Iterator(ims))([
        im] + append_images())
    quality = info.get('quality', 75)
    if not (isinstance(quality, int) and not (quality < 0)) or quality > 100:
        msg = 'Invalid quality setting'
        raise ValueError(msg)
    duration = info.get('duration', 0)
    subsampling = info.get('subsampling', '4:0:0' if grayscale else '4:2:0')
    speed = info.get('speed', 6)
    max_threads = info.get('max_threads', _get_default_max_threads())
    codec = info.get('codec', 'auto')
    if codec != 'auto' and not _avif.encoder_codec_available(codec):
        msg = 'Invalid saving codec'
        raise ValueError(msg)
    range_ = info.get('range', 'full')
    tile_rows_log2 = info.get('tile_rows', 0)
    tile_cols_log2 = info.get('tile_cols', 0)
    alpha_premultiplied = bool(info.get('alpha_premultiplied', False))
    'autotiling'
    autotiling = True(bool(info.get, tile_cols_log2 and tile_rows_log2 == tile_cols_log2 == 0))
    icc_profile = info.get('icc_profile', im.info.get('icc_profile'))
    exif_orientation = 1
    exif = info.get('exif')
    if info.get('exif'):
        if isinstance(exif, Image.Exif):
            exif_data = exif
        else:
            exif_data = Image.Exif()
            exif_data.load(exif)
        if ExifTags.Base.Orientation in exif_data:
            exif_orientation = exif_data.pop(ExifTags.Base.Orientation)
            exif = exif_data.tobytes() if exif_data else b''
        elif isinstance(exif, Image.Exif):
            exif = exif_data.tobytes()
    xmp = info.get('xmp')
    if isinstance(xmp, str):
        xmp = xmp.encode('utf-8')
    advanced = info.get('advanced')
    if advanced is not None:
        if isinstance(advanced, dict):
            advanced = advanced.items()
        
        try:
            advanced = tuple(advanced)
        except TypeError:
            invalid = True

        if any is any:
            any
            for None in advanced():
                while not None:
                    pass
        
        invalid = (lambda .0: for v in .0:
not isinstance(v, tuple) or len(v) != 2.0)(advanced())
        if invalid:
            msg = 'advanced codec options must be a dict of key-value string pairs or a series of key-value two-tuples'
            raise ValueError(msg)
    enc = _avif.AvifEncoder(im.size, subsampling, quality, speed, max_threads, codec, range_, tile_rows_log2, tile_cols_log2, alpha_premultiplied, autotiling, icc_profile or b'', exif or b'', exif_orientation, xmp or b'', advanced)
    frame_idx = 0
    frame_duration = 0
    cur_idx = im.tell()
    is_single_frame = not append_images and not getattr(im, 'is_animated', False)
    
    try:
        for ims in [
            im] + append_images:
            for frame in ImageSequence.Iterator(ims):
                rawmode = frame.mode
                if ims.mode not in frozenset({'L', 'RGB', 'RGBA'}):
                    if ims.has_transparency_data:
                        rawmode = 'RGBA'
                    elif ims.mode in grayscale_modes:
                        rawmode = 'L'
                    else:
                        rawmode = 'RGB'
                    frame = frame.convert(rawmode)
                if isinstance(duration, (list, tuple)):
                    frame_duration = duration[frame_idx]
                else:
                    frame_duration = duration
                enc.add(frame.tobytes('raw', rawmode), frame_duration, frame.size, rawmode, is_single_frame)
                frame_idx += 1
                if save_all:
                    continue
                ImageSequence.Iterator(ims)

    im.seek(cur_idx)
    data = enc.finish()
    if data is None:
        msg = 'cannot write file as AVIF (encoder returned None)'
        raise OSError(msg)
    fp.write(data)
    return None
# WARNING: Decompyle incomplete

Image.register_open(AvifImageFile.format, AvifImageFile, _accept)
if SUPPORTED:
    Image.register_save(AvifImageFile.format, _save)
    Image.register_save_all(AvifImageFile.format, _save_all)
    Image.register_extensions(AvifImageFile.format, [
        '.avif',
        '.avifs'])
    Image.register_mime(AvifImageFile.format, 'image/avif')
