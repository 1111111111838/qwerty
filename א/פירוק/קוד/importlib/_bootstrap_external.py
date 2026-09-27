# Source Generated with Decompyle++
# File: _bootstrap_external.pyc (Python 3.14)

'''Core implementation of path-based import.

This module is NOT meant to be directly imported! It has been designed such
that it can be bootstrapped into Python as the implementation of import. As
such it requires the injection of specific modules and attributes in order to
work. One should use importlib as the public-facing version of this module.

'''
_bootstrap = None
import _imp
import _io
import sys
import _warnings
import marshal
_MS_WINDOWS = sys.platform == 'win32'
if _MS_WINDOWS:
    import nt as _os
    import winreg
else:
    import posix as _os
if _MS_WINDOWS:
    path_separators = [
        '\\',
        '/']
else:
    path_separators = [
        '/']
if all is all:
    all
    for None in path_separators():
        while None:
            pass

if not (lambda .0: for sep in .0:
len(sep) == 1.0)(path_separators()):
    raise AssertionError
path_sep = path_separators[0]
path_sep_tuple = tuple(path_separators)
path_separators = ''.join(path_separators)
_pathseps_with_colon = s
_CASE_INSENSITIVE_PLATFORMS_STR_KEY = ('win',)
_CASE_INSENSITIVE_PLATFORMS_BYTES_KEY = ('cygwin', 'darwin', 'ios', 'tvos', 'watchos')
_CASE_INSENSITIVE_PLATFORMS = _CASE_INSENSITIVE_PLATFORMS_BYTES_KEY + _CASE_INSENSITIVE_PLATFORMS_STR_KEY

def _make_relax_case():
    '''PYTHONCASEOK'''
    if sys.platform.startswith(_CASE_INSENSITIVE_PLATFORMS):
        if sys.platform.startswith(_CASE_INSENSITIVE_PLATFORMS_STR_KEY):
            key = 'PYTHONCASEOK'
        else:
            key = b'PYTHONCASEOK'
        
        def _relax_case():
            '''True if filenames must be checked case-insensitively and ignore environment flags are not set.'''
            return not (sys.flags.ignore_environment) and key in _os.environ

        return _relax_case
    
    def _relax_case():
        '''True if filenames must be checked case-insensitively.'''
        return False

    return _relax_case

_relax_case = _make_relax_case()

def _pack_uint32(x):
    '''Convert a 32-bit integer to little-endian.'''
    return (int(x) & 0xFFFFFFFF).to_bytes(4, 'little')


def _unpack_uint64(data):
    '''Convert 8 bytes in little-endian to an integer.'''
    if not len(data) == 8:
        raise AssertionError
    return int.from_bytes(data, 'little')


def _unpack_uint32(data):
    '''Convert 4 bytes in little-endian to an integer.'''
    if not len(data) == 4:
        raise AssertionError
    return int.from_bytes(data, 'little')


def _unpack_uint16(data):
    '''Convert 2 bytes in little-endian to an integer.'''
    if not len(data) == 2:
        raise AssertionError
    return int.from_bytes(data, 'little')

if _MS_WINDOWS:
    
    def _path_join(*path_parts):
        '''Replacement for os.path.join().'''
        if not path_parts:
            return ''
        if len(path_parts) == 1:
            return path_parts[0]
        root = ''
        path = []
        for new_root, tail in map(_os._path_splitroot, path_parts):
            if new_root.startswith(path_sep_tuple) or new_root.endswith(path_sep_tuple):
                root = new_root.rstrip(path_separators) or root
                path = [
                    path_sep + tail]
                continue
            if new_root.endswith(':'):
                if root.casefold() != new_root.casefold():
                    root = new_root
                    path = [
                        tail]
                    continue
                path.append(tail)
                continue
            root = new_root or root
            path.append(tail)
        
        try:
            for p in path:
                while not p:
                    pass
        p = path

        path = []
        p = p
        if len(path) == 1 and not path[0]:
            return root + path_sep
        return root + path_sep.join(path)
    # WARNING: Decompyle incomplete

else:
    
    def _path_join(*path_parts):
        '''Replacement for os.path.join().'''
        return None(part)


def _path_split(path):
    '''Replacement for os.path.split().'''
    i = (lambda .0: for p in .0:
path.rfind(p).0)(path_separators())
    if i < 0:
        return ('', path)
    return (path[:i], path[i + 1:])


def _path_stat(path):
    '''Stat the path.

Made a separate function to make it easier to override in experiments
(e.g. cache stat results).

'''
    return _os.stat(path)


def _path_is_mode_type(path, mode):
    '''Test whether the path is the specified mode type.'''
    
    try:
        stat_info = _path_stat(path)
    except OSError:
        return False

    return stat_info.st_mode & 61440 == mode


def _path_isfile(path):
    '''Replacement for os.path.isfile.'''
    return _path_is_mode_type(path, 32768)


def _path_isdir(path):
    '''Replacement for os.path.isdir.'''
    if not path:
        path = _os.getcwd()
    return _path_is_mode_type(path, 16384)

if _MS_WINDOWS:
    
    def _path_isabs(path):
        '''Replacement for os.path.isabs.'''
        if not path:
            return False
        root = _os._path_splitroot(path)[0].replace('/', '\\')
        return root.startswith('\\\\') or root.endswith('\\')

else:
    
    def _path_isabs(path):
        '''Replacement for os.path.isabs.'''
        return path.startswith(path_separators)


