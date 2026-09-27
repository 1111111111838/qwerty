# Source Generated with Decompyle++
# File: PngImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import itertools
import logging
import re
import struct
import warnings
import zlib
from enum import IntEnum
from fractions import Fraction
from typing import IO, NamedTuple, cast
from . import Image, ImageChops, ImageFile, ImagePalette, ImageSequence
from ._binary import i16be as i16
from ._binary import i32be as i32
from ._binary import o8
from ._binary import o16be as o16
from ._binary import o32be as o32
from ._deprecate import deprecate
from ._util import DeferredError
TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, NoReturn
    from . import _imaging
logger = logging.getLogger(__name__)
is_cid = re.compile(b'\\w\\w\\w\\w').match
_MAGIC = b'\x89PNG\r\n\x1a\n'
_MODES = {
    (16, 6): ('RGBA', 'RGBA;16B'),
    (8, 6): ('RGBA', 'RGBA'),
    (16, 4): ('RGBA', 'LA;16B'),
    (8, 4): ('LA', 'LA'),
    (8, 3): ('P', 'P'),
    (4, 3): ('P', 'P;4'),
    (2, 3): ('P', 'P;2'),
    (1, 3): ('P', 'P;1'),
    (16, 2): ('RGB', 'RGB;16B'),
    (8, 2): ('RGB', 'RGB'),
    (16, 0): ('I;16', 'I;16B'),
    (8, 0): ('L', 'L'),
    (4, 0): ('L', 'L;4'),
    (2, 0): ('L', 'L;2'),
    (1, 0): ('1', '1') }
_simple_palette = re.compile(b'^\xff*\x00\xff*$')
MAX_TEXT_CHUNK = ImageFile.SAFEBLOCK
MAX_TEXT_MEMORY = 64 * MAX_TEXT_CHUNK

class Disposal(IntEnum):
    OP_NONE = 0
    OP_BACKGROUND = 1
    OP_PREVIOUS = 2


class Blend(IntEnum):
    OP_SOURCE = 0
    OP_OVER = 1


def _safe_zlib_decompress(s):
    '''Decompressed data too large for PngImagePlugin.MAX_TEXT_CHUNK'''
    dobj = zlib.decompressobj()
    plaintext = dobj.decompress(s, MAX_TEXT_CHUNK)
    if dobj.unconsumed_tail:
        msg = 'Decompressed data too large for PngImagePlugin.MAX_TEXT_CHUNK'
        raise ValueError(msg)
    return plaintext


def _crc32(data, seed = 0):
    return zlib.crc32(data, seed) & 0xFFFFFFFF


class ChunkStream:
    
    def __init__(self, fp):
        self.fp = fp
        self.queue = []

    
    def read(self):
        '''Fetch a new chunk. Returns header information.'''
        cid = None
        if self.fp is None:
            raise AssertionError
        if self.queue:
            (cid, pos, length) = self.queue.pop()
            self.fp.seek(pos)
        else:
            s = self.fp.read(8)
            cid = s[slice(4, None, None)]
            pos = self.fp.tell()
            length = i32(s)
        if not is_cid(cid) and not (ImageFile.LOAD_TRUNCATED_IMAGES):
            msg = f'''broken PNG file (chunk {repr(cid)})'''
            raise SyntaxError(msg)
        return (cid, pos, length)

    
    def __enter__(self):
        return self

    
    def __exit__(self, *args):
        self.close()

    
    def close(self):
        self.queue = None
        self.fp = None

    
    def push(self, cid, pos, length):
        if self.queue is None:
            raise AssertionError
        self.queue.append((cid, pos, length))

    
    def call(self, cid, pos, length):
        '''Call the appropriate chunk handler'''
        logger.debug('STREAM %r %s %s', cid, pos, length)
        return getattr(self, f'''chunk_{cid.decode('ascii')}''')(pos, length)

    
    def crc(self, cid, data):
        '''Read and verify checksum'''
        if ImageFile.LOAD_TRUNCATED_IMAGES and cid[0] >> 5 & 1:
            self.crc_skip(cid, data)
            return None
        if self.fp is None:
            raise AssertionError
        
        try:
            crc1 = _crc32(data, _crc32(cid))
            crc2 = i32(self.fp.read(4))
            if crc1 != crc2:
                msg = f'''broken PNG file (bad header checksum in {repr(cid)})'''
                raise SyntaxError(msg)
        except struct.error as e:
            msg = f'''broken PNG file (incomplete checksum in {repr(cid)})'''
            raise SyntaxError(msg) from e


    
    def crc_skip(self, cid, data):
        '''Read checksum'''
        if self.fp is None:
            raise AssertionError
        self.fp.read(4)

    
    def verify(self, endchunk = b'IEND'):
        cids = []
        if self.fp is None:
            raise AssertionError
        
        try:
            (cid, pos, length) = self.read()
        except struct.error as e:
            msg = 'truncated PNG file'
            raise OSError(msg) from e

        if cid == endchunk:
            return cids
        self.crc(cid, ImageFile._safe_read(self.fp, length))
        cids.append(cid)



class iTXt(str):
    tkey: 'str | bytes | None' = '\nSubclass of string to allow iTXt chunks to look like strings while\nkeeping their extra information\n\n'
    __new__ = (lambda cls, text, lang = None, tkey = None: self = str.__new__(cls, text)self.lang = langself.tkey = tkeyself)()


