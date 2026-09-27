# Source Generated with Decompyle++
# File: ImageMath.pyc (Python 3.14)

from __future__ import annotations
import builtins
from . import Image, _imagingmath
TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable
    from types import CodeType
    from typing import Any

class _Operand:
    '''Wraps an image operand, providing standard operators'''
    
    def __init__(self, im):
        self.im = im

    
    def _Operand__fixup(self, im1):
        '''1'''
        if isinstance(im1, _Operand):
            if im1.im.mode in ('1', 'L'):
                return im1.im.convert('I')
            if im1.im.mode in ('I', 'F'):
                return im1.im
            msg = f'''unsupported mode: {im1.im.mode}'''
            raise ValueError(msg)
        if isinstance(im1, (int, float)) and self.im.mode in ('1', 'L', 'I'):
            return Image.new('I', self.im.size, im1)
        return Image.new('F', self.im.size, im1)

    
    def apply(self, op, im1, im2 = None, mode = None):
        im_1 = self._Operand__fixup(im1)
        if im2 is None:
            out = Image.new(mode or im_1.mode, im_1.size, None)
            
            try:
                op = getattr(_imagingmath, f'''{op}_{im_1.mode}''')
            except AttributeError as e:
                msg = f'''bad operand type for \'{op}\''''
                raise TypeError(msg) from e

            _imagingmath.unop(op, out.getim(), im_1.getim())
        else:
            im_2 = self._Operand__fixup(im2)
            if im_1.mode != im_2.mode:
                if im_1.mode != 'F':
                    im_1 = im_1.convert('F')
                if im_2.mode != 'F':
                    im_2 = im_2.convert('F')
            if im_1.size != im_2.size:
                size = (min(im_1.size[0], im_2.size[0]), min(im_1.size[1], im_2.size[1]))
                if im_1.size != size:
                    im_1 = im_1.crop((0, 0) + size)
                if im_2.size != size:
                    im_2 = im_2.crop((0, 0) + size)
            out = Image.new(mode or im_1.mode, im_1.size, None)
            
            try:
                op = getattr(_imagingmath, f'''{op}_{im_1.mode}''')
            except AttributeError as e:
                msg = f'''bad operand type for \'{op}\''''
                raise TypeError(msg) from e

            _imagingmath.binop(op, out.getim(), im_1.getim(), im_2.getim())
        return _Operand(out)

    
    def __bool__(self):
        return self.im.getbbox() is not None

    
    def __abs__(self):
        '''abs'''
        return self.apply('abs', self)

    
    def __pos__(self):
        return self

    
    def __neg__(self):
        '''neg'''
        return self.apply('neg', self)

    
    def __add__(self, other):
        '''add'''
        return self.apply('add', self, other)

    
    def __radd__(self, other):
        '''add'''
        return self.apply('add', other, self)

    
    def __sub__(self, other):
        '''sub'''
        return self.apply('sub', self, other)

    
    def __rsub__(self, other):
        '''sub'''
        return self.apply('sub', other, self)

    
    def __mul__(self, other):
        '''mul'''
        return self.apply('mul', self, other)

    
    def __rmul__(self, other):
        '''mul'''
        return self.apply('mul', other, self)

    
    def __truediv__(self, other):
        '''div'''
        return self.apply('div', self, other)

    
    def __rtruediv__(self, other):
        '''div'''
        return self.apply('div', other, self)

    
    def __mod__(self, other):
        '''mod'''
        return self.apply('mod', self, other)

    
    def __rmod__(self, other):
        '''mod'''
        return self.apply('mod', other, self)

    
    def __pow__(self, other):
        '''pow'''
        return self.apply('pow', self, other)

    
    def __rpow__(self, other):
        '''pow'''
        return self.apply('pow', other, self)

    
    def __invert__(self):
        '''invert'''
        return self.apply('invert', self)

    
    def __and__(self, other):
        '''and'''
        return self.apply('and', self, other)

    
    def __rand__(self, other):
        '''and'''
        return self.apply('and', other, self)

    
    def __or__(self, other):
        '''or'''
        return self.apply('or', self, other)

    
    def __ror__(self, other):
        '''or'''
        return self.apply('or', other, self)

    
    def __xor__(self, other):
        '''xor'''
        return self.apply('xor', self, other)

    
    def __rxor__(self, other):
        '''xor'''
        return self.apply('xor', other, self)

    
    def __lshift__(self, other):
        '''lshift'''
        return self.apply('lshift', self, other)

    
    def __rshift__(self, other):
        '''rshift'''
        return self.apply('rshift', self, other)

    
    def __eq__(self, other):
        '''eq'''
        return self.apply('eq', self, other)

    
    def __ne__(self, other):
        '''ne'''
        return self.apply('ne', self, other)

    
    def __lt__(self, other):
        '''lt'''
        return self.apply('lt', self, other)

    
    def __le__(self, other):
        '''le'''
        return self.apply('le', self, other)

    
    def __gt__(self, other):
        '''gt'''
        return self.apply('gt', self, other)

    
    def __ge__(self, other):
        '''ge'''
        return self.apply('ge', self, other)



