# Source Generated with Decompyle++
# File: _endian.pyc (Python 3.14)

import sys
from ctypes import Array, Structure, Union
_array_type = type(Array)

def _other_endian(typ):
    """Return the type with the 'other' byte order.  Simple types like
c_int and so on already have __ctype_be__ and __ctype_le__
attributes which contain the types, for more complicated types
arrays and structures are supported.
"""
    if hasattr(typ, _OTHER_ENDIAN):
        return getattr(typ, _OTHER_ENDIAN)
    if isinstance(typ, _array_type):
        return _other_endian(typ._type_) * typ._length_
    if issubclass(typ, (Structure, Union)):
        return typ
    raise TypeError('This type does not support other endian: %s' % typ)


class _swapped_meta:
    
    def __setattr__(self, attrname, value):
        '''_fields_'''
        if attrname == '_fields_':
            fields = []
            for desc in value:
                name = desc[0]
                typ = desc[1]
                rest = desc[slice(2, None, None)]
                fields.append((name, _other_endian(typ)) + rest)
            value = fields
        # unsupported opcode LOAD_SUPER_ATTR
        self(attrname, value)
        return None
    # WARNING: Decompyle incomplete



def _swapped_struct_meta():
    '''_swapped_struct_meta'''
    pass

_swapped_struct_meta = __build_class__(_swapped_struct_meta, '_swapped_struct_meta', _swapped_meta, type(Structure))

def _swapped_union_meta():
    '''_swapped_union_meta'''
    pass

_swapped_union_meta = __build_class__(_swapped_union_meta, '_swapped_union_meta', _swapped_meta, type(Union))
if sys.byteorder == 'little':
    _OTHER_ENDIAN = '__ctype_be__'
    LittleEndianStructure = Structure
    
    def BigEndianStructure():
        '''BigEndianStructure'''
        __doc__ = 'Structure with big endian byte order'
        __slots__ = ()
        _swappedbytes_ = None

    BigEndianStructure = __build_class__(BigEndianStructure, 'BigEndianStructure', Structure, metaclass = _swapped_struct_meta)
    LittleEndianUnion = Union
    
    def BigEndianUnion():
        '''BigEndianUnion'''
        __doc__ = 'Union with big endian byte order'
        __slots__ = ()
        _swappedbytes_ = None

    BigEndianUnion = __build_class__(BigEndianUnion, 'BigEndianUnion', Union, metaclass = _swapped_union_meta)
if sys.byteorder == 'big':
    _OTHER_ENDIAN = '__ctype_le__'
    BigEndianStructure = Structure
    
    def LittleEndianStructure():
        '''LittleEndianStructure'''
        __doc__ = 'Structure with little endian byte order'
        __slots__ = ()
        _swappedbytes_ = None

    LittleEndianStructure = __build_class__(LittleEndianStructure, 'LittleEndianStructure', Structure, metaclass = _swapped_struct_meta)
    BigEndianUnion = Union
    
    def LittleEndianUnion():
        '''LittleEndianUnion'''
        __doc__ = 'Union with little endian byte order'
        __slots__ = ()
        _swappedbytes_ = None

    LittleEndianUnion = __build_class__(LittleEndianUnion, 'LittleEndianUnion', Union, metaclass = _swapped_union_meta)
raise RuntimeError('Invalid byteorder')
