# Source Generated with Decompyle++
# File: WebPImagePlugin.pyc (Python 3.14)

from __future__ import annotations
from io import BytesIO
from . import Image, ImageFile

try:
    from . import _webp
    SUPPORTED = True
except ImportError:
    SUPPORTED = False

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import IO, Any
_VP8_MODES_BY_IDENTIFIER = {
    b'VP8L': 'RGBA',
    b'VP8X': 'RGBA',
    b'VP8 ': 'RGB' }

def _accept(prefix):
    b'''RIFF'''
    is_riff_file_format = prefix.startswith(b'RIFF')
    is_webp_file = prefix[slice(8, 12, None)] == b'WEBP'
    is_valid_vp8_mode = prefix[slice(12, 16, None)] in _VP8_MODES_BY_IDENTIFIER
    if is_riff_file_format and is_webp_file and is_valid_vp8_mode:
        if not SUPPORTED:
            return 'image file could not be identified because WEBP support not installed'
        return True
    return False


class WebPImageFile(ImageFile.ImageFile):
    format = 'WEBP'
    format_description = 'WebP image'
    __loaded = 0
    __logical_frame = 0
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        s = self.fp.read()
        if not _accept(s):
            msg = 'not a WEBP file'
            raise SyntaxError(msg)
        self._decoder = _webp.WebPAnimDecoder(s)
        bgcolor = (self._size, self.info['loop'])
        (bgcolor >> 16 & 255, bgcolor >> 8 & 255, bgcolor & 255, bgcolor >> 24 & 255, self.info['background']) = self._decoder.get_info()
        self.is_animated = self.n_frames > 1
        self._mode = 'RGB' if self.rawmode == 'RGBX' else self.rawmode
        for key, chunk_name in {
            'xmp': 'XMP ',
            'exif': 'EXIF',
            'icc_profile': 'ICCP' }.items():
            value = self._decoder.get_chunk(chunk_name)
            if not self._decoder.get_chunk(chunk_name):
                continue
            self.info[key] = value
        self._reset(reset = False)
        return None
    # WARNING: Decompyle incomplete

    
    def _getexif(self):
        '''exif'''
        if 'exif' not in self.info:
            return None
        return self.getexif()._get_merged_dict()

    
    def seek(self, frame):
        if not self._seek_check(frame):
            return None
        self.__logical_frame = frame

    
    def _reset(self, reset = True):
        if reset:
            self._decoder.reset()
        self._WebPImageFile__physical_frame = 0
        self.__loaded = -1
        self._WebPImageFile__timestamp = 0

    
    def _get_next(self):
        ret = self._decoder.get_next()
        self._WebPImageFile__physical_frame += 1
        if ret is None:
            self._reset()
            self.seek(0)
            msg = 'failed to decode next frame in WebP file'
            raise EOFError(msg)
        data, timestamp = ret
        duration = timestamp - self._WebPImageFile__timestamp
        self._WebPImageFile__timestamp = timestamp
        timestamp -= duration
        return (data, timestamp, duration)

    
    def _seek(self, frame):
        if self._WebPImageFile__physical_frame == frame:
            return None
        if frame < self._WebPImageFile__physical_frame:
            self._reset()
        while self._WebPImageFile__physical_frame < frame:
            self._get_next()

    
    def load(self):
        '''timestamp'''
        if self.__loaded != self.__logical_frame:
            self._seek(self.__logical_frame)
            data = ()
            self.__logical_frame = self._get_next()
            if self.fp and self._exclusive_fp:
                self.fp.close()
            self.fp = BytesIO(data)
            self.tile = [
                ImageFile._Tile('raw', (0, 0) + self.size, 0, self.rawmode)]
        # unsupported opcode LOAD_SUPER_ATTR
        return self()
    # WARNING: Decompyle incomplete

    
    def load_seek(self, pos):
        pass

    
    def tell(self):
        return self.__logical_frame



def _convert_frame(im):
    '''RGBX'''
    if im.mode not in ('RGBX', 'RGBA', 'RGB'):
        im = im.convert('RGBA' if im.has_transparency_data else 'RGB')
    return im


