# Source Generated with Decompyle++
# File: TiffImagePlugin.pyc (Python 3.14)

__conditional_annotations__ = {}
from __future__ import annotations
import io
import itertools
import logging
import math
import os
import struct
import warnings
from collections.abc import Callable, MutableMapping
from fractions import Fraction
from numbers import Number, Rational
from typing import IO, Any, cast
from . import ExifTags, Image, ImageFile, ImageOps, ImagePalette, TiffTags
from ._binary import i16be as i16
from ._binary import i32be as i32
from ._binary import o8
from ._util import DeferredError, is_path
from .TiffTags import TYPES
TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import NoReturn
    from ._typing import Buffer, IntegralLike, StrOrBytesPath
logger = logging.getLogger(__name__)
READ_LIBTIFF = False
WRITE_LIBTIFF = False
STRIP_SIZE = 65536
II = b'II'
MM = b'MM'
OSUBFILETYPE = 255
IMAGEWIDTH = 256
IMAGELENGTH = 257
BITSPERSAMPLE = 258
COMPRESSION = 259
PHOTOMETRIC_INTERPRETATION = 262
FILLORDER = 266
IMAGEDESCRIPTION = 270
STRIPOFFSETS = 273
SAMPLESPERPIXEL = 277
ROWSPERSTRIP = 278
STRIPBYTECOUNTS = 279
X_RESOLUTION = 282
Y_RESOLUTION = 283
PLANAR_CONFIGURATION = 284
RESOLUTION_UNIT = 296
TRANSFERFUNCTION = 301
SOFTWARE = 305
DATE_TIME = 306
ARTIST = 315
PREDICTOR = 317
COLORMAP = 320
TILEWIDTH = 322
TILELENGTH = 323
TILEOFFSETS = 324
TILEBYTECOUNTS = 325
SUBIFD = 330
EXTRASAMPLES = 338
SAMPLEFORMAT = 339
JPEGTABLES = 347
YCBCRSUBSAMPLING = 530
REFERENCEBLACKWHITE = 532
COPYRIGHT = 33432
IPTC_NAA_CHUNK = 33723
PHOTOSHOP_CHUNK = 34377
ICCPROFILE = 34675
EXIFIFD = 34665
XMP = 700
JPEGQUALITY = 65537
IMAGEJ_META_DATA_BYTE_COUNTS = 50838
IMAGEJ_META_DATA = 50839
COMPRESSION_INFO = {
    1: 'raw',
    2: 'tiff_ccitt',
    3: 'group3',
    4: 'group4',
    5: 'tiff_lzw',
    6: 'tiff_jpeg',
    7: 'jpeg',
    8: 'tiff_adobe_deflate',
    32771: 'tiff_raw_16',
    32773: 'packbits',
    32809: 'tiff_thunderscan',
    32946: 'tiff_deflate',
    34676: 'tiff_sgilog',
    34677: 'tiff_sgilog24',
    34925: 'lzma',
    50000: 'zstd',
    50001: 'webp' }
COMPRESSION_INFO_REV = None
OPEN_INFO = {
    (II, 0, (1,), 1, (1,), ()): ('1', '1;I'),
    (MM, 0, (1,), 1, (1,), ()): ('1', '1;I'),
    (II, 0, (1,), 2, (1,), ()): ('1', '1;IR'),
    (MM, 0, (1,), 2, (1,), ()): ('1', '1;IR'),
    (II, 1, (1,), 1, (1,), ()): ('1', '1'),
    (MM, 1, (1,), 1, (1,), ()): ('1', '1'),
    (II, 1, (1,), 2, (1,), ()): ('1', '1;R'),
    (MM, 1, (1,), 2, (1,), ()): ('1', '1;R'),
    (II, 0, (1,), 1, (2,), ()): ('L', 'L;2I'),
    (MM, 0, (1,), 1, (2,), ()): ('L', 'L;2I'),
    (II, 0, (1,), 2, (2,), ()): ('L', 'L;2IR'),
    (MM, 0, (1,), 2, (2,), ()): ('L', 'L;2IR'),
    (II, 1, (1,), 1, (2,), ()): ('L', 'L;2'),
    (MM, 1, (1,), 1, (2,), ()): ('L', 'L;2'),
    (II, 1, (1,), 2, (2,), ()): ('L', 'L;2R'),
    (MM, 1, (1,), 2, (2,), ()): ('L', 'L;2R'),
    (II, 0, (1,), 1, (4,), ()): ('L', 'L;4I'),
    (MM, 0, (1,), 1, (4,), ()): ('L', 'L;4I'),
    (II, 0, (1,), 2, (4,), ()): ('L', 'L;4IR'),
    (MM, 0, (1,), 2, (4,), ()): ('L', 'L;4IR'),
    (II, 1, (1,), 1, (4,), ()): ('L', 'L;4'),
    (MM, 1, (1,), 1, (4,), ()): ('L', 'L;4'),
    (II, 1, (1,), 2, (4,), ()): ('L', 'L;4R'),
    (MM, 1, (1,), 2, (4,), ()): ('L', 'L;4R'),
    (II, 0, (1,), 1, (8,), ()): ('L', 'L;I'),
    (MM, 0, (1,), 1, (8,), ()): ('L', 'L;I'),
    (II, 0, (1,), 2, (8,), ()): ('L', 'L;IR'),
    (MM, 0, (1,), 2, (8,), ()): ('L', 'L;IR'),
    (II, 1, (1,), 1, (8,), ()): ('L', 'L'),
    (MM, 1, (1,), 1, (8,), ()): ('L', 'L'),
    (II, 1, (2,), 1, (8,), ()): ('L', 'L'),
    (MM, 1, (2,), 1, (8,), ()): ('L', 'L'),
    (II, 1, (1,), 2, (8,), ()): ('L', 'L;R'),
    (MM, 1, (1,), 2, (8,), ()): ('L', 'L;R'),
    (II, 1, (1,), 1, (12,), ()): ('I;16', 'I;12'),
    (II, 0, (1,), 1, (16,), ()): ('I;16', 'I;16'),
    (II, 1, (1,), 1, (16,), ()): ('I;16', 'I;16'),
    (MM, 1, (1,), 1, (16,), ()): ('I;16B', 'I;16B'),
    (II, 1, (1,), 2, (16,), ()): ('I;16', 'I;16R'),
    (II, 1, (2,), 1, (16,), ()): ('I', 'I;16S'),
    (MM, 1, (2,), 1, (16,), ()): ('I', 'I;16BS'),
    (II, 0, (3,), 1, (32,), ()): ('F', 'F;32F'),
    (MM, 0, (3,), 1, (32,), ()): ('F', 'F;32BF'),
    (II, 1, (1,), 1, (32,), ()): ('I', 'I;32N'),
    (II, 1, (2,), 1, (32,), ()): ('I', 'I;32S'),
    (MM, 1, (2,), 1, (32,), ()): ('I', 'I;32BS'),
    (II, 1, (3,), 1, (32,), ()): ('F', 'F;32F'),
    (MM, 1, (3,), 1, (32,), ()): ('F', 'F;32BF'),
    (II, 1, (1,), 1, (8, 8), (2,)): ('LA', 'LA'),
    (MM, 1, (1,), 1, (8, 8), (2,)): ('LA', 'LA'),
    (II, 2, (1,), 1, (8, 8, 8), ()): ('RGB', 'RGB'),
    (MM, 2, (1,), 1, (8, 8, 8), ()): ('RGB', 'RGB'),
    (II, 2, (1,), 2, (8, 8, 8), ()): ('RGB', 'RGB;R'),
    (MM, 2, (1,), 2, (8, 8, 8), ()): ('RGB', 'RGB;R'),
    (II, 2, (1,), 1, (8, 8, 8, 8), ()): ('RGBA', 'RGBA'),
    (MM, 2, (1,), 1, (8, 8, 8, 8), ()): ('RGBA', 'RGBA'),
    (II, 2, (1,), 1, (8, 8, 8, 8), (0,)): ('RGB', 'RGBX'),
    (MM, 2, (1,), 1, (8, 8, 8, 8), (0,)): ('RGB', 'RGBX'),
    (II, 2, (1,), 1, (8, 8, 8, 8, 8), (0, 0)): ('RGB', 'RGBXX'),
    (MM, 2, (1,), 1, (8, 8, 8, 8, 8), (0, 0)): ('RGB', 'RGBXX'),
    (II, 2, (1,), 1, (8, 8, 8, 8, 8, 8), (0, 0, 0)): ('RGB', 'RGBXXX'),
    (MM, 2, (1,), 1, (8, 8, 8, 8, 8, 8), (0, 0, 0)): ('RGB', 'RGBXXX'),
    (II, 2, (1,), 1, (8, 8, 8, 8), (1,)): ('RGBA', 'RGBa'),
    (MM, 2, (1,), 1, (8, 8, 8, 8), (1,)): ('RGBA', 'RGBa'),
    (II, 2, (1,), 1, (8, 8, 8, 8, 8), (1, 0)): ('RGBA', 'RGBaX'),
    (MM, 2, (1,), 1, (8, 8, 8, 8, 8), (1, 0)): ('RGBA', 'RGBaX'),
    (II, 2, (1,), 1, (8, 8, 8, 8, 8, 8), (1, 0, 0)): ('RGBA', 'RGBaXX'),
    (MM, 2, (1,), 1, (8, 8, 8, 8, 8, 8), (1, 0, 0)): ('RGBA', 'RGBaXX'),
    (II, 2, (1,), 1, (8, 8, 8, 8), (2,)): ('RGBA', 'RGBA'),
    (MM, 2, (1,), 1, (8, 8, 8, 8), (2,)): ('RGBA', 'RGBA'),
    (II, 2, (1,), 1, (8, 8, 8, 8, 8), (2, 0)): ('RGBA', 'RGBAX'),
    (MM, 2, (1,), 1, (8, 8, 8, 8, 8), (2, 0)): ('RGBA', 'RGBAX'),
    (II, 2, (1,), 1, (8, 8, 8, 8, 8, 8), (2, 0, 0)): ('RGBA', 'RGBAXX'),
    (MM, 2, (1,), 1, (8, 8, 8, 8, 8, 8), (2, 0, 0)): ('RGBA', 'RGBAXX'),
    (II, 2, (1,), 1, (8, 8, 8, 8), (999,)): ('RGBA', 'RGBA'),
    (MM, 2, (1,), 1, (8, 8, 8, 8), (999,)): ('RGBA', 'RGBA'),
    (II, 2, (1,), 1, (16, 16, 16), ()): ('RGB', 'RGB;16L'),
    (MM, 2, (1,), 1, (16, 16, 16), ()): ('RGB', 'RGB;16B'),
    (II, 2, (1,), 1, (16, 16, 16, 16), ()): ('RGBA', 'RGBA;16L'),
    (MM, 2, (1,), 1, (16, 16, 16, 16), ()): ('RGBA', 'RGBA;16B'),
    (II, 2, (1,), 1, (16, 16, 16, 16), (0,)): ('RGB', 'RGBX;16L'),
    (MM, 2, (1,), 1, (16, 16, 16, 16), (0,)): ('RGB', 'RGBX;16B'),
    (II, 2, (1,), 1, (16, 16, 16, 16), (1,)): ('RGBA', 'RGBa;16L'),
    (MM, 2, (1,), 1, (16, 16, 16, 16), (1,)): ('RGBA', 'RGBa;16B'),
    (II, 2, (1,), 1, (16, 16, 16, 16), (2,)): ('RGBA', 'RGBA;16L'),
    (MM, 2, (1,), 1, (16, 16, 16, 16), (2,)): ('RGBA', 'RGBA;16B'),
    (II, 3, (1,), 1, (1,), ()): ('P', 'P;1'),
    (MM, 3, (1,), 1, (1,), ()): ('P', 'P;1'),
    (II, 3, (1,), 2, (1,), ()): ('P', 'P;1R'),
    (MM, 3, (1,), 2, (1,), ()): ('P', 'P;1R'),
    (II, 3, (1,), 1, (2,), ()): ('P', 'P;2'),
    (MM, 3, (1,), 1, (2,), ()): ('P', 'P;2'),
    (II, 3, (1,), 2, (2,), ()): ('P', 'P;2R'),
    (MM, 3, (1,), 2, (2,), ()): ('P', 'P;2R'),
    (II, 3, (1,), 1, (4,), ()): ('P', 'P;4'),
    (MM, 3, (1,), 1, (4,), ()): ('P', 'P;4'),
    (II, 3, (1,), 2, (4,), ()): ('P', 'P;4R'),
    (MM, 3, (1,), 2, (4,), ()): ('P', 'P;4R'),
    (II, 3, (1,), 1, (8,), ()): ('P', 'P'),
    (MM, 3, (1,), 1, (8,), ()): ('P', 'P'),
    (II, 3, (1,), 1, (8, 8), (0,)): ('P', 'PX'),
    (MM, 3, (1,), 1, (8, 8), (0,)): ('P', 'PX'),
    (II, 3, (1,), 1, (8, 8), (2,)): ('PA', 'PA'),
    (MM, 3, (1,), 1, (8, 8), (2,)): ('PA', 'PA'),
    (II, 3, (1,), 2, (8,), ()): ('P', 'P;R'),
    (MM, 3, (1,), 2, (8,), ()): ('P', 'P;R'),
    (II, 5, (1,), 1, (8, 8, 8, 8), ()): ('CMYK', 'CMYK'),
    (MM, 5, (1,), 1, (8, 8, 8, 8), ()): ('CMYK', 'CMYK'),
    (II, 5, (1,), 1, (8, 8, 8, 8, 8), (0,)): ('CMYK', 'CMYKX'),
    (MM, 5, (1,), 1, (8, 8, 8, 8, 8), (0,)): ('CMYK', 'CMYKX'),
    (II, 5, (1,), 1, (8, 8, 8, 8, 8, 8), (0, 0)): ('CMYK', 'CMYKXX'),
    (MM, 5, (1,), 1, (8, 8, 8, 8, 8, 8), (0, 0)): ('CMYK', 'CMYKXX'),
    (II, 5, (1,), 1, (16, 16, 16, 16), ()): ('CMYK', 'CMYK;16L'),
    (MM, 5, (1,), 1, (16, 16, 16, 16), ()): ('CMYK', 'CMYK;16B'),
    (II, 6, (1,), 1, (8,), ()): ('L', 'L'),
    (MM, 6, (1,), 1, (8,), ()): ('L', 'L'),
    (II, 6, (1,), 1, (8, 8, 8), ()): ('RGB', 'RGBX'),
    (MM, 6, (1,), 1, (8, 8, 8), ()): ('RGB', 'RGBX'),
    (II, 8, (1,), 1, (8, 8, 8), ()): ('LAB', 'LAB'),
    (MM, 8, (1,), 1, (8, 8, 8), ()): ('LAB', 'LAB') }