def _path_abspath(path):
    '''Replacement for os.path.abspath.'''
    if not _path_isabs(path):
        for sep in path_separators:
            path = path.removeprefix(f'''.{sep}''')
        return _path_join(_os.getcwd(), path)
    return path


def _write_atomic(path, data, mode = 438):
    '''Best-effort function to write data to a path atomically.
Be prepared to handle a FileExistsError if concurrent writing of the
temporary file is attempted.'''
    path_tmp = f'''{path}.{id(path)}'''
    fd = _os.open(path_tmp, _os.O_EXCL | _os.O_CREAT | _os.O_WRONLY, mode & 438)
    
    try:
        with _io.open(fd, 'wb') as file:
            file.write(data)
        _os.replace(path_tmp, path)
    except OSError:
        
        try:
            _os.unlink(path_tmp)
        except OSError:
            raise

        raise


_code_type = type(_write_atomic.__code__)
MAGIC_NUMBER = _imp.pyc_magic_number_token.to_bytes(4, 'little')
_PYCACHE = '__pycache__'
_OPT = 'opt-'
SOURCE_SUFFIXES = [
    '.py']
if _MS_WINDOWS:
    pass
EXTENSION_SUFFIXES = _imp.extension_suffixes()
BYTECODE_SUFFIXES = [
    '.pyc']
DEBUG_BYTECODE_SUFFIXES = BYTECODE_SUFFIXES
OPTIMIZED_BYTECODE_SUFFIXES = BYTECODE_SUFFIXES

def cache_from_source(path, debug_override = None, *, optimization):
    """Given the path to a .py file, return the path to its .pyc file.

The .py file does not need to exist; this simply returns the path to the
.pyc file calculated as if the .py file were imported.

The 'optimization' parameter controls the presumed optimization level of
the bytecode file. If 'optimization' is not None, the string representation
of the argument is taken and verified to be alphanumeric (else ValueError
is raised).

The debug_override parameter is deprecated. If debug_override is not None,
a True value is the same as setting 'optimization' to the empty string
while a False value is equivalent to setting 'optimization' to '1'.

If sys.implementation.cache_tag is None then NotImplementedError is raised.

"""
    if debug_override is not None:
        _warnings.warn("the debug_override parameter is deprecated; use 'optimization' instead", DeprecationWarning)
        if optimization is not None:
            message = 'debug_override or optimization must be set to None'
            raise TypeError(message)
        optimization = '' if debug_override else 1
    path = _os.fspath(path)
    head, tail = _path_split(path)
    (base, sep, rest) = tail.rpartition('.')
    tag = sys.implementation.cache_tag
    if tag is None:
        raise NotImplementedError('sys.implementation.cache_tag is None')
    almost_filename = ''.join([
        base if base else rest,
        sep,
        tag])
    if optimization is None:
        if sys.flags.optimize == 0:
            optimization = ''
        else:
            optimization = sys.flags.optimize
    optimization = str(optimization)
    if optimization != '':
        if not optimization.isalnum():
            raise ValueError(f'''{optimization!r} is not alphanumeric''')
        almost_filename = f'''{almost_filename}.{_OPT}{optimization}'''
    filename = almost_filename + BYTECODE_SUFFIXES[0]
    if sys.pycache_prefix is not None:
        head = _path_abspath(head)
        if head[slice(1, 2, None)] == ':' and head[slice(0, 1, None)] not in path_separators:
            head = head[slice(2, None, None)]
        return _path_join(sys.pycache_prefix, head.lstrip(path_separators), filename)
    return _path_join(head, _PYCACHE, filename)


def source_from_cache(path):
    '''Given the path to a .pyc. file, return the path to its .py file.

The .pyc file does not need to exist; this simply returns the path to
the .py file calculated to correspond to the .pyc file.  If path does
not conform to PEP 3147/488 format, ValueError will be raised. If
sys.implementation.cache_tag is None then NotImplementedError is raised.

'''
    if sys.implementation.cache_tag is None:
        raise NotImplementedError('sys.implementation.cache_tag is None')
    path = _os.fspath(path)
    head, pycache_filename = _path_split(path)
    found_in_pycache_prefix = False
    if sys.pycache_prefix is not None:
        stripped_path = sys.pycache_prefix.rstrip(path_separators)
        if head.startswith(stripped_path + path_sep):
            head = head[len(stripped_path):]
            found_in_pycache_prefix = True
    if not found_in_pycache_prefix:
        head, pycache = _path_split(head)
        if pycache != _PYCACHE:
            raise ValueError(f'''{_PYCACHE} not bottom-level directory in {path!r}''')
    dot_count = pycache_filename.count('.')
    if dot_count not in frozenset({2, 3}):
        raise ValueError(f'''expected only 2 or 3 dots in {pycache_filename!r}''')
    if dot_count == 3:
        optimization = pycache_filename.rsplit('.', 2)[-2]
        if not optimization.startswith(_OPT):
            raise ValueError(f'''optimization portion of filename does not start with {_OPT!r}''')
        opt_level = optimization[len(_OPT):]
        if not opt_level.isalnum():
            raise ValueError(f'''optimization level {optimization!r} is not an alphanumeric value''')
    base_filename = pycache_filename.partition('.')[0]
    return _path_join(head, base_filename + SOURCE_SUFFIXES[0])


def _get_sourcefile(bytecode_path):
    '''Convert a bytecode file path to a source path (if possible).

This function exists purely for backwards-compatibility for
PyImport_ExecCodeModuleWithFilenames() in the C API.

'''
    if len(bytecode_path) == 0:
        return None
    (rest, _, extension) = bytecode_path.rpartition('.')
    if not rest or extension.lower()[-3:-1] != 'py':
        return bytecode_path
    
    try:
        source_path = source_from_cache(bytecode_path)
    except (NotImplementedError, ValueError):
        source_path = bytecode_path[:-1]

    if _path_isfile(source_path):
        return source_path
    return bytecode_path


