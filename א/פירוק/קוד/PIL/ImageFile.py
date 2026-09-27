# Source Generated with Decompyle++
# File: ImageFile.pyc (Python 3.14)

from __future__ import annotations
import abc
import io
import itertools
import logging
import os
import struct
from typing import IO, Any, NamedTuple, cast
from . import ExifTags, Image
from ._util import DeferredError, is_path
TYPE_CHECKING = False
if TYPE_CHECKING:
    from ._typing import StrOrBytesPath
logger = logging.getLogger(__name__)
MAXBLOCK = 65536
SAFEBLOCK = 1048576
LOAD_TRUNCATED_IMAGES = False
ERRORS = {
    -9: 'out of memory error',
    -8: 'bad configuration',
    -3: 'unknown error',
    -2: 'decoding error',
    -1: 'image buffer overrun error' }

def _get_oserror(error, *, encoder):
    '''encoder'''
    
    try:
        msg = Image.core.getcodecstatus(error)
    except AttributeError:
        msg = ERRORS.get(error)

    if not msg:
        msg = f'''{'encoder' if encoder else 'decoder'} error {error}'''
    msg += f''' when {'writing' if encoder else 'reading'} image file'''
    return OSError(msg)


def _tilesort(t):
    return t[2]


class _Tile(NamedTuple):
    extents: 'tuple[int, int, int, int] | None' = '_Tile'
    offset: 'int' = 0
    args: 'tuple[Any, ...] | str | None' = None


