# Source Generated with Decompyle++
# File: abc.pyc (Python 3.14)

'''Abstract base classes related to import.'''
from . import _bootstrap_external
from . import machinery

try:
    import _frozen_importlib
except ImportError as exc:
    if exc.name != '_frozen_importlib':
        raise
    _frozen_importlib = None


try:
    import _frozen_importlib_external
except ImportError:
    _frozen_importlib_external = _bootstrap_external

from ._abc import Loader
import abc
__all__ = [
    'Loader',
    'MetaPathFinder',
    'PathEntryFinder',
    'ResourceLoader',
    'InspectLoader',
    'ExecutionLoader',
    'FileLoader',
    'SourceLoader']

def _register(abstract_cls, *classes):
    for cls in classes:
        abstract_cls.register(cls)
        while _frozen_importlib:
            pass
        
        try:
            frozen_cls = getattr(_frozen_importlib, cls.__name__)
        except AttributeError:
            frozen_cls = getattr(_frozen_importlib_external, cls.__name__)

        abstract_cls.register(frozen_cls)


def MetaPathFinder():
    '''MetaPathFinder'''
    __doc__ = 'Abstract base class for import finders on sys.meta_path.'
    
    def invalidate_caches(self):
        """An optional method for clearing the finder's cache, if any.
This method is used by importlib.invalidate_caches().
"""
        pass


MetaPathFinder = __build_class__(MetaPathFinder, 'MetaPathFinder', metaclass = abc.ABCMeta)
_register(MetaPathFinder, machinery.BuiltinImporter, machinery.FrozenImporter, machinery.PathFinder, machinery.WindowsRegistryFinder)

def PathEntryFinder():
    '''PathEntryFinder'''
    __doc__ = 'Abstract base class for path entry finders used by PathFinder.'
    
    def invalidate_caches(self):
        """An optional method for clearing the finder's cache, if any.
This method is used by PathFinder.invalidate_caches().
"""
        pass


PathEntryFinder = __build_class__(PathEntryFinder, 'PathEntryFinder', metaclass = abc.ABCMeta)
_register(PathEntryFinder, machinery.FileFinder)

class ResourceLoader(Loader):
    '''Abstract base class for loaders which can return data from their
back-end storage to facilitate reading data to perform an import.

This ABC represents one of the optional protocols specified by PEP 302.

For directly loading resources, use TraversableResources instead. This class
primarily exists for backwards compatibility with other ABCs in this module.

'''
    get_data = (lambda self, path: raise OSError)()


class InspectLoader(Loader):
    '''Abstract base class for loaders which support inspection about the
modules they can load.

This ABC represents one of the optional protocols specified by PEP 302.

'''
    
    def is_package(self, fullname):
        '''Optional method which when implemented should return whether the
module is a package.  The fullname is a str.  Returns a bool.

Raises ImportError if the module cannot be found.
'''
        raise ImportError

    
    def get_code(self, fullname):
        '''Method which returns the code object for the module.

The fullname is a str.  Returns a types.CodeType if possible, else
returns None if a code object does not make sense
(e.g. built-in module). Raises ImportError if the module cannot be
found.
'''
        source = self.get_source(fullname)
        if source is None:
            return None
        return self.source_to_code(source)

    get_source = (lambda self, fullname: raise ImportError)()
    source_to_code = (lambda data, path = '<string>': compile(data, path, 'exec', dont_inherit = True))()
    exec_module = _bootstrap_external._LoaderBasics.exec_module
    load_module = _bootstrap_external._LoaderBasics.load_module

_register(InspectLoader, machinery.BuiltinImporter, machinery.FrozenImporter, machinery.NamespaceLoader)

class ExecutionLoader(InspectLoader):
    '''Abstract base class for loaders that wish to support the execution of
modules as scripts.

This ABC represents one of the optional protocols specified in PEP 302.

'''
    get_filename = (lambda self, fullname: raise ImportError)()
    
    def get_code(self, fullname):
        '''Method to return the code object for fullname.

Should return None if not applicable (e.g. built-in module).
Raise ImportError if the module cannot be found.
'''
        source = self.get_source(fullname)
        if source is None:
            return None
        
        try:
            path = self.get_filename(fullname)
        except ImportError:
            return self.source_to_code(source)

        return self.source_to_code(source, path)


_register(ExecutionLoader, machinery.ExtensionFileLoader, machinery.AppleFrameworkLoader)

class FileLoader(ExecutionLoader, ResourceLoader, _bootstrap_external.FileLoader):
    '''Abstract base class partially implementing the ResourceLoader and
ExecutionLoader ABCs.'''
    pass

_register(FileLoader, machinery.SourceFileLoader, machinery.SourcelessFileLoader)

class SourceLoader(ExecutionLoader, ResourceLoader, _bootstrap_external.SourceLoader):
    '''Abstract base class for loading source code (and optionally any
corresponding bytecode).

To support loading from source code, the abstractmethods inherited from
ResourceLoader and ExecutionLoader need to be implemented. To also support
loading from bytecode, the optional methods specified directly by this ABC
is required.

Inherited abstractmethods not implemented in this ABC:

    * ResourceLoader.get_data
    * ExecutionLoader.get_filename

'''
    
    def path_mtime(self, path):
        '''Return the (int) modification time for the path (str).'''
        import warnings
        warnings.warn('SourceLoader.path_mtime is deprecated in favour of SourceLoader.path_stats().', DeprecationWarning, stacklevel = 2)
        if self.path_stats.__func__ is SourceLoader.path_stats:
            raise OSError
        return int(self.path_stats(path)['mtime'])

    
    def path_stats(self, path):
        """Return a metadata dict for the source pointed to by the path (str).
Possible keys:
- 'mtime' (mandatory) is the numeric timestamp of last source
  code modification;
- 'size' (optional) is the size in bytes of the source code.
"""
        if self.path_mtime.__func__ is SourceLoader.path_mtime:
            raise OSError
        return {
            'mtime': self.path_mtime(path) }

    
    def set_data(self, path, data):
        '''Write the bytes to the path (if possible).

Accepts a str path and data as bytes.

Any needed intermediary directories are to be created. If for some
reason the file cannot be written because of permissions, fail
silently.
'''
        pass


_register(SourceLoader, machinery.SourceFileLoader)