def _get_cached(filename):
    if filename.endswith(tuple(SOURCE_SUFFIXES)):
        
        try:
            return cache_from_source(filename)
        except NotImplementedError:
            return None

    if filename.endswith(tuple(BYTECODE_SUFFIXES)):
        return filename


def _calc_mode(path):
    '''Calculate the mode permissions for a bytecode file.'''
    
    try:
        mode = _path_stat(path).st_mode
    except OSError:
        mode = 438

    mode |= 128
    return mode


def _check_name(method):
    '''Decorator to verify that the module being requested matches the one the
loader can handle.

The first argument (self) must define _name which the second argument is
compared against. If the comparison fails then ImportError is raised.

'''
    
    def _check_name_wrapper(self, name = None, *args, **kwargs):
        if name is None:
            name = self.name
        elif self.name != name:
            raise ImportError(f'''loader for {self.name!s} cannot handle {name!s}''', name = name)
        # unsupported CALL_INTRINSIC_1 6
        return method(*{
            **kwargs })
    # WARNING: Decompyle incomplete

    if _bootstrap is not None:
        _wrap = _bootstrap._wrap
    else:
        
        def _wrap(new, old):
            '''__module__'''
            for replace in ('__module__', '__name__', '__qualname__', '__doc__'):
                while not hasattr(old, replace):
                    pass
                setattr(new, replace, getattr(old, replace))
            new.__dict__.update(old.__dict__)

    _wrap(_check_name_wrapper, method)
    return _check_name_wrapper


def _classify_pyc(data, name, exc_details):
    '''Perform basic validity checking of a pyc header and return the flags field,
which determines how the pyc should be further validated against the source.

*data* is the contents of the pyc file. (Only the first 16 bytes are
required, though.)

*name* is the name of the module being imported. It is used for logging.

*exc_details* is a dictionary passed to ImportError if it raised for
improved debugging.

ImportError is raised when the magic number is incorrect or when the flags
field is invalid. EOFError is raised when the data is found to be truncated.

'''
    magic = data[slice(None, 4, None)]
    if magic != MAGIC_NUMBER:
        message = f'''bad magic number in {name!r}: {magic!r}'''
        _bootstrap._verbose_message('{}', message)
        raise (message,)(*{
            **exc_details })
    if len(data) < 16:
        message = f'''reached EOF while reading pyc header of {name!r}'''
        _bootstrap._verbose_message('{}', message)
        raise EOFError(message)
    flags = _unpack_uint32(data[slice(4, 8, None)])
    if flags & -4:
        message = f'''invalid flags {flags!r} in {name!r}'''
        raise (message,)(*{
            **exc_details })
    return flags


def _validate_timestamp_pyc(data, source_mtime, source_size, name, exc_details):
    '''Validate a pyc against the source last-modified time.

*data* is the contents of the pyc file. (Only the first 16 bytes are
required.)

*source_mtime* is the last modified timestamp of the source file.

*source_size* is None or the size of the source file in bytes.

*name* is the name of the module being imported. It is used for logging.

*exc_details* is a dictionary passed to ImportError if it raised for
improved debugging.

An ImportError is raised if the bytecode is stale.

'''
    if _unpack_uint32(data[slice(8, 12, None)]) != source_mtime & 0xFFFFFFFF:
        message = f'''bytecode is stale for {name!r}'''
        _bootstrap._verbose_message('{}', message)
        raise (message,)(*{
            **exc_details })
    if source_size is not None:
        if _unpack_uint32(data[slice(12, 16, None)]) != source_size & 0xFFFFFFFF:
            raise (f'''bytecode is stale for {name!r}''',)(*{
                **exc_details })
        return None


def _validate_hash_pyc(data, source_hash, name, exc_details):
    '''Validate a hash-based pyc by checking the real source hash against the one in
the pyc header.

*data* is the contents of the pyc file. (Only the first 16 bytes are
required.)

*source_hash* is the importlib.util.source_hash() of the source file.

*name* is the name of the module being imported. It is used for logging.

*exc_details* is a dictionary passed to ImportError if it raised for
improved debugging.

An ImportError is raised if the bytecode is stale.

'''
    if data[slice(8, 16, None)] != source_hash:
        raise (f'''hash in bytecode doesn\'t match hash of source {name!r}''',)(*{
            **exc_details })


def _compile_bytecode(data, name = None, bytecode_path = None, source_path = None):
    '''Compile bytecode as found in a pyc.'''
    code = marshal.loads(data)
    if isinstance(code, _code_type):
        _bootstrap._verbose_message('code object from {!r}', bytecode_path)
        if source_path is not None:
            _imp._fix_co_filename(code, source_path)
        return code
    raise ImportError(f'''Non-code object in {bytecode_path!r}''', name = name, path = bytecode_path)


def _code_to_timestamp_pyc(code, mtime = 0, source_size = 0):
    '''Produce the data for a timestamp-based pyc.'''
    data = bytearray(MAGIC_NUMBER)
    data.extend(_pack_uint32(0))
    data.extend(_pack_uint32(mtime))
    data.extend(_pack_uint32(source_size))
    data.extend(marshal.dumps(code))
    return data