class ImageFile(Image.Image):
    '''Base class for image file format handlers.'''
    
    def __init__(self, fp, filename = None):
        # unsupported opcode LOAD_SUPER_ATTR
        self()
        self._min_frame = 0
        self.custom_mimetype = None
        self.tile = []
        self.readonly = 1
        self.decoderconfig = ()
        self.decodermaxblock = MAXBLOCK
        self
        self
        if is_path(fp):
            self.fp = open(fp, 'rb')
            self.filename = os.fspath(fp)
            self._exclusive_fp = True
        else:
            self.fp = cast(IO[bytes], fp)
            self.filename = filename if filename is not None else ''
            self._exclusive_fp = False
        
        try:
            self._open()
            if isinstance(self, StubImageFile):
                loader = self._load()
                if self._load():
                    loader.open(self)
        except (IndexError, TypeError, KeyError, EOFError, struct.error) as v:
            raise SyntaxError(v) from v

        
        try:
            if not (self.mode and not (self.size[0] <= 0)) or self.size[1] <= 0:
                msg = 'not identified by this driver'
                raise SyntaxError(msg)
        except BaseException:
            if self._exclusive_fp:
                self.fp.close()
            raise

        return None
    # WARNING: Decompyle incomplete

    
    def _open(self):
        pass

    
    def __enter__(self):
        return self

    
    def _close_fp(self):
        '''_fp'''
        if getattr(self, '_fp', False) and not isinstance(self._fp, DeferredError):
            if self._fp != self.fp:
                self._fp.close()
            self._fp = DeferredError(ValueError('Operation on closed image'))
        if self.fp:
            self.fp.close()
            return None

    
    def __exit__(self, *args):
        '''_exclusive_fp'''
        if getattr(self, '_exclusive_fp', False):
            self._close_fp()
        self.fp = None

    
    def close(self):
        '''
Closes the file pointer, if possible.

This operation will destroy the image core and release its memory.
The image data will be unusable afterward.

This function is required to close images that have multiple frames or
have not had their file read and closed by the
:py:meth:`~PIL.Image.Image.load` method. See :ref:`file-handling` for
more information.
'''
        
        try:
            self._close_fp()
            self.fp = None
        while <exception value><EXCEPTION MATCH>Exception:
            msg = <exception value>
            logger.debug('Error closing: %s', msg)
            msg = None
            del msg
            continue
            msg = None
            del msg

        # unsupported opcode LOAD_SUPER_ATTR
        self()
        return None
    # WARNING: Decompyle incomplete

    
    def get_child_images(self):
        child_images = []
        exif = self.getexif()
        ifds = []
        if ExifTags.Base.SubIFDs in exif:
            subifd_offsets = exif[ExifTags.Base.SubIFDs]
            if subifd_offsets:
                if not isinstance(subifd_offsets, tuple):
                    subifd_offsets = (subifd_offsets,)
                
                try:
                    for subifd_offset in subifd_offsets:
                        pass
                subifd_offset = None

                ifds = []
                subifd_offset = subifd_offset
        ifd1 = exif.get_ifd(ExifTags.IFD.IFD1)
        if ifd1 and ifd1.get(ExifTags.Base.JpegIFOffset):
            if exif._info is None:
                raise AssertionError
            ifds.append((ifd1, exif._info.next))
        offset = None
        for ifd, ifd_offset in ifds:
            if self.fp is None:
                raise AssertionError
            current_offset = self.fp.tell()
            if offset is None:
                offset = current_offset
            fp = self.fp
            if ifd is not None:
                thumbnail_offset = ifd.get(ExifTags.Base.JpegIFOffset)
                if thumbnail_offset is not None:
                    thumbnail_offset += getattr(self, '_exif_offset', 0)
                    self.fp.seek(thumbnail_offset)
                    length = ifd.get(ExifTags.Base.JpegIFByteCount)
                    if not isinstance(length, int):
                        raise AssertionError
                    data = self.fp.read(length)
                    fp = io.BytesIO(data)
            with Image.open(fp) as im:
                from . import TiffImagePlugin
                if thumbnail_offset is None and isinstance(im, TiffImagePlugin.TiffImageFile):
                    im._frame_pos = [
                        ifd_offset]
                    im._seek(0)
                im.load()
                child_images.append(im)
        if offset is not None:
            if self.fp is None:
                raise AssertionError
            self.fp.seek(offset)
        return child_images
    # WARNING: Decompyle incomplete

    
    def get_format_mimetype(self):
        if self.custom_mimetype:
            return self.custom_mimetype
        if self.format is not None:
            return Image.MIME.get(self.format.upper())

    
    def __getstate__(self):
        # unsupported opcode LOAD_SUPER_ATTR
        return self() + [
            self.filename]
    # WARNING: Decompyle incomplete

    
    def __setstate__(self, state):
        self.tile = []
        if len(state) > 5:
            self.filename = state[5]
        # unsupported opcode LOAD_SUPER_ATTR
        self(state)
        return None
    # WARNING: Decompyle incomplete

    
    def verify(self):
        '''Check file integrity'''
        if self._exclusive_fp and self.fp:
            self.fp.close()
        self.fp = None

    
    def load(self):
        '''Load image data based on tile list'''
        if not (self.tile) and self._im is None:
            msg = 'cannot load this image'
            raise OSError(msg)
        pixel = Image.Image.load(self)
        if not self.tile:
            return pixel
        self.map = None
        use_mmap = self.filename and len(self.tile) == 1
        if self.fp is None:
            raise AssertionError
        readonly = 0
        if hasattr(self, 'load_read'):
            read = self.load_read
            use_mmap = False
        else:
            read = self.fp.read
        if hasattr(self, 'load_seek'):
            seek = self.load_seek
            use_mmap = False
        else:
            seek = self.fp.seek
        if use_mmap:
            decoder_name, extents, offset, args = self.tile[0]
            if isinstance(args, str):
                args = (args, 0, 1)
            if decoder_name == 'raw' and isinstance(args, tuple) and len(args) >= 3 and args[0] == self.mode and args[0] in Image._MAPMODES:
                if offset < 0:
                    msg = 'Tile offset cannot be negative'
                    raise ValueError(msg)
                
                try:
                    import mmap
                    with open(self.filename) as fp:
                        self.map = mmap.mmap(fp.fileno(), 0, access = mmap.ACCESS_READ)
                    if offset + self.size[1] * args[1] > self.map.size():
                        msg = 'buffer is not large enough'
                        raise OSError(msg)
                    self.im = Image.core.map_buffer(self.map, self.size, decoder_name, offset, args)
                    readonly = 1
                    if self.palette:
                        self.palette.dirty = 1
                except (AttributeError, OSError, ImportError):
                    self.map = None

        self.load_prepare()
        err_code = -3
        if not self.map:
            self.tile.sort(key = _tilesort)
            prefix = getattr(self, 'tile_prefix', b'')
            self.tile = _
            for decoder_name, extents, offset, args in enumerate(self.tile):
                decoder = Image._getdecoder(self.mode, decoder_name, args, self.decoderconfig)
                
                try:
                    decoder.setimage(self.im, extents)
                    if decoder.pulls_fd:
                        decoder.setfd(self.fp)
                        err_code = decoder.decode(b'')[1]
                    else:
                        b = prefix
                        read_bytes = self.decodermaxblock
                        if i + 1 < len(self.tile):
                            next_offset = self.tile[i + 1].offset
                            if next_offset > offset:
                                read_bytes = next_offset - offset
                        
                        try:
                            s = read(read_bytes)
                        except (IndexError, struct.error) as e:
                            if LOAD_TRUNCATED_IMAGES:
                                pass
                            msg = 'image file is truncated'
                            raise OSError(msg) from e

                        if not s:
                            if LOAD_TRUNCATED_IMAGES:
                                pass
                            else:
                                msg = f'''image file is truncated ({len(b)} bytes not processed)'''
                                raise OSError(msg)
                        b = b + s
                        (n, err_code) = decoder.decode(b)
                        if n < 0:
                            pass
                        else:
                            b = b[n:]
                            continue

                decoder.cleanup()
        self.tile = []
        self.readonly = readonly
        self.load_end()
        if self._exclusive_fp and self._close_exclusive_fp_after_loading:
            self.fp.close()
        self.fp = None
        if not (self.map) and not LOAD_TRUNCATED_IMAGES and err_code < 0:
            raise _get_oserror(err_code, encoder = False)
        return Image.Image.load(self)

    
    def load_prepare(self):
        if self._im is None:
            self.im = Image.core.new(self.mode, self.size)
        if self.mode == 'P':
            Image.Image.load(self)
            return None

    
    def load_end(self):
        pass

    
    def _seek_check(self, frame):
        '''_n_frames'''
        if not frame < self._min_frame:
            if (not hasattr(self, '_n_frames') or self._n_frames is not None) and frame >= getattr(self, 'n_frames') + self._min_frame:
                msg = 'attempt to seek outside sequence'
                raise EOFError(msg)
        return self.tell() != frame



