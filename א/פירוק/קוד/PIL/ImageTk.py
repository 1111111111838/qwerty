# Source Generated with Decompyle++
# File: ImageTk.pyc (Python 3.14)

from __future__ import annotations
import tkinter
from io import BytesIO
from typing import Any
from . import Image, ImageFile
TYPE_CHECKING = False
if TYPE_CHECKING:
    from ._typing import CapsuleType

def _get_image_from_kw(kw):
    source = None
    if 'file' in kw:
        source = kw.pop('file')
    elif 'data' in kw:
        source = BytesIO(kw.pop('data'))
    if not source:
        return None
    return Image.open(source)


def _pyimagingtkcall(command, photo, ptr):
    tk = photo.tk
    
    try:
        tk.call(command, photo, repr(ptr))
    except tkinter.TclError:
        from . import _imagingtk
        _imagingtk.tkinit(tk.interpaddr())
        tk.call(command, photo, repr(ptr))
        return None



class PhotoImage:
    '''
A Tkinter-compatible photo image.  This can be used
everywhere Tkinter expects an image object.  If the image is an RGBA
image, pixels having alpha 0 are treated as transparent.

The constructor takes either a PIL image, or a mode and a size.
Alternatively, you can use the ``file`` or ``data`` options to initialize
the photo image object.

:param image: Either a PIL image, or a mode string.  If a mode string is
              used, a size must also be given.
:param size: If the first argument is a mode string, this defines the size
             of the image.
:keyword file: A filename to load the image from (using
               ``Image.open(file)``).
:keyword data: An 8-bit string containing image data (as loaded from an
               image file).
'''
    
    def __init__(self, image = None, size = None, **kw):
        if image is None:
            image = _get_image_from_kw(kw)
        if image is None:
            msg = 'Image is required'
            raise ValueError(msg)
        if isinstance(image, str):
            mode = image
            image = None
            if size is None:
                msg = 'If first argument is mode, size is required'
                raise ValueError(msg)
        else:
            mode = image.mode
            if mode == 'P':
                image.apply_transparency()
                image.load()
                mode = image.palette.mode if image.palette else 'RGB'
            size = image.size
            (kw['width'], kw['height']) = size
        if mode not in ('1', 'L', 'RGB', 'RGBA'):
            mode = Image.getmodebase(mode)
        self._PhotoImage__mode = mode
        self._PhotoImage__size = size
        self._PhotoImage__photo = ()(*{
            **kw })
        self.tk = self._PhotoImage__photo.tk
        if image:
            self.paste(image)
            return None

    
    def __del__(self):
        
        try:
            name = self._PhotoImage__photo.name
        except AttributeError:
            return None

        self._PhotoImage__photo.name = None
        
        try:
            self._PhotoImage__photo.tk.call('image', 'delete', name)
        except Exception:
            return None


    
    def __str__(self):
        '''
Get the Tkinter photo image identifier.  This method is automatically
called by Tkinter whenever a PhotoImage object is passed to a Tkinter
method.

:return: A Tkinter photo image identifier (a string).
'''
        return str(self._PhotoImage__photo)

    
    def width(self):
        '''
Get the width of the image.

:return: The width, in pixels.
'''
        return self._PhotoImage__size[0]

    
    def height(self):
        '''
Get the height of the image.

:return: The height, in pixels.
'''
        return self._PhotoImage__size[1]

    
    def paste(self, im):
        '''
Paste a PIL image into the photo image.  Note that this can
be very slow if the photo image is displayed.

:param im: A PIL image. The size must match the target region.  If the
           mode does not match, the image is converted to the mode of
           the bitmap image.
'''
        ptr = im.getim()
        image = im.im
        if not image.isblock() or im.mode != self._PhotoImage__mode:
            block = Image.core.new_block(self._PhotoImage__mode, im.size)
            image.convert2(block, image)
            ptr = block.ptr
        _pyimagingtkcall('PyImagingPhoto', self._PhotoImage__photo, ptr)



class BitmapImage:
    '''
A Tkinter-compatible bitmap image.  This can be used everywhere Tkinter
expects an image object.

The given image must have mode "1".  Pixels having value 0 are treated as
transparent.  Options, if any, are passed on to Tkinter.  The most commonly
used option is ``foreground``, which is used to specify the color for the
non-transparent parts.  See the Tkinter documentation for information on
how to specify colours.

:param image: A PIL image.
'''
    
    def __init__(self, image = None, **kw):
        if image is None:
            image = _get_image_from_kw(kw)
        if image is None:
            msg = 'Image is required'
            raise ValueError(msg)
        self._BitmapImage__mode = image.mode
        self._BitmapImage__size = image.size
        self._BitmapImage__photo = ()(*{
            'data': image.tobitmap(),
            **kw })

    
    def __del__(self):
        
        try:
            name = self._BitmapImage__photo.name
        except AttributeError:
            return None

        self._BitmapImage__photo.name = None
        
        try:
            self._BitmapImage__photo.tk.call('image', 'delete', name)
        except Exception:
            return None


    
    def width(self):
        '''
Get the width of the image.

:return: The width, in pixels.
'''
        return self._BitmapImage__size[0]

    
    def height(self):
        '''
Get the height of the image.

:return: The height, in pixels.
'''
        return self._BitmapImage__size[1]

    
    def __str__(self):
        '''
Get the Tkinter bitmap image identifier.  This method is automatically
called by Tkinter whenever a BitmapImage object is passed to a Tkinter
method.

:return: A Tkinter bitmap image identifier (a string).
'''
        return str(self._BitmapImage__photo)



def getimage(photo):
    '''Copies the contents of a PhotoImage to a PIL image memory.'''
    im = Image.new('RGBA', (photo.width(), photo.height()))
    _pyimagingtkcall('PyImagingPhotoGet', photo, im.getim())
    return im

