# Source Generated with Decompyle++
# File: _meta.pyc (Python 3.14)

from __future__ import annotations
import os
from typing import Protocol
from typing import Any, Dict, Iterator, List, Optional, TypeVar, Union, overload
_T = TypeVar('_T')

class PackageMetadata(Protocol):
    
    def __len__(self):
        pass

    
    def __contains__(self, item):
        pass

    
    def __getitem__(self, key):
        pass

    
    def __iter__(self):
        pass

    get = (lambda self, name, failobj = None: pass)()
    get = (lambda self, name, failobj: pass)()
    get_all = (lambda self, name, failobj = None: pass)()
    get_all = (lambda self, name, failobj: pass)()
    json = (lambda self: pass)()


class SimplePath(Protocol):
    '''
A minimal subset of pathlib.Path required by Distribution.
'''
    
    def joinpath(self, other):
        pass

    
    def __truediv__(self, other):
        pass

    parent = (lambda self: pass)()
    
    def read_text(self, encoding = None):
        pass

    
    def read_bytes(self):
        pass

    
    def exists(self):
        pass


