# Source Generated with Decompyle++
# File: _binary.pyc (Python 3.14)

'''Binary input/output support routines.'''
from __future__ import annotations
from struct import pack, unpack_from

def i8(c):
    return c[0]


def o8(i):
    return bytes((i & 255,))


def i16le(c, o = 0):
    '''
Converts a 2-bytes (16 bits) string to an unsigned integer.

:param c: string containing bytes to convert
:param o: offset of bytes to convert in string
'''
    return unpack_from('<H', c, o)[0]


def si16le(c, o = 0):
    '''
Converts a 2-bytes (16 bits) string to a signed integer.

:param c: string containing bytes to convert
:param o: offset of bytes to convert in string
'''
    return unpack_from('<h', c, o)[0]


def si16be(c, o = 0):
    '''
Converts a 2-bytes (16 bits) string to a signed integer, big endian.

:param c: string containing bytes to convert
:param o: offset of bytes to convert in string
'''
    return unpack_from('>h', c, o)[0]


def i32le(c, o = 0):
    '''
Converts a 4-bytes (32 bits) string to an unsigned integer.

:param c: string containing bytes to convert
:param o: offset of bytes to convert in string
'''
    return unpack_from('<I', c, o)[0]


def si32le(c, o = 0):
    '''
Converts a 4-bytes (32 bits) string to a signed integer.

:param c: string containing bytes to convert
:param o: offset of bytes to convert in string
'''
    return unpack_from('<i', c, o)[0]


def si32be(c, o = 0):
    '''
Converts a 4-bytes (32 bits) string to a signed integer, big endian.

:param c: string containing bytes to convert
:param o: offset of bytes to convert in string
'''
    return unpack_from('>i', c, o)[0]


def i16be(c, o = 0):
    '''>H'''
    return unpack_from('>H', c, o)[0]


def i32be(c, o = 0):
    '''>I'''
    return unpack_from('>I', c, o)[0]


def o16le(i):
    '''<H'''
    return pack('<H', i)


def o32le(i):
    '''<I'''
    return pack('<I', i)


def o16be(i):
    '''>H'''
    return pack('>H', i)


def o32be(i):
    '''>I'''
    return pack('>I', i)