class PngInfo:
    '''
PNG chunk container (for use with save(pnginfo=))

'''
    
    def __init__(self):
        self.chunks = []

    
    def add(self, cid, data, after_idat = False):
        '''Appends an arbitrary chunk. Use with caution.

:param cid: a byte string, 4 bytes long.
:param data: a byte string of the encoded data
:param after_idat: for use with private chunks. Whether the chunk
                   should be written after IDAT

'''
        self.chunks.append((cid, data, after_idat))

    
    def add_itxt(self, key, value, lang = '', tkey = '', zip = False):
        '''Appends an iTXt chunk.

:param key: latin-1 encodable text key name
:param value: value for this key
:param lang: language code
:param tkey: UTF-8 version of the key name
:param zip: compression flag

'''
        if not isinstance(key, bytes):
            key = key.encode('latin-1', 'strict')
        if not isinstance(value, bytes):
            value = value.encode('utf-8', 'strict')
        if not isinstance(lang, bytes):
            lang = lang.encode('utf-8', 'strict')
        if not isinstance(tkey, bytes):
            tkey = tkey.encode('utf-8', 'strict')
        if zip:
            self.add(b'iTXt', key + b'\x00\x01\x00' + lang + b'\x00' + tkey + b'\x00' + zlib.compress(value))
            return None
        self.add(b'iTXt', key + b'\x00\x00\x00' + lang + b'\x00' + tkey + b'\x00' + value)

    
    def add_text(self, key, value, zip = False):
        '''Appends a text chunk.

:param key: latin-1 encodable text key name
:param value: value for this key, text or an
   :py:class:`PIL.PngImagePlugin.iTXt` instance
:param zip: compression flag

'''
        if isinstance(value, iTXt):
            if value.tkey is not None:
                return self.add_itxt(key, value, value.lang if value.lang is not None else b'', value.tkey, zip = zip)
            return self.add_itxt(key, value, value.lang if value.lang is not None else b'', b'', zip = zip)
        if not isinstance(value, bytes):
            
            try:
                value = value.encode('latin-1', 'strict')
            except UnicodeError:
                return self.add_itxt(key, value, zip = zip)

        if not isinstance(key, bytes):
            key = key.encode('latin-1', 'strict')
        if zip:
            self.add(b'zTXt', key + b'\x00\x00' + zlib.compress(value))
            return None
        self.add(b'tEXt', key + b'\x00' + value)



class _RewindState(NamedTuple):
    seq_num: 'int | None' = '_RewindState'