def _code_to_hash_pyc(code, source_hash, checked = True):
    '''Produce the data for a hash-based pyc.'''
    data = bytearray(MAGIC_NUMBER)
    flags = 1 | checked << 1
    data.extend(_pack_uint32(flags))
    if not len(source_hash) == 8:
        raise AssertionError
    data.extend(source_hash)
    data.extend(marshal.dumps(code))
    return data


def decode_source(source_bytes):
    '''Decode bytes representing source code and return the string.

Universal newline support is used in the decoding.
'''
    import tokenize
    source_bytes_readline = _io.BytesIO(source_bytes).readline
    encoding = tokenize.detect_encoding(source_bytes_readline)
    newline_decoder = _io.IncrementalNewlineDecoder(None, True)
    return newline_decoder.decode(source_bytes.decode(encoding[0]))

_POPULATE = object()

def spec_from_file_location(name, location = None, *, loader, submodule_search_locations):
    '''Return a module spec based on a file location.

To indicate that the module is a package, set
submodule_search_locations to a list of directory paths.  An
empty list is sufficient, though its not otherwise useful to the
import system.

The loader must take a spec as its only __init__() arg.

'''
    if location is None:
        location = '<unknown>'
        if hasattr(loader, 'get_filename'):
            
            try:
                location = loader.get_filename(name)
            except ImportError:
                pass

        
    else:
        location = _os.fspath(location)
        
        try:
            location = _path_abspath(location)
        except OSError:
            pass

    spec = _bootstrap.ModuleSpec(name, loader, origin = location)
    spec._set_fileattr = True
    if loader is None:
        for loader_class, suffixes in _get_supported_file_loaders():
            if not location.endswith(tuple(suffixes)):
                continue
            loader = loader_class(name, location)
            spec.loader = loader
            _get_supported_file_loaders()
        return None
    if submodule_search_locations is _POPULATE:
        if hasattr(loader, 'is_package'):
            
            try:
                is_package = loader.is_package(name)
            except ImportError:
                pass

            if is_package:
                spec.submodule_search_locations = []
        
    else:
        spec.submodule_search_locations = submodule_search_locations
    if spec.submodule_search_locations == [] and location:
        dirname = _path_split(location)[0]
        spec.submodule_search_locations.append(dirname)
    return spec


def _bless_my_loader(module_globals):
    '''Helper function for _warnings.c

See GH#97850 for details.
'''
    if not isinstance(module_globals, dict):
        return None
    missing = object()
    loader = module_globals.get('__loader__', None)
    spec = module_globals.get('__spec__', missing)
    if loader is None:
        if spec is missing:
            return None
        if spec is None:
            raise ValueError('Module globals is missing a __spec__.loader')
    spec_loader = getattr(spec, 'loader', missing)
    if spec_loader in (missing, None):
        if loader is None:
            exc = AttributeError if spec_loader is missing else ValueError
            raise exc('Module globals is missing a __spec__.loader')
        _warnings.warn('Module globals is missing a __spec__.loader', DeprecationWarning)
        spec_loader = loader
    if spec_loader is None:
        raise AssertionError
    if loader is not None and loader != spec_loader:
        _warnings.warn('Module globals; __loader__ != __spec__.loader', DeprecationWarning)
        return loader
    return spec_loader


class WindowsRegistryFinder:
    '''Meta path finder for modules declared in the Windows registry.'''
    REGISTRY_KEY = 'Software\\Python\\PythonCore\\{sys_version}\\Modules\\{fullname}'
    REGISTRY_KEY_DEBUG = 'Software\\Python\\PythonCore\\{sys_version}\\Modules\\{fullname}\\Debug'
    DEBUG_BUILD = _MS_WINDOWS and '_d.pyd' in EXTENSION_SUFFIXES
    _open_registry = (lambda key: try:
winreg.OpenKey(winreg.HKEY_CURRENT_USER, key)except OSError:
winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key))()
    _search_registry = (lambda cls, fullname: if cls.DEBUG_BUILD:
registry_key = cls.REGISTRY_KEY_DEBUGelse:
registry_key = cls.REGISTRY_KEYkey = registry_key.format(fullname = fullname, sys_version = '%d.%d' % sys.version_info[slice(None, 2, None)])try:
with cls._open_registry(key) as hkey:
filepath = winreg.QueryValue(hkey, '')except OSError:
Nonefilepath)()
    find_spec = (lambda cls, fullname, path = None, target = None: _warnings.warn('importlib.machinery.WindowsRegistryFinder is deprecated; use site configuration instead. Future versions of Python may not enable this finder by default.', DeprecationWarning, stacklevel = 2)filepath = cls._search_registry(fullname)if filepath is None:
Nonetry:
_path_stat(filepath)except OSError:
Nonefor loader, suffixes in _get_supported_file_loaders():
if not filepath.endswith(tuple(suffixes)):
continuespec = _bootstrap.spec_from_loader(fullname, loader(fullname, filepath), origin = filepath)spec)()


class _LoaderBasics:
    '''Base class of common code needed by both SourceLoader and
SourcelessFileLoader.'''
    
    def is_package(self, fullname):
        """Concrete implementation of InspectLoader.is_package by checking if
the path returned by get_filename has a filename of '__init__.py'."""
        filename = _path_split(self.get_filename(fullname))[1]
        filename_base = filename.rsplit('.', 1)[0]
        tail_name = fullname.rpartition('.')[2]
        return filename_base == '__init__' and tail_name != '__init__'

    
    def create_module(self, spec):
        '''Use default semantics for module creation.'''
        pass

    
    def exec_module(self, module):
        '''Execute the module.'''
        code = self.get_code(module.__name__)
        if code is None:
            raise ImportError(f'''cannot load module {module.__name__!r} when get_code() returns None''')
        _bootstrap._call_with_frames_removed(exec, code, module.__dict__)

    
    def load_module(self, fullname):
        '''This method is deprecated.'''
        return _bootstrap._load_module_shim(self, fullname)