class StubHandler(abc.ABC):
    
    def open(self, im):
        pass

    load = (lambda self, im: pass)()


def StubImageFile():
    '''StubImageFile'''
    __doc__ = '\nBase class for stub image loaders.\n\nA stub loader is an image loader that can identify files of a\ncertain format, but relies on external code to load the file.\n'
    _open = (lambda self: pass)()
    
    def load(self):
        loader = self._load()
        if loader is None:
            msg = f'''cannot find loader for this {self.format} file'''
            raise OSError(msg)
        image = loader.load(self)
        if image is None:
            raise AssertionError
        self.__class__ = image.__class__
        self.__dict__ = image.__dict__
        return image.load()

    _load = (lambda self: pass)()

StubImageFile = __build_class__(StubImageFile, 'StubImageFile', ImageFile, metaclass = abc.ABCMeta)

class Parser:
    '''
Incremental image parser.  This class implements the standard
feed/close consumer interface.
'''
    incremental = None
    image: 'Image.Image | None' = None
    data: 'bytes | None' = None
    decoder: 'Image.core.ImagingDecoder | PyDecoder | None' = None
    offset = 0
    finished = 0
    
    def reset(self):
        """
(Consumer) Reset the parser.  Note that you can only call this
method immediately after you've created a parser; parser
instances cannot be reused.
"""
        if self.data is not None:
            raise 'cannot reuse parsers'()

    
    def feed(self, data):
        '''
(Consumer) Feed data to the parser.

:param data: A string buffer.
:exception OSError: If the parser failed to parse the image file.
'''
        if self.finished:
            return None
        if self.data is None:
            self.data = data
        else:
            self.data = self.data + data
        if self.decoder:
            if self.offset > 0:
                skip = min(len(self.data), self.offset)
                self.data = self.data[skip:]
                self.offset = self.offset - skip
                if self.offset > 0 or not (self.data):
                    return None
            n, e = self.decoder.decode(self.data)
            if n < 0:
                self.data = None
                self.finished = 1
                if e < 0:
                    self.image = None
                    raise _get_oserror(e, encoder = False)
                return None
            self.data = self.data[n:]
            return None
        if self.image:
            return None
        
        try:
            with io.BytesIO(self.data) as fp:
                im = Image.open(fp)
        except OSError:
            return None

        flag = hasattr(im, 'load_seek') or hasattr(im, 'load_read')
        if not flag and len(im.tile) == 1:
            im.load_prepare()
            d, e, o, a = im.tile[0]
            im.tile = []
            self.decoder = Image._getdecoder(im.mode, d, a, im.decoderconfig)
            self.decoder.setimage(im.im, e)
            self.offset = o
            if self.offset <= len(self.data):
                self.data = self.data[self.offset:]
                self.offset = 0
        self.image = im

    
    def __enter__(self):
        return self

    
    def __exit__(self, *args):
        self.close()

    
    def close(self):
        '''
(Consumer) Close the stream.

:returns: An image object.
:exception OSError: If the parser failed to parse the image file either
                    because it cannot be identified or cannot be
                    decoded.
'''
        if self.decoder:
            self.feed(b'')
            self.data = None
            self.decoder = None
            if not self.finished:
                msg = 'image was incomplete'
                raise OSError(msg)
        if not self.image:
            msg = 'cannot parse this image'
            raise OSError(msg)
        if self.data:
            fp = io.BytesIO(self.data).__enter__()
            
            try:
                self.image = Image.open(fp)
                return io.BytesIO(self.data).__exit__
            finally:
                self.image.load()
                io.BytesIO(self.data).__exit__(None, None, None)
                return self.image




