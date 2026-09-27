# Source Generated with Decompyle++
# File: IcnsImagePlugin.pyc (Python 3.14)

from __future__ import annotations
import io
import os
import struct
import sys
from typing import IO
from . import Image, ImageFile, PngImagePlugin, features
enable_jpeg2k = features.check_codec('jpg_2000')
if enable_jpeg2k:
    from . import Jpeg2KImagePlugin
MAGIC = b'icns'
HEADERSIZE = 8

def nextheader(fobj):
    '''>4sI'''
    return struct.unpack('>4sI', fobj.read(HEADERSIZE))


def read_32t(fobj, start_length, size):
    start, length = start_length
    fobj.seek(start)
    sig = fobj.read(4)
    if sig != b'\x00\x00\x00\x00':
        msg = 'Unknown signature, expecting 0x00000000'
        raise SyntaxError(msg)
    return read_32(fobj, (start + 4, length - 4), size)


def read_32(fobj, start_length, size):
    '''
Read a 32bit RGB icon resource.  Seems to be either uncompressed or
an RLE packbits-like scheme.
'''
    start, length = start_length
    fobj.seek(start)
    pixel_size = (size[0] * size[2], size[1] * size[2])
    sizesq = pixel_size[0] * pixel_size[1]
    if length == sizesq * 3:
        indata = fobj.read(length)
        im = Image.frombuffer('RGB', pixel_size, indata, 'raw', 'RGB', 0, 1)
        return {
            'RGB': im }
    im = Image.new('RGB', pixel_size, None)
    for band_ix in range(3):
        data = []
        bytesleft = sizesq
        while bytesleft > 0:
            byte = fobj.read(1)
            if not byte:
                pass
            else:
                byte_int = byte[0]
                if byte_int & 128:
                    blocksize = byte_int - 125
                    byte = fobj.read(1)
                    data.extend([
                        byte] * blocksize)
                else:
                    blocksize = byte_int + 1
                    data.append(fobj.read(blocksize))
                bytesleft -= blocksize
                if not bytesleft <= 0:
                    continue
        if bytesleft != 0:
            msg = f'''Error reading channel [{repr(bytesleft)} left]'''
            raise SyntaxError(msg)
        band = Image.frombuffer('L', pixel_size, b''.join(data), 'raw', 'L', 0, 1)
        im.im.putband(band.im, band_ix)
    return {
        'RGB': im }


def read_mk(fobj, start_length, size):
    start = start_length[0]
    fobj.seek(start)
    pixel_size = (size[0] * size[2], size[1] * size[2])
    sizesq = pixel_size[0] * pixel_size[1]
    band = Image.frombuffer('L', pixel_size, fobj.read(sizesq), 'raw', 'L', 0, 1)
    return {
        'A': band }


def read_png_or_jpeg2000(fobj, start_length, size):
    start, length = start_length
    fobj.seek(start)
    sig = fobj.read(12)
    if sig.startswith(b'\x89PNG\r\n\x1a\n'):
        fobj.seek(start)
        im = PngImagePlugin.PngImageFile(fobj)
        Image._decompression_bomb_check(im.size)
        return {
            'RGBA': im }
    if sig.startswith((b'\xffO\xffQ', b'\r\n\x87\n')) or sig == b'\x00\x00\x00\x0cjP  \r\n\x87\n':
        if not enable_jpeg2k:
            msg = 'Unsupported icon subimage format (rebuild PIL with JPEG 2000 support to fix this)'
            raise ValueError(msg)
        fobj.seek(start)
        jp2kstream = fobj.read(length)
        f = io.BytesIO(jp2kstream)
        im = Jpeg2KImagePlugin.Jpeg2KImageFile(f)
        Image._decompression_bomb_check(im.size)
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        return {
            'RGBA': im }
    msg = 'Unsupported icon subimage format'
    raise ValueError(msg)


class IcnsFile:
    SIZES = {
        (16, 16, 1): [
            (b'icp4', read_png_or_jpeg2000),
            (b'is32', read_32),
            (b's8mk', read_mk)],
        (16, 16, 2): [
            (b'ic11', read_png_or_jpeg2000)],
        (32, 32, 1): [
            (b'icp5', read_png_or_jpeg2000),
            (b'il32', read_32),
            (b'l8mk', read_mk)],
        (48, 48, 1): [
            (b'ih32', read_32),
            (b'h8mk', read_mk)],
        (32, 32, 2): [
            (b'ic12', read_png_or_jpeg2000)],
        (64, 64, 1): [
            (b'icp6', read_png_or_jpeg2000)],
        (128, 128, 1): [
            (b'ic07', read_png_or_jpeg2000),
            (b'it32', read_32t),
            (b't8mk', read_mk)],
        (128, 128, 2): [
            (b'ic13', read_png_or_jpeg2000)],
        (256, 256, 1): [
            (b'ic08', read_png_or_jpeg2000)],
        (256, 256, 2): [
            (b'ic14', read_png_or_jpeg2000)],
        (512, 512, 1): [
            (b'ic09', read_png_or_jpeg2000)],
        (512, 512, 2): [
            (b'ic10', read_png_or_jpeg2000)] }
    
    def __init__(self, fobj):
        '''
fobj is a file-like object as an icns resource
'''
        self.dct = { }
        self.fobj = fobj
        sig, filesize = nextheader(fobj)
        if not _accept(sig):
            msg = 'not an icns file'
            raise SyntaxError(msg)
        i = HEADERSIZE
        while i < filesize:
            sig, blocksize = nextheader(fobj)
            if blocksize <= 0:
                msg = 'invalid block header'
                raise SyntaxError(msg)
            i += HEADERSIZE
            blocksize -= HEADERSIZE
            self.dct[sig] = (i, blocksize)
            fobj.seek(blocksize, io.SEEK_CUR)
            i += blocksize

    
    def itersizes(self):
        sizes = []
        for size, fmts in self.SIZES.items():
            for fmt, reader in fmts:
                while not fmt in self.dct:
                    pass
                sizes.append(size)
                fmts
        return sizes

    
    def bestsize(self):
        '''No 32bit icon resources found'''
        sizes = self.itersizes()
        if not sizes:
            msg = 'No 32bit icon resources found'
            raise SyntaxError(msg)
        return max(sizes)

    
    def dataforsize(self, size):
        '''
Get an icon resource as {channel: array}.  Note that
the arrays are bottom-up like windows bitmaps and will likely
need to be flipped or transposed in some way.
'''
        dct = { }
        for code, reader in self.SIZES[size]:
            desc = self.dct.get(code)
            if desc is None:
                continue
            dct.update(reader(self.fobj, desc, size))
        return dct

    
    def getimage(self, size = None):
        if size is None:
            size = self.bestsize()
        elif len(size) == 2:
            size = (size[0], size[1], 1)
        channels = self.dataforsize(size)
        im = channels.get('RGBA')
        if im:
            return im
        im = channels['RGB'].copy()
        
        try:
            im.putalpha(channels['A'])
        except KeyError:
            return im

        return im



