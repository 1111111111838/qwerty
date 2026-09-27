# Source Generated with Decompyle++
# File: _typing.pyc (Python 3.14)

from __future__ import annotations
import os
import sys
from collections.abc import Sequence
from typing import Any, Protocol, TypeVar
TYPE_CHECKING = False
if TYPE_CHECKING:
    from numbers import _IntegralLike as IntegralLike
    
    try:
        from numpy.typing import typing as npt
        NumpyArray = npt.NDArray[Any]
    except ImportError:
        pass

if sys.version_info >= (3, 13):
    from types import CapsuleType
else:
    CapsuleType = object
if sys.version_info >= (3, 12):
    from collections.abc import Buffer
else:
    Buffer = Any
_Ink = float | tuple[(int, ...)] | str
Coords = Sequence[float] | Sequence[Sequence[float]]
_T_co = TypeVar('_T_co', covariant = True)

def SupportsRead():
    '''SupportsRead'''
    
    def read(self, length = ...):
        pass


SupportsRead = __build_class__(SupportsRead, 'SupportsRead', Protocol[_T_co])
StrOrBytesPath = str | bytes | os.PathLike[str] | os.PathLike[bytes]
__all__ = [
    'Buffer',
    'IntegralLike',
    'StrOrBytesPath',
    'SupportsRead']