class PngStream(ChunkStream):
    
    def __init__(self, fp):
        # unsupported opcode LOAD_SUPER_ATTR
        self(fp)
        self.im_info = { }
        self.im_text = { }
        self.im_size = (0, 0)
        self.im_mode = ''
        self.im_tile = []
        self.im_palette = None
        self.im_custom_mimetype = None
        self.im_n_frames = None
        self._seq_num = None
        self.rewind_state = _RewindState({ }, [], None)
        self.text_memory = 0
        return None
    # WARNING: Decompyle incomplete

    
    def __enter__(self):
        return self

    
    def check_text_memory(self, chunklen):
        '''Too much memory used in text chunks: '''
        self.text_memory += chunklen
        if self.text_memory > MAX_TEXT_MEMORY:
            msg = f'''Too much memory used in text chunks: {self.text_memory}>MAX_TEXT_MEMORY'''
            raise ValueError(msg)

    
    def save_rewind(self):
        self.rewind_state = _RewindState(self.im_info.copy(), self.im_tile, self._seq_num)

    
    def rewind(self):
        self.im_info = self.rewind_state.info.copy()
        self.im_tile = self.rewind_state.tile
        self._seq_num = self.rewind_state.seq_num

    
    def chunk_iCCP(self, pos, length):
        if self.fp is None:
            raise AssertionError
        s = ImageFile._safe_read(self.fp, length)
        i = s.find(b'\x00')
        logger.debug('iCCP profile name %r', s[:i])
        comp_method = s[i + 1]
        logger.debug('Compression method %s', comp_method)
        if comp_method != 0:
            msg = f'''Unknown compression method {comp_method} in iCCP chunk'''
            raise SyntaxError(msg)
        
        try:
            icc_profile = _safe_zlib_decompress(s[i + 2:])
        while <exception value><EXCEPTION MATCH>ValueError:
            if ImageFile.LOAD_TRUNCATED_IMAGES:
                icc_profile = None
        raise
        except zlib.error:
            icc_profile = None

        self.im_info['icc_profile'] = icc_profile
        return s

    
    def chunk_IHDR(self, pos, length):
        if self.fp is None:
            raise AssertionError
        s = ImageFile._safe_read(self.fp, length)
        if length < 13:
            if ImageFile.LOAD_TRUNCATED_IMAGES:
                return s
            msg = 'Truncated IHDR chunk'
            raise ValueError(msg)
        self.im_size = (i32(s, 0), i32(s, 4))
        
        try:
            (self.im_mode, self.im_rawmode) = _MODES[(s[8], s[9])]
        except KeyError:
            pass

        if s[12]:
            self.im_info['interlace'] = 1
        if s[11]:
            msg = 'unknown filter category'
            raise SyntaxError(msg)
        return s

    
    def chunk_IDAT(self, pos, length):
        '''bbox'''
        if 'bbox' in self.im_info:
            tile = [
                ImageFile._Tile('zip', self.im_info['bbox'], pos, self.im_rawmode)]
        elif self.im_n_frames is not None:
            self.im_info['default_image'] = True
        tile = [
            ImageFile._Tile('zip', (0, 0) + self.im_size, pos, self.im_rawmode)]
        self.im_tile = tile
        self.im_idat = length
        msg = 'image data found'
        raise EOFError(msg)

    
    def chunk_IEND(self, pos, length):
        '''end of PNG image'''
        msg = 'end of PNG image'
        raise EOFError(msg)

    
    def chunk_PLTE(self, pos, length):
        if self.fp is None:
            raise AssertionError
        s = ImageFile._safe_read(self.fp, length)
        if self.im_mode == 'P':
            self.im_palette = ('RGB', s)
        return s

    
    def chunk_tRNS(self, pos, length):
        if self.fp is None:
            raise AssertionError
        s = ImageFile._safe_read(self.fp, length)
        if self.im_mode == 'P':
            if _simple_palette.match(s):
                i = s.find(b'\x00')
                if i >= 0:
                    self.im_info['transparency'] = i
                return s
            self.im_info['transparency'] = s
            return s
        if self.im_mode == '1':
            self.im_info['transparency'] = 255 if i16(s) else 0
            return s
        if self.im_mode in ('L', 'I;16'):
            self.im_info['transparency'] = i16(s)
            return s
        if self.im_mode == 'RGB':
            self.im_info['transparency'] = (i16(s), i16(s, 2), i16(s, 4))
        return s

    
    def chunk_gAMA(self, pos, length):
        if self.fp is None:
            raise AssertionError
        s = ImageFile._safe_read(self.fp, length)
        self.im_info['gamma'] = i32(s) / 100000
        return s

    
    def chunk_cHRM(self, pos, length):
        if self.fp is None:
            raise AssertionError
        s = ImageFile._safe_read(self.fp, length)
        raw_vals = struct.unpack(f'''>{len(s) // 4}I''', s)
        if tuple is tuple:
            tuple
            for None in raw_vals():
                pass
            # unsupported CALL_INTRINSIC_1 6
        
        self.im_info['chromaticity'] = (lambda .0: for elt in .0:
elt / 100000.0)(raw_vals())
        return s
    # WARNING: Decompyle incomplete

    
    def chunk_sRGB(self, pos, length):
        if self.fp is None:
            raise AssertionError
        s = ImageFile._safe_read(self.fp, length)
        if length < 1:
            if ImageFile.LOAD_TRUNCATED_IMAGES:
                return s
            msg = 'Truncated sRGB chunk'
            raise ValueError(msg)
        self.im_info['srgb'] = s[0]
        return s

    
    def chunk_pHYs(self, pos, length):
        if self.fp is None:
            raise AssertionError
        s = ImageFile._safe_read(self.fp, length)
        if length < 9:
            if ImageFile.LOAD_TRUNCATED_IMAGES:
                return s
            msg = 'Truncated pHYs chunk'
            raise ValueError(msg)
        py = i32(s, 0)
        px = i32(s, 4)
        unit = s[8]
        if unit == 1:
            dpi = (px * 0.0254, py * 0.0254)
            self.im_info['dpi'] = dpi
            return s
        if unit == 0:
            self.im_info['aspect'] = (px, py)
        return s

    
    def chunk_tEXt(self, pos, length):
        if self.fp is None:
            raise AssertionError
        s = ImageFile._safe_read(self.fp, length)
        
        try:
            k, v = s.split(b'\x00', 1)
        except ValueError:
            k = s
            v = b''

        if k:
            k_str = k.decode('latin-1', 'strict')
            v_str = v.decode('latin-1', 'replace')
            self.im_info[k_str] = v if k == b'exif' else v_str
            self.im_text[k_str] = v_str
            self.check_text_memory(len(v_str))
        return s

    
    def chunk_zTXt(self, pos, length):
        if self.fp is None:
            raise AssertionError
        s = ImageFile._safe_read(self.fp, length)
        
        try:
            k, v = s.split(b'\x00', 1)
        except ValueError:
            k = s
            v = b''

        if v:
            comp_method = v[0]
        else:
            comp_method = 0
        if comp_method != 0:
            msg = f'''Unknown compression method {comp_method} in zTXt chunk'''
            raise SyntaxError(msg)
        
        try:
            v = _safe_zlib_decompress(v[slice(1, None, None)])
        except ValueError:
            if ImageFile.LOAD_TRUNCATED_IMAGES:
                v = b''
            raise

        if k:
            k_str = k.decode('latin-1', 'strict')
            v_str = v.decode('latin-1', 'replace')
            self.im_info[k_str] = v_str
            self.im_text[k_str] = v_str
            self.check_text_memory(len(v_str))
        return s

    
    def chunk_iTXt(self, pos, length):
        if self.fp is None:
            raise AssertionError
        r = ImageFile._safe_read(self.fp, length)
        s = ImageFile._safe_read(self.fp, length)
        
        try:
            k, r = r.split(b'\x00', 1)
        except ValueError:
            return s

        if len(r) < 2:
            return s
        r = r[1]
        cm = r[slice(2, None, None)]
        cf = r[0]
        
        try:
            (lang, tk, v) = r.split(b'\x00', 2)
        except ValueError:
            return s

        if cf != 0:
            if cm == 0:
                
                try:
                    v = _safe_zlib_decompress(v)
                except ValueError:
                    if ImageFile.LOAD_TRUNCATED_IMAGES:
                        return s
                    raise

            else:
                return s
        if k == b'XML:com.adobe.xmp':
            self.im_info['xmp'] = v
        
        try:
            k_str = k.decode('latin-1', 'strict')
            lang_str = lang.decode('utf-8', 'strict')
            tk_str = tk.decode('utf-8', 'strict')
            v_str = v.decode('utf-8', 'strict')
        except UnicodeError:
            return s

        self.im_info[k_str] = iTXt(v_str, lang_str, tk_str)
        self.im_text[k_str] = iTXt(v_str, lang_str, tk_str)
        self.check_text_memory(len(v_str))
        return s
    # WARNING: Decompyle incomplete

    
    def chunk_eXIf(self, pos, length):
        if self.fp is None:
            raise AssertionError
        s = ImageFile._safe_read(self.fp, length)
        self.im_info['exif'] = b'Exif\x00\x00' + s
        return s

    
    def chunk_acTL(self, pos, length):
        if self.fp is None:
            raise AssertionError
        s = ImageFile._safe_read(self.fp, length)
        if length < 8:
            if ImageFile.LOAD_TRUNCATED_IMAGES:
                return s
            msg = 'APNG contains truncated acTL chunk'
            raise ValueError(msg)
        if self.im_n_frames is not None:
            self.im_n_frames = None
            warnings.warn('Invalid APNG, will use default PNG image if possible')
            return s
        n_frames = i32(s)
        if n_frames == 0 or n_frames > 0x80000000:
            warnings.warn('Invalid APNG, will use default PNG image if possible')
            return s
        self.im_n_frames = n_frames
        self.im_info['loop'] = i32(s, 4)
        self.im_custom_mimetype = 'image/apng'
        return s

    
    def chunk_fcTL(self, pos, length):
        if self.fp is None:
            raise AssertionError
        s = ImageFile._safe_read(self.fp, length)
        if length < 26:
            if ImageFile.LOAD_TRUNCATED_IMAGES:
                return s
            msg = 'APNG contains truncated fcTL chunk'
            raise ValueError(msg)
        seq = i32(s)
        if not (not (self._seq_num is None) or not (seq != 0)) or self._seq_num is not None and self._seq_num != seq - 1:
            msg = 'APNG contains frame sequence errors'
            raise SyntaxError(msg)
        self._seq_num = seq
        height = i32(s, 4)
        width = i32(s, 8)
        py = i32(s, 12)
        px = i32(s, 16)
        im_w, im_h = self.im_size
        if px + width > im_w or py + height > im_h:
            msg = 'APNG contains invalid frames'
            raise SyntaxError(msg)
        self.im_info['bbox'] = (px, py, px + width, py + height)
        delay_den = i16(s, 20)
        delay_num = i16(s, 22)
        if delay_den == 0:
            delay_den = 100
        self.im_info['duration'] = (float(delay_num) / float(delay_den)) * 1000
        self.im_info['disposal'] = s[24]
        self.im_info['blend'] = s[25]
        return s

    
    def chunk_fdAT(self, pos, length):
        if self.fp is None:
            raise AssertionError
        if length < 4:
            if ImageFile.LOAD_TRUNCATED_IMAGES:
                s = ImageFile._safe_read(self.fp, length)
                return s
            msg = 'APNG contains truncated fDAT chunk'
            raise ValueError(msg)
        s = ImageFile._safe_read(self.fp, 4)
        seq = i32(s)
        if self._seq_num != seq - 1:
            msg = 'APNG contains frame sequence errors'
            raise SyntaxError(msg)
        self._seq_num = seq
        return self.chunk_IDAT(pos + 4, length - 4)