MAX_SAMPLESPERPIXEL = (lambda .0: for key_tp in .0:
len(key_tp[4]).0)(OPEN_INFO())
PREFIXES = [
    b'MM\x00*',
    b'II*\x00',
    b'MM*\x00',
    b'II\x00*',
    b'MM\x00+',
    b'II+\x00']

def _accept(prefix):
    return prefix.startswith(tuple(PREFIXES))


def _limit_rational(val, max_val):
    inv = abs(val) > 1
    n_d = IFDRational(1 / val if inv else val).limit_rational(max_val)
    if inv:
        return n_d[::-1]
    return n_d


def _limit_signed_rational(val, max_val, min_val):
    frac = Fraction(val)
    n_d = (frac.numerator, frac.denominator)
    if (lambda .0: for i in .0:
float(i).0)(n_d()) < min_val:
        n_d = _limit_rational(val, abs(min_val))
    if tuple is tuple:
        tuple
        for None in n_d():
            pass
        # unsupported CALL_INTRINSIC_1 6
    
    n_d_float = (lambda .0: for i in .0:
float(i).0)(n_d())
    if max(n_d_float) > max_val:
        n_d = _limit_rational(n_d_float[0] / n_d_float[1], max_val)
    return n_d
# WARNING: Decompyle incomplete

_load_dispatch: 'dict[int, tuple[int, _LoaderFunc]]' = { }
_write_dispatch: 'dict[int, Callable[..., Any]]' = { }

def _delegate(op):
    
    def delegate(self, *args):
        return args()

    return delegate


class IFDRational(Rational):
    '''Implements a rational class where 0/0 is a legal value to match
the in the wild use of exif rationals.

e.g., DigitalZoomRatio - 0.00/0.00  indicates that no digital zoom was used
'''
    __slots__ = ('_numerator', '_denominator', '_val')
    
    def __init__(self, value, denominator = 1):
        '''
:param value: either an integer numerator, a
float/rational/other number, or an IFDRational
:param denominator: Optional integer denominator
'''
        self
        if isinstance(value, IFDRational):
            self._numerator = value.numerator
            self._denominator = value.denominator
            self._val = value._val
            return None
        if isinstance(value, Fraction):
            self._numerator = value.numerator
            self._denominator = value.denominator
        elif TYPE_CHECKING:
            self._numerator = cast(IntegralLike, value)
        else:
            self._numerator = value
        self._denominator = denominator
        if denominator == 0:
            self._val = float('nan')
            return None
        if denominator == 1:
            self._val = Fraction(value)
            return None
        if int(value) == value:
            self._val = Fraction(int(value), denominator)
            return None
        self._val = Fraction(value / denominator)

    numerator = (lambda self: self._numerator)()
    denominator = (lambda self: self._denominator)()
    
    def limit_rational(self, max_denominator):
        '''

:param max_denominator: Integer, the maximum denominator value
:returns: Tuple of (numerator, denominator)
'''
        if self.denominator == 0:
            return (self.numerator, self.denominator)
        if not isinstance(self._val, Fraction):
            raise AssertionError
        f = self._val.limit_denominator(max_denominator)
        return (f.numerator, f.denominator)

    
    def __repr__(self):
        return str(float(self._val))

    
    def __hash__(self):
        return self._val.__hash__()

    
    def __eq__(self, other):
        val = self._val
        if isinstance(other, IFDRational):
            other = other._val
        if isinstance(other, float):
            val = float(val)
        return val == other

    
    def __getstate__(self):
        return [
            self._val,
            self._numerator,
            self._denominator]

    
    def __setstate__(self, state):
        IFDRational.__init__(self, 0)
        (_val, _numerator, _denominator) = state
        if not isinstance(_val, (float, Fraction)):
            raise AssertionError
        self._val = _val
        if TYPE_CHECKING:
            self._numerator = cast(IntegralLike, _numerator)
        else:
            self._numerator = _numerator
        if not isinstance(_denominator, int):
            raise AssertionError
        self._denominator = _denominator

    __add__ = _delegate('__add__')
    __radd__ = _delegate('__radd__')
    __sub__ = _delegate('__sub__')
    __rsub__ = _delegate('__rsub__')
    __mul__ = _delegate('__mul__')
    __rmul__ = _delegate('__rmul__')
    __truediv__ = _delegate('__truediv__')
    __rtruediv__ = _delegate('__rtruediv__')
    __floordiv__ = _delegate('__floordiv__')
    __rfloordiv__ = _delegate('__rfloordiv__')
    __mod__ = _delegate('__mod__')
    __rmod__ = _delegate('__rmod__')
    __pow__ = _delegate('__pow__')
    __rpow__ = _delegate('__rpow__')
    __pos__ = _delegate('__pos__')
    __neg__ = _delegate('__neg__')
    __abs__ = _delegate('__abs__')
    __trunc__ = _delegate('__trunc__')
    __lt__ = _delegate('__lt__')
    __gt__ = _delegate('__gt__')
    __le__ = _delegate('__le__')
    __ge__ = _delegate('__ge__')
    __bool__ = _delegate('__bool__')
    __ceil__ = _delegate('__ceil__')
    __floor__ = _delegate('__floor__')
    __round__ = _delegate('__round__')
    __float__ = _delegate('__float__')
    if hasattr(Fraction, '__int__'):
        __int__ = _delegate('__int__')
        return None