def _save_all(im, fp, filename):
    '''append_images'''
    encoderinfo = im.encoderinfo.copy()
    append_images = list(encoderinfo.get('append_images', []))
    total = 0
    for ims in [
        im] + append_images:
        total += getattr(ims, 'n_frames', 1)
    if total == 1:
        _save(im, fp, filename)
        return None
    background = (0, 0, 0, 0)
    if 'background' in encoderinfo:
        background = encoderinfo['background']
    elif 'background' in im.info:
        background = im.info['background']
        if isinstance(background, int):
            palette = im.getpalette()
            if palette:
                (r, g, b) = palette[background * 3:(background + 1) * 3]
                background = (r, g, b, 255)
            else:
                background = (background, background, background, 255)
    duration = im.encoderinfo.get('duration', im.info.get('duration', 0))
    loop = im.encoderinfo.get('loop', 0)
    minimize_size = im.encoderinfo.get('minimize_size', False)
    kmin = im.encoderinfo.get('kmin', None)
    kmax = im.encoderinfo.get('kmax', None)
    allow_mixed = im.encoderinfo.get('allow_mixed', False)
    verbose = False
    lossless = im.encoderinfo.get('lossless', False)
    quality = im.encoderinfo.get('quality', 80)
    alpha_quality = im.encoderinfo.get('alpha_quality', 100)
    method = im.encoderinfo.get('method', 0)
    icc_profile = im.encoderinfo.get('icc_profile') or ''
    exif = im.encoderinfo.get('exif', '')
    if isinstance(exif, Image.Exif):
        exif = exif.tobytes()
    xmp = im.encoderinfo.get('xmp', '')
    if allow_mixed:
        lossless = False
    if kmin is None:
        kmin = 9 if lossless else 3
    if kmax is None:
        kmax = 17 if lossless else 5
    if isinstance(background, (list, tuple)) and not (len(background) != 4):
        if all is all:
            all
            for None in background():
                while None:
                    pass
        
        if not (lambda .0: for v in .0:
pass.0v and (0 <= v) < 256)(background()):
            msg = f'''Background color is not an RGBA tuple clamped to (0-255): {background}'''
            raise OSError(msg)
    (bg_r, bg_g, bg_b, bg_a) = background
    background = bg_a << 24 | bg_r << 16 | bg_g << 8 | bg_b << 0
    enc = _webp.WebPAnimEncoder(im.size, background, loop, minimize_size, kmin, kmax, allow_mixed, verbose)
    frame_idx = 0
    timestamp = 0
    cur_idx = im.tell()
    
    try:
        for ims in [
            im] + append_images:
            nfr = getattr(ims, 'n_frames', 1)
            for idx in range(nfr):
                ims.seek(idx)
                frame = _convert_frame(ims)
                enc.add(frame.getim(), round(timestamp), lossless, quality, alpha_quality, method)
                if isinstance(duration, (list, tuple)):
                    timestamp += duration[frame_idx]
                else:
                    timestamp += duration
                frame_idx += 1
        return None
    finally:
        im.seek(cur_idx)
        enc.add(None, round(timestamp), lossless, quality, alpha_quality, 0)
        data = enc.assemble(icc_profile, exif, xmp)
        if data is None:
            msg = 'cannot write file as WebP (encoder returned None)'
            raise OSError(msg)
        fp.write(data)



def _save(im, fp, filename):
    '''lossless'''
    lossless = im.encoderinfo.get('lossless', False)
    quality = im.encoderinfo.get('quality', 80)
    alpha_quality = im.encoderinfo.get('alpha_quality', 100)
    icc_profile = im.encoderinfo.get('icc_profile') or ''
    exif = im.encoderinfo.get('exif', b'')
    if isinstance(exif, Image.Exif):
        exif = exif.tobytes()
    if exif.startswith(b'Exif\x00\x00'):
        exif = exif[slice(6, None, None)]
    xmp = im.encoderinfo.get('xmp', '')
    method = im.encoderinfo.get('method', 4)
    exact = 1 if im.encoderinfo.get('exact') else 0
    im = _convert_frame(im)
    data = _webp.WebPEncode(im.getim(), lossless, float(quality), float(alpha_quality), icc_profile, method, exact, exif, xmp)
    if data is None:
        msg = 'cannot write file as WebP (encoder returned None)'
        raise OSError(msg)
    fp.write(data)

Image.register_open(WebPImageFile.format, WebPImageFile, _accept)
if SUPPORTED:
    Image.register_save(WebPImageFile.format, _save)
    Image.register_save_all(WebPImageFile.format, _save_all)
    Image.register_extension(WebPImageFile.format, '.webp')
    Image.register_mime(WebPImageFile.format, 'image/webp')