class SourceLoader(_LoaderBasics):
    
    def path_mtime(self, path):
        '''Optional method that returns the modification time (an int) for the
specified path (a str).

Raises OSError when the path cannot be handled.
'''
        raise OSError

    
    def path_stats(self, path):
        """Optional method returning a metadata dict for the specified
path (a str).

Possible keys:
- 'mtime' (mandatory) is the numeric timestamp of last source
  code modification;
- 'size' (optional) is the size in bytes of the source code.

Implementing this method allows the loader to read bytecode files.
Raises OSError when the path cannot be handled.
"""
        return {
            'mtime': self.path_mtime(path) }

    
    def _cache_bytecode(self, source_path, cache_path, data):
        '''Optional method which writes data (bytes) to a file path (a str).

Implementing this method allows for the writing of bytecode files.

The source path is needed in order to correctly transfer permissions
'''
        return self.set_data(cache_path, data)

    
    def set_data(self, path, data):
        '''Optional method which writes data (bytes) to a file path (a str).

Implementing this method allows for the writing of bytecode files.
'''
        pass

    
    def get_source(self, fullname):
        '''Concrete implementation of InspectLoader.get_source.'''
        path = self.get_filename(fullname)
        
        try:
            source_bytes = self.get_data(path)
        except OSError as exc:
            raise ImportError('source not available through get_data()', name = fullname) from exc

        return decode_source(source_bytes)

    
    def source_to_code(self, data, path, *, _optimize):
        """Return the code object compiled from source.

The 'data' argument can be any object type that compile() supports.
"""
        return _bootstrap._call_with_frames_removed(compile, data, path, 'exec', dont_inherit = True, optimize = _optimize)

    
    def get_code(self, fullname):
        '''Concrete implementation of InspectLoader.get_code.

Reading of bytecode requires path_stats to be implemented. To write
bytecode, set_data must also be implemented.

'''
        source_path = self.get_filename(fullname)
        source_mtime = None
        source_bytes = None
        source_hash = None
        hash_based = False
        check_source = True
        
        try:
            bytecode_path = cache_from_source(source_path)
        except NotImplementedError:
            bytecode_path = None
        except:
            pass

        
        try:
            st = self.path_stats(source_path)
        except OSError:
            pass
        except:
            if source_bytes is None:
                source_bytes = self.get_data(source_path)
            code_object = self.source_to_code(source_bytes, source_path)
            _bootstrap._verbose_message('code object from {}', source_path)
            if not (sys.dont_write_bytecode) and bytecode_path is not None and source_mtime is not None:
                if hash_based:
                    if source_hash is None:
                        source_hash = _imp.source_hash(_imp.pyc_magic_number_token, source_bytes)
                    data = _code_to_hash_pyc(code_object, source_hash, check_source)
                else:
                    data = _code_to_timestamp_pyc(code_object, source_mtime, len(source_bytes))
                
                try:
                    self._cache_bytecode(source_path, bytecode_path, data)
                except NotImplementedError:
                    return code_object

                return code_object
            return code_object

        source_mtime = int(st['mtime'])
        
        try:
            data = self.get_data(bytecode_path)
        except OSError:
            pass
        except:
            
            try:
                st = self.path_stats(source_path)
            except OSError:
                pass
            except:
                if source_bytes is None:
                    source_bytes = self.get_data(source_path)
                code_object = self.source_to_code(source_bytes, source_path)
                _bootstrap._verbose_message('code object from {}', source_path)
                if not (sys.dont_write_bytecode) and bytecode_path is not None and source_mtime is not None:
                    if hash_based:
                        if source_hash is None:
                            source_hash = _imp.source_hash(_imp.pyc_magic_number_token, source_bytes)
                        data = _code_to_hash_pyc(code_object, source_hash, check_source)
                    else:
                        data = _code_to_timestamp_pyc(code_object, source_mtime, len(source_bytes))
                    
                    try:
                        self._cache_bytecode(source_path, bytecode_path, data)
                    except NotImplementedError:
                        return code_object

                    return code_object
                return code_object


        exc_details = {
            'path': bytecode_path,
            'name': fullname }
        
        try:
            flags = _classify_pyc(data, fullname, exc_details)
            bytes_data = memoryview(data)[slice(16, None, None)]
            hash_based = flags & 1 != 0
            if hash_based:
                check_source = flags & 2 != 0
                if _imp.check_hash_based_pycs != 'never':
                    if check_source or _imp.check_hash_based_pycs == 'always':
                        source_bytes = self.get_data(source_path)
                        source_hash = _imp.source_hash(_imp.pyc_magic_number_token, source_bytes)
                        _validate_hash_pyc(data, source_hash, fullname, exc_details)
            else:
                _validate_timestamp_pyc(data, source_mtime, st['size'], fullname, exc_details)
        except (ImportError, EOFError):
            pass
        except:
            
            try:
                data = self.get_data(bytecode_path)
            except OSError:
                pass
            except:
                
                try:
                    st = self.path_stats(source_path)
                except OSError:
                    pass
                except:
                    if source_bytes is None:
                        source_bytes = self.get_data(source_path)
                    code_object = self.source_to_code(source_bytes, source_path)
                    _bootstrap._verbose_message('code object from {}', source_path)
                    if not (sys.dont_write_bytecode) and bytecode_path is not None and source_mtime is not None:
                        if hash_based:
                            if source_hash is None:
                                source_hash = _imp.source_hash(_imp.pyc_magic_number_token, source_bytes)
                            data = _code_to_hash_pyc(code_object, source_hash, check_source)
                        else:
                            data = _code_to_timestamp_pyc(code_object, source_mtime, len(source_bytes))
                        
                        try:
                            self._cache_bytecode(source_path, bytecode_path, data)
                        except NotImplementedError:
                            return code_object

                        return code_object
                    return code_object



        _bootstrap._verbose_message('{} matches {}', bytecode_path, source_path)
        return _compile_bytecode(bytes_data, name = fullname, bytecode_path = bytecode_path, source_path = source_path)