_LoaderFunc = Callable[([
    'ImageFileDirectory_v2',
    bytes,
    bool], Any)]

def _register_loader(idx, size):
    
    def decorator(func):
        from .TiffTags import TYPES
        if func.__name__.startswith('load_'):
            TYPES[idx] = func.__name__[slice(5, None, None)].replace('_', ' ')
        _load_dispatch[idx] = (size, func)
        return func

    return decorator


def _register_writer(idx):
    
    def decorator(func):
        _write_dispatch[idx] = func
        return func

    return decorator


def _register_basic(idx_fmt_name):
    from .TiffTags import TYPES
    (idx, fmt, name) = idx_fmt_name
    TYPES[idx] = name
    size = struct.calcsize(f'''={fmt}''')
    
    def basic_handler(self, data, legacy_api = True):
        return self._unpack(f'''{len(data) // size}{fmt}''', data)

    _load_dispatch[idx] = (size, basic_handler)
    
    _write_dispatch[idx] = lambda self, *values: (lambda .0: for value in .0:
self._pack(fmt, value).0)(values())


if TYPE_CHECKING:
    _IFDv2Base = MutableMapping[(int, Any)]
else:
    _IFDv2Base = MutableMapping

class ImageFileDirectory_v2(_IFDv2Base):
    """This class represents a TIFF tag directory.  To speed things up, we
don't decode tags unless they're asked for.

Exposes a dictionary interface of the tags in the directory::

    ifd = ImageFileDirectory_v2()
    ifd[key] = 'Some Data'
    ifd.tagtype[key] = TiffTags.ASCII
    print(ifd[key])
    'Some Data'

Individual values are returned as the strings or numbers, sequences are
returned as tuples of the values.

The tiff metadata type of each item is stored in a dictionary of
tag types in
:attr:`~PIL.TiffImagePlugin.ImageFileDirectory_v2.tagtype`. The types
are read from a tiff file, guessed from the type added, or added
manually.

Data Structures:

    * ``self.tagtype = {}``

      * Key: numerical TIFF tag number
      * Value: integer corresponding to the data type from
        :py:data:`.TiffTags.TYPES`

      .. versionadded:: 3.0.0

'Internal' data structures:

    * ``self._tags_v2 = {}``

      * Key: numerical TIFF tag number
      * Value: decoded data, as tuple for multiple values

    * ``self._tagdata = {}``

      * Key: numerical TIFF tag number
      * Value: undecoded byte string from file

    * ``self._tags_v1 = {}``

      * Key: numerical TIFF tag number
      * Value: decoded data in the v1 format

Tags will be found in the private attributes ``self._tagdata``, and in
``self._tags_v2`` once decoded.

``self.legacy_api`` is a value for internal use, and shouldn't be changed
from outside code. In cooperation with
:py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v1`, if ``legacy_api``
is true, then decoded tags will be populated into both ``_tags_v1`` and
``_tags_v2``. ``_tags_v2`` will be used if this IFD is used in the TIFF
save routine. Tags should be read from ``_tags_v1`` if
``legacy_api == true``.

"""
    _load_dispatch: 'dict[int, tuple[int, _LoaderFunc]]' = { }
    _write_dispatch: 'dict[int, Callable[..., Any]]' = { }
    
    def __init__(self, ifh = b'II*\x00\x00\x00\x00\x00', prefix = None, group = None):
        """Initialize an ImageFileDirectory.

To construct an ImageFileDirectory from a real file, pass the 8-byte
magic header to the constructor.  To only set the endianness, pass it
as the 'prefix' keyword argument.

:param ifh: One of the accepted magic headers (cf. PREFIXES); also sets
      endianness.
:param prefix: Override the endianness of the file.
"""
        if not _accept(ifh):
            msg = f'''not a TIFF file (header {repr(ifh)} not valid)'''
            raise SyntaxError(msg)
        self._prefix = prefix if prefix is not None else ifh[slice(None, 2, None)]
        if self._prefix == MM:
            self._endian = '>'
        elif self._prefix == II:
            self._endian = '<'
        else:
            msg = 'not a TIFF IFD'
            raise SyntaxError(msg)
        self._bigtiff = ifh[2] == 43
        self.group = group
        self.tagtype = { }
        self.reset()
        self.next = self._unpack('Q', ifh[slice(8, None, None)])[0] if self._bigtiff else self._unpack('L', ifh[slice(4, None, None)])[0]
        self._legacy_api = False

    prefix = property((lambda self: self._prefix))
    offset = property((lambda self: self._offset))
    legacy_api = (lambda self: self._legacy_api)()
    legacy_api = (lambda self, value: msg = 'Not allowing setting of legacy api'raise Exception(msg))()
    
    def reset(self):
        self._tags_v1 = { }
        self._tags_v2 = { }
        self._tagdata = { }
        self.tagtype = { }
        self._next = None
        self._offset = None

    
    def __str__(self):
        return str(dict(self))

    
    def named(self):
        '''
:returns: dict of name|key: value

Returns the complete tag dictionary, with named tags where possible.
'''
        return None
    # WARNING: Decompyle incomplete

    
    def __len__(self):
        return len(set(self._tagdata) | set(self._tags_v2))

    
    def __getitem__(self, tag):
        if tag not in self._tags_v2:
            data = self._tagdata[tag]
            typ = self.tagtype[tag]
            size, handler = self._load_dispatch[typ]
            self[tag] = handler(self, data, self.legacy_api)
        val = self._tags_v2[tag]
        if self.legacy_api and not isinstance(val, (tuple, bytes)):
            val = (val,)
        return val

    
    def __contains__(self, tag):
        return tag in self._tags_v2 or tag in self._tagdata

    
    def __setitem__(self, tag, value):
        self._setitem(tag, value, self.legacy_api)

    
    def _setitem(self, tag, value, legacy_api):
        basetypes = (Number, bytes, str)
        info = TiffTags.lookup(tag, self.group)
        values = [
            value] if isinstance(value, basetypes) else value
        if tag not in self.tagtype:
            if info.type:
                self.tagtype[tag] = info.type
            else:
                self.tagtype[tag] = TiffTags.UNDEFINED
                if all is all:
                    all
                    for None in values():
                        while None:
                            pass
                
                if (lambda .0: for v in .0:
isinstance(v, IFDRational).0)(values()):
                    for v in values:
                        if not isinstance(v, IFDRational):
                            raise AssertionError
                        while not v < 0:
                            pass
                        self.tagtype[tag] = TiffTags.SIGNED_RATIONAL
                        values
                    self.tagtype[tag] = TiffTags.RATIONAL
                elif all is all:
                    all
                    for None in values():
                        while None:
                            pass
                
                if (lambda .0: for v in .0:
isinstance(v, int).0)(values()):
                    short = True
                    signed_short = True
                    long = True
                    for v in values:
                        if not isinstance(v, int):
                            raise AssertionError
                        if short:
                            if not (0 <= v) or not (v < 65536):
                                short = False
                        if signed_short:
                            if not (-32768 < v) or not (v < 32768):
                                signed_short = False
                        if not long:
                            continue
                        if not v < 0:
                            continue
                        long = False
                    if short:
                        self.tagtype[tag] = TiffTags.SHORT
                    elif signed_short:
                        self.tagtype[tag] = TiffTags.SIGNED_SHORT
                    elif long:
                        self.tagtype[tag] = TiffTags.LONG
                    else:
                        self.tagtype[tag] = TiffTags.SIGNED_LONG
                elif all is all:
                    all
                    for None in values():
                        while None:
                            pass
                
                if (lambda .0: for v in .0:
isinstance(v, float).0)(values()):
                    self.tagtype[tag] = TiffTags.DOUBLE
                elif all is all:
                    all
                    for None in values():
                        while None:
                            pass
                
                if (lambda .0: for v in .0:
isinstance(v, str).0)(values()):
                    self.tagtype[tag] = TiffTags.ASCII
                elif all is all:
                    all
                    for None in values():
                        while None:
                            pass
                
                if (lambda .0: for v in .0:
isinstance(v, bytes).0)(values()):
                    self.tagtype[tag] = TiffTags.BYTE
        if self.tagtype[tag] == TiffTags.UNDEFINED:
            
            try:
                for v in values:
                    pass
            v = True
            
            try:
                for v in values:
                    pass
            v = True


            values = []
            v = v
        elif self.tagtype[tag] == TiffTags.RATIONAL:
            
            try:
                for v in values:
                    pass
            v = True

            values = []
            v = v
        is_ifd = self.tagtype[tag] == TiffTags.LONG and isinstance(values, dict)
        if not is_ifd:
            if tuple is tuple:
                tuple
                for None in values():
                    pass
                # unsupported CALL_INTRINSIC_1 6
            
            values = (lambda .0: for value in .0:
info.cvt_enum(value) if isinstance(value, str) else value.0)(values())
        dest = self._tags_v1 if legacy_api else self._tags_v2
        if not is_ifd:
            if (not (not (info.length == 1) and not (self.tagtype[tag] == TiffTags.BYTE)) or info.length is None and len(values) == 1) and not legacy_api:
                if legacy_api and self.tagtype[tag] in (TiffTags.RATIONAL, TiffTags.SIGNED_RATIONAL):
                    values = (values,)
                
                try:
                    (dest[tag],) = values
                except ValueError:
                    warnings.warn(f'''Metadata Warning, tag {tag} had too many entries: {len(values)}, expected 1''')
                    dest[tag] = values[0]
                    return None

                return None
        dest[tag] = values
        return None
    # WARNING: Decompyle incomplete

    
    def __delitem__(self, tag):
        self._tags_v2.pop(tag, None)
        self._tags_v1.pop(tag, None)
        self._tagdata.pop(tag, None)

    
    def __iter__(self):
        return iter(set(self._tagdata) | set(self._tags_v2))

    
    def _unpack(self, fmt, data):
        return struct.unpack(self._endian + fmt, data)

    
    def _pack(self, fmt, *values):
        # unsupported CALL_INTRINSIC_1 6
        return struct.pack()
    # WARNING: Decompyle incomplete

    list(map(_register_basic, [
        (TiffTags.SHORT, 'H', 'short'),
        (TiffTags.LONG, 'L', 'long'),
        (TiffTags.SIGNED_BYTE, 'b', 'signed byte'),
        (TiffTags.SIGNED_SHORT, 'h', 'signed short'),
        (TiffTags.SIGNED_LONG, 'l', 'signed long'),
        (TiffTags.FLOAT, 'f', 'float'),
        (TiffTags.DOUBLE, 'd', 'double'),
        (TiffTags.IFD, 'L', 'long'),
        (TiffTags.LONG8, 'Q', 'long8')]))
    load_byte = (lambda self, data, legacy_api = True: data)()
    write_byte = (lambda self, data: if isinstance(data, IFDRational):
data = int(data)if isinstance(data, int):
data = bytes((data,))data)()
    load_string = (lambda self, data, legacy_api = True: if data.endswith(b'\x00'):
data = data[:-1]data.decode('latin-1', 'replace'))()
    write_string = (lambda self, value: if isinstance(value, int):
value = str(value)if not isinstance(value, bytes):
value = value.encode('ascii', 'replace')value + b'\x00')()
    load_rational = (lambda self, data, legacy_api = True: vals = self._unpack(f'''{len(data) // 4}L''', data)
def combine(a, b):
if legacy_api:
(a, b)IFDRational(a, b)if tuple is tuple:
tuplefor None in zip(vals[slice(None, None, 2)], vals[slice(1, None, 2)])():
pass# unsupported CALL_INTRINSIC_1 6(lambda .0: for num, denom in .0:
combine(num, denom).0)
        return (lambda .0: for num, denom in .0:
combine(num, denom).0)(zip(vals[slice(None, None, 2)], vals[slice(1, None, 2)])())
    # WARNING: Decompyle incomplete
)()
    write_rational = (lambda self: (lambda .0: for frac in .0:
# unsupported CALL_INTRINSIC_1 6self._pack().0None# WARNING: Decompyle incomplete
)(values())
)()
    load_undefined = (lambda self, data, legacy_api = True: data)()
    write_undefined = (lambda self, value: if isinstance(value, IFDRational):
value = int(value)if isinstance(value, int):
value = str(value).encode('ascii', 'replace')value)()
    load_signed_rational = (lambda self, data, legacy_api = True: vals = self._unpack(f'''{len(data) // 4}l''', data)
def combine(a, b):
if legacy_api:
(a, b)IFDRational(a, b)if tuple is tuple:
tuplefor None in zip(vals[slice(None, None, 2)], vals[slice(1, None, 2)])():
pass# unsupported CALL_INTRINSIC_1 6(lambda .0: for num, denom in .0:
combine(num, denom).0)
        return (lambda .0: for num, denom in .0:
combine(num, denom).0)(zip(vals[slice(None, None, 2)], vals[slice(1, None, 2)])())
    # WARNING: Decompyle incomplete
)()
    write_signed_rational = (lambda self: (lambda .0: for frac in .0:
# unsupported CALL_INTRINSIC_1 6self._pack().0None# WARNING: Decompyle incomplete
)(values())
)()
    
    def _ensure_read(self, fp, size):
        '''Corrupt EXIF data.  Expecting to read '''
        ret = fp.read(size)
        if len(ret) != size:
            msg = f'''Corrupt EXIF data.  Expecting to read {size} bytes but only got {len(ret)}. '''
            raise OSError(msg)
        return ret

    
    def load(self, fp):
        '''Q'''
        self.reset()
        self._offset = fp.tell()
        
        try:
            tag_count = self._unpack('Q', self._ensure_read(fp, 8)) if self._bigtiff else self._unpack('H', self._ensure_read(fp, 2))[0]
            for i in range(tag_count):
                tag, typ, count, data = self._unpack('HHQ8s', self._ensure_read(fp, 20)) if self._bigtiff else self._unpack('HHL4s', self._ensure_read(fp, 12))
                tagname = TiffTags.lookup(tag, self.group).name
                typname = TYPES.get(typ, 'unknown')
                msg = f'''tag: {tagname} ({tag}) - type: {typname} ({typ})'''
                
                try:
                    unit_size, handler = self._load_dispatch[typ]
                except KeyError:
                    logger.debug('%s - unsupported type %s', msg, typ)

                size = count * unit_size
                if size > 8 if self._bigtiff else 4:
                    here = fp.tell()
                    (offset,) = self._unpack('Q' if self._bigtiff else 'L', data)
                    msg += f''' Tag Location: {here} - Data Location: {offset}'''
                    fp.seek(offset)
                    data = ImageFile._safe_read(fp, size)
                    fp.seek(here)
                else:
                    data = data[:size]
                if len(data) != size:
                    warnings.warn(f'''Possibly corrupt EXIF data.  Expecting to read {size} bytes but only got {len(data)}. Skipping tag {tag}''')
                    logger.debug(msg)
                    continue
                if not data:
                    logger.debug(msg)
                    continue
                self._tagdata[tag] = data
                self.tagtype[tag] = typ
                msg += ' - value: '
                msg += f'''<table: {size} bytes>''' if size > 32 else repr(data)
                logger.debug(msg)
            (self.next,) = self._unpack('Q', self._ensure_read(fp, 8)) if self._bigtiff else self._unpack('L', self._ensure_read(fp, 4))
        except OSError as msg:
            warnings.warn(str(msg))
            return None


    
    def _get_ifh(self):
        '''H'''
        ifh = self._prefix + self._pack('H', 43 if self._bigtiff else 42)
        if self._bigtiff:
            ifh += self._pack('HH', 8, 0)
        if self._bigtiff:
            ifh += self._pack('Q', 16)
            return ifh
        ifh += self._pack('L', 8)
        return ifh

    
    def tobytes(self, offset = 0):
        '''Q'''
        result = self._pack('Q' if self._bigtiff else 'H', len(self._tags_v2))
        entries = []
        fmt = 'Q' if self._bigtiff else 'L'
        fmt_size = 8 if self._bigtiff else 4
        offset += len(result) + len(self._tags_v2) * 20 if self._bigtiff else 12 + fmt_size
        stripoffsets = None
        for tag, value in sorted(self._tags_v2.items()):
            if tag == STRIPOFFSETS:
                stripoffsets = len(entries)
            typ = self.tagtype[tag]
            logger.debug('Tag %s, Type: %s, Value: %s', tag, typ, repr(value))
            is_ifd = typ == TiffTags.LONG and isinstance(value, dict)
            if is_ifd:
                ifd = ImageFileDirectory_v2(self._get_ifh(), group = tag)
                values = self._tags_v2[tag]
                for ifd_tag, ifd_value in values.items():
                    ifd[ifd_tag] = ifd_value
                data = ifd.tobytes(offset)
            elif isinstance(value, tuple):
                pass
            
            values = (value,)
            # unsupported CALL_INTRINSIC_1 6
            data = self._write_dispatch[typ]()
            tagname = TiffTags.lookup(tag, self.group).name
            typname = 'ifd' if is_ifd else TYPES.get(typ, 'unknown')
            msg = f'''save: {tagname} ({tag}) - type: {typname} ({typ}) - value: '''
            msg += f'''<table: {len(data)} bytes>''' if len(data) >= 16 else str(values)
            logger.debug(msg)
            if is_ifd:
                count = 1
            elif typ in (TiffTags.BYTE, TiffTags.ASCII, TiffTags.UNDEFINED):
                count = len(data)
            else:
                count = len(values)
            if len(data) <= fmt_size:
                entries.append((tag, typ, count, data.ljust(fmt_size, b'\x00'), b''))
                continue
            entries.append((tag, typ, count, self._pack(fmt, offset), data))
            offset += ((len(data) + 1) // 2) * 2
        if stripoffsets is not None:
            tag, typ, count, value, data = entries[stripoffsets]
            if data:
                (size, handler) = self._load_dispatch[typ]
                
                try:
                    for val in handler(self, data, self.legacy_api):
                        pass
                val = None

                values = []
                val = val
                # unsupported CALL_INTRINSIC_1 6
                data = self._write_dispatch[typ]()
            else:
                value = self._pack(fmt, self._unpack(fmt, value)[0] + offset)
            entries[stripoffsets] = (tag, typ, count, value, data)
        for tag, typ, count, value, data in entries:
            logger.debug('%s %s %s %s %s', tag, typ, count, repr(value), repr(data))
            result += self._pack('HHQ8s' if self._bigtiff else 'HHL4s', tag, typ, count, value)
        result += self._pack(fmt, 0)
        for tag, typ, count, value, data in entries:
            result += data
            if not len(data) & 1:
                continue
            result += b'\x00'
        return result
    # WARNING: Decompyle incomplete

    
    def save(self, fp):
        if fp.tell() == 0:
            fp.write(self._get_ifh())
        offset = fp.tell()
        result = self.tobytes(offset)
        fp.write(result)
        return offset + len(result)


ImageFileDirectory_v2._load_dispatch = _load_dispatch
ImageFileDirectory_v2._write_dispatch = _write_dispatch
del _load_dispatch
del _write_dispatch
del idx
del name

class ImageFileDirectory_v1(ImageFileDirectory_v2):
    """This class represents the **legacy** interface to a TIFF tag directory.

Exposes a dictionary interface of the tags in the directory::

    ifd = ImageFileDirectory_v1()
    ifd[key] = 'Some Data'
    ifd.tagtype[key] = TiffTags.ASCII
    print(ifd[key])
    ('Some Data',)

Also contains a dictionary of tag types as read from the tiff image file,
:attr:`~PIL.TiffImagePlugin.ImageFileDirectory_v1.tagtype`.

Values are returned as a tuple.

..  deprecated:: 3.0.0
"""
    
    def __init__(self, *args, **kwargs):
        # unsupported opcode LOAD_SUPER_ATTR
        args(*{
            **kwargs })
        self._legacy_api = True
        return None
    # WARNING: Decompyle incomplete

    tags = property((lambda self: self._tags_v1))
    tagtype: 'dict[int, int]' = property((lambda self: self._tagdata))
    from_v2 = (lambda cls, original: ifd = cls(prefix = original.prefix)ifd._tagdata = original._tagdataifd.tagtype = original.tagtypeifd.next = original.nextifd)()
    
    def to_v2(self):
        '''Returns an
:py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v2`
instance with the same data as is contained in the original
:py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v1`
instance.

:returns: :py:class:`~PIL.TiffImagePlugin.ImageFileDirectory_v2`

'''
        ifd = ImageFileDirectory_v2(prefix = self.prefix)
        ifd._tagdata = dict(self._tagdata)
        ifd.tagtype = dict(self.tagtype)
        ifd._tags_v2 = dict(self._tags_v2)
        return ifd

    
    def __contains__(self, tag):
        return tag in self._tags_v1 or tag in self._tagdata

    
    def __len__(self):
        return len(set(self._tagdata) | set(self._tags_v1))

    
    def __iter__(self):
        return iter(set(self._tagdata) | set(self._tags_v1))

    
    def __setitem__(self, tag, value):
        for legacy_api in (False, True):
            self._setitem(tag, value, legacy_api)

    
    def __getitem__(self, tag):
        if tag not in self._tags_v1:
            data = self._tagdata[tag]
            typ = self.tagtype[tag]
            size, handler = self._load_dispatch[typ]
            for legacy in (False, True):
                self._setitem(tag, handler(self, data, legacy), legacy)
        val = self._tags_v1[tag]
        if not isinstance(val, (tuple, bytes)):
            val = (val,)
        return val


ImageFileDirectory = ImageFileDirectory_v1

class TiffImageFile(ImageFile.ImageFile):
    format = 'TIFF'
    format_description = 'Adobe TIFF'
    _close_exclusive_fp_after_loading = False
    
    def __init__(self, fp, filename = None):
        self
        self
        # unsupported opcode LOAD_SUPER_ATTR
        self(fp, filename)
        return None
    # WARNING: Decompyle incomplete

    
    def _open(self):
        '''Open the first image in a TIFF file'''
        if self.fp is None:
            raise AssertionError
        ifh = self.fp.read(8)
        if ifh[2] == 43:
            ifh += self.fp.read(8)
        self.tag_v2 = ImageFileDirectory_v2(ifh)
        self._TiffImageFile__first = self.tag_v2.next
        self._TiffImageFile__next = self.tag_v2.next
        self._TiffImageFile__frame = -1
        self._fp = self.fp
        self._frame_pos = []
        self._n_frames = None
        logger.debug('*** TiffImageFile._open ***')
        logger.debug('- __first: %s', self._TiffImageFile__first)
        logger.debug('- ifh: %s', repr(ifh))
        self._seek(0)

    n_frames = (lambda self: current_n_frames = self._n_framesif current_n_frames is None:
current = self.tell()self._seek(len(self._frame_pos))while self._n_frames:
self._seek(self.tell() + 1)self.seek(current)if self._n_frames is None:
raise AssertionErrorself._n_frames)()
    
    def seek(self, frame):
        '''Select a given frame as current image'''
        if not self._seek_check(frame):
            return None
        self._seek(frame)
        if self._im is not None:
            if not (not (self.im.size != self._tile_size) and not (self.im.mode != self.mode)) or self.readonly:
                self._im = None
                return None
            return None

    
    def _seek(self, frame):
        '''no more images in TIFF file'''
        if isinstance(self._fp, DeferredError):
            raise self._fp.ex
        self.fp = self._fp
        while len(self._frame_pos) <= frame:
            if not self._TiffImageFile__next:
                msg = 'no more images in TIFF file'
                raise EOFError(msg)
            logger.debug('Seeking to frame %s, on frame %s, __next %s, location: %s', frame, self._TiffImageFile__frame, self._TiffImageFile__next, self.fp.tell())
            if self._TiffImageFile__next >= 0x8000000000000000:
                msg = 'Unable to seek to frame'
                raise ValueError(msg)
            self.fp.seek(self._TiffImageFile__next)
            self._frame_pos.append(self._TiffImageFile__next)
            logger.debug('Loading tags, location: %s', self.fp.tell())
            self.tag_v2.load(self.fp)
            if self.tag_v2.next in self._frame_pos:
                self._TiffImageFile__next = 0
            else:
                self._TiffImageFile__next = self.tag_v2.next
            if self._TiffImageFile__next == 0:
                self._n_frames = frame + 1
            if len(self._frame_pos) == 1:
                self.is_animated = self._TiffImageFile__next != 0
            self._TiffImageFile__frame += 1
        self.fp.seek(self._frame_pos[frame])
        self.tag_v2.load(self.fp)
        if XMP in self.tag_v2:
            xmp = self.tag_v2[XMP]
            if isinstance(xmp, tuple) and len(xmp) == 1:
                xmp = xmp[0]
            self.info['xmp'] = xmp
        elif 'xmp' in self.info:
            del self.info['xmp']
        self._reload_exif()
        self.tag = ImageFileDirectory_v1.from_v2(self.tag_v2)
        self.ifd = ImageFileDirectory_v1.from_v2(self.tag_v2)
        self._TiffImageFile__frame = frame
        self._setup()

    
    def tell(self):
        '''Return the current frame number'''
        return self._TiffImageFile__frame

    
    def get_photoshop_blocks(self):
        '''
Returns a dictionary of Photoshop "Image Resource Blocks".
The keys are the image resource ID. For more information, see
https://www.adobe.com/devnet-apps/photoshop/fileformatashtml/#50577409_pgfId-1037727

:returns: Photoshop "Image Resource Blocks" in a dictionary.
'''
        blocks = { }
        val = self.tag_v2.get(ExifTags.Base.ImageResources)
        if val:
            while val.startswith(b'8BIM') and len(val) >= 12:
                id = i16(val[slice(4, 6, None)])
                n = math.ceil((val[6] + 1) / 2) * 2
                
                try:
                    size = i32(val[6 + n:10 + n])
                except struct.error:
                    return blocks

                data = val[10 + n:10 + n + size]
                blocks[id] = {
                    'data': data }
                val = val[math.ceil((10 + n + size) / 2) * 2:]
        return blocks

    
    def load(self):
        if self.tile and self.use_load_libtiff:
            return self._load_libtiff()
        # unsupported opcode LOAD_SUPER_ATTR
        return self()
    # WARNING: Decompyle incomplete

    
    def load_prepare(self):
        if self._im is None:
            Image._decompression_bomb_check(self._tile_size)
            self.im = Image.core.new(self.mode, self._tile_size)
        ImageFile.ImageFile.load_prepare(self)

    
    def load_end(self):
        if not self.is_animated:
            self._close_exclusive_fp_after_loading = True
            exif = self.getexif()
            for key in TiffTags.TAGS_V2_GROUPS:
                while key not in exif:
                    pass
                exif.get_ifd(key)
        ImageOps.exif_transpose(self, in_place = True)
        if ExifTags.Base.Orientation in self.tag_v2:
            del self.tag_v2[ExifTags.Base.Orientation]
            return None

    
    def _load_libtiff(self):
        '''Overload method triggered when we detect a compressed tiff
Calls out to libtiff'''
        Image.Image.load(self)
        self.load_prepare()
        if not len(self.tile) == 1:
            msg = 'Not exactly one tile'
            raise OSError(msg)
        extents = self.tile[0][1]
        args = self.tile[0][3]
        if self.fp is None:
            raise AssertionError
        
        try:
            fp = hasattr(self.fp, 'fileno') and self.fp.fileno()
            if hasattr(self.fp, 'flush'):
                self.fp.flush()
        except OSError:
            fp = False

        if fp:
            if not isinstance(args, tuple):
                raise AssertionError
            args_list = list(args)
            args_list[2] = fp
            args = tuple(args_list)
        decoder = Image._getdecoder(self.mode, 'libtiff', args, self.decoderconfig)
        
        try:
            decoder.setimage(self.im, extents)
        except ValueError as e:
            msg = "Couldn't set the image"
            raise OSError(msg) from e

        close_self_fp = self._exclusive_fp and not (self.is_animated)
        if hasattr(self.fp, 'getvalue'):
            logger.debug('have getvalue. just sending in a string from getvalue')
            n, err = decoder.decode(self.fp.getvalue())
        elif fp:
            logger.debug('have fileno, calling fileno version of the decoder.')
            if not close_self_fp:
                self.fp.seek(0)
            pos = os.lseek(fp, 0, os.SEEK_CUR)
            n, err = decoder.decode(b'fpfp')
            os.lseek(fp, pos, os.SEEK_SET)
        else:
            logger.debug("don't have fileno or getvalue. just reading")
            self.fp.seek(0)
            n, err = decoder.decode(self.fp.read())
        self.tile = []
        self.readonly = 0
        self.load_end()
        if close_self_fp:
            self.fp.close()
            self.fp = None
        if err < 0:
            msg = f'''decoder error {err}'''
            raise OSError(msg)
        return Image.Image.load(self)

    
    def _setup(self):
        '''Setup this image object based on current tags'''
        if 48129 in self.tag_v2:
            msg = 'Windows Media Photo files not yet supported'
            raise OSError(msg)
        self._compression = COMPRESSION_INFO[self.tag_v2.get(COMPRESSION, 1)]
        self._planar_configuration = self.tag_v2.get(PLANAR_CONFIGURATION, 1)
        photo = self.tag_v2.get(PHOTOMETRIC_INTERPRETATION, 0)
        if self._compression == 'tiff_jpeg':
            photo = 6
        fillorder = self.tag_v2.get(FILLORDER, 1)
        logger.debug('*** Summary ***')
        logger.debug('- compression: %s', self._compression)
        logger.debug('- photometric_interpretation: %s', photo)
        logger.debug('- planar_configuration: %s', self._planar_configuration)
        logger.debug('- fill_order: %s', fillorder)
        logger.debug('- YCbCr subsampling: %s', self.tag_v2.get(YCBCRSUBSAMPLING))
        
        try:
            xsize = self.tag_v2[IMAGEWIDTH]
            ysize = self.tag_v2[IMAGELENGTH]
        except KeyError as e:
            msg = 'Missing dimensions'
            raise TypeError(msg) from e

        if not isinstance(xsize, int) or not isinstance(ysize, int):
            msg = 'Invalid dimensions'
            raise ValueError(msg)
        self._tile_size = (xsize, ysize)
        orientation = self.tag_v2.get(ExifTags.Base.Orientation)
        if orientation in (5, 6, 7, 8):
            self._size = (ysize, xsize)
        else:
            self._size = (xsize, ysize)
        logger.debug('- size: %s', self.size)
        sample_format = self.tag_v2.get(SAMPLEFORMAT, (1,))
        if len(sample_format) > 1 and max(sample_format) == min(sample_format):
            sample_format = (sample_format[0],)
        bps_tuple = self.tag_v2.get(BITSPERSAMPLE, (1,))
        extra_tuple = self.tag_v2.get(EXTRASAMPLES, ())
        samples_per_pixel = self.tag_v2.get(SAMPLESPERPIXEL, 3 if self._compression == 'tiff_jpeg' and photo in (2, 6) else 1)
        if photo in (2, 6, 8):
            bps_count = 3
        elif photo == 5:
            bps_count = 4
        else:
            bps_count = 1
        if self._planar_configuration == 2 and extra_tuple and max(extra_tuple) == 0:
            bps_tuple = bps_tuple[:-len(extra_tuple)]
            samples_per_pixel -= len(extra_tuple)
            extra_tuple = ()
        bps_count += len(extra_tuple)
        bps_actual_count = len(bps_tuple)
        if samples_per_pixel > MAX_SAMPLESPERPIXEL:
            logger.error('More samples per pixel than can be decoded: %s', samples_per_pixel)
            msg = 'Invalid value for samples per pixel'
            raise SyntaxError(msg)
        if samples_per_pixel < bps_actual_count:
            bps_tuple = bps_tuple[:samples_per_pixel]
        elif samples_per_pixel > bps_actual_count and bps_actual_count == 1:
            bps_tuple = bps_tuple * samples_per_pixel
        if len(bps_tuple) != samples_per_pixel:
            msg = 'unknown data organization'
            raise SyntaxError(msg)
        key = (self.tag_v2.prefix, photo, sample_format, fillorder, bps_tuple, extra_tuple)
        logger.debug('format key: %s', key)
        
        try:
            (self._mode, rawmode) = OPEN_INFO[key]
        except KeyError as e:
            logger.debug('- unsupported format')
            msg = 'unknown pixel mode'
            raise SyntaxError(msg) from e

        logger.debug('- raw mode: %s', rawmode)
        logger.debug('- pil mode: %s', self.mode)
        self.info['compression'] = self._compression
        xres = self.tag_v2.get(X_RESOLUTION, 1)
        yres = self.tag_v2.get(Y_RESOLUTION, 1)
        if xres and yres:
            resunit = self.tag_v2.get(RESOLUTION_UNIT)
            if resunit == 2:
                self.info['dpi'] = (xres, yres)
            elif resunit == 3:
                self.info['dpi'] = (xres * 2.54, yres * 2.54)
            elif resunit is None:
                self.info['dpi'] = (xres, yres)
                self.info['resolution'] = (xres, yres)
            else:
                self.info['resolution'] = (xres, yres)
        x = 0
        y = 0
        layer = 0
        self.tile = []
        self.use_load_libtiff = READ_LIBTIFF or self._compression != 'raw'
        if self.use_load_libtiff:
            if fillorder == 2:
                key = key[slice(None, 3, None)] + (1,) + key[slice(4, None, None)]
                logger.debug('format key: %s', key)
                (self._mode, rawmode) = OPEN_INFO[key]
            if photo == 6 and self._compression == 'jpeg' and self._planar_configuration == 1:
                rawmode = 'RGB'
            elif rawmode == 'I;16':
                rawmode = 'I;16N'
            elif rawmode.endswith((';16B', ';16L')):
                rawmode = rawmode[:-1] + 'N'
            a = (rawmode, self._compression, False, self.tag_v2.offset)
            self.tile.append(ImageFile._Tile('libtiff', (0, 0, xsize, ysize), 0, a))
        elif STRIPOFFSETS in self.tag_v2 or TILEOFFSETS in self.tag_v2:
            if STRIPOFFSETS in self.tag_v2:
                offsets = self.tag_v2[STRIPOFFSETS]
                h = self.tag_v2.get(ROWSPERSTRIP, ysize)
                w = xsize
            else:
                offsets = self.tag_v2[TILEOFFSETS]
                tilewidth = self.tag_v2.get(TILEWIDTH)
                h = self.tag_v2.get(TILELENGTH)
                if not isinstance(tilewidth, int) or not isinstance(h, int):
                    msg = 'Invalid tile dimensions'
                    raise ValueError(msg)
                w = tilewidth
            if w == xsize and h == ysize and self._planar_configuration != 2:
                offsets = offsets[-1:]
            for offset in offsets:
                if x + w > xsize:
                    stride = w * sum(bps_tuple) / 8
                else:
                    stride = 0
                tile_rawmode = rawmode
                if self._planar_configuration == 2:
                    tile_rawmode = rawmode[layer]
                    stride /= bps_count
                args = (tile_rawmode, int(stride), 1)
                self.tile.append(ImageFile._Tile(self._compression, (x, y, min(x + w, xsize), min(y + h, ysize)), offset, args))
                x += w
                if not x >= xsize:
                    continue
                y = y + h
                x = 0
                if not y >= ysize:
                    continue
                y = 0
                layer += 1
        else:
            logger.debug('- unsupported data organization')
            msg = 'unknown data organization'
            raise SyntaxError(msg)
        if ICCPROFILE in self.tag_v2:
            self.info['icc_profile'] = self.tag_v2[ICCPROFILE]
        if self.mode in ('P', 'PA'):
            
            try:
                for b in self.tag_v2[COLORMAP]:
                    pass
            b = None

            palette = []
            b = b
            self.palette = ImagePalette.raw('RGB;L', b''.join(palette))
            return None
        return None
    # WARNING: Decompyle incomplete


SAVE_INFO = {
    '1': ('1', II, 1, 1, (1,), None),
    'L': ('L', II, 1, 1, (8,), None),
    'LA': ('LA', II, 1, 1, (8, 8), 2),
    'P': ('P', II, 3, 1, (8,), None),
    'PA': ('PA', II, 3, 1, (8, 8), 2),
    'I': ('I;32S', II, 1, 2, (32,), None),
    'I;16': ('I;16', II, 1, 1, (16,), None),
    'I;16L': ('I;16L', II, 1, 1, (16,), None),
    'F': ('F;32F', II, 1, 3, (32,), None),
    'RGB': ('RGB', II, 2, 1, (8, 8, 8), None),
    'RGBX': ('RGBX', II, 2, 1, (8, 8, 8, 8), 0),
    'RGBA': ('RGBA', II, 2, 1, (8, 8, 8, 8), 2),
    'CMYK': ('CMYK', II, 5, 1, (8, 8, 8, 8), None),
    'YCbCr': ('YCbCr', II, 6, 1, (8, 8, 8), None),
    'LAB': ('LAB', II, 8, 1, (8, 8, 8), None),
    'I;16B': ('I;16B', MM, 1, 1, (16,), None) }

def _save(im, fp, filename):
    '''cannot write mode '''
    
    try:
        rawmode, prefix, photo, format, bits, extra = SAVE_INFO[im.mode]
    except KeyError as e:
        msg = f'''cannot write mode {im.mode} as TIFF'''
        raise OSError(msg) from e

    encoderinfo = im.encoderinfo
    encoderconfig = im.encoderconfig
    ifd = ImageFileDirectory_v2(prefix = prefix)
    if encoderinfo.get('big_tiff'):
        ifd._bigtiff = True
    
    try:
        compression = encoderinfo['compression']
    except KeyError:
        compression = im.info.get('compression')
        if isinstance(compression, int):
            compression = None

    if compression is None:
        compression = 'raw'
    elif compression == 'tiff_jpeg':
        compression = 'jpeg'
    elif compression == 'tiff_deflate':
        compression = 'tiff_adobe_deflate'
    libtiff = WRITE_LIBTIFF or compression != 'raw'
    ifd[PLANAR_CONFIGURATION] = 1
    ifd[IMAGEWIDTH] = im.size[0]
    ifd[IMAGELENGTH] = im.size[1]
    if 'tiffinfo' in encoderinfo:
        info = encoderinfo['tiffinfo']
    elif 'exif' in encoderinfo:
        info = encoderinfo['exif']
        if isinstance(info, bytes):
            exif = Image.Exif()
            exif.load(info)
            info = exif
    else:
        info = { }
    logger.debug('Tiffinfo Keys: %s', list(info))
    if isinstance(info, ImageFileDirectory_v1):
        info = info.to_v2()
    for key in info:
        if isinstance(info, Image.Exif) and key in TiffTags.TAGS_V2_GROUPS:
            ifd[key] = info.get_ifd(key)
        else:
            ifd[key] = info.get(key)
        
        try:
            ifd.tagtype[key] = info.tagtype[key]
        except Exception:
            pass

    legacy_ifd = { }
    if hasattr(im, 'tag'):
        legacy_ifd = im.tag.to_v2()
    supplied_tags = {
        **legacy_ifd,
        **getattr(im, 'tag_v2', { }) }
    if supplied_tags.get(PLANAR_CONFIGURATION) == 2 and EXTRASAMPLES in supplied_tags:
        if SAMPLESPERPIXEL in supplied_tags:
            supplied_tags[SAMPLESPERPIXEL] -= len(supplied_tags[EXTRASAMPLES])
        del supplied_tags[EXTRASAMPLES]
    for tag in (EXIFIFD, SAMPLEFORMAT):
        while not tag in supplied_tags:
            pass
        del supplied_tags[tag]
    if hasattr(im, 'tag_v2'):
        for key in (RESOLUTION_UNIT, X_RESOLUTION, Y_RESOLUTION, IPTC_NAA_CHUNK, PHOTOSHOP_CHUNK, XMP):
            while not key in im.tag_v2:
                pass
            while key == IPTC_NAA_CHUNK and im.tag_v2.tagtype[key] not in (TiffTags.BYTE, TiffTags.UNDEFINED):
                del supplied_tags[key]
            ifd[key] = im.tag_v2[key]
            ifd.tagtype[key] = im.tag_v2.tagtype[key]
    icc = encoderinfo.get('icc_profile', im.info.get('icc_profile'))
    if icc:
        ifd[ICCPROFILE] = icc
    for key, name in ((IMAGEDESCRIPTION, 'description'), (X_RESOLUTION, 'resolution'), (Y_RESOLUTION, 'resolution'), (X_RESOLUTION, 'x_resolution'), (Y_RESOLUTION, 'y_resolution'), (RESOLUTION_UNIT, 'resolution_unit'), (SOFTWARE, 'software'), (DATE_TIME, 'date_time'), (ARTIST, 'artist'), (COPYRIGHT, 'copyright')):
        while not name in encoderinfo:
            pass
        ifd[key] = encoderinfo[name]
    dpi = encoderinfo.get('dpi')
    if dpi:
        ifd[RESOLUTION_UNIT] = 2
        ifd[X_RESOLUTION] = dpi[0]
        ifd[Y_RESOLUTION] = dpi[1]
    if bits != (1,):
        ifd[BITSPERSAMPLE] = bits
        if len(bits) != 1:
            ifd[SAMPLESPERPIXEL] = len(bits)
    if extra is not None:
        ifd[EXTRASAMPLES] = extra
    if format != 1:
        ifd[SAMPLEFORMAT] = format
    if PHOTOMETRIC_INTERPRETATION not in ifd:
        ifd[PHOTOMETRIC_INTERPRETATION] = photo
    elif im.mode in ('1', 'L') and ifd[PHOTOMETRIC_INTERPRETATION] == 0:
        if im.mode == '1':
            inverted_im = im.copy()
            px = inverted_im.load()
            if px is not None:
                for y in range(inverted_im.height):
                    for x in range(inverted_im.width):
                        px[(x, y)] = 0 if px[(x, y)] == 255 else 255
                im = inverted_im
        else:
            im = ImageOps.invert(im)
    if im.mode in ('P', 'PA'):
        lut = im.im.getpalette('RGB', 'RGB;L')
        colormap = []
        colors = len(lut) // 3
        for i in range(3):
            range(3) += v
            colormap += [
                0] * (256 - colors)
            ifd[COLORMAP] = colormap
            h = ifd[IMAGELENGTH]
            w = ifd[IMAGEWIDTH]
            stride = len(bits) * ((w * bits[0] + 7) // 8)
            if ROWSPERSTRIP not in ifd:
                if libtiff:
                    im_strip_size = encoderinfo.get('strip_size', STRIP_SIZE)
                    rows_per_strip = 1 if stride == 0 else min(im_strip_size // stride, h)
                    if compression == 'jpeg':
                        rows_per_strip = min(((rows_per_strip + 7) // 8) * 8, h)
                else:
                    rows_per_strip = h
                if rows_per_strip == 0:
                    rows_per_strip = 1
                ifd[ROWSPERSTRIP] = rows_per_strip
            strip_byte_counts = 1 if stride == 0 else stride * ifd[ROWSPERSTRIP]
            strips_per_image = (h + ifd[ROWSPERSTRIP] - 1) // ifd[ROWSPERSTRIP]
            if strip_byte_counts >= 65536:
                ifd.tagtype[STRIPBYTECOUNTS] = TiffTags.LONG
            ifd[STRIPBYTECOUNTS] = (strip_byte_counts,) * (strips_per_image - 1) + (stride * h - strip_byte_counts * (strips_per_image - 1),)
            ifd[STRIPOFFSETS] = tuple(range(0, strip_byte_counts * strips_per_image, strip_byte_counts))
            ifd[COMPRESSION] = COMPRESSION_INFO_REV.get(compression, 1)
            if im.mode == 'YCbCr':
                pass
            blocklist = [
                TILEWIDTH,
                TILELENGTH,
                TILEOFFSETS,
                TILEBYTECOUNTS]
            if libtiff:
                if 'quality' in encoderinfo:
                    quality = encoderinfo['quality']
                    if not (isinstance(quality, int) and not (quality < 0)) or quality > 100:
                        msg = 'Invalid quality setting'
                        raise ValueError(msg)
                    if compression != 'jpeg':
                        msg = "quality setting only supported for 'jpeg' compression"
                        raise ValueError(msg)
                    ifd[JPEGQUALITY] = quality
                logger.debug('Items: %s', sorted(ifd.items()))
                _fp = 0
                if hasattr(fp, 'fileno'):
                    
                    try:
                        fp.seek(0)
                        _fp = fp.fileno()
                    except io.UnsupportedOperation:
                        pass

                types = { }
                blocklist += [
                    OSUBFILETYPE,
                    REFERENCEBLACKWHITE,
                    STRIPBYTECOUNTS,
                    STRIPOFFSETS,
                    TRANSFERFUNCTION,
                    SUBIFD]
                atts = {
                    BITSPERSAMPLE: bits[0] }
                for tag, value in itertools.chain(ifd.items(), supplied_tags.items()):
                    types[tag] = TiffTags.LONG8
                if tag in ifd.tagtype:
                    types[tag] = ifd.tagtype[tag]
                elif isinstance(value, (int, float, str, bytes)) or isinstance(value, tuple):
                    if all is all:
                        all
                        for None in value():
                            while None:
                                pass
                    
                    if (lambda .0: for v in .0:
isinstance(v, (int, float, IFDRational)).0)(value()):
                        type = TiffTags.lookup(tag).type
                        if type:
                            types[tag] = type
                if not tag not in atts:
                    continue
                if not tag not in blocklist:
                    continue
                if isinstance(value, str):
                    atts[tag] = value.encode('ascii', 'replace') + b'\x00'
                    continue
                if isinstance(value, IFDRational):
                    atts[tag] = float(value)
                    continue
                atts[tag] = value
                continue
                if SAMPLEFORMAT in atts and len(atts[SAMPLEFORMAT]) == 1:
                    atts[SAMPLEFORMAT] = atts[SAMPLEFORMAT][0]
                logger.debug('Converted items: %s', sorted(atts.items()))
                if im.mode in ('I;16', 'I;16B', 'I;16L'):
                    rawmode = 'I;16N'
                tags = list(atts.items())
                tags.sort()
                a = (rawmode, compression, _fp, filename, tags, types)
                encoder = Image._getencoder(im.mode, 'libtiff', a, encoderconfig)
                encoder.setimage(im.im, (0, 0) + im.size)
                (errcode, data) = encoder.encode(ImageFile.MAXBLOCK)[slice(1, None, None)]
                if not _fp:
                    fp.write(data)
                if not errcode:
                    continue
                if errcode < 0:
                    msg = f'''encoder error {errcode} when writing image file'''
                    raise OSError(msg)
            else:
                for tag in blocklist:
                    del ifd[tag]
                offset = ifd.save(fp)
                ImageFile._save(im, fp, [
                    ImageFile._Tile('raw', (0, 0) + im.size, offset, (rawmode, stride, 1))])
            if '_debug_multipage' in encoderinfo:
                setattr(im, '_debug_multipage', ifd)
                return None
            return None
# WARNING: Decompyle incomplete


class AppendingTiffWriter(io.BytesIO):
    fieldSizes = [
        0,
        1,
        1,
        2,
        4,
        8,
        1,
        1,
        2,
        4,
        8,
        4,
        8,
        4,
        2,
        4,
        8]
    Tags = {
        519,
        520,
        521,
        273,
        288,
        324}
    
    def __init__(self, fn, new = False):
        self
        if is_path(fn):
            self.name = fn
            self.close_fp = True
            
            try:
                self.f = open(fn, 'w+b' if new else 'r+b')
            except OSError:
                self.f = open(fn, 'w+b')

        else:
            self.f = cast(IO[bytes], fn)
            self.close_fp = False
        self.beginning = self.f.tell()
        self.setup()

    
    def setup(self):
        self.f.seek(self.beginning, os.SEEK_SET)
        self.whereToWriteNewIFDOffset = None
        self.offsetOfNewPage = 0
        self.IIMM = self.f.read(4)
        iimm = self.f.read(4)
        self._bigtiff = b'+' in iimm
        if not iimm:
            self.isFirst = True
            return None
        self.isFirst = False
        if iimm not in PREFIXES:
            msg = 'Invalid TIFF file header'
            raise RuntimeError(msg)
        self.setEndian('<' if iimm.startswith(II) else '>')
        if self._bigtiff:
            self.f.seek(4, os.SEEK_CUR)
        self.skipIFDs()
        self.goToEnd()

    
    def finalize(self):
        if self.isFirst:
            return None
        self.f.seek(self.offsetOfNewPage)
        iimm = self.f.read(4)
        if not iimm:
            return None
        if iimm != self.IIMM:
            msg = "IIMM of new page doesn't match IIMM of first page"
            raise RuntimeError(msg)
        if self._bigtiff:
            self.f.seek(4, os.SEEK_CUR)
        ifd_offset = self._read(8 if self._bigtiff else 4)
        ifd_offset += self.offsetOfNewPage
        if self.whereToWriteNewIFDOffset is None:
            raise AssertionError
        self.f.seek(self.whereToWriteNewIFDOffset)
        self._write(ifd_offset, 8 if self._bigtiff else 4)
        self.f.seek(ifd_offset)
        self.fixIFD()

    
    def newFrame(self):
        self.finalize()
        self.setup()

    
    def __enter__(self):
        return self

    
    def __exit__(self, *args):
        if self.close_fp:
            self.close()
            return None

    
    def tell(self):
        return self.f.tell() - self.offsetOfNewPage

    
    def seek(self, offset, whence = io.SEEK_SET):
        '''
:param offset: Distance to seek.
:param whence: Whether the distance is relative to the start,
               end or current position.
:returns: The resulting position, relative to the start.
'''
        if whence == os.SEEK_SET:
            offset += self.offsetOfNewPage
        self.f.seek(offset, whence)
        return self.tell()

    
    def goToEnd(self):
        self.f.seek(0, os.SEEK_END)
        pos = self.f.tell()
        pad_bytes = 16 - pos % 16
        if 0 < pad_bytes and pad_bytes < 16:
            self.f.write(bytes(pad_bytes))
        self.offsetOfNewPage = self.f.tell()

    
    def setEndian(self, endian):
        '''L'''
        self.endian = endian
        self.longFmt = f'''{self.endian}L'''
        self.shortFmt = f'''{self.endian}H'''
        self.tagFormat = f'''{self.endian}HH''' + 'Q' if self._bigtiff else 'L'

    
    def skipIFDs(self):
        ifd_offset = self._read(8 if self._bigtiff else 4)
        if ifd_offset == 0:
            self.whereToWriteNewIFDOffset = self.f.tell() - 8 if self._bigtiff else 4
            return None
        self.f.seek(ifd_offset)
        num_tags = self._read(8 if self._bigtiff else 2)
        self.f.seek(num_tags * 20 if self._bigtiff else 12, os.SEEK_CUR)

    
    def write(self, data):
        return self.f.write(data)

    
    def _fmt(self, field_size):
        
        try:
            return {
                8: 'Q',
                4: 'L',
                2: 'H' }[field_size]
        except KeyError:
            msg = 'offset is not supported'
            raise RuntimeError(msg)


    
    def _read(self, field_size):
        (value,) = struct.unpack(self.endian + self._fmt(field_size), self.f.read(field_size))
        return value

    
    def readShort(self):
        return self._read(2)

    
    def readLong(self):
        return self._read(4)

    _verify_bytes_written = (lambda bytes_written, expected: if bytes_written is not None:
if bytes_written != expected:
msg = f'''wrote only {bytes_written} bytes but wanted {expected}'''raise RuntimeError(msg)None)()
    
    def _rewriteLast(self, value, field_size, new_field_size = 0):
        self.f.seek(-field_size, os.SEEK_CUR)
        if not new_field_size:
            new_field_size = field_size
        bytes_written = self.f.write(struct.pack(self.endian + self._fmt(new_field_size), value))
        self._verify_bytes_written(bytes_written, new_field_size)

    
    def rewriteLastShortToLong(self, value):
        self._rewriteLast(value, 2, 4)

    
    def rewriteLastShort(self, value):
        return self._rewriteLast(value, 2)

    
    def rewriteLastLong(self, value):
        return self._rewriteLast(value, 4)

    
    def _write(self, value, field_size):
        bytes_written = self.f.write(struct.pack(self.endian + self._fmt(field_size), value))
        self._verify_bytes_written(bytes_written, field_size)

    
    def writeShort(self, value):
        self._write(value, 2)

    
    def writeLong(self, value):
        self._write(value, 4)

    
    def close(self):
        self.finalize()
        if self.close_fp:
            self.f.close()
            return None

    
    def fixIFD(self):
        num_tags = self._read(8 if self._bigtiff else 2)
        for i in range(num_tags):
            (tag, field_type, count) = struct.unpack(self.tagFormat, self.f.read(12 if self._bigtiff else 8))
            field_size = self.fieldSizes[field_type]
            total_size = field_size * count
            fmt_size = 8 if self._bigtiff else 4
            is_local = total_size <= fmt_size
            if not is_local:
                offset = self._read(fmt_size) + self.offsetOfNewPage
                self._rewriteLast(offset, fmt_size)
            if tag in self.Tags:
                cur_pos = self.f.tell()
                logger.debug('fixIFD: %s (%d) - type: %s (%d) - type size: %d - count: %d', TiffTags.lookup(tag).name, tag, TYPES.get(field_type, 'unknown'), field_type, field_size, count)
                if is_local:
                    self._fixOffsets(count, field_size)
                    self.f.seek(cur_pos + fmt_size)
                    continue
                self.f.seek(offset)
                self._fixOffsets(count, field_size)
                self.f.seek(cur_pos)
                continue
            if not is_local:
                continue
            self.f.seek(fmt_size, os.SEEK_CUR)

    
    def _fixOffsets(self, count, field_size):
        for i in range(count):
            offset = self._read(field_size)
            offset += self.offsetOfNewPage
            new_field_size = 0
            if self._bigtiff and field_size in (2, 4) and offset >= 0x100000000:
                new_field_size = 8
            elif field_size == 2 and offset >= 65536:
                new_field_size = 4
            if new_field_size:
                if count != 1:
                    msg = 'not implemented'
                    raise RuntimeError(msg)
                self._rewriteLast(offset, field_size, new_field_size)
                rewind = -new_field_size - 4 - 2
                self.f.seek(rewind, os.SEEK_CUR)
                self.writeShort(new_field_size)
                self.f.seek(2 - rewind, os.SEEK_CUR)
                continue
            self._rewriteLast(offset, field_size)

    
    def fixOffsets(self, count, isShort = False, isLong = False):
        if isShort:
            field_size = 2
        elif isLong:
            field_size = 4
        else:
            field_size = 0
        return self._fixOffsets(count, field_size)



def _save_all(im, fp, filename):
    '''append_images'''
    append_images = list(im.encoderinfo.get('append_images', []))
    if not hasattr(im, 'n_frames') and not append_images:
        return _save(im, fp, filename)
    cur_idx = im.tell()
    
    try:
        with AppendingTiffWriter(fp) as tf:
            for ims in [
                im] + append_images:
                encoderinfo = ims._attach_default_encoderinfo(im)
                if not hasattr(ims, 'encoderconfig'):
                    ims.encoderconfig = ()
                nfr = getattr(ims, 'n_frames', 1)
                for idx in range(nfr):
                    ims.seek(idx)
                    ims.load()
                    _save(ims, tf, filename)
                    tf.newFrame()
                ims.encoderinfo = encoderinfo

    im.seek(cur_idx)

Image.register_save(TiffImageFile.format, _save)
Image.register_save_all(TiffImageFile.format, _save_all)
Image.register_extensions(TiffImageFile.format, [
    '.tif',
    '.tiff'])
Image.register_mime(TiffImageFile.format, 'image/tiff')
return None
# WARNING: Decompyle incomplete
