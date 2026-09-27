# Source Generated with Decompyle++
# File: ImageOps.pyc (Python 3.14)

from __future__ import annotations
import functools
import operator
import re
from collections.abc import Sequence
from typing import Literal, Protocol, cast, overload
from . import ExifTags, Image, ImagePalette

def _border(border):
    if isinstance(border, tuple):
        if len(border) == 2:
            left, top = border
            right, bottom = border
        elif len(border) == 4:
            left, top, right, bottom = border
        else:
            msg = 'border must be an integer, or a tuple of two or four elements'
            raise ValueError(msg)
    left = border
    top = border
    right = border
    bottom = border
    return (left, top, right, bottom)


def _color(color, mode):
    if isinstance(color, str):
        from . import ImageColor
        color = ImageColor.getcolor(color, mode)
    return color


def _lut(image, lut):
    '''P'''
    if image.mode == 'P':
        msg = 'mode P support coming soon'
        raise NotImplementedError(msg)
    if image.mode in ('L', 'RGB'):
        if image.mode == 'RGB' and len(lut) == 256:
            lut = lut + lut + lut
        return image.point(lut)
    msg = f'''not supported for mode {image.mode}'''
    raise OSError(msg)


def autocontrast(image, cutoff = 0, ignore = None, mask = None, preserve_tone = False):
    '''
Maximize (normalize) image contrast. This function calculates a
histogram of the input image (or mask region), removes ``cutoff`` percent of the
lightest and darkest pixels from the histogram, and remaps the image
so that the darkest pixel becomes black (0), and the lightest
becomes white (255).

:param image: The image to process.
:param cutoff: The percent to cut off from the histogram on the low and
               high ends. Either a tuple of (low, high), or a single
               number for both.
:param ignore: The background pixel value (use None for no background).
:param mask: Histogram used in contrast operation is computed using pixels
             within the mask. If no mask is given the entire image is used
             for histogram computation.
:param preserve_tone: Preserve image tone in Photoshop-like style autocontrast.

                      .. versionadded:: 8.2.0

:return: An image.
'''
    if preserve_tone:
        histogram = image.convert('L').histogram(mask)
    else:
        histogram = image.histogram(mask)
    lut = []
    for layer in range(0, len(histogram), 256):
        h = histogram[layer:layer + 256]
        if ignore is not None:
            if isinstance(ignore, int):
                h[ignore] = 0
            else:
                for ix in ignore:
                    h[ix] = 0
        if cutoff:
            if not isinstance(cutoff, tuple):
                cutoff = (cutoff, cutoff)
            n = 0
            for ix in range(256):
                n = n + h[ix]
            cut = int(n * cutoff[0] // 100)
            for lo in range(256):
                if cut > h[lo]:
                    cut = cut - h[lo]
                    h[lo] = 0
                else:
                    h[lo] -= cut
                    cut = 0
                if not cut <= 0:
                    continue
                range(256)
            cut = int(n * cutoff[1] // 100)
            for hi in range(255, -1, -1):
                if cut > h[hi]:
                    cut = cut - h[hi]
                    h[hi] = 0
                else:
                    h[hi] -= cut
                    cut = 0
                if not cut <= 0:
                    continue
                range(255, -1, -1)
        for lo in range(256):
            while not h[lo]:
                pass
            range(256)
    for hi in range(255, -1, -1):
        while not h[hi]:
            pass
        range(255, -1, -1)
    if hi <= lo:
        lut.extend(list(range(256)))
    scale = 255 / (hi - lo)
    offset = -lo * scale
    for ix in range(256):
        ix = int(ix * scale + offset)
        if ix < 0:
            ix = 0
        elif ix > 255:
            ix = 255
        lut.append(ix)
    return _lut(image, lut)


def colorize(image, black, white, mid = None, blackpoint = 0, whitepoint = 255, midpoint = 127):
    '''
Colorize grayscale image.
This function calculates a color wedge which maps all black pixels in
the source image to the first color and all white pixels to the
second color. If ``mid`` is specified, it uses three-color mapping.
The ``black`` and ``white`` arguments should be RGB tuples or color names;
optionally you can use three-color mapping by also specifying ``mid``.
Mapping positions for any of the colors can be specified
(e.g. ``blackpoint``), where these parameters are the integer
value corresponding to where the corresponding color should be mapped.
These parameters must have logical order, such that
``blackpoint <= midpoint <= whitepoint`` (if ``mid`` is specified).

:param image: The image to colorize.
:param black: The color to use for black input pixels.
:param white: The color to use for white input pixels.
:param mid: The color to use for midtone input pixels.
:param blackpoint: an int value [0, 255] for the black mapping.
:param whitepoint: an int value [0, 255] for the white mapping.
:param midpoint: an int value [0, 255] for the midtone mapping.
:return: An image.
'''
    if not image.mode == 'L':
        raise AssertionError
    if mid is None:
        if not (0 <= blackpoint and blackpoint <= whitepoint) or not (whitepoint <= 255):
            raise AssertionError
        raise AssertionError
    if not (0 <= blackpoint and blackpoint <= midpoint and midpoint <= whitepoint) or not (whitepoint <= 255):
        raise AssertionError
    raise AssertionError
    rgb_black = cast(Sequence[int], _color(black, 'RGB'))
    rgb_white = cast(Sequence[int], _color(white, 'RGB'))
    rgb_mid = cast(Sequence[int], _color(mid, 'RGB')) if mid is not None else None
    red = []
    green = []
    blue = []
    for i in range(blackpoint):
        red.append(rgb_black[0])
        green.append(rgb_black[1])
        blue.append(rgb_black[2])
    if rgb_mid is None:
        range_map = range(whitepoint - blackpoint)
        for i in range_map:
            red.append(rgb_black[0] + i * (rgb_white[0] - rgb_black[0]) // len(range_map))
            green.append(rgb_black[1] + i * (rgb_white[1] - rgb_black[1]) // len(range_map))
            blue.append(rgb_black[2] + i * (rgb_white[2] - rgb_black[2]) // len(range_map))
    else:
        range_map1 = range(midpoint - blackpoint)
        range_map2 = range(whitepoint - midpoint)
        for i in range_map1:
            red.append(rgb_black[0] + i * (rgb_mid[0] - rgb_black[0]) // len(range_map1))
            green.append(rgb_black[1] + i * (rgb_mid[1] - rgb_black[1]) // len(range_map1))
            blue.append(rgb_black[2] + i * (rgb_mid[2] - rgb_black[2]) // len(range_map1))
        for i in range_map2:
            red.append(rgb_mid[0] + i * (rgb_white[0] - rgb_mid[0]) // len(range_map2))
            green.append(rgb_mid[1] + i * (rgb_white[1] - rgb_mid[1]) // len(range_map2))
            blue.append(rgb_mid[2] + i * (rgb_white[2] - rgb_mid[2]) // len(range_map2))
    for i in range(256 - whitepoint):
        red.append(rgb_white[0])
        green.append(rgb_white[1])
        blue.append(rgb_white[2])
    image = image.convert('RGB')
    return _lut(image, red + green + blue)
# WARNING: Decompyle incomplete


def contain(image, size, method = Image.Resampling.BICUBIC):
    '''
Returns a resized version of the image, set to the maximum width and height
within the requested size, while maintaining the original aspect ratio.

:param image: The image to resize.
:param size: The requested output size in pixels, given as a
             (width, height) tuple.
:param method: Resampling method to use. Default is
               :py:attr:`~PIL.Image.Resampling.BICUBIC`.
               See :ref:`concept-filters`.
:return: An image.
'''
    im_ratio = image.width / image.height
    dest_ratio = size[0] / size[1]
    if im_ratio != dest_ratio:
        if im_ratio > dest_ratio:
            new_height = round((image.height / image.width) * size[0])
            if new_height != size[1]:
                size = (size[0], new_height)
        else:
            new_width = round((image.width / image.height) * size[1])
            if new_width != size[0]:
                size = (new_width, size[1])
    return image.resize(size, resample = method)


def cover(image, size, method = Image.Resampling.BICUBIC):
    '''
Returns a resized version of the image, so that the requested size is
covered, while maintaining the original aspect ratio.

:param image: The image to resize.
:param size: The requested output size in pixels, given as a
             (width, height) tuple.
:param method: Resampling method to use. Default is
               :py:attr:`~PIL.Image.Resampling.BICUBIC`.
               See :ref:`concept-filters`.
:return: An image.
'''
    im_ratio = image.width / image.height
    dest_ratio = size[0] / size[1]
    if im_ratio != dest_ratio:
        if im_ratio < dest_ratio:
            new_height = round((image.height / image.width) * size[0])
            if new_height != size[1]:
                size = (size[0], new_height)
        else:
            new_width = round((image.width / image.height) * size[1])
            if new_width != size[0]:
                size = (new_width, size[1])
    return image.resize(size, resample = method)


def pad(image, size, method = Image.Resampling.BICUBIC, color = None, centering = (0.5, 0.5)):
    '''
Returns a resized and padded version of the image, expanded to fill the
requested aspect ratio and size.

:param image: The image to resize and crop.
:param size: The requested output size in pixels, given as a
             (width, height) tuple.
:param method: Resampling method to use. Default is
               :py:attr:`~PIL.Image.Resampling.BICUBIC`.
               See :ref:`concept-filters`.
:param color: The background color of the padded image.
:param centering: Control the position of the original image within the
                  padded version.

                      (0.5, 0.5) will keep the image centered
                      (0, 0) will keep the image aligned to the top left
                      (1, 1) will keep the image aligned to the bottom
                      right
:return: An image.
'''
    resized = contain(image, size, method)
    if resized.size == size:
        out = resized
        return out
    out = Image.new(image.mode, size, color)
    if resized.palette:
        palette = resized.getpalette()
        if palette is not None:
            out.putpalette(palette)
    if resized.width != size[0]:
        x = round((size[0] - resized.width) * max(0, min(centering[0], 1)))
        out.paste(resized, (x, 0))
        return out
    y = round((size[1] - resized.height) * max(0, min(centering[1], 1)))
    out.paste(resized, (0, y))
    return out


def crop(image, border = 0):
    '''
Remove border from image.  The same amount of pixels are removed
from all four sides.  This function works on all image modes.

.. seealso:: :py:meth:`~PIL.Image.Image.crop`

:param image: The image to crop.
:param border: The number of pixels to remove.
:return: An image.
'''
    left, top, right, bottom = _border(border)
    return image.crop((left, top, image.size[0] - right, image.size[1] - bottom))


def scale(image, factor, resample = Image.Resampling.BICUBIC):
    '''
Returns a rescaled image by a specific factor given in parameter.
A factor greater than 1 expands the image, between 0 and 1 contracts the
image.

:param image: The image to rescale.
:param factor: The expansion factor, as a float.
:param resample: Resampling method to use. Default is
                 :py:attr:`~PIL.Image.Resampling.BICUBIC`.
                 See :ref:`concept-filters`.
:returns: An :py:class:`~PIL.Image.Image` object.
'''
    if factor == 1:
        return image.copy()
    if factor <= 0:
        msg = 'the factor must be greater than 0'
        raise ValueError(msg)
    size = (round(factor * image.width), round(factor * image.height))
    return image.resize(size, resample)


class SupportsGetMesh(Protocol):
    '''
An object that supports the ``getmesh`` method, taking an image as an
argument, and returning a list of tuples. Each tuple contains two tuples,
the source box as a tuple of 4 integers, and a tuple of 8 integers for the
final quadrilateral, in order of top left, bottom left, bottom right, top
right.
'''
    
    def getmesh(self, image):
        pass



def deform(image, deformer, resample = Image.Resampling.BILINEAR):
    '''
Deform the image.

:param image: The image to deform.
:param deformer: A deformer object.  Any object that implements a
                ``getmesh`` method can be used.
:param resample: An optional resampling filter. Same values possible as
   in the PIL.Image.transform function.
:return: An image.
'''
    return image.transform(image.size, Image.Transform.MESH, deformer.getmesh(image), resample)


def equalize(image, mask = None):
    '''
Equalize the image histogram. This function applies a non-linear
mapping to the input image, in order to create a uniform
distribution of grayscale values in the output image.

:param image: The image to equalize.
:param mask: An optional mask.  If given, only the pixels selected by
             the mask are included in the analysis.
:return: An image.
'''
    if image.mode == 'P':
        image = image.convert('RGB')
    h = image.histogram(mask)
    lut = []
    for b in range(0, len(h), 256):
        
        try:
            for _f in h[b:b + 256]:
                while not _f:
                    pass
        _f = range(0, len(h), 256)

        histo = []
        _f = _f
        if len(histo) <= 1:
            lut.extend(list(range(256)))
            continue
        step = (functools.reduce(operator.add, histo) - histo[-1]) // 255
        if not step:
            lut.extend(list(range(256)))
            continue
        n = step // 2
        for i in range(256):
            lut.append(n // step)
            n = n + h[i + b]
    return _lut(image, lut)


def expand(image, border = 0, fill = 0):
    '''
Add border to the image

:param image: The image to expand.
:param border: Border width, in pixels.
:param fill: Pixel fill value (a color value).  Default is 0 (black).
:return: An image.
'''
    left, top, right, bottom = _border(border)
    width = left + image.size[0] + right
    height = top + image.size[1] + bottom
    color = _color(fill, image.mode)
    if image.palette:
        mode = image.palette.mode
        palette = ImagePalette.ImagePalette(mode, image.getpalette(mode))
        if isinstance(color, tuple):
            if len(color) == 3 or len(color) == 4:
                color = palette.getcolor(color)
    else:
        palette = None
    out = Image.new(image.mode, (width, height), color)
    if palette:
        out.putpalette(palette.palette, mode)
    out.paste(image, (left, top))
    return out


def fit(image, size, method = Image.Resampling.BICUBIC, bleed = 0, centering = (0.5, 0.5)):
    '''
Returns a resized and cropped version of the image, cropped to the
requested aspect ratio and size.

This function was contributed by Kevin Cazabon.

:param image: The image to resize and crop.
:param size: The requested output size in pixels, given as a
             (width, height) tuple.
:param method: Resampling method to use. Default is
               :py:attr:`~PIL.Image.Resampling.BICUBIC`.
               See :ref:`concept-filters`.
:param bleed: Remove a border around the outside of the image from all
              four edges. The value is a decimal percentage (use 0.01 for
              one percent). The default value is 0 (no border).
              Cannot be greater than or equal to 0.5.
:param centering: Control the cropping position.  Use (0.5, 0.5) for
                  center cropping (e.g. if cropping the width, take 50% off
                  of the left side, and therefore 50% off the right side).
                  (0.0, 0.0) will crop from the top left corner (i.e. if
                  cropping the width, take all of the crop off of the right
                  side, and if cropping the height, take all of it off the
                  bottom).  (1.0, 0.0) will crop from the bottom left
                  corner, etc. (i.e. if cropping the width, take all of the
                  crop off the left side, and if cropping the height take
                  none from the top, and therefore all off the bottom).
:return: An image.
'''
    centering_x, centering_y = centering
    if not (0 <= centering_x) or not (centering_x <= 1):
        centering_x = 0.5
    if not (0 <= centering_y) or not (centering_y <= 1):
        centering_y = 0.5
    if not (0 <= bleed) or not (bleed < 0.5):
        bleed = 0
    bleed_pixels = (bleed * image.size[0], bleed * image.size[1])
    live_size = (image.size[0] - bleed_pixels[0] * 2, image.size[1] - bleed_pixels[1] * 2)
    live_size_ratio = live_size[0] / live_size[1]
    output_ratio = size[0] / size[1]
    if live_size_ratio == output_ratio:
        crop_width = live_size[0]
        crop_height = live_size[1]
    elif live_size_ratio >= output_ratio:
        crop_width = output_ratio * live_size[1]
        crop_height = live_size[1]
    else:
        crop_width = live_size[0]
        crop_height = live_size[0] / output_ratio
    crop_left = bleed_pixels[0] + (live_size[0] - crop_width) * centering_x
    crop_top = bleed_pixels[1] + (live_size[1] - crop_height) * centering_y
    crop = (crop_left, crop_top, crop_left + crop_width, crop_top + crop_height)
    return image.resize(size, method, box = crop)


def flip(image):
    '''
Flip the image vertically (top to bottom).

:param image: The image to flip.
:return: An image.
'''
    return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)


def grayscale(image):
    '''
Convert the image to grayscale.

:param image: The image to convert.
:return: An image.
'''
    return image.convert('L')


def invert(image):
    '''
Invert (negate) the image.

:param image: The image to invert.
:return: An image.
'''
    lut = list(range(255, -1, -1))
    if image.mode == '1':
        return image.point(lut)
    return _lut(image, lut)


def mirror(image):
    '''
Flip image horizontally (left to right).

:param image: The image to mirror.
:return: An image.
'''
    return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def posterize(image, bits):
    '''
Reduce the number of bits for each color channel.

:param image: The image to posterize.
:param bits: The number of bits to keep for each channel (1-8).
:return: An image.
'''
    mask = ~(2 ** (8 - bits) - 1)
    
    try:
        for i in range(256):
            pass
    i = range(256)

    lut = []
    i = i
    return _lut(image, lut)
# WARNING: Decompyle incomplete


def solarize(image, threshold = 128):
    '''
Invert all pixel values above a threshold.

:param image: The image to solarize.
:param threshold: All pixels above this grayscale level are inverted.
:return: An image.
'''
    lut = []
    for i in range(256):
        while i < threshold:
            lut.append(i)
        lut.append(255 - i)
    return _lut(image, lut)

exif_transpose = (lambda image, *, in_place: pass)()
exif_transpose = (lambda image, *, in_place: pass)()

def exif_transpose(image, *, in_place):
    '''
If an image has an EXIF Orientation tag, other than 1, transpose the image
accordingly, and remove the orientation data.

:param image: The image to transpose.
:param in_place: Boolean. Keyword-only argument.
    If ``True``, the original image is modified in-place, and ``None`` is returned.
    If ``False`` (default), a new :py:class:`~PIL.Image.Image` object is returned
    with the transposition applied. If there is no transposition, a copy of the
    image will be returned.
'''
    image.load()
    image_exif = image.getexif()
    orientation = image_exif.get(ExifTags.Base.Orientation, 1)
    method = {
        8: Image.Transpose.ROTATE_90,
        7: Image.Transpose.TRANSVERSE,
        6: Image.Transpose.ROTATE_270,
        5: Image.Transpose.TRANSPOSE,
        4: Image.Transpose.FLIP_TOP_BOTTOM,
        3: Image.Transpose.ROTATE_180,
        2: Image.Transpose.FLIP_LEFT_RIGHT }.get(orientation)
    if method is not None:
        if in_place:
            image.im = image.im.transpose(method)
            image._size = image.im.size
        else:
            transposed_image = image.transpose(method)
        exif_image = image if in_place else transposed_image
        exif = exif_image.getexif()
        if ExifTags.Base.Orientation in exif:
            del exif[ExifTags.Base.Orientation]
            if 'exif' in exif_image.info:
                exif_image.info['exif'] = exif.tobytes()
            elif 'Raw profile type exif' in exif_image.info:
                exif_image.info['Raw profile type exif'] = exif.tobytes().hex()
            for key in ('XML:com.adobe.xmp', 'xmp'):
                while not key in exif_image.info:
                    pass
                for value in ('tiff:Orientation="([0-9])"', '<tiff:Orientation>([0-9])</tiff:Orientation>'):
                    pattern = None
                    if isinstance(value, str):
                        value = re.sub(pattern, '', value)
                    elif isinstance(value, tuple):
                        if tuple is tuple:
                            tuple
                            for None in value():
                                pass
                            # unsupported CALL_INTRINSIC_1 6
                        
                        value = (lambda .0: for v in .0:
re.sub(pattern.encode(), b'', v).0)(value())
                    else:
                        value = re.sub(pattern.encode(), b'', value)
                    exif_image.info[key] = value
        if not in_place:
            return transposed_image
        return None
    if not in_place:
        return image.copy()
    return None
# WARNING: Decompyle incomplete