def _accept(prefix):
    return prefix.startswith(_MAGIC)


class PngImageFile(ImageFile.ImageFile):
    format = 'PNG'
    format_description = 'Portable network graphics'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        if not _accept(self.fp.read(8)):
            msg = 'not a PNG file'
            raise SyntaxError(msg)
        self._fp = self.fp
        self._PngImageFile__frame = 0
        self.private_chunks = []
        self.png = PngStream(self.fp)
        (cid, pos, length) = self.png.read()
        
        try:
            s = self.png.call(cid, pos, length)
        except EOFError:
            pass
        except AttributeError:
            logger.debug('%r %s %s (unknown)', cid, pos, length)
            s = ImageFile._safe_read(self.fp, length)
            if cid[slice(1, 2, None)].islower():
                self.private_chunks.append((cid, s))

        self.png.crc(cid, s)
        self._mode = self.png.im_mode
        self._size = self.png.im_size
        self.info = self.png.im_info
        self._text = None
        self.tile = self.png.im_tile
        self.custom_mimetype = self.png.im_custom_mimetype
        self.n_frames = self.png.im_n_frames or 1
        self.default_image = self.info.get('default_image', False)
        if self.png.im_palette:
            rawmode, data = self.png.im_palette
            self.palette = ImagePalette.raw(rawmode, data)
        if cid == b'fdAT':
            self._PngImageFile__prepare_idat = length - 4
        else:
            self._PngImageFile__prepare_idat = length
        if self.png.im_n_frames is not None:
            self._close_exclusive_fp_after_loading = False
            self.png.save_rewind()
            self._PngImageFile__rewind_idat = self._PngImageFile__prepare_idat
            self._PngImageFile__rewind = self._fp.tell()
            if self.default_image:
                self.n_frames += 1
            self._seek(0)
        self.is_animated = self.n_frames > 1

    text = (lambda self: if self._text is None:
if self.is_animated:
frame = self._PngImageFile__frameself.seek(self.n_frames - 1)self.load()if self.is_animated:
self.seek(frame)if self._text is None:
raise AssertionErrorself._text)()
    
    def verify(self):
        '''Verify PNG file'''
        if self.fp is None:
            msg = 'verify must be called directly after open'
            raise RuntimeError(msg)
        self.fp.seek(self.tile[0][2] - 8)
        if self.png is None:
            raise AssertionError
        self.png.verify()
        self.png.close()
        # unsupported opcode LOAD_SUPER_ATTR
        self()
        return None
    # WARNING: Decompyle incomplete

    
    def seek(self, frame):
        if not self._seek_check(frame):
            return None
        if frame < self._PngImageFile__frame:
            self._seek(0, True)
        last_frame = self._PngImageFile__frame
        
        try:
            for f in range(self._PngImageFile__frame + 1, frame + 1):
                self._seek(f)
        except EOFError as e:
            self.seek(last_frame)
            msg = 'no more images in APNG file'
            raise EOFError(msg) from e


    
    def _seek(self, frame, rewind = False):
        if self.png is None:
            raise AssertionError
        if isinstance(self._fp, DeferredError):
            raise self._fp.ex
        self
        dispose_extent = None
        if frame == 0:
            if rewind:
                self._fp.seek(self._PngImageFile__rewind)
                self.png.rewind()
                self._PngImageFile__prepare_idat = self._PngImageFile__rewind_idat
                self._im = None
                self.info = self.png.im_info
                self.tile = self.png.im_tile
                self.fp = self._fp
            self._prev_im = None
            self.dispose = None
            self.default_image = self.info.get('default_image', False)
            self.dispose_op = self.info.get('disposal')
            self.blend_op = self.info.get('blend')
            dispose_extent = self.info.get('bbox')
            self._PngImageFile__frame = 0
        elif frame != self._PngImageFile__frame + 1:
            msg = f'''cannot seek to frame {frame}'''
            raise ValueError(msg)
        self.load()
        if self.dispose:
            self.im.paste(self.dispose, self.dispose_extent)
        self._prev_im = self.im.copy()
        self.fp = self._fp
        if self._PngImageFile__prepare_idat:
            ImageFile._safe_read(self.fp, self._PngImageFile__prepare_idat)
            self._PngImageFile__prepare_idat = 0
        frame_start = False
        self.fp.read(4)
        
        try:
            (cid, pos, length) = self.png.read()
        except (struct.error, SyntaxError):
            pass
        except:
            pass

        if cid == b'IEND':
            msg = 'No more images in APNG file'
            raise EOFError(msg)
        if cid == b'fcTL':
            if frame_start:
                msg = 'APNG missing frame data'
                raise SyntaxError(msg)
            frame_start = True
        
        try:
            self.png.call(cid, pos, length)
        except UnicodeDecodeError:
            pass
        except EOFError:
            if cid == b'fdAT':
                length -= 4
                if frame_start:
                    self._PngImageFile__prepare_idat = length
                else:
                    ImageFile._safe_read(self.fp, length)
        except AttributeError:
            logger.debug('%r %s %s (unknown)', cid, pos, length)
            ImageFile._safe_read(self.fp, length)

        if dispose_extent:
            self.dispose_extent = dispose_extent
        if self._prev_im is None and self.dispose_op == Disposal.OP_PREVIOUS:
            self.dispose_op = Disposal.OP_BACKGROUND
        self.dispose = None
        if self.dispose_op == Disposal.OP_PREVIOUS:
            if self._prev_im:
                self.dispose = self._prev_im.copy()
                self.dispose = self._crop(self.dispose, self.dispose_extent)
                return None
            return None
        if self.dispose_op == Disposal.OP_BACKGROUND:
            self.dispose = Image.core.fill(self.mode, self.size)
            self.dispose = self._crop(self.dispose, self.dispose_extent)
            return None

    
    def tell(self):
        return self._PngImageFile__frame

    
    def load_prepare(self):
        '''internal: prepare to read PNG file'''
        if self.info.get('interlace'):
            self.decoderconfig = self.decoderconfig + (1,)
        self._PngImageFile__idat = self._PngImageFile__prepare_idat
        ImageFile.ImageFile.load_prepare(self)

    
    def load_read(self, read_bytes):
        '''internal: read more image data'''
        if self.png is None:
            raise AssertionError
        if self.fp is None:
            raise AssertionError
        while self._PngImageFile__idat == 0:
            self.fp.read(4)
            (cid, pos, length) = self.png.read()
            if cid not in (b'IDAT', b'DDAT', b'fdAT'):
                self.png.push(cid, pos, length)
                return b''
            if cid == b'fdAT':
                
                try:
                    self.png.call(cid, pos, length)
                except EOFError:
                    pass

                self._PngImageFile__idat = length - 4
                continue
            self._PngImageFile__idat = length
        if read_bytes <= 0:
            read_bytes = self._PngImageFile__idat
        else:
            read_bytes = min(read_bytes, self._PngImageFile__idat)
        self._PngImageFile__idat = self._PngImageFile__idat - read_bytes
        return self.fp.read(read_bytes)

    
    def load_end(self):
        '''internal: finished reading image data'''
        if self.png is None:
            raise AssertionError
        if self.fp is None:
            raise AssertionError
        if self._PngImageFile__idat != 0:
            self.fp.read(self._PngImageFile__idat)
        self.fp.read(4)
        
        try:
            (cid, pos, length) = self.png.read()
        except (struct.error, SyntaxError):
            pass

        if cid == b'IEND':
            pass
        elif cid == b'fcTL' and self.is_animated:
            self._PngImageFile__prepare_idat = 0
            self.png.push(cid, pos, length)
        else:
            
            try:
                self.png.call(cid, pos, length)
            except UnicodeDecodeError:
                pass

        self._text = self.png.im_text
        if not self.is_animated:
            self.png.close()
            self.png = None
            return None
        if self._prev_im:
            if self.blend_op == Blend.OP_OVER:
                updated = self._crop(self.im, self.dispose_extent)
                if self.im.mode == 'RGB' and 'transparency' in self.info:
                    mask = updated.convert_transparent('RGBA', self.info['transparency'])
                elif self.im.mode == 'P' and 'transparency' in self.info:
                    t = self.info['transparency']
                    if isinstance(t, bytes):
                        updated.putpalettealphas(t)
                    elif isinstance(t, int):
                        updated.putpalettealpha(t)
                mask = updated.convert('RGBA')
                self._prev_im.paste(updated, self.dispose_extent, mask)
                self.im = self._prev_im
                return None
            return None

    
    def _getexif(self):
        '''exif'''
        if 'exif' not in self.info:
            self.load()
        if 'exif' not in self.info and 'Raw profile type exif' not in self.info:
            return None
        return self.getexif()._get_merged_dict()

    
    def getexif(self):
        '''exif'''
        if 'exif' not in self.info:
            self.load()
        # unsupported opcode LOAD_SUPER_ATTR
        return self()
    # WARNING: Decompyle incomplete


