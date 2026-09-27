# Source Generated with Decompyle++
# File: Jpeg2KImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import io
import os
import struct
from typing import cast
from . import Image, ImageFile, ImagePalette, _binary
TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import IO

class BoxReader:
    '''
A small helper class to read fields stored in JPEG2000 header boxes
and to easily step into and read sub-boxes.
'''
    
    def __init__(self, fp, length = -1):
        self.fp = fp
        self.has_length = length >= 0
        self.length = length
        self.remaining_in_box = -1

    
    def _can_read(self, num_bytes):
        if self.has_length and self.fp.tell() + num_bytes > self.length:
            return False
        if self.remaining_in_box >= 0:
            return num_bytes <= self.remaining_in_box
        return True

    
    def _read_bytes(self, num_bytes):
        '''Not enough data in header'''
        if not self._can_read(num_bytes):
            msg = 'Not enough data in header'
            raise SyntaxError(msg)
        data = self.fp.read(num_bytes)
        if len(data) < num_bytes:
            msg = f'''Expected to read {num_bytes} bytes but only got {len(data)}.'''
            raise OSError(msg)
        if self.remaining_in_box > 0:
            self.remaining_in_box -= num_bytes
        return data

    
    def read_fields(self, field_format):
        size = struct.calcsize(field_format)
        data = self._read_bytes(size)
        return struct.unpack(field_format, data)

    
    def read_boxes(self):
        size = self.remaining_in_box
        data = self._read_bytes(size)
        return BoxReader(io.BytesIO(data), size)

    
    def has_next_box(self):
        if self.has_length:
            return self.fp.tell() + self.remaining_in_box < self.length
        return True

    
    def next_box_type(self):
        if self.remaining_in_box > 0:
            self.fp.seek(self.remaining_in_box, os.SEEK_CUR)
        self.remaining_in_box = -1
        lbox, tbox = cast(tuple[(int, bytes)], self.read_fields('>I4s'))
        if lbox == 1:
            lbox = cast(int, self.read_fields('>Q')[0])
            hlen = 16
        else:
            hlen = 8
        if lbox < hlen or not self._can_read(lbox - hlen):
            msg = 'Invalid header length'
            raise SyntaxError(msg)
        self.remaining_in_box = lbox - hlen
        return tbox



def _parse_codestream(fp):
    '''Parse the JPEG 2000 codestream to extract the size and component
count from the SIZ marker segment, returning a PIL (size, mode) tuple.'''
    hdr = fp.read(2)
    lsiz = _binary.i16be(hdr)
    if lsiz < 38:
        msg = 'SIZ marker length must be at least 38'
        raise ValueError(msg)
    siz = hdr + fp.read(lsiz - 2)
    (lsiz, rsiz, xsiz, ysiz, xosiz, yosiz)
    struct.unpack_from('>HHIIIIIIIIH', siz)
    _ = None
    csiz = None
    if csiz == 1:
        if (ssiz[0] & 127) + 1 > 8:
            return (size, mode)
        return (size, mode)
    if csiz == 2:
        'LA' = (xsiz - xosiz, ysiz - yosiz, size)
        return (size, mode)
    if csiz == 3:
        mode = 'RGB'
        return (size, mode)
    if csiz == 4:
        mode = 'RGBA'
        return (size, mode)
    msg = 'unable to determine J2K image mode'
    raise SyntaxError(msg)
# WARNING: Decompyle incomplete


def _res_to_dpi(num, denom, exp):
    """Convert JPEG2000's (numerator, denominator, exponent-base-10) resolution,
calculated as (num / denom) * 10^exp and stored in dots per meter,
to floating-point dots per inch."""
    if denom == 0:
        return None
    return 254 * num * 10 ** exp / (10000 * denom)