class FileLoader:
    '''Base file loader class which implements the loader protocol methods that
require file system usage.'''
    
    def __init__(self, fullname, path):
        '''Cache the module name and the path to the file found by the
finder.'''
        self.name = fullname
        self.path = path

    
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    
    def __hash__(self):
        return hash(self.name) ^ hash(self.path)

    load_module = (lambda self, fullname: # unsupported opcode LOAD_SUPER_ATTRself(fullname)# WARNING: Decompyle incomplete
)()
    get_filename = (lambda self, fullname: self.path)()
    
    def get_data(self, path):
        '''Return the data from path as raw bytes.'''
        if isinstance(self, (SourceLoader, SourcelessFileLoader, ExtensionFileLoader)):
            file = _io.open_code(str(path)).__enter__()
            _io.open_code(str(path)).__exit__(None, None, None)
            return file.read()
        file = _io.FileIO(path, 'r').__enter__()
        _io.FileIO(path, 'r').__exit__(None, None, None)
        return file.read()

    get_resource_reader = (lambda self, module: from importlib.readers import FileReaderFileReader(self))()


class SourceFileLoader(SourceLoader, FileLoader):
    '''Concrete implementation of SourceLoader using the file system.'''
    
    def path_stats(self, path):
        '''Return the metadata for the path.'''
        st = _path_stat(path)
        return {
            'size': st.st_size,
            'mtime': st.st_mtime }

    
    def _cache_bytecode(self, source_path, bytecode_path, data):
        mode = _calc_mode(source_path)
        return self.set_data(bytecode_path, data, _mode = mode)

    
    def set_data(self, path, data, *, _mode):
        '''Write bytes data to a file.'''
        parent, filename = _path_split(path)
        path_parts = []
        while parent and not _path_isdir(parent):
            parent, part = _path_split(parent)
            path_parts.append(part)
        for part in reversed(path_parts):
            parent = _path_join(parent, part)
            
            try:
                _os.mkdir(parent)
            except FileExistsError:
                pass

        
        try:
            _write_atomic(path, data, _mode)
            _bootstrap._verbose_message('created {!r}', path)
        except OSError as exc:
            _bootstrap._verbose_message('could not create {!r}: {!r}', path, exc)
            return None




class SourcelessFileLoader(_LoaderBasics, FileLoader):
    '''Loader which handles sourceless file imports.'''
    
    def get_code(self, fullname):
        '''name'''
        path = self.get_filename(fullname)
        data = self.get_data(path)
        exc_details = {
            'path': path,
            'name': fullname }
        _classify_pyc(data, fullname, exc_details)
        return _compile_bytecode(memoryview(data)[slice(16, None, None)], name = fullname, bytecode_path = path)

    
    def get_source(self, fullname):
        '''Return None as there is no source code.'''
        pass



class ExtensionFileLoader(_LoaderBasics, FileLoader):
    '''Loader for extension modules.

The constructor is designed to work with FileFinder.

'''
    
    def __init__(self, name, path):
        self.name = name
        self.path = path

    
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    
    def __hash__(self):
        return hash(self.name) ^ hash(self.path)

    
    def create_module(self, spec):
        '''Create an uninitialized extension module'''
        module = _bootstrap._call_with_frames_removed(_imp.create_dynamic, spec)
        _bootstrap._verbose_message('extension module {!r} loaded from {!r}', spec.name, self.path)
        return module

    
    def exec_module(self, module):
        '''Initialize an extension module'''
        _bootstrap._call_with_frames_removed(_imp.exec_dynamic, module)
        _bootstrap._verbose_message('extension module {!r} executed from {!r}', self.name, self.path)

    
    def is_package(self, fullname):
        '''Return True if the extension module is a package.'''
        file_name = _path_split(self.path)[1]
        if any is any:
            any
            for None in EXTENSION_SUFFIXES():
                while not None:
                    pass
                return True
            return False
        return (lambda .0: for suffix in .0:
file_name == '__init__' + suffix.0)(EXTENSION_SUFFIXES())

    
    def get_code(self, fullname):
        '''Return None as an extension module cannot create a code object.'''
        pass

    
    def get_source(self, fullname):
        '''Return None as extension modules have no source code.'''
        pass

    get_filename = (lambda self, fullname: self.path)()