_OUTMODES = {
    'RGBA': ('RGBA', b'\x08', b'\x06'),
    'RGB': ('RGB', b'\x08', b'\x02'),
    'P': ('P', b'\x08', b'\x03'),
    'P;4': ('P;4', b'\x04', b'\x03'),
    'P;2': ('P;2', b'\x02', b'\x03'),
    'P;1': ('P;1', b'\x01', b'\x03'),
    'I;16B': ('I;16B', b'\x10', b'\x00'),
    'I;16': ('I;16B', b'\x10', b'\x00'),
    'I': ('I;16B', b'\x10', b'\x00'),
    'LA': ('LA', b'\x08', b'\x04'),
    'L': ('L', b'\x08', b'\x00'),
    'L;4': ('L;4', b'\x04', b'\x00'),
    'L;2': ('L;2', b'\x02', b'\x00'),
    'L;1': ('L;1', b'\x01', b'\x00'),
    '1': ('1', b'\x01', b'\x00') }

def putchunk(fp, cid, *data):
    '''Write a PNG chunk (including CRC field)'''
    byte_data = b''.join(data)
    fp.write(o32(len(byte_data)) + cid)
    fp.write(byte_data)
    crc = _crc32(byte_data, _crc32(cid))
    fp.write(o32(crc))