class IcnsImageFile(ImageFile.ImageFile):
    """
PIL image support for Mac OS .icns files.
Chooses the best resolution, but will possibly load
a different size image if you mutate the size attribute
before calling 'load'.

The info dictionary has a key 'sizes' that is a list
of sizes that the icns file has.
"""
    format = 'ICNS'
    format_description = 'Mac OS icns resource'
    
    def _open(self):
        if self.fp is None:
            raise AssertionError
        self.icns = IcnsFile(self.fp)
        self._mode = 'RGBA'
        self.info['sizes'] = self.icns.itersizes()
        self.best_size = self.icns.bestsize()
        self.size = (self.best_size[0] * self.best_size[2], self.best_size[1] * self.best_size[2])

    size = (lambda self: self._size)()
    size = (lambda self, value: for size in self.info['sizes']:
simple_size = (size[0] * size[2], size[1] * size[2])scale = simple_size[0] // value[0]if not simple_size[1] / value[1] == scale:
continueself._size = valueself.info['sizes']Nonemsg = 'This is not one of the allowed sizes of this image'raise ValueError(msg))()
    
    def load(self, scale = None):
        if scale is not None:
            width, height = self.size[slice(None, 2, None)]
            self.size = (width * scale, height * scale)
            self.best_size = (width, height, scale)
        px = Image.Image.load(self)
        if self._im is not None and self.im.size == self.size:
            return px
        self.load_prepare()
        im = self.icns.getimage(self.best_size)
        px = im.load()
        self.im = im.im
        self._mode = im.mode
        self.size = im.size
        return px



def _save(im, fp, filename):
    '''
Saves the image as a series of PNG files,
that are then combined into a .icns file.
'''
    if hasattr(fp, 'flush'):
        fp.flush()
    sizes = {
        b'ic14': 512,
        b'ic13': 256,
        b'ic12': 64,
        b'ic11': 32,
        b'ic10': 1024,
        b'ic09': 512,
        b'ic08': 256,
        b'ic07': 128 }
    
    try:
        for im in im.encoderinfo.get('append_images', []):
            pass
    im = im.encoderinfo.get('append_images', [])

    provided_images = im
    im = None
    size_streams = { }
    for size in set(sizes.values()):
        image = provided_images[size] if size in provided_images else im.resize((size, size))
        temp = io.BytesIO()
        image.save(temp, 'png')
        size_streams[size] = temp.getvalue()
    entries = []
    for type, size in sizes.items():
        stream = size_streams[size]
        entries.append((type, HEADERSIZE + len(stream), stream))
    fp.write(MAGIC)
    file_length = HEADERSIZE
    file_length += HEADERSIZE + 8 * len(entries)
    sum += (lambda .0: for entry in .0:
entry[1].0)(entries())
    fp.write(struct.pack('>i', file_length))
    fp.write(b'TOC ')
    fp.write(struct.pack('>i', HEADERSIZE + len(entries) * HEADERSIZE))
    for entry in entries:
        fp.write(entry[0])
        fp.write(struct.pack('>i', entry[1]))
    for entry in entries:
        fp.write(entry[0])
        fp.write(struct.pack('>i', entry[1]))
        fp.write(entry[2])
    if hasattr(fp, 'flush'):
        fp.flush()
        return None
    return None
# WARNING: Decompyle incomplete


def _accept(prefix):
    return prefix.startswith(MAGIC)

Image.register_open(IcnsImageFile.format, IcnsImageFile, _accept)
Image.register_extension(IcnsImageFile.format, '.icns')
Image.register_save(IcnsImageFile.format, _save)
Image.register_mime(IcnsImageFile.format, 'image/icns')
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Syntax: python3 IcnsImagePlugin.py [file]')
        sys.exit()
    with open(sys.argv[1], 'rb').__enter__() as fp:
        imf = IcnsImageFile(fp)
        for size in imf.info['sizes']:
            (width, height, scale) = size
            imf.size = size
            imf.save(f'''out-{width}-{height}-{scale}.png''')
        with Image.open(sys.argv[1]).__enter__() as im:
            im.save('out.png')
        if sys.platform == 'windows':
            os.startfile('out.png')