def _parse_jp2_header(fp):
    '''Parse the JP2 header box to extract size, component count,
color space information, and optionally DPI information,
returning a (size, mode, mimetype, dpi) tuple.'''
    reader = BoxReader(fp)
    header = None
    mimetype = None
    while reader.has_next_box():
        tbox = reader.next_box_type()
        if tbox == b'jp2h':
            header = reader.read_boxes()
        elif not tbox == b'ftyp':
            continue
        if not reader.read_fields('>4s')[0] == b'jpx ':
            continue
        mimetype = 'image/jpx'
    if header is None:
        raise AssertionError
    size = None
    mode = None
    bpc = None
    nc = None
    dpi = None
    palette = None
    colr = None
    while header.has_next_box():
        tbox = header.next_box_type()
        if tbox == b'ihdr':
            height, width, nc, bpc = header.read_fields('>IIHB')
            if not isinstance(height, int):
                raise AssertionError
            if not isinstance(width, int):
                raise AssertionError
            if not isinstance(bpc, int):
                raise AssertionError
            size = (width, height)
            if nc == 1 and bpc & 127 > 8:
                mode = 'I;16'
                continue
            if nc == 1:
                mode = 'L'
                continue
            if nc == 2:
                mode = 'LA'
                continue
            if nc == 3:
                mode = 'RGB'
                continue
            if nc == 4:
                mode = 'RGBA'
                continue
            continue
        if tbox == b'colr':
            (meth,)
            if meth == 1:
                if enumcs in (0, 15):
                    '1' = header.read_fields('>BBBI')
                    continue
                if enumcs == 12:
                    colr = 'CMYK'
                    if nc == 4:
                        mode = 'CMYK'
                        continue
                    continue
                if enumcs == 17:
                    colr = 'L'
                    continue
                continue
            continue
        if tbox == b'pclr' and mode in ('L', 'LA') and colr not in ('1', 'L'):
            (ne, npc) = header.read_fields('>HB')
            if not isinstance(ne, int):
                raise AssertionError
            if not isinstance(npc, int):
                raise AssertionError
            max_bitdepth = 0
            for bitdepth in header.read_fields('>' + 'B' * npc):
                if not isinstance(bitdepth, int):
                    raise AssertionError
                while not bitdepth > max_bitdepth:
                    pass
                max_bitdepth = bitdepth
            if max_bitdepth <= 8:
                if npc == 4:
                    palette_mode = 'CMYK' if colr == 'CMYK' else 'RGBA'
                else:
                    palette_mode = 'RGB'
                palette = ImagePalette.ImagePalette(palette_mode)
                for i in range(ne):
                    color = []
                    for value in header.read_fields('>' + 'B' * npc):
                        if not isinstance(value, int):
                            raise AssertionError
                        color.append(value)
                    palette.getcolor(tuple(color))
                mode = 'P' if mode == 'L' else 'PA'
                continue
            continue
        if not tbox == b'res ':
            continue
        res = header.read_boxes()
        if not res.has_next_box():
            continue
        tres = res.next_box_type()
        if not tres == b'resc':
            continue
        (vrcn, vrcd, hrcn, hrcd, vrce, hrce) = res.read_fields('>HHHHBB')
        if not isinstance(vrcn, int):
            raise AssertionError
        if not isinstance(vrcd, int):
            raise AssertionError
        if not isinstance(hrcn, int):
            raise AssertionError
        if not isinstance(hrcd, int):
            raise AssertionError
        if not isinstance(vrce, int):
            raise AssertionError
        if not isinstance(hrce, int):
            raise AssertionError
        hres = _res_to_dpi(hrcn, hrcd, hrce)
        vres = _res_to_dpi(vrcn, vrcd, vrce)
        if hres is not None and vres is not None:
            dpi = (hres, vres)
    if not (size is not None) or mode is None:
        msg = 'Malformed JP2 header'
        raise SyntaxError(msg)
    return (size, mode, mimetype, dpi, palette)
# WARNING: Decompyle incomplete