class _idat:
    
    def __init__(self, fp, chunk):
        self.fp = fp
        self.chunk = chunk

    
    def write(self, data):
        b'''IDAT'''
        self.chunk(self.fp, b'IDAT', data)



class _fdat:
    
    def __init__(self, fp, chunk, seq_num):
        self.fp = fp
        self.chunk = chunk
        self.seq_num = seq_num

    
    def write(self, data):
        b'''fdAT'''
        self.chunk(self.fp, b'fdAT', o32(self.seq_num), data)
        self.seq_num += 1



def _apply_encoderinfo(im, encoderinfo):
    '''optimize'''
    im.encoderconfig = (encoderinfo.get('optimize', False), encoderinfo.get('compress_level', -1), encoderinfo.get('compress_type', -1), encoderinfo.get('dictionary', b''))


class _Frame(NamedTuple):
    encoderinfo: 'dict[str, Any]' = '_Frame'


def _write_multiple_frames(im, fp, chunk, mode, rawmode, default_image, append_images):
    '''duration'''
    duration = im.encoderinfo.get('duration')
    loop = im.encoderinfo.get('loop', im.info.get('loop', 0))
    disposal = im.encoderinfo.get('disposal', im.info.get('disposal', Disposal.OP_NONE))
    blend = im.encoderinfo.get('blend', im.info.get('blend', Blend.OP_SOURCE))
    if default_image:
        chain = itertools.chain(append_images)
    else:
        chain = itertools.chain([
            im], append_images)
    im_frames = []
    frame_count = 0
    for im_seq in chain:
        for im_frame in ImageSequence.Iterator(im_seq):
            if im_frame.mode == mode:
                im_frame = im_frame.copy()
            else:
                im_frame = im_frame.convert(mode)
            encoderinfo = im.encoderinfo.copy()
            if isinstance(duration, (list, tuple)):
                encoderinfo['duration'] = duration[frame_count]
            elif duration is None and 'duration' in im_frame.info:
                encoderinfo['duration'] = im_frame.info['duration']
            if isinstance(disposal, (list, tuple)):
                encoderinfo['disposal'] = disposal[frame_count]
            if isinstance(blend, (list, tuple)):
                encoderinfo['blend'] = blend[frame_count]
            frame_count += 1
            if im_frames:
                previous = im_frames[-1]
                prev_disposal = previous.encoderinfo.get('disposal')
                prev_blend = previous.encoderinfo.get('blend')
                if prev_disposal == Disposal.OP_PREVIOUS and len(im_frames) < 2:
                    prev_disposal = Disposal.OP_BACKGROUND
                if prev_disposal == Disposal.OP_BACKGROUND:
                    base_im = previous.im.copy()
                    dispose = Image.core.fill('RGBA', im.size, (0, 0, 0, 0))
                    bbox = previous.bbox
                    if bbox:
                        dispose = dispose.crop(bbox)
                    else:
                        bbox = (0, 0) + im.size
                    base_im.paste(dispose, bbox)
                elif prev_disposal == Disposal.OP_PREVIOUS:
                    base_im = im_frames[-2].im
                else:
                    base_im = previous.im
                delta = ImageChops.subtract_modulo(im_frame.convert('RGBA'), base_im.convert('RGBA'))
                bbox = delta.getbbox(alpha_only = False)
                if not bbox and prev_disposal == encoderinfo.get('disposal') and prev_blend == encoderinfo.get('blend') and 'duration' in encoderinfo:
                    previous.encoderinfo['duration'] += encoderinfo['duration']
                    continue
            else:
                bbox = None
            im_frames.append(_Frame(im_frame, bbox, encoderinfo))
    if len(im_frames) == 1 and not default_image:
        return im_frames[0].im
    chunk(fp, b'acTL', o32(len(im_frames)), o32(loop))
    if default_image:
        default_im = im if im.mode == mode else im.convert(mode)
        _apply_encoderinfo(default_im, im.encoderinfo)
        ImageFile._save(default_im, cast(IO[bytes], _idat(fp, chunk)), [
            ImageFile._Tile('zip', (0, 0) + im.size, 0, rawmode)])
    seq_num = 0
    for frame, frame_data in enumerate(im_frames):
        im_frame = frame_data.im
        if not frame_data.bbox:
            bbox = (0, 0) + im_frame.size
        else:
            bbox = frame_data.bbox
            im_frame = im_frame.crop(bbox)
        size = im_frame.size
        encoderinfo = frame_data.encoderinfo
        frame_duration = encoderinfo.get('duration', 0)
        delay = Fraction(frame_duration / 1000).limit_denominator(65535)
        if delay.numerator > 65535:
            msg = 'cannot write duration'
            raise ValueError(msg)
        frame_disposal = encoderinfo.get('disposal', disposal)
        frame_blend = encoderinfo.get('blend', blend)
        chunk(fp, b'fcTL', o32(seq_num), o32(size[0]), o32(size[1]), o32(bbox[0]), o32(bbox[1]), o16(delay.numerator), o16(delay.denominator), o8(frame_disposal), o8(frame_blend))
        seq_num += 1
        _apply_encoderinfo(im_frame, im.encoderinfo)
        if frame == 0 and not default_image:
            ImageFile._save(im_frame, cast(IO[bytes], _idat(fp, chunk)), [
                ImageFile._Tile('zip', (0, 0) + im_frame.size, 0, rawmode)])
            continue
        fdat_chunks = _fdat(fp, chunk, seq_num)
        ImageFile._save(im_frame, cast(IO[bytes], fdat_chunks), [
            ImageFile._Tile('zip', (0, 0) + im_frame.size, 0, rawmode)])
        seq_num = fdat_chunks.seq_num