def _save(im, fp, tile, bufsize = 0):
    '''Helper to save image based on tile list

:param im: Image object.
:param fp: File object.
:param tile: Tile list.
:param bufsize: Optional buffer size
'''
    im.load()
    if not hasattr(im, 'encoderconfig'):
        im.encoderconfig = ()
    tile.sort(key = _tilesort)
    bufsize = max(MAXBLOCK, bufsize, im.size[0] * 4)
    
    try:
        fh = fp.fileno()
        fp.flush()
        _encode_tile(im, fp, tile, bufsize, fh)
    except (AttributeError, io.UnsupportedOperation) as exc:
        _encode_tile(im, fp, tile, bufsize, None, exc)

    if hasattr(fp, 'flush'):
        fp.flush()
        return None


def _encode_tile(im, fp, tile, bufsize, fh, exc = None):
    for encoder_name, extents, offset, args in tile:
        if offset > 0:
            fp.seek(offset)
        encoder = Image._getencoder(im.mode, encoder_name, args, im.encoderconfig)
        
        try:
            encoder.setimage(im.im, extents)
            if encoder.pushes_fd:
                encoder.setfd(fp)
                errcode = encoder.encode_to_pyfd()[1]
            elif exc:
                
                try:
                    errcode, data = encoder.encode(bufsize)[slice(1, None, None)]
                    fp.write(data)
                finally:
                    if not tile:
                        continue
                    
                    try:
                        return errcode
                    if fh is None:
                        raise AssertionError
                    errcode = encoder.encode_to_file(fh, bufsize)
                    if errcode < 0:
                        raise _get_oserror(errcode, encoder = True) from exc
                    continue
                    encoder.cleanup()



# WARNING: Decompyle incomplete


def _safe_read(fp, size):
    """
Reads large blocks in a safe way.  Unlike fp.read(n), this function
doesn't trust the user.  If the requested size is larger than
SAFEBLOCK, the file is read block by block.

:param fp: File handle.  Must implement a <b>read</b> method.
:param size: Number of bytes to read.
:returns: A string containing <i>size</i> bytes of data.

Raises an OSError if the file is truncated and the read cannot be completed

"""
    if size <= 0:
        return b''
    if size <= SAFEBLOCK:
        data = fp.read(size)
        if len(data) < size:
            msg = 'Truncated File Read'
            raise OSError(msg)
        return data
    blocks = []
    remaining_size = size
    while remaining_size > 0:
        block = fp.read(min(remaining_size, SAFEBLOCK))
        if not block:
            pass
        else:
            blocks.append(block)
            remaining_size -= len(block)
    if (lambda .0: for block in .0:
len(block).0)(blocks()) < size:
        msg = 'Truncated File Read'
        raise OSError(msg)
    return b''.join(blocks)


class PyCodecState:
    
    def __init__(self):
        self.xsize = 0
        self.ysize = 0
        self.xoff = 0
        self.yoff = 0

    
    def extents(self):
        return (self.xoff, self.yoff, self.xoff + self.xsize, self.yoff + self.ysize)



