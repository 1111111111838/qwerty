# Source Generated with Decompyle++
# File: FitsImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import gzip
import math
from . import Image, ImageFile

def _accept(prefix):
    b'''SIMPLE'''
    return prefix.startswith(b'SIMPLE')


class FitsImageFile(ImageFile.ImageFile):
    format = 'FITS'
    format_description = 'FITS'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        headers = { }
        header_in_progress = False
        decoder_name = ''
        header = self.fp.read(80)
        if not header:
            msg = 'Truncated FITS file'
            raise OSError(msg)
        keyword = header[slice(None, 8, None)].strip()
        if keyword in (b'SIMPLE', b'XTENSION'):
            header_in_progress = True
        elif headers and not header_in_progress:
            pass
        elif keyword == b'END':
            self.fp.seek(math.ceil(self.fp.tell() / 2880) * 2880)
            if not decoder_name:
                (decoder_name, offset, args) = self._parse_headers(headers)
            header_in_progress = False
        if decoder_name:
            pass
        value = header[slice(8, None, None)].split(b'/')[0].strip()
        if value.startswith(b'='):
            value = value[slice(1, None, None)].strip()
        if not headers:
            if not _accept(keyword) or value != b'T':
                msg = 'Not a FITS file'
                raise SyntaxError(msg)
        headers[keyword] = value
        if not decoder_name:
            msg = 'No image data'
            raise ValueError(msg)
        offset += self.fp.tell() - 80
        self.tile = [
            ImageFile._Tile(decoder_name, (0, 0) + self.size, offset, args)]

    
    def _get_size(self, headers, prefix):
        b'''NAXIS'''
        naxis = int(headers[prefix + b'NAXIS'])
        if naxis == 0:
            return None
        if naxis == 1:
            return (1, int(headers[prefix + b'NAXIS1']))
        return (int(headers[prefix + b'NAXIS1']), int(headers[prefix + b'NAXIS2']))

    
    def _parse_headers(self, headers):
        b''
        prefix = b''
        decoder_name = 'raw'
        offset = 0
        if headers.get(b'XTENSION') == b"'BINTABLE'" and headers.get(b'ZIMAGE') == b'T' and headers[b'ZCMPTYPE'] == b"'GZIP_1  '":
            no_prefix_size = self._get_size(headers, prefix) or (0, 0)
            number_of_bits = int(headers[b'BITPIX'])
            offset = no_prefix_size[0] * no_prefix_size[1] * (number_of_bits // 8)
            prefix = b'Z'
            decoder_name = 'fits_gzip'
        size = self._get_size(headers, prefix)
        if not size:
            return ('', 0, ())
        self._size = size
        number_of_bits = int(headers[prefix + b'BITPIX'])
        if number_of_bits == 8:
            self._mode = 'L'
        elif number_of_bits == 16:
            self._mode = 'I;16'
        elif number_of_bits == 32:
            self._mode = 'I'
        elif number_of_bits in (-32, -64):
            self._mode = 'F'
        if decoder_name == 'raw':
            args = (self.mode, 0, -1)
        else:
            args = (number_of_bits,)
        return (decoder_name, offset, args)



class FitsGzipDecoder(ImageFile.PyDecoder):
    _pulls_fd = True
    
    def decode(self, buffer):
        if self.fd is None:
            raise AssertionError
        with gzip.open(self.fd) as fp:
            value = fp.read(self.state.xsize * self.state.ysize * 4)
            rows = []
            offset = 0
            number_of_bits = min(self.args[0] // 8, 4)
            for y in range(self.state.ysize):
                row = bytearray()
                for x in range(self.state.xsize):
                    row += value[offset + (4 - number_of_bits):offset + 4]
                    offset += 4
                rows.append(row)
        for row in rows[::-1]:
            self.set_as_raw(bytes([]))
            return (-1, 0)


Image.register_open(FitsImageFile.format, FitsImageFile, _accept)
Image.register_decoder('fits_gzip', FitsGzipDecoder)
Image.register_extensions(FitsImageFile.format, [
    '.fit',
    '.fits'])