def _save_all(im, fp, filename):
    _save(im, fp, filename, save_all = True)


def _save(im, fp, filename, chunk = putchunk, save_all = False):
    '''default_image'''
    if save_all:
        default_image = im.encoderinfo.get('default_image', im.info.get('default_image'))
        modes = set()
        sizes = set()
        append_images = im.encoderinfo.get('append_images', [])
        for im_seq in itertools.chain([
            im], append_images):
            for im_frame in ImageSequence.Iterator(im_seq):
                modes.add(im_frame.mode)
                sizes.add(im_frame.size)
        for mode in ('RGBA', 'RGB', 'P'):
            while not mode in modes:
                pass
            ('RGBA', 'RGB', 'P')
        mode = modes.pop()
        if tuple is tuple:
            tuple
            for None in range(2)():
                pass
            # unsupported CALL_INTRINSIC_1 6
        
        size = (lambda .0: for None in .0:
i = None(lambda .0: for frame_size in .0:
frame_size[i].0)(sizes())
)(range(2)())
    else:
        size = im.size
        mode = im.mode
    outmode = mode
    palette = []
    if im.palette:
        palette = im.getpalette() or []
    if mode == 'P':
        if 'bits' in im.encoderinfo:
            colors = min(1 << im.encoderinfo['bits'], 256)
        elif im.palette:
            colors = max(min(len(palette) // 3, 256), 1)
        else:
            colors = 256
        if colors <= 16:
            if colors <= 2:
                bits = 1
            elif colors <= 4:
                bits = 2
            else:
                bits = 4
            outmode += f''';{bits}'''
    
    try:
        (rawmode, bit_depth, color_type) = _OUTMODES[outmode]
    except KeyError as e:
        msg = f'''cannot write mode {mode} as PNG'''
        raise OSError(msg) from e

    if outmode == 'I':
        deprecate('Saving I mode images as PNG', 13, stacklevel = 4)
    fp.write(_MAGIC)
    chunk(fp, b'IHDR', o32(size[0]), o32(size[1]), bit_depth, color_type, b'\x00', b'\x00', b'\x00')
    chunks = [
        b'cHRM',
        b'cICP',
        b'gAMA',
        b'sBIT',
        b'sRGB',
        b'tIME']
    icc = im.encoderinfo.get('icc_profile', im.info.get('icc_profile'))
    if im.encoderinfo.get('icc_profile', im.info.get('icc_profile')):
        name = b'ICC Profile'
        data = name + b'\x00\x00' + zlib.compress(icc)
        chunk(fp, b'iCCP', data)
        chunks.remove(b'sRGB')
    info = im.encoderinfo.get('pnginfo')
    if im.encoderinfo.get('pnginfo'):
        chunks_multiple_allowed = [
            b'sPLT',
            b'iTXt',
            b'tEXt',
            b'zTXt']
        for info_chunk in info.chunks:
            (cid, data) = info_chunk[slice(None, 2, None)]
            while cid in chunks:
                chunks.remove(cid)
                chunk(fp, cid, data)
            if cid in chunks_multiple_allowed:
                chunk(fp, cid, data)
                continue
            if not cid[slice(1, 2, None)].islower():
                continue
            after_idat = len(info_chunk) == 3 and info_chunk[2]
            if after_idat:
                continue
            chunk(fp, cid, data)
    if im.mode == 'P':
        palette_byte_number = colors * 3
        palette_bytes = bytes(palette[:palette_byte_number])
        while len(palette_bytes) < palette_byte_number:
            palette_bytes += b'\x00'
        chunk(fp, b'PLTE', palette_bytes)
    transparency = im.encoderinfo.get('transparency', im.info.get('transparency'))
    if transparency is not None:
        if im.mode == 'P':
            alpha_bytes = colors
            if isinstance(transparency, bytes):
                chunk(fp, b'tRNS', transparency[:alpha_bytes])
            elif isinstance(transparency, int):
                transparency = max(0, min(255, transparency))
                alpha = b'\xff' * transparency + b'\x00'
                chunk(fp, b'tRNS', alpha[:alpha_bytes])
            else:
                msg = 'transparency for P must be an integer or bytes'
                raise ValueError(msg)
        if im.mode in ('1', 'L', 'I', 'I;16'):
            if isinstance(transparency, int):
                transparency = max(0, min(65535, transparency))
                chunk(fp, b'tRNS', o16(transparency))
            else:
                msg = f'''transparency for {im.mode} must be an integer'''
                raise ValueError(msg)
        if im.mode == 'RGB':
            if not isinstance(transparency, (list, tuple)):
                msg = 'transparency for RGB must be list or tuple'
                raise ValueError(msg)
            if len(transparency) != 3:
                msg = 'transparency for RGB must have length 3'
                raise ValueError(msg)
            (red, green, blue) = transparency
            chunk(fp, b'tRNS', o16(red) + o16(green) + o16(blue))
        elif im.encoderinfo.get('transparency') is not None:
            msg = 'cannot use transparency for this mode'
            raise OSError(msg)
    elif im.mode == 'P' and im.im.getpalettemode() == 'RGBA':
        alpha = im.im.getpalette('RGBA', 'A')
        alpha_bytes = colors
        chunk(fp, b'tRNS', alpha[:alpha_bytes])
    dpi = im.encoderinfo.get('dpi')
    if im.encoderinfo.get('dpi'):
        chunk(fp, b'pHYs', o32(int(dpi[0] / 0.0254 + 0.5)), o32(int(dpi[1] / 0.0254 + 0.5)), b'\x01')
    if info:
        chunks = [
            b'bKGD',
            b'hIST']
        for info_chunk in info.chunks:
            (cid, data) = info_chunk[slice(None, 2, None)]
            while not cid in chunks:
                pass
            chunks.remove(cid)
            chunk(fp, cid, data)
    exif = im.encoderinfo.get('exif')
    if im.encoderinfo.get('exif'):
        if isinstance(exif, Image.Exif):
            exif = exif.tobytes(8)
        if exif.startswith(b'Exif\x00\x00'):
            exif = exif[slice(6, None, None)]
        chunk(fp, b'eXIf', exif)
    single_im = im
    if save_all:
        single_im = _write_multiple_frames(im, fp, chunk, mode, rawmode, default_image, append_images)
    if single_im:
        _apply_encoderinfo(single_im, im.encoderinfo)
        ImageFile._save(single_im, cast(IO[bytes], _idat(fp, chunk)), [
            ImageFile._Tile('zip', (0, 0) + single_im.size, 0, rawmode)])
    if info:
        for info_chunk in info.chunks:
            (cid, data) = info_chunk[slice(None, 2, None)]
            if not cid[slice(1, 2, None)].islower():
                continue
            after_idat = len(info_chunk) == 3 and info_chunk[2]
            if not after_idat:
                continue
            chunk(fp, cid, data)
    chunk(fp, b'IEND', b'')
    if hasattr(fp, 'flush'):
        fp.flush()
        return None
    return None
# WARNING: Decompyle incomplete


def getchunks(im, **params):
    '''Return a list of PNG chunks representing this image.'''
    from io import BytesIO
    chunks = []
    
    def append(fp, cid, *data):
        b''
        byte_data = b''.join(data)
        crc = o32(_crc32(byte_data, _crc32(cid)))
        chunks.append((cid, byte_data, crc))

    fp = BytesIO()
    
    try:
        im.encoderinfo = params
        _save(im, fp, '', append)
        return chunks
    finally:
        del im.encoderinfo


Image.register_open(PngImageFile.format, PngImageFile, _accept)
Image.register_save(PngImageFile.format, _save)
Image.register_save_all(PngImageFile.format, _save_all)
Image.register_extensions(PngImageFile.format, [
    '.png',
    '.apng'])
Image.register_mime(PngImageFile.format, 'image/png')