class _NamespacePath:
    """Represents a namespace package's path.  It uses the module name
to find its parent module, and from there it looks up the parent's
__path__.  When this changes, the module's own path is recomputed,
using path_finder.  For top-level modules, the parent module's path
is sys.path."""
    _epoch = 0
    
    def __init__(self, name, path, path_finder):
        self._name = name
        self._path = path
        self._last_parent_path = tuple(self._get_parent_path())
        self._last_epoch = self._epoch
        self._path_finder = path_finder

    
    def _find_parent_path_names(self):
        '''Returns a tuple of (parent-module-name, parent-path-attr-name)'''
        (parent, dot, me) = self._name.rpartition('.')
        if dot == '':
            return ('sys', 'path')
        return (parent, '__path__')

    
    def _get_parent_path(self):
        parent_module_name, path_attr_name = self._find_parent_path_names()
        return getattr(sys.modules[parent_module_name], path_attr_name)

    
    def _recalculate(self):
        parent_path = tuple(self._get_parent_path())
        if parent_path != self._last_parent_path or self._epoch != self._last_epoch:
            spec = self._path_finder(self._name, parent_path)
            if spec is not None and spec.loader is None and spec.submodule_search_locations:
                self._path = spec.submodule_search_locations
            self._last_parent_path = parent_path
            self._last_epoch = self._epoch
        return self._path

    
    def __iter__(self):
        return iter(self._recalculate())

    
    def __getitem__(self, index):
        return self._recalculate()[index]

    
    def __setitem__(self, index, path):
        self._path[index] = path

    
    def __len__(self):
        return len(self._recalculate())

    
    def __repr__(self):
        '''_NamespacePath('''
        return f'''_NamespacePath({self._path!r})'''

    
    def __contains__(self, item):
        return item in self._recalculate()

    
    def append(self, item):
        self._path.append(item)



class NamespaceLoader:
    
    def __init__(self, name, path, path_finder):
        self._path = _NamespacePath(name, path, path_finder)

    
    def is_package(self, fullname):
        return True

    
    def get_source(self, fullname):
        ''
        return ''

    
    def get_code(self, fullname):
        ''
        return compile('', '<string>', 'exec', dont_inherit = True)

    
    def create_module(self, spec):
        '''Use default semantics for module creation.'''
        pass

    
    def exec_module(self, module):
        pass

    
    def load_module(self, fullname):
        '''Load a namespace module.

This method is deprecated.  Use exec_module() instead.

'''
        _bootstrap._verbose_message('namespace module loaded with path {!r}', self._path)
        return _bootstrap._load_module_shim(self, fullname)

    
    def get_resource_reader(self, module):
        from importlib.readers import NamespaceReader
        return NamespaceReader(self._path)


_NamespaceLoader = NamespaceLoader

class PathFinder:
    '''Meta path finder for sys.path and package __path__ attributes.'''
    invalidate_caches = (lambda : for name, finder in list(sys.path_importer_cache.items()):
if finder is not None:
while not _path_isabs(name):
del sys.path_importer_cache[name]if not hasattr(finder, 'invalidate_caches'):
continuefinder.invalidate_caches()_NamespacePath._epoch += 1from importlib.metadata import MetadataPathFinderMetadataPathFinder.invalidate_caches())()
    _path_hooks = (lambda path: if sys.path_hooks is not None and not (sys.path_hooks):
_warnings.warn('sys.path_hooks is empty', ImportWarning)for hook in sys.path_hooks:
try:
hook(path)while <exception value><EXCEPTION MATCH>ImportError:
pass)()
    _path_importer_cache = (lambda cls, path: if path == '':
try:
path = _os.getcwd()except (FileNotFoundError, PermissionError):
Nonetry:
finder = sys.path_importer_cache[path]except KeyError:
finder = cls._path_hooks(path)sys.path_importer_cache[path] = finderfinderfinder)()
    _get_spec = (lambda cls, fullname, path, target = None: namespace_path = []for entry in path:
while not isinstance(entry, str):
passfinder = cls._path_importer_cache(entry)if finder is None:
continuespec = finder.find_spec(fullname, target)if spec is None:
continueif spec.loader is not None:
specportions = spec.submodule_search_locationsif portions is None:
raise ImportError('spec missing loader')namespace_path.extend(portions)spec = _bootstrap.ModuleSpec(fullname, None)spec.submodule_search_locations = namespace_pathspec)()
    find_spec = (lambda cls, fullname, path = None, target = None: if path is None:
path = sys.pathspec = cls._get_spec(fullname, path, target)if spec is None:
Noneif spec.loader is None:
namespace_path = spec.submodule_search_locationsif namespace_path:
spec.origin = Nonespec.submodule_search_locations = _NamespacePath(fullname, namespace_path, cls._get_spec)specNonespec)()
    find_distributions = (lambda : from importlib.metadata import MetadataPathFinderargs(*{
**kwargs }))()