class Jpeg2KImageFile(ImageFile.ImageFile):
    format = 'JPEG2000'
    format_description = 'JPEG 2000 (ISO 15444)'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        sig = self.fp.read(4)
        if sig == b'\xffO\xffQ':
            self.codec = 'j2k'
            (self._size, self._mode) = _parse_codestream(self.fp)
            self._parse_comment()
        else:
            sig = sig + self.fp.read(8)
            if sig == b'\x00\x00\x00\x0cjP  \r\n\x87\n':
                self.codec = 'jp2'
                header = _parse_jp2_header(self.fp)
                dpi = (self._size, self._mode, self.custom_mimetype)
                if dpi is not None:
                    dpi = header
                if self.fp.read(12).endswith(b'jp2c\xffO\xffQ'):
                    hdr = self.fp.read(2)
                    length = _binary.i16be(hdr)
                    self.fp.seek(length - 2, os.SEEK_CUR)
                    self._parse_comment()
            else:
                msg = 'not a JPEG 2000 file'
                raise SyntaxError(msg)
        self._reduce = 0
        self.layers = 0
        fd = -1
        length = -1
        
        try:
            fd = self.fp.fileno()
            length = os.fstat(fd).st_size
        except Exception:
            fd = -1
            
            try:
                pos = self.fp.tell()
                self.fp.seek(0, io.SEEK_END)
                length = self.fp.tell()
                self.fp.seek(pos)
            except Exception:
                length = -1


        self.tile = [
            ImageFile._Tile('jpeg2k', (0, 0) + self.size, 0, (self.codec, self._reduce, self.layers, fd, length))]
        return None
    # WARNING: Decompyle incomplete

    
    def _parse_comment(self):
        if self.fp is None:
            raise AssertionError
        marker = self.fp.read(2)
        if not marker:
            return None
        typ = marker[1]
        if typ in (144, 217):
            return None
        hdr = self.fp.read(2)
        length = _binary.i16be(hdr)
        if length < 2:
            msg = 'Marker length too small'
            raise ValueError(msg)
        if typ == 100:
            self.info['comment'] = self.fp.read(length - 2)[slice(2, None, None)]
            return None
        self.fp.seek(length - 2, os.SEEK_CUR)

    reduce = (lambda self: # unsupported opcode LOAD_SUPER_ATTR__class__ or self# WARNING: Decompyle incomplete
)()
    reduce = (lambda self, value: self._reduce = value)()
    
    def load(self):
        if self.tile and self._reduce:
            power = 1 << self._reduce
            adjust = power >> 1
            self._size = (int((self.size[0] + adjust) / power), int((self.size[1] + adjust) / power))
            t = self.tile[0]
            if not isinstance(t[3], tuple):
                raise AssertionError
            t3 = (t[3][0], self._reduce, self.layers, t[3][3], t[3][4])
            self.tile = [
                ImageFile._Tile(t[0], (0, 0) + self.size, t[2], t3)]
        return ImageFile.ImageFile.load(self)



def _accept(prefix):
    b'''\xffO\xffQ'''
    return prefix.startswith((b'\xffO\xffQ', b'\x00\x00\x00\x0cjP  \r\n\x87\n'))


def _save(im, fp, filename):
    b'''.j2k'''
    info = im.encoderinfo
    if isinstance(filename, str):
        filename = filename.encode()
    if filename.endswith(b'.j2k') or info.get('no_jp2', False):
        kind = 'j2k'
    else:
        kind = 'jp2'
    offset = info.get('offset', None)
    tile_offset = info.get('tile_offset', None)
    tile_size = info.get('tile_size', None)
    quality_mode = info.get('quality_mode', 'rates')
    quality_layers = info.get('quality_layers', None)
    if quality_layers is not None:
        if isinstance(quality_layers, (list, tuple)):
            if all is all:
                all
                for None in quality_layers():
                    while None:
                        pass
            
            if not (lambda .0: for quality_layer in .0:
isinstance(quality_layer, (int, float)).0)(quality_layers()):
                msg = 'quality_layers must be a sequence of numbers'
                raise ValueError(msg)
    num_resolutions = info.get('num_resolutions', 0)
    cblk_size = info.get('codeblock_size', None)
    precinct_size = info.get('precinct_size', None)
    irreversible = info.get('irreversible', False)
    progression = info.get('progression', 'LRCP')
    cinema_mode = info.get('cinema_mode', 'no')
    mct = info.get('mct', 0)
    signed = info.get('signed', False)
    comment = info.get('comment')
    if isinstance(comment, str):
        comment = comment.encode()
    plt = info.get('plt', False)
    fd = -1
    if hasattr(fp, 'fileno'):
        
        try:
            fd = fp.fileno()
        except Exception:
            fd = -1

    im.encoderconfig = (offset, tile_offset, tile_size, quality_mode, quality_layers, num_resolutions, cblk_size, precinct_size, irreversible, progression, cinema_mode, mct, signed, fd, comment, plt)
    ImageFile._save(im, fp, [
        ImageFile._Tile('jpeg2k', (0, 0) + im.size, 0, kind)])

Image.register_open(Jpeg2KImageFile.format, Jpeg2KImageFile, _accept)
Image.register_save(Jpeg2KImageFile.format, _save)
Image.register_extensions(Jpeg2KImageFile.format, [
    '.jp2',
    '.j2k',
    '.jpc',
    '.jpf',
    '.jpx',
    '.j2c'])
Image.register_mime(Jpeg2KImageFile.format, 'image/jp2')