class PyCodec:
    fd: 'IO[bytes] | None' = 'PyCodec'
    
    def __init__(self, mode, *args):
        self.im = None
        self.state = PyCodecState()
        self.fd = None
        self.mode = mode
        self.init(args)

    
    def init(self, args):
        '''
Override to perform codec specific initialization

:param args: Tuple of arg items from the tile entry
:returns: None
'''
        self.args = args

    
    def cleanup(self):
        '''
Override to perform codec specific cleanup

:returns: None
'''
        pass

    
    def setfd(self, fd):
        '''
Called from ImageFile to set the Python file-like object

:param fd: A Python file-like object
:returns: None
'''
        self.fd = fd

    
    def setimage(self, im, extents = None):
        '''
Called from ImageFile to set the core output image for the codec

:param im: A core image object
:param extents: a 4 tuple of (x0, y0, x1, y1) defining the rectangle
    for this tile
:returns: None
'''
        self.im = im
        if extents:
            x0, y0, x1, y1 = extents
            if not (not (x0 < 0) and not (y0 < 0) and not (x1 > self.im.size[0])) or y1 > self.im.size[1]:
                msg = 'Tile cannot extend outside image'
                raise ValueError(msg)
            self.state.xoff = x0
            self.state.yoff = y0
            self.state.xsize = x1 - x0
            self.state.ysize = y1 - y0
        else:
            (self.state.xsize, self.state.ysize) = self.im.size
        if self.state.xsize <= 0 or self.state.ysize <= 0:
            msg = 'Size must be positive'
            raise ValueError(msg)



class PyDecoder(PyCodec):
    '''
Python implementation of a format decoder. Override this class and
add the decoding logic in the :meth:`decode` method.

See :ref:`Writing Your Own File Codec in Python<file-codecs-py>`
'''
    _pulls_fd = False
    pulls_fd = (lambda self: self._pulls_fd)()
    
    def decode(self, buffer):
        '''
Override to perform the decoding process.

:param buffer: A bytes object with the data to be decoded.
:returns: A tuple of ``(bytes consumed, errcode)``.
    If finished with decoding return -1 for the bytes consumed.
    Err codes are from :data:`.ImageFile.ERRORS`.
'''
        msg = 'unavailable in base decoder'
        raise NotImplementedError(msg)

    
    def set_as_raw(self, data, rawmode = None, extra = ()):
        '''
Convenience method to set the internal image from a stream of raw data

:param data: Bytes to be set
:param rawmode: The rawmode to be used for the decoder.
    If not specified, it will default to the mode of the image
:param extra: Extra arguments for the decoder.
:returns: None
'''
        if not rawmode:
            rawmode = self.mode
        d = Image._getdecoder(self.mode, 'raw', rawmode, extra)
        if self.im is None:
            raise AssertionError
        d.setimage(self.im, self.state.extents())
        s = d.decode(data)
        if s[0] >= 0:
            msg = 'not enough image data'
            raise ValueError(msg)
        if s[1] != 0:
            msg = 'cannot decode image data'
            raise ValueError(msg)



class PyEncoder(PyCodec):
    '''
Python implementation of a format encoder. Override this class and
add the decoding logic in the :meth:`encode` method.

See :ref:`Writing Your Own File Codec in Python<file-codecs-py>`
'''
    _pushes_fd = False
    pushes_fd = (lambda self: self._pushes_fd)()
    
    def encode(self, bufsize):
        '''
Override to perform the encoding process.

:param bufsize: Buffer size.
:returns: A tuple of ``(bytes encoded, errcode, bytes)``.
    If finished with encoding return 1 for the error code.
    Err codes are from :data:`.ImageFile.ERRORS`.
'''
        msg = 'unavailable in base encoder'
        raise NotImplementedError(msg)

    
    def encode_to_pyfd(self):
        '''
If ``pushes_fd`` is ``True``, then this method will be used,
and ``encode()`` will only be called once.

:returns: A tuple of ``(bytes consumed, errcode)``.
    Err codes are from :data:`.ImageFile.ERRORS`.
'''
        if not self.pushes_fd:
            return (0, -8)
        (bytes_consumed, errcode, data) = self.encode(0)
        if data:
            if self.fd is None:
                raise AssertionError
            self.fd.write(data)
        return (bytes_consumed, errcode)

    
    def encode_to_file(self, fh, bufsize):
        '''
:param fh: File handle.
:param bufsize: Buffer size.

:returns: If finished successfully, return 0.
    Otherwise, return an error code. Err codes are from
    :data:`.ImageFile.ERRORS`.
'''
        errcode = 0
        while errcode == 0:
            (status, errcode, buf) = self.encode(bufsize)
            if not status > 0:
                continue
            os.write(fh, buf[status:])
        return errcode


