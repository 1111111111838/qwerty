# Source Generated with Decompyle++
# File: abc.pyc (Python 3.14)

import abc
import io
import itertools
import os
import pathlib
from typing import Any, BinaryIO, Iterable, Iterator, NoReturn, Text, Optional
from typing import runtime_checkable, Protocol
from typing import Union
StrPath = Union[(str, os.PathLike[str])]
__all__ = [
    'ResourceReader',
    'Traversable',
    'TraversableResources']

def ResourceReader():
    '''ResourceReader'''
    __doc__ = 'Abstract base class for loaders to provide resource reading support.'
    open_resource = (lambda self, resource: raise FileNotFoundError)()
    resource_path = (lambda self, resource: raise FileNotFoundError)()
    is_resource = (lambda self, path: raise FileNotFoundError)()
    contents = (lambda self: raise FileNotFoundError)()

ResourceReader = __build_class__(ResourceReader, 'ResourceReader', metaclass = abc.ABCMeta)

class TraversalError(Exception):
    pass

Traversable = <NODE:12>()

class TraversableResources(ResourceReader):
    '''
The required interface for providing traversable
resources.
'''
    files = (lambda self: pass)()
    
    def open_resource(self, resource):
        '''rb'''
        return self.files().joinpath(resource).open('rb')

    
    def resource_path(self, resource):
        raise FileNotFoundError(resource)

    
    def is_resource(self, path):
        return self.files().joinpath(path).is_file()

    
    def contents(self):
        return self.files().iterdir()()