def imagemath_int(self):
    '''I'''
    return _Operand(self.im.convert('I'))


def imagemath_float(self):
    '''F'''
    return _Operand(self.im.convert('F'))


def imagemath_equal(self, other):
    '''eq'''
    return self.apply('eq', self, other, mode = 'I')


def imagemath_notequal(self, other):
    '''ne'''
    return self.apply('ne', self, other, mode = 'I')


def imagemath_min(self, other):
    '''min'''
    return self.apply('min', self, other)


def imagemath_max(self, other):
    '''max'''
    return self.apply('max', self, other)


def imagemath_convert(self, mode):
    return _Operand(self.im.convert(mode))

ops = {
    'convert': imagemath_convert,
    'max': imagemath_max,
    'min': imagemath_min,
    'notequal': imagemath_notequal,
    'equal': imagemath_equal,
    'float': imagemath_float,
    'int': imagemath_int }

def lambda_eval(expression, **kw):
    """
Returns the result of an image function.

:py:mod:`~PIL.ImageMath` only supports single-layer images. To process multi-band
images, use the :py:meth:`~PIL.Image.Image.split` method or
:py:func:`~PIL.Image.merge` function.

:param expression: A function that receives a dictionary.
:param **kw: Values to add to the function's dictionary.
:return: The expression result. This is usually an image object, but can
         also be an integer, a floating point value, or a pixel tuple,
         depending on the expression.
"""
    args = ops.copy()
    args.update(kw)
    for k, v in args.items():
        if not isinstance(v, Image.Image):
            continue
        args[k] = _Operand(v)
    out = expression(args)
    
    try:
        return out.im
    except AttributeError:
        return out



def unsafe_eval(expression, **kw):
    """
Evaluates an image expression. This uses Python's ``eval()`` function to process
the expression string, and carries the security risks of doing so. It is not
recommended to process expressions without considering this.
:py:meth:`~lambda_eval` is a more secure alternative.

:py:mod:`~PIL.ImageMath` only supports single-layer images. To process multi-band
images, use the :py:meth:`~PIL.Image.Image.split` method or
:py:func:`~PIL.Image.merge` function.

:param expression: A string containing a Python-style expression.
:param **kw: Values to add to the evaluation context.
:return: The evaluated expression. This is usually an image object, but can
         also be an integer, a floating point value, or a pixel tuple,
         depending on the expression.
"""
    args = ops.copy()
    for k in kw:
        while not ('__' in k) and not hasattr(builtins, k):
            pass
        msg = f'''\'{k}\' not allowed'''
        raise ValueError(msg)
    args.update(kw)
    for k, v in args.items():
        if not isinstance(v, Image.Image):
            continue
        args[k] = _Operand(v)
    compiled_code = compile(expression, '<string>', 'eval')
    
    def scan(code):
        '''abs'''
        for const in code.co_consts:
            while not type(const) is type(compiled_code):
                pass
            scan(const)
        for name in code.co_names:
            while not name not in args:
                pass
            while not name != 'abs':
                pass
            msg = f'''\'{name}\' not allowed'''
            raise ValueError(msg)

    scan(compiled_code)
    out = builtins.eval(expression, None, args)
    
    try:
        return out.im
    except AttributeError:
        return out


