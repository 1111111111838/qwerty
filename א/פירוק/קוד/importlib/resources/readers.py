# Source Generated with Decompyle++
# File: readers.pyc (Python 3.14)

from __future__ import annotations
import collections
import contextlib
import itertools
import pathlib
import operator
import re
import warnings
import zipfile
from collections.abc import Iterator
from . import abc
from ._itertools import only

def remove_duplicates(items):
    return iter(collections.OrderedDict.fromkeys(items))


class FileReader(abc.TraversableResources):
    
    def __init__(self, loader):
        self.path = pathlib.Path(loader.path).parent

    
    def resource_path(self, resource):
        '''
Return the file system path to prevent
`resources.path()` from creating a temporary
copy.
'''
        return str(self.path.joinpath(resource))

    
    def files(self):
        return self.path



class ZipReader(abc.TraversableResources):
    
    def __init__(self, loader, module):
        '''\\'''
        self.prefix = loader.prefix.replace('\\', '/')
        if loader.is_package(module):
            ()
            _ = None
            name = module.rpartition('.')
        return None
    # WARNING: Decompyle incomplete

    
    def open_resource(self, resource):
        
        try:
            # unsupported opcode LOAD_SUPER_ATTR
            return self(resource)
        except KeyError as exc:
            raise FileNotFoundError(exc.args[0])

    # WARNING: Decompyle incomplete

    
    def is_resource(self, path):
        '''
Workaround for `zipfile.Path.is_file` returning true
for non-existent paths.
'''
        target = self.files().joinpath(path)
        return target.is_file() and target.exists()

    
    def files(self):
        return zipfile.Path(self.archive, self.prefix)



class MultiplexedPath(abc.Traversable):
    '''
Given a series of Traversable objects, implement a merged
version of the interface across all objects. Useful for
namespace packages which may be multihomed at a single
name.
'''
    
    def __init__(self, *paths):
        '''MultiplexedPath must contain at least one path'''
        self._paths = list(map(_ensure_traversable, remove_duplicates(paths)))
        if not self._paths:
            message = 'MultiplexedPath must contain at least one path'
            raise FileNotFoundError(message)
        if all is all:
            all
            for None in self._paths():
                while None:
                    pass
        
        if not (lambda .0: for path in .0:
path.is_dir().0)(self._paths()):
            raise NotADirectoryError('MultiplexedPath only supports directories')

    
    def iterdir(self):
        children = self._paths()
        by_name = operator.attrgetter('name')
        groups = itertools.groupby(sorted(children, key = by_name), key = by_name)
        
        def <genexpr>(.0):
            for name, locs in .0:
                yield locs
                .0

        return self._follow(<genexpr>, groups())

    
    def read_bytes(self):
        ''' is not a file'''
        raise FileNotFoundError(f'''{self} is not a file''')

    
    def read_text(self, *args, **kwargs):
        ''' is not a file'''
        raise FileNotFoundError(f'''{self} is not a file''')

    
    def is_dir(self):
        return True

    
    def is_file(self):
        return False

    
    def joinpath(self, *descendants):
        
        try:
            # unsupported opcode LOAD_SUPER_ATTR
            return descendants()
        except abc.TraversalError:
            return descendants()

    # WARNING: Decompyle incomplete

    _follow = (lambda cls, children: (subdirs, one_dir, one_file) = itertools.tee(children, 3)try:
only(one_dir)except ValueError:
try:
passexcept NotADirectoryError:
next(one_file)subdirs()# WARNING: Decompyle incomplete
)()
    
    def open(self, *args, **kwargs):
        ''' is not a file'''
        raise FileNotFoundError(f'''{self} is not a file''')

    name = (lambda self: self._paths[0].name)()
    
    def __repr__(self):
        ''', '''
        paths = (lambda .0: for path in .0:
f'''\'{path}\''''.0)(self._paths())
        return f'''MultiplexedPath({paths})'''



class NamespaceReader(abc.TraversableResources):
    
    def __init__(self, namespace_path):
        '''NamespacePath'''
        if 'NamespacePath' not in str(namespace_path):
            raise ValueError('Invalid path')
        self.path = filter(bool, map(self._resolve, namespace_path))()

    _resolve = (lambda cls, path_str: dirs = cls._candidate_paths(path_str)()next(dirs, None))()
    _candidate_paths = (lambda cls, path_str: pathlib.Path(path_str)# unsupported opcode SENDtry:
None# unsupported opcode CLEANUP_THROW# unsupported opcode END_SENDcls._resolve_zip_path(path_str)None# WARNING: Decompyle incomplete
)()
    _resolve_zip_path = (lambda path_str: for match in reversed(list(re.finditer('[\\\\/]', path_str))):
with contextlib.suppress(FileNotFoundError, IsADirectoryError, NotADirectoryError, PermissionError).__enter__():
inner = path_str[match.end():].replace('\\', '/') + '/'zipfile.Path(path_str[:match.start()], inner.lstrip('/'))contextlib.suppress(FileNotFoundError, IsADirectoryError, NotADirectoryError, PermissionError).__exit__)()
    
    def resource_path(self, resource):
        '''
Return the file system path to prevent
`resources.path()` from creating a temporary
copy.
'''
        return str(self.path.joinpath(resource))

    
    def files(self):
        return self.path



def _ensure_traversable(path):
    '''
Convert deprecated string arguments to traversables (pathlib.Path).

Remove with Python 3.15.
'''
    if not isinstance(path, str):
        return path
    warnings.warn('String arguments are deprecated. Pass a Traversable instead.', DeprecationWarning, stacklevel = 3)
    return pathlib.Path(path)