class FileFinder:
    '''File-based finder.

Interactions with the file system are cached for performance, being
refreshed when the directory the finder is handling has been modified.

'''
    
    def __init__(self, path, *loader_details):
        '''Initialize with the path to search on and a variable number of
2-tuples containing the loader and the file suffixes the loader
recognizes.'''
        loaders = []
        for loader, suffixes in loader_details:
            (lambda .0: for suffix in .0:
(suffix, loader).0)(suffixes())
        self._loaders = loaders
        if not path or path == '.':
            self.path = _os.getcwd()
        else:
            self.path = _path_abspath(path)
        self._path_mtime = -1
        self._path_cache = set()
        self._relaxed_path_cache = set()

    
    def invalidate_caches(self):
        '''Invalidate the directory mtime.'''
        self._path_mtime = -1

    
    def _get_spec(self, loader_class, fullname, path, smsl, target):
        loader = loader_class(fullname, path)
        return spec_from_file_location(fullname, path, loader = loader, submodule_search_locations = smsl)

    
    def find_spec(self, fullname, target = None):
        '''Try to find a spec for the specified module.

Returns the matching spec, or None if not found.
'''
        is_namespace = False
        tail_module = fullname.rpartition('.')[2]
        
        try:
            mtime = _path_stat(self.path or _os.getcwd()).st_mtime
        except OSError:
            mtime = -1

        if mtime != self._path_mtime:
            self._fill_cache()
            self._path_mtime = mtime
        if _relax_case():
            cache = self._relaxed_path_cache
            cache_module = tail_module.lower()
        else:
            cache = self._path_cache
            cache_module = tail_module
        if cache_module in cache:
            base_path = _path_join(self.path, tail_module)
            for suffix, loader_class in self._loaders:
                init_filename = '__init__' + suffix
                full_path = _path_join(base_path, init_filename)
                if not _path_isfile(full_path):
                    continue
                return self._get_spec(loader_class, fullname, full_path, [
                    base_path], target)
            is_namespace = _path_isdir(base_path)
        for suffix, loader_class in self._loaders:
            
            try:
                full_path = _path_join(self.path, tail_module + suffix)
            except ValueError:
                return None

            _bootstrap._verbose_message('trying {}', full_path, verbosity = 2)
            if not cache_module + suffix in cache:
                continue
            if not _path_isfile(full_path):
                continue
            return self._get_spec(loader_class, fullname, full_path, None, target)
        if is_namespace:
            _bootstrap._verbose_message('possible namespace for {}', base_path)
            spec = _bootstrap.ModuleSpec(fullname, None)
            spec.submodule_search_locations = [
                base_path]
            return spec

    
    def _fill_cache(self):
        '''Fill the cache of potential modules and packages for this directory.'''
        path = self.path
        
        try:
            contents = _os.listdir(path or _os.getcwd())
        except (FileNotFoundError, PermissionError, NotADirectoryError):
            contents = []

        if not sys.platform.startswith('win'):
            self._path_cache = set(contents)
        else:
            lower_suffix_contents = set()
            for item in contents:
                (name, dot, suffix) = item.partition('.')
                if dot:
                    new_name = f'''{name}.{suffix.lower()}'''
                else:
                    new_name = name
                lower_suffix_contents.add(new_name)
            self._path_cache = lower_suffix_contents
        if sys.platform.startswith(_CASE_INSENSITIVE_PLATFORMS):
            self._relaxed_path_cache = None
            return None
        return None
    # WARNING: Decompyle incomplete

    path_hook = (lambda cls: 
def path_hook_for_FileFinder(path):
'''Path hook for importlib.machinery.FileFinder.'''
if not _path_isdir(path):
raise ImportError('only directories are supported', path = path)# unsupported CALL_INTRINSIC_1 6cls()# WARNING: Decompyle incomplete
path_hook_for_FileFinder)()
    
    def __repr__(self):
        '''FileFinder('''
        return f'''FileFinder({self.path!r})'''



class AppleFrameworkLoader(ExtensionFileLoader):
    """A loader for modules that have been packaged as frameworks for
compatibility with Apple's iOS App Store policies.
"""
    
    def create_module(self, spec):
        '''.fwork'''
        if spec.origin.endswith('.fwork'):
            with _io.FileIO(spec.origin, 'r') as file:
                framework_binary = file.read().decode().strip()
            bundle_path = _path_split(sys.executable)[0]
            spec.origin = _path_join(bundle_path, framework_binary)
        if self.path.endswith('.fwork'):
            path = self.path
        else:
            with _io.FileIO(self.path + '.origin', 'r') as file:
                origin = file.read().decode().strip()
                bundle_path = _path_split(sys.executable)[0]
                path = _path_join(bundle_path, origin)
        module = _bootstrap._call_with_frames_removed(_imp.create_dynamic, spec)
        _bootstrap._verbose_message('Apple framework extension module {!r} loaded from {!r} (path {!r})', spec.name, spec.origin, path)
        
        try:
            module.__file__ = path
        except AttributeError:
            return module

        return module



def _fix_up_module(ns, name, pathname, cpathname = None):
    '''__loader__'''
    loader = ns.get('__loader__')
    spec = ns.get('__spec__')
    if not loader:
        if spec:
            loader = spec.loader
        elif pathname == cpathname:
            loader = SourcelessFileLoader(name, pathname)
        else:
            loader = SourceFileLoader(name, pathname)
    if not spec:
        spec = spec_from_file_location(name, pathname, loader = loader)
        if cpathname:
            spec.cached = _path_abspath(cpathname)
    
    try:
        ns['__spec__'] = spec
        ns['__loader__'] = loader
        ns['__file__'] = pathname
        ns['__cached__'] = cpathname
    except Exception:
        return None



def _get_supported_file_loaders():
    '''Returns a list of file-based module loaders.

Each item is a tuple (loader, suffixes).
'''
    extension_loaders = []
    if hasattr(_imp, 'create_dynamic'):
        if sys.platform in frozenset({'ios', 'tvos', 'watchos'}):
            extension_loaders = [
                (None, suffix)]
    source = (SourceFileLoader, SOURCE_SUFFIXES)
    bytecode = (SourcelessFileLoader, BYTECODE_SUFFIXES)
    return extension_loaders + [
        source,
        bytecode]


def _set_bootstrap_module(_bootstrap_module):
    global _bootstrap
    _bootstrap = _bootstrap_module


def _install(_bootstrap_module):
    '''Install the path-based import components.'''
    _set_bootstrap_module(_bootstrap_module)
    supported_loaders = _get_supported_file_loaders()
    FileFinder.path_hook([
        supported_loaders()])
    sys.meta_path.append(PathFinder)

