# Source Generated with Decompyle++
# File: QoiImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import os
from typing import IO
from . import Image, ImageFile
from ._binary import i32be as i32
from ._binary import o8
from ._binary import o32be as o32

def _accept(prefix):
    b'''qoif'''
    return prefix.startswith(b'qoif')


class QoiImageFile(ImageFile.ImageFile):
    format = 'QOI'
    format_description = 'Quite OK Image'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        if not _accept(self.fp.read(4)):
            msg = 'not a QOI file'
            raise SyntaxError(msg)
        self._size = (i32(self.fp.read(4)), i32(self.fp.read(4)))
        channels = self.fp.read(1)[0]
        self._mode = 'RGB' if channels == 3 else 'RGBA'
        self.fp.seek(1, os.SEEK_CUR)
        self.tile = [
            ImageFile._Tile('qoi', (0, 0) + self._size, self.fp.tell())]



class QoiDecoder(ImageFile.PyDecoder):
    _pulls_fd = True
    _previous_pixel: 'bytes | bytearray | None' = None
    _previously_seen_pixels: 'dict[int, bytes | bytearray]' = { }
    
    def _add_to_previous_pixels(self, value):
        self._previous_pixel = value
        r, g, b, a = value
        hash_value = (r * 3 + g * 5 + b * 7 + a * 11) % 64
        self._previously_seen_pixels[hash_value] = value

    
    def decode(self, buffer):
        if self.fd is None:
            raise AssertionError
        self._previously_seen_pixels = { }
        self._previous_pixel = bytearray((0, 0, 0, 255))
        data = bytearray()
        bands = Image.getmodebands(self.mode)
        dest_length = self.state.xsize * self.state.ysize * bands
        while len(data) < dest_length:
            byte = self.fd.read(1)[0]
            if byte == 254 and self._previous_pixel:
                value = bytearray(self.fd.read(3)) + self._previous_pixel[slice(3, None, None)]
            elif byte == 255:
                value = self.fd.read(4)
            else:
                op = byte >> 6
                if op == 0:
                    op_index = byte & 63
                    value = self._previously_seen_pixels.get(op_index, bytearray((0, 0, 0, 0)))
                elif op == 1 and self._previous_pixel:
                    value = bytearray(((self._previous_pixel[0] + ((byte & 48) >> 4) - 2) % 256, (self._previous_pixel[1] + ((byte & 12) >> 2) - 2) % 256, (self._previous_pixel[2] + (byte & 3) - 2) % 256, self._previous_pixel[3]))
                elif op == 2 and self._previous_pixel:
                    second_byte = self.fd.read(1)[0]
                    diff_green = (byte & 63) - 32
                    diff_red = ((second_byte & 240) >> 4) - 8
                    diff_blue = (second_byte & 15) - 8
                    if tuple is tuple:
                        tuple
                        for None in enumerate((diff_red, 0, diff_blue))():
                            pass
                        # unsupported CALL_INTRINSIC_1 6
                    
                    value = (lambda .0: for i, diff in .0:
(self._previous_pixel[i] + diff_green + diff) % 256.0)((lambda .0: for i, diff in .0:
(self._previous_pixel[i] + diff_green + diff) % 256.0)(enumerate((diff_red, 0, diff_blue))()))
                    value += self._previous_pixel[slice(3, None, None)]
                elif op == 3 and self._previous_pixel:
                    run_length = (byte & 63) + 1
                    value = self._previous_pixel
                    if bands == 3:
                        value = value[slice(None, 3, None)]
                    data += value * run_length
                    continue
            self._add_to_previous_pixels(value)
            if bands == 3:
                value = value[slice(None, 3, None)]
            data += value
        self.set_as_raw(data)
        return (-1, 0)
    # WARNING: Decompyle incomplete



def _save(im, fp, filename):
    '''RGB'''
    if im.mode == 'RGB':
        channels = 3
    elif im.mode == 'RGBA':
        channels = 4
    else:
        msg = 'Unsupported QOI image mode'
        raise ValueError(msg)
    colorspace = 0 if im.encoderinfo.get('colorspace') == 'sRGB' else 1
    fp.write(b'qoif')
    fp.write(o32(im.size[0]))
    fp.write(o32(im.size[1]))
    fp.write(o8(channels))
    fp.write(o8(colorspace))
    ImageFile._save(im, fp, [
        ImageFile._Tile('qoi', (0, 0) + im.size)])


class QoiEncoder(ImageFile.PyEncoder):
    _pushes_fd = True
    _previous_pixel: 'tuple[int, int, int, int] | None' = None
    _previously_seen_pixels: 'dict[int, tuple[int, int, int, int]]' = { }
    _run = 0
    
    def _write_run(self):
        data = o8(192 | self._run - 1)
        self._run = 0
        return data

    
    def _delta(self, left, right):
        result = left - right & 255
        if result >= 128:
            result -= 256
        return result

    
    def encode(self, bufsize):
        if self.im is None:
            raise AssertionError
        self._previously_seen_pixels = {
            0: (0, 0, 0, 0) }
        self._previous_pixel = (0, 0, 0, 255)
        data = bytearray()
        w, h = self.im.size
        bands = Image.getmodebands(self.mode)
        for y in range(h):
            for x in range(w):
                pixel = self.im.getpixel((x, y))
                if bands == 3:
                    # unsupported CALL_INTRINSIC_1 6
                    pixel = range(w)[255]
                if pixel == self._previous_pixel:
                    self._run += 1
                    if self._run == 62:
                        data += self._write_run()
                elif self._run:
                    data += self._write_run()
                r, g, b, a = pixel
                hash_value = (r * 3 + g * 5 + b * 7 + a * 11) % 64
                if self._previously_seen_pixels.get(hash_value) == pixel:
                    data += o8(hash_value)
                elif self._previous_pixel:
                    self._previously_seen_pixels[hash_value] = pixel
                    (prev_r, prev_g, prev_b, prev_a) = self._previous_pixel
                    if prev_a == a:
                        delta_r = self._delta(r, prev_r)
                        delta_g = self._delta(g, prev_g)
                        delta_b = self._delta(b, prev_b)
                        if -2 <= delta_r and delta_r < 2 and -2 <= delta_g and delta_g < 2 and -2 <= delta_b and delta_b < 2:
                            data += o8(64 | delta_r + 2 << 4 | delta_g + 2 << 2 | delta_b + 2)
                        else:
                            delta_gr = self._delta(delta_r, delta_g)
                            delta_gb = self._delta(delta_b, delta_g)
                            if -8 <= delta_gr and delta_gr < 8 and -32 <= delta_g and delta_g < 32 and -8 <= delta_gb and delta_gb < 8:
                                data += o8(128 | delta_g + 32)
                                data += o8(delta_gr + 8 << 4 | delta_gb + 8)
                            else:
                                data += o8(254)
                                data += bytes(pixel[slice(None, 3, None)])
                    else:
                        data += o8(255)
                        data += bytes(pixel)
                self._previous_pixel = pixel
        if self._run:
            data += self._write_run()
        data += bytes((0, 0, 0, 0, 0, 0, 0, 1))
        return (len(data), 0, bytes(data))
    # WARNING: Decompyle incomplete


Image.register_open(QoiImageFile.format, QoiImageFile, _accept)
Image.register_decoder('qoi', QoiDecoder)
Image.register_extension(QoiImageFile.format, '.qoi')
Image.register_save(QoiImageFile.format, _save)
Image.register_encoder('qoi', QoiEncoder)
