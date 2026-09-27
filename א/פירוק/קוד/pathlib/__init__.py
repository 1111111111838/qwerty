# Source Generated with Decompyle++
# File: __init__.pyc (Python 3.14)

'''Object-oriented filesystem paths.

This module provides classes to represent abstract paths and concrete
paths with operations that have semantics appropriate for different
operating systems.
'''
import io
import ntpath
import operator
import os
import posixpath
import sys
from errno import *
from glob import _StringGlobber, _no_recurse_symlinks
from itertools import chain
from stat import S_ISDIR, S_ISREG, S_ISSOCK, S_ISBLK, S_ISCHR, S_ISFIFO
from _collections_abc import Sequence

try:
    import pwd
except ImportError:
    pwd = None


try:
    import grp
except ImportError:
    grp = None

from pathlib._os import PathInfo, DirEntryInfo, ensure_different_files, ensure_distinct_paths, copyfile2, copyfileobj, magic_open, copy_info
__all__ = [
    'UnsupportedOperation',
    'PurePath',
    'PurePosixPath',
    'PureWindowsPath',
    'Path',
    'PosixPath',
    'WindowsPath']

class UnsupportedOperation(NotImplementedError):
    '''An exception that is raised when an unsupported operation is attempted.
    '''
    pass


class _PathParents(Sequence):
    """This object provides sequence-like access to the logical ancestors
of a path.  Don't try to construct it yourself."""
    __slots__ = ('_path', '_drv', '_root', '_tail')
    
    def __init__(self, path):
        self._path = path
        self._drv = path.drive
        self._root = path.root
        self._tail = path._tail

    
    def __len__(self):
        return len(self._tail)

    
    def __getitem__(self, idx):
        if isinstance(idx, slice):
            if tuple is tuple:
                tuple
                for None in idx.indices(len(self))()():
                    pass
                # unsupported CALL_INTRINSIC_1 6
                return range
            return range(idx.indices(len(self))()())
        if idx >= len(self) or idx < -len(self):
            raise IndexError(idx)
        if idx < 0:
            idx += len(self)
        return self._path._from_parsed_parts(self._drv, self._root, self._tail[:-idx - 1])
    # WARNING: Decompyle incomplete

    
    def __repr__(self):
        '''<{}.parents>'''
        return '<{}.parents>'.format(type(self._path).__name__)



class PurePath:
    """Base class for manipulating paths without I/O.

PurePath represents a filesystem path and offers operations which
don't imply any actual filesystem I/O.  Depending on your system,
instantiating a PurePath will return either a PurePosixPath or a
PureWindowsPath object.  You can also instantiate either of these classes
directly, regardless of your system.
"""
    __slots__ = ('_raw_paths', '_drv', '_root', '_tail_cached', '_str', '_str_normcase_cached', '_parts_normcase_cached', '_hash')
    parser = os.path
    
    def __new__(cls, *args, **kwargs):
        '''Construct a PurePath from one or several strings and or existing
PurePath objects.  The strings and path objects are combined so as
to yield a canonicalized path, which is incorporated into the
new PurePath object.
'''
        if cls is PurePath:
            cls = PureWindowsPath if os.name == 'nt' else PurePosixPath
        return object.__new__(cls)

    
    def __init__(self, *args):
        '''argument should be a str or an os.PathLike object where __fspath__ returns a str, not '''
        paths = []
        for arg in args:
            while isinstance(arg, PurePath):
                if arg.parser is not self.parser:
                    paths.append(arg.as_posix())
                    continue
                paths.extend(arg._raw_paths)
            
            try:
                path = os.fspath(arg)
            except TypeError:
                path = arg

            if not isinstance(path, str):
                raise TypeError(f'''argument should be a str or an os.PathLike object where __fspath__ returns a str, not {type(path).__name__!r}''')
            paths.append(path)
        self._raw_paths = paths

    
    def with_segments(self, *pathsegments):
        '''Construct a new path object from any number of path-like objects.
Subclasses may override this method to customize how new path objects
are created from methods like `iterdir()`.
'''
        return pathsegments()

    
    def joinpath(self, *pathsegments):
        '''Combine this path with one or several arguments, and return a
new path representing either a subpath (if all arguments are relative
paths) or a totally different path (if one of the arguments is
anchored).
'''
        # unsupported CALL_INTRINSIC_1 6
        return self.with_segments()
    # WARNING: Decompyle incomplete

    
    def __truediv__(self, key):
        
        try:
            return self.with_segments(self, key)
        except TypeError:
            return NotImplemented


    
    def __rtruediv__(self, key):
        
        try:
            return self.with_segments(key, self)
        except TypeError:
            return NotImplemented


    
    def __reduce__(self):
        return (self.__class__, tuple(self._raw_paths))

    
    def __repr__(self):
        '''{}({!r})'''
        return '{}({!r})'.format(self.__class__.__name__, self.as_posix())

    
    def __fspath__(self):
        return str(self)

    
    def __bytes__(self):
        '''Return the bytes representation of the path.  This is only
recommended to use under Unix.'''
        return os.fsencode(self)

    _str_normcase = (lambda self: try:
self._str_normcase_cachedexcept AttributeError:
if self.parser is posixpath:
self._str_normcase_cached = str(self)else:
self._str_normcase_cached = str(self).lower()self._str_normcase_cached)()
    
    def __hash__(self):
        
        try:
            return self._hash
        except AttributeError:
            self._hash = hash(self._str_normcase)
            return self._hash


    
    def __eq__(self, other):
        if not isinstance(other, PurePath):
            return NotImplemented
        return self._str_normcase == other._str_normcase and self.parser is other.parser

    _parts_normcase = (lambda self: try:
self._parts_normcase_cachedexcept AttributeError:
self._parts_normcase_cached = self._str_normcase.split(self.parser.sep)self._parts_normcase_cached)()
    
    def __lt__(self, other):
        if not isinstance(other, PurePath) or self.parser is not other.parser:
            return NotImplemented
        return self._parts_normcase < other._parts_normcase

    
    def __le__(self, other):
        if not isinstance(other, PurePath) or self.parser is not other.parser:
            return NotImplemented
        return self._parts_normcase <= other._parts_normcase

    
    def __gt__(self, other):
        if not isinstance(other, PurePath) or self.parser is not other.parser:
            return NotImplemented
        return self._parts_normcase > other._parts_normcase

    
    def __ge__(self, other):
        if not isinstance(other, PurePath) or self.parser is not other.parser:
            return NotImplemented
        return self._parts_normcase >= other._parts_normcase

    
    def __str__(self):
        '''Return the string representation of the path, suitable for
passing to system calls.'''
        
        try:
            return self._str
        except AttributeError:
            self._str = self._format_parsed_parts(self.drive, self.root, self._tail) or '.'
            return self._str


    _format_parsed_parts = (lambda cls, drv, root, tail: if drv or root:
drv + root + cls.parser.sep.join(tail)if tail and cls.parser.splitdrive(tail[0])[0]:
tail = [
'.'] + tailcls.parser.sep.join(tail))()
    
    def _from_parsed_parts(self, drv, root, tail):
        path = self._from_parsed_string(self._format_parsed_parts(drv, root, tail))
        path._drv = drv
        path._root = root
        path._tail_cached = tail
        return path

    
    def _from_parsed_string(self, path_str):
        '''.'''
        path = self.with_segments(path_str)
        path._str = path_str or '.'
        return path

    _parse_path = (lambda cls, path: if not path:
('', '', [])sep = cls.parser.sepaltsep = cls.parser.altsepif altsep:
path = path.replace(altsep, sep)(drv, root, rel) = cls.parser.splitroot(path)if not root and drv.startswith(sep) and not drv.endswith(sep):
drv_parts = drv.split(sep)if len(drv_parts) == 4 and drv_parts[2] not in '?.':
root = sepelif len(drv_parts) == 6:
root = sep(None, drv, x))()
    _parse_pattern = (lambda cls, pattern: (drv, root, rel) = cls.parser.splitroot(pattern)if root or drv:
raise NotImplementedError('Non-relative patterns are unsupported')sep = cls.parser.sepaltsep = cls.parser.altsepif altsep:
rel = rel.replace(altsep, sep)try:
for x in rel.split(sep):
while not x:
passwhile not x != '.':
passx = rel.split(sep)parts = []x = xif not parts:
raise ValueError(f'''Unacceptable pattern: {str(pattern)!r}''')if rel.endswith(sep):
parts.append('')parts# WARNING: Decompyle incomplete
)()
    
    def as_posix(self):
        '''Return the string representation of the path with forward (/)
slashes.'''
        return str(self).replace(self.parser.sep, '/')

    _raw_path = (lambda self: paths = self._raw_pathsif len(paths) == 1:
paths[0]if paths:
paths()'')()
    drive = (lambda self: try:
self._drvexcept AttributeError:
(self._drv, self._root, self._tail_cached) = self._parse_path(self._raw_path)self._drv)()
    root = (lambda self: try:
self._rootexcept AttributeError:
(self._drv, self._root, self._tail_cached) = self._parse_path(self._raw_path)self._root)()
    _tail = (lambda self: try:
self._tail_cachedexcept AttributeError:
(self._drv, self._root, self._tail_cached) = self._parse_path(self._raw_path)self._tail_cached)()
    anchor = (lambda self: self.drive + self.root)()
    parts = (lambda self: (self.drive + self.root,) + tuple(self._tail) if self.drive or self.root else tuple(self._tail))()
    parent = (lambda self: drv = self.driveroot = self.roottail = self._tailif not tail:
selfself._from_parsed_parts(drv, root, tail[:-1]))()
    parents = (lambda self: _PathParents(self))()
    name = (lambda self: tail = self._tailif not tail:
''tail[-1])()
    
    def with_name(self, name):
        '''Return a new path with the file name changed.'''
        p = self.parser
        if name and not (p.sep in name):
            if not (not (p.altsep) or not (p.altsep in name)) or name == '.':
                raise ValueError(f'''Invalid name {name!r}''')
        tail = self._tail.copy()
        if not tail:
            raise ValueError(f'''{self!r} has an empty name''')
        tail[-1] = name
        return self._from_parsed_parts(self.drive, self.root, tail)

    
    def with_stem(self, stem):
        '''Return a new path with the stem changed.'''
        suffix = self.suffix
        if not suffix:
            return self.with_name(stem)
        if not stem:
            raise ValueError(f'''{self!r} has a non-empty suffix''')
        return self.with_name(stem + suffix)

    
    def with_suffix(self, suffix):
        '''Return a new path with the file suffix changed.  If the path
has no suffix, add given suffix.  If the given suffix is an empty
string, remove the suffix from the path.
'''
        stem = self.stem
        if not stem:
            raise ValueError(f'''{self!r} has an empty name''')
        if suffix and not suffix.startswith('.'):
            raise ValueError(f'''Invalid suffix {suffix!r}''')
        return self.with_name(stem + suffix)

    stem = (lambda self: name = self.namei = name.rfind('.')if i != -1:
stem = name[:i]if stem.lstrip('.'):
stemname)()
    suffix = (lambda self: name = self.name.lstrip('.')i = name.rfind('.')if i != -1:
name[i:]'')()
    suffixes = (lambda self: None# WARNING: Decompyle incomplete
)()
    
    def relative_to(self, other, *, walk_up):
        '''Return the relative path to another path identified by the passed
arguments.  If the operation is not possible (because this is not
related to the other path), raise ValueError.

The *walk_up* parameter controls whether `..` may be used to resolve
the path.
'''
        if not hasattr(other, 'with_segments'):
            other = self.with_segments(other)
        for step, path in enumerate(chain([
            other], other.parents)):
            if path == self or path in self.parents:
                enumerate(chain([
                    other], other.parents))
            elif not walk_up:
                raise ValueError(f'''{str(self)!r} is not in the subpath of {str(other)!r}''')
            if not path.name == '..':
                continue
            raise ValueError(f'''\'..\' segment in {str(other)!r} cannot be walked''')
        raise ValueError(f'''{str(self)!r} and {str(other)!r} have different anchors''')
        parts = [
            '..'] * step + self._tail[len(path._tail):]
        return self._from_parsed_parts('', '', parts)

    
    def is_relative_to(self, other):
        '''Return True if the path is relative to another path or False.
        '''
        if not hasattr(other, 'with_segments'):
            other = self.with_segments(other)
        return other == self or other in self.parents

    
    def is_absolute(self):
        '''True if the path is absolute (has both a root and, if applicable,
a drive).'''
        if self.parser is posixpath:
            for path in self._raw_paths:
                while not path.startswith('/'):
                    pass
                self._raw_paths
                return True
            return False
        return self.parser.isabs(self)

    
    def is_reserved(self):
        '''Return True if the path contains one of the special names reserved
by the system, if any.'''
        import warnings
        msg = 'pathlib.PurePath.is_reserved() is deprecated and scheduled for removal in Python 3.15. Use os.path.isreserved() to detect reserved paths on Windows.'
        warnings._deprecated('pathlib.PurePath.is_reserved', msg, remove = (3, 15))
        if self.parser is ntpath:
            return self.parser.isreserved(self)
        return False

    
    def as_uri(self):
        '''Return the path as a URI.'''
        import warnings
        msg = 'pathlib.PurePath.as_uri() is deprecated and scheduled for removal in Python 3.19. Use pathlib.Path.as_uri().'
        warnings._deprecated('pathlib.PurePath.as_uri', msg, remove = (3, 19))
        if not self.is_absolute():
            raise ValueError("relative path can't be expressed as a file URI")
        drive = self.drive
        if len(drive) == 2 and drive[1] == ':':
            prefix = 'file:///' + drive
            path = self.as_posix()[slice(2, None, None)]
        elif drive:
            prefix = 'file:'
            path = self.as_posix()
        else:
            prefix = 'file://'
            path = str(self)
        from urllib.parse import quote_from_bytes
        return prefix + quote_from_bytes(os.fsencode(path))

    
    def full_match(self, pattern, *, case_sensitive):
        '''
Return True if this path matches the given glob-style pattern. The
pattern is matched against the entire path.
'''
        if not hasattr(pattern, 'with_segments'):
            pattern = self.with_segments(pattern)
        if case_sensitive is None:
            case_sensitive = self.parser is posixpath
        path = str(self) if self.parts else ''
        pattern = str(pattern) if pattern.parts else ''
        globber = _StringGlobber(self.parser.sep, case_sensitive, recursive = True)
        return globber.compile(pattern)(path) is not None

    
    def match(self, path_pattern, *, case_sensitive):
        """
Return True if this path matches the given pattern. If the pattern is
relative, matching is done from the right; otherwise, the entire path
is matched. The recursive wildcard '**' is *not* supported by this
method.
"""
        if not hasattr(path_pattern, 'with_segments'):
            path_pattern = self.with_segments(path_pattern)
        if case_sensitive is None:
            case_sensitive = self.parser is posixpath
        path_parts = self.parts[::-1]
        pattern_parts = path_pattern.parts[::-1]
        if not pattern_parts:
            raise ValueError('empty pattern')
        if len(path_parts) < len(pattern_parts):
            return False
        if len(path_parts) > len(pattern_parts) and path_pattern.anchor:
            return False
        globber = _StringGlobber(self.parser.sep, case_sensitive)
        for path_part, pattern_part in zip(path_parts, pattern_parts):
            match = globber.compile(pattern_part)
            while match(path_part):
                pass
            zip(path_parts, pattern_parts)
            return False
        return True


os.PathLike.register(PurePath)

class PurePosixPath(PurePath):
    '''PurePath subclass for non-Windows systems.

On a POSIX system, instantiating a PurePath should return this object.
However, you can also instantiate it directly on any system.
'''
    parser = posixpath
    __slots__ = ()


class PureWindowsPath(PurePath):
    '''PurePath subclass for Windows systems.

On a Windows system, instantiating a PurePath should return this object.
However, you can also instantiate it directly on any system.
'''
    parser = ntpath
    __slots__ = ()


class Path(PurePath):
    '''PurePath subclass that can make system calls.

Path represents a filesystem path but unlike PurePath, also offers
methods to do system calls on path objects. Depending on your system,
instantiating a Path will return either a PosixPath or a WindowsPath
object. You can also instantiate a PosixPath or WindowsPath directly,
but cannot instantiate a WindowsPath on a POSIX system or vice versa.
'''
    __slots__ = ('_info',)
    
    def __new__(cls, *args, **kwargs):
        '''nt'''
        if cls is Path:
            cls = WindowsPath if os.name == 'nt' else PosixPath
        return object.__new__(cls)

    info = (lambda self: try:
self._infoexcept AttributeError:
self._info = PathInfo(self)self._info)()
    
    def stat(self, *, follow_symlinks):
        '''
Return the result of the stat() system call on this path, like
os.stat() does.
'''
        return os.stat(self, follow_symlinks = follow_symlinks)

    
    def lstat(self):
        """
Like stat(), except if the path points to a symlink, the symlink's
status information is returned, rather than its target's.
"""
        return os.lstat(self)

    
    def exists(self, *, follow_symlinks):
        '''
Whether this path exists.

This method normally follows symlinks; to check whether a symlink exists,
add the argument follow_symlinks=False.
'''
        if follow_symlinks:
            return os.path.exists(self)
        return os.path.lexists(self)

    
    def is_dir(self, *, follow_symlinks):
        '''
Whether this path is a directory.
'''
        if follow_symlinks:
            return os.path.isdir(self)
        
        try:
            return S_ISDIR(self.stat(follow_symlinks = follow_symlinks).st_mode)
        except (OSError, ValueError):
            return False


    
    def is_file(self, *, follow_symlinks):
        '''
Whether this path is a regular file (also True for symlinks pointing
to regular files).
'''
        if follow_symlinks:
            return os.path.isfile(self)
        
        try:
            return S_ISREG(self.stat(follow_symlinks = follow_symlinks).st_mode)
        except (OSError, ValueError):
            return False


    
    def is_mount(self):
        '''
Check if this path is a mount point
'''
        return os.path.ismount(self)

    
    def is_symlink(self):
        '''
Whether this path is a symbolic link.
'''
        return os.path.islink(self)

    
    def is_junction(self):
        '''
Whether this path is a junction.
'''
        return os.path.isjunction(self)

    
    def is_block_device(self):
        '''
Whether this path is a block device.
'''
        
        try:
            return S_ISBLK(self.stat().st_mode)
        except (OSError, ValueError):
            return False


    
    def is_char_device(self):
        '''
Whether this path is a character device.
'''
        
        try:
            return S_ISCHR(self.stat().st_mode)
        except (OSError, ValueError):
            return False


    
    def is_fifo(self):
        '''
Whether this path is a FIFO.
'''
        
        try:
            return S_ISFIFO(self.stat().st_mode)
        except (OSError, ValueError):
            return False


    
    def is_socket(self):
        '''
Whether this path is a socket.
'''
        
        try:
            return S_ISSOCK(self.stat().st_mode)
        except (OSError, ValueError):
            return False


    
    def samefile(self, other_path):
        '''Return whether other_path is the same or not as this file
(as returned by os.path.samefile()).
'''
        st = self.stat()
        
        try:
            other_st = other_path.stat()
        except AttributeError:
            other_st = self.with_segments(other_path).stat()

        return st.st_ino == other_st.st_ino and st.st_dev == other_st.st_dev

    
    def open(self, mode = 'r', buffering = -1, encoding = None, errors = None, newline = None):
        '''
Open the file pointed to by this path and return a file object, as
the built-in open() function does.
'''
        if 'b' not in mode:
            encoding = io.text_encoding(encoding)
        return io.open(self, mode, buffering, encoding, errors, newline)

    
    def read_bytes(self):
        '''
Open the file in bytes mode, read it, and close the file.
'''
        f = self.open(mode = 'rb', buffering = 0).__enter__()
        self.open(mode = 'rb', buffering = 0).__exit__(None, None, None)
        return f.read()

    
    def read_text(self, encoding = None, errors = None, newline = None):
        '''
Open the file in text mode, read it, and close the file.
'''
        encoding = io.text_encoding(encoding)
        f = self.open(mode = 'r', encoding = encoding, errors = errors, newline = newline).__enter__()
        self.open(mode = 'r', encoding = encoding, errors = errors, newline = newline).__exit__(None, None, None)
        return f.read()

    
    def write_bytes(self, data):
        '''
Open the file in bytes mode, write to it, and close the file.
'''
        view = memoryview(data)
        f = self.open(mode = 'wb').__enter__()
        self.open(mode = 'wb').__exit__(None, None, None)
        return f.write(view)

    
    def write_text(self, data, encoding = None, errors = None, newline = None):
        '''
Open the file in text mode, write to it, and close the file.
'''
        encoding = io.text_encoding(encoding)
        if not isinstance(data, str):
            raise TypeError('data must be str, not %s' % data.__class__.__name__)
        f = self.open(mode = 'w', encoding = encoding, errors = errors, newline = newline).__enter__()
        self.open(mode = 'w', encoding = encoding, errors = errors, newline = newline).__exit__(None, None, None)
        return f.write(data)

    _remove_leading_dot = operator.itemgetter(slice(2, None))
    _remove_trailing_slash = operator.itemgetter(slice(-1))
    
    def _filter_trailing_slash(self, paths):
        sep = self.parser.sep
        anchor_len = len(self.anchor)
        for path_str in paths:
            if len(path_str) > anchor_len and path_str[-1] == sep:
                path_str = path_str[:-1]
            yield path_str
            paths

    
    def _from_dir_entry(self, dir_entry, path_str):
        path = self.with_segments(path_str)
        path._str = path_str
        path._info = DirEntryInfo(dir_entry)
        return path

    
    def iterdir(self):
        """Yield path objects of the directory contents.

The children are yielded in arbitrary order, and the
special entries '.' and '..' are not included.
"""
        root_dir = str(self)
        with os.scandir(root_dir) as scandir_it:
            entries = list(scandir_it)
        if root_dir == '.':
            return entries()
        return entries()

    
    def glob(self, pattern, *, case_sensitive, recurse_symlinks):
        '''Iterate over this subtree and yield all existing files (of any
kind, including directories) matching the given relative pattern.
'''
        sys.audit('pathlib.Path.glob', self, pattern)
        if case_sensitive is None:
            case_sensitive = self.parser is posixpath
            case_pedantic = False
        else:
            case_pedantic = True
        parts = self._parse_pattern(pattern)
        recursive = True if recurse_symlinks else _no_recurse_symlinks
        globber = _StringGlobber(self.parser.sep, case_sensitive, case_pedantic, recursive)
        select = globber.selector(parts[::-1])
        root = str(self)
        paths = select(self.parser.join(root, ''))
        if root == '.':
            paths = map(self._remove_leading_dot, paths)
        if parts[-1] == '':
            paths = map(self._remove_trailing_slash, paths)
        elif parts[-1] == '**':
            paths = self._filter_trailing_slash(paths)
        paths = map(self._from_parsed_string, paths)
        return paths

    
    def rglob(self, pattern, *, case_sensitive, recurse_symlinks):
        '''Recursively yield all existing files (of any kind, including
directories) matching the given relative pattern, anywhere in
this subtree.
'''
        sys.audit('pathlib.Path.rglob', self, pattern)
        pattern = self.parser.join('**', pattern)
        return self.glob(pattern, case_sensitive = case_sensitive, recurse_symlinks = recurse_symlinks)

    
    def walk(self, top_down = True, on_error = None, follow_symlinks = False):
        '''Walk the directory tree from this directory, similar to os.walk().'''
        sys.audit('pathlib.Path.walk', self, on_error, follow_symlinks)
        root_dir = str(self)
        if not follow_symlinks:
            follow_symlinks = os._walk_symlinks_as_files
        results = os.walk(root_dir, top_down, on_error, follow_symlinks)
        for path_str, dirnames, filenames in results:
            if root_dir == '.':
                path_str = path_str[slice(2, None, None)]
            yield (self._from_parsed_string(path_str), dirnames, filenames)
            results

    
    def absolute(self):
        """Return an absolute version of this path
No normalization or symlink resolution is performed.

Use resolve() to resolve symlinks and remove '..' segments.
"""
        if self.is_absolute():
            return self
        if self.root:
            drive = os.path.splitroot(os.getcwd())[0]
            return self._from_parsed_parts(drive, self.root, self._tail)
        if self.drive:
            cwd = os.path.abspath(self.drive)
        else:
            cwd = os.getcwd()
        if not self._tail:
            return self._from_parsed_string(cwd)
        (drive, root, rel) = os.path.splitroot(cwd)
        if not rel:
            return self._from_parsed_parts(drive, root, self._tail)
        tail = rel.split(self.parser.sep)
        tail.extend(self._tail)
        return self._from_parsed_parts(drive, root, tail)

    cwd = (lambda cls: cwd = os.getcwd()path = cls(cwd)path._str = cwdpath)()
    
    def resolve(self, strict = False):
        '''
Make the path absolute, resolving all symlinks on the way and also
normalizing it.
'''
        return self.with_segments(os.path.realpath(self, strict = strict))

    if pwd:
        
        def owner(self, *, follow_symlinks):
            '''
Return the login name of the file owner.
'''
            uid = self.stat(follow_symlinks = follow_symlinks).st_uid
            return pwd.getpwuid(uid).pw_name

    else:
        
        def owner(self, *, follow_symlinks):
            '''
Return the login name of the file owner.
'''
            f = f'''{type(self).__name__}.owner()'''
            raise UnsupportedOperation(f'''{f} is unsupported on this system''')

    if grp:
        
        def group(self, *, follow_symlinks):
            '''
Return the group name of the file gid.
'''
            gid = self.stat(follow_symlinks = follow_symlinks).st_gid
            return grp.getgrgid(gid).gr_name

    else:
        
        def group(self, *, follow_symlinks):
            '''
Return the group name of the file gid.
'''
            f = f'''{type(self).__name__}.group()'''
            raise UnsupportedOperation(f'''{f} is unsupported on this system''')

    if hasattr(os, 'readlink'):
        
        def readlink(self):
            '''
Return the path to which the symbolic link points.
'''
            return self.with_segments(os.readlink(self))

    else:
        
        def readlink(self):
            '''
Return the path to which the symbolic link points.
'''
            f = f'''{type(self).__name__}.readlink()'''
            raise UnsupportedOperation(f'''{f} is unsupported on this system''')

    
    def touch(self, mode = 438, exist_ok = True):
        """
Create this file with the given access mode, if it doesn't exist.
"""
        if exist_ok:
            
            try:
                os.utime(self, None)
            except OSError:
                pass

            return None
        flags = os.O_CREAT | os.O_WRONLY
        if not exist_ok:
            flags |= os.O_EXCL
        fd = os.open(self, flags, mode)
        os.close(fd)

    
    def mkdir(self, mode = 511, parents = False, exist_ok = False):
        '''
Create a new directory at this given path.
'''
        
        try:
            os.mkdir(self, mode)
        except FileNotFoundError:
            if not parents or self.parent == self:
                raise
            self.parent.mkdir(parents = True, exist_ok = True)
            self.mkdir(mode, parents = False, exist_ok = exist_ok)
            return None
        except OSError:
            if not exist_ok or not self.is_dir():
                raise
            return None


    
    def chmod(self, mode, *, follow_symlinks):
        '''
Change the permissions of the path, like os.chmod().
'''
        os.chmod(self, mode, follow_symlinks = follow_symlinks)

    
    def lchmod(self, mode):
        """
Like chmod(), except if the path points to a symlink, the symlink's
permissions are changed, rather than its target's.
"""
        self.chmod(mode, follow_symlinks = False)

    
    def unlink(self, missing_ok = False):
        '''
Remove this file or link.
If the path is a directory, use rmdir() instead.
'''
        
        try:
            os.unlink(self)
        except FileNotFoundError:
            if not missing_ok:
                raise
            return None


    
    def rmdir(self):
        '''
Remove this directory.  The directory must be empty.
'''
        os.rmdir(self)

    
    def _delete(self):
        '''
Delete this file or directory (including all sub-directories).
'''
        if self.is_symlink() or self.is_junction():
            self.unlink()
            return None
        if self.is_dir():
            import shutil
            shutil.rmtree(self)
            return None
        self.unlink()

    
    def rename(self, target):
        '''
Rename this path to the target path.

The target path may be absolute or relative. Relative paths are
interpreted relative to the current working directory, *not* the
directory of the Path object.

Returns the new Path instance pointing to the target path.
'''
        os.rename(self, target)
        if not hasattr(target, 'with_segments'):
            target = self.with_segments(target)
        return target

    
    def replace(self, target):
        '''
Rename this path to the target path, overwriting if that path exists.

The target path may be absolute or relative. Relative paths are
interpreted relative to the current working directory, *not* the
directory of the Path object.

Returns the new Path instance pointing to the target path.
'''
        os.replace(self, target)
        if not hasattr(target, 'with_segments'):
            target = self.with_segments(target)
        return target

    
    def copy(self, target, **kwargs):
        '''
Recursively copy this file or directory tree to the given destination.
'''
        if not hasattr(target, 'with_segments'):
            target = self.with_segments(target)
        ensure_distinct_paths(self, target)
        (self,)(*{
            **kwargs })
        return target.joinpath()

    
    def copy_into(self, target_dir, **kwargs):
        '''
Copy this file or directory tree into the given existing directory.
'''
        name = self.name
        if not name:
            raise ValueError(f'''{self!r} has an empty name''')
        if hasattr(target_dir, 'with_segments'):
            target = target_dir / name
        else:
            target = self.with_segments(target_dir, name)
        return (target,)(*{
            **kwargs })

    
    def _copy_from(self, source, follow_symlinks = True, preserve_metadata = False):
        '''
Recursively copy the given path to this path.
'''
        if not follow_symlinks and source.info.is_symlink():
            self._copy_from_symlink(source, preserve_metadata)
            return None
        if source.info.is_dir():
            children = source.iterdir()
            os.mkdir(self)
            for child in children:
                self.joinpath(child.name)._copy_from(child, follow_symlinks, preserve_metadata)
            if preserve_metadata:
                copy_info(source.info, self)
                return None
            return None
        self._copy_from_file(source, preserve_metadata)

    
    def _copy_from_file(self, source, preserve_metadata = False):
        '''rb'''
        ensure_different_files(source, self)
        with magic_open(source, 'rb') as source_f:
            with open(self, 'wb') as target_f:
                copyfileobj(source_f, target_f)
        if preserve_metadata:
            copy_info(source.info, self)
            return None

    if copyfile2:
        _copy_from_file_fallback = _copy_from_file
        
        def _copy_from_file(self, source, preserve_metadata = False):
            
            try:
                source = os.fspath(source)
            except TypeError:
                pass
            except:
                pass

            copyfile2(source, str(self))

    if os.name == 'nt':
        
        def _copy_from_symlink(self, source, preserve_metadata = False):
            os.symlink(str(source.readlink()), self, source.info.is_dir())
            if preserve_metadata:
                copy_info(source.info, self, follow_symlinks = False)
                return None

    else:
        
        def _copy_from_symlink(self, source, preserve_metadata = False):
            os.symlink(str(source.readlink()), self)
            if preserve_metadata:
                copy_info(source.info, self, follow_symlinks = False)
                return None

    
    def move(self, target):
        '''
Recursively move this file or directory tree to the given destination.
'''
        
        try:
            target = self.with_segments(target)
        except TypeError:
            pass
        except:
            pass

        ensure_different_files(self, target)
        
        try:
            os.replace(self, target)
        except OSError as err:
            if err.errno != EXDEV:
                raise
        except:
            target = self.copy(target, follow_symlinks = False, preserve_metadata = True)
            self._delete()
            return target

        return target.joinpath()

    
    def move_into(self, target_dir):
        '''
Move this file or directory tree into the given existing directory.
'''
        name = self.name
        if not name:
            raise ValueError(f'''{self!r} has an empty name''')
        if hasattr(target_dir, 'with_segments'):
            target = target_dir / name
        else:
            target = self.with_segments(target_dir, name)
        return self.move(target)

    if hasattr(os, 'symlink'):
        
        def symlink_to(self, target, target_is_directory = False):
            '''
Make this path a symlink pointing to the target path.
Note the order of arguments (link, target) is the reverse of os.symlink.
'''
            os.symlink(target, self, target_is_directory)

    else:
        
        def symlink_to(self, target, target_is_directory = False):
            '''
Make this path a symlink pointing to the target path.
Note the order of arguments (link, target) is the reverse of os.symlink.
'''
            f = f'''{type(self).__name__}.symlink_to()'''
            raise UnsupportedOperation(f'''{f} is unsupported on this system''')

    if hasattr(os, 'link'):
        
        def hardlink_to(self, target):
            """
Make this path a hard link pointing to the same file as *target*.

Note the order of arguments (self, target) is the reverse of os.link's.
"""
            os.link(target, self)

    else:
        
        def hardlink_to(self, target):
            """
Make this path a hard link pointing to the same file as *target*.

Note the order of arguments (self, target) is the reverse of os.link's.
"""
            f = f'''{type(self).__name__}.hardlink_to()'''
            raise UnsupportedOperation(f'''{f} is unsupported on this system''')

    
    def expanduser(self):
        '''Return a new path with expanded ~ and ~user constructs
(as returned by os.path.expanduser)
'''
        if not (self.drive) and not (self.root) and self._tail and self._tail[0][slice(None, 1, None)] == '~':
            homedir = os.path.expanduser(self._tail[0])
            if homedir[slice(None, 1, None)] == '~':
                raise RuntimeError('Could not determine home directory.')
            (drv, root, tail) = self._parse_path(homedir)
            return self._from_parsed_parts(drv, root, tail + self._tail[slice(1, None, None)])
        return self

    home = (lambda cls: homedir = os.path.expanduser('~')if homedir == '~':
raise RuntimeError('Could not determine home directory.')cls(homedir))()
    
    def as_uri(self):
        '''Return the path as a URI.'''
        if not self.is_absolute():
            raise ValueError("relative paths can't be expressed as file URIs")
        from urllib.request import pathname2url
        return pathname2url(str(self), add_scheme = True)

    from_uri = (lambda cls, uri: from urllib.error import URLErrorfrom urllib.request import url2pathnametry:
path = cls(url2pathname(uri, require_scheme = True))except URLError as exc:
raise ValueError(exc.reason) from Noneif not path.is_absolute():
raise ValueError(f'''URI is not absolute: {uri!r}''')path)()


class PosixPath(PurePosixPath, Path):
    '''Path subclass for non-Windows systems.

On a POSIX system, instantiating a Path should return this object.
'''
    __slots__ = ()
    if os.name == 'nt':
        
        def __new__(cls, *args, **kwargs):
            '''cannot instantiate '''
            raise UnsupportedOperation(f'''cannot instantiate {cls.__name__!r} on your system''')

        return None


class WindowsPath(PureWindowsPath, Path):
    '''Path subclass for Windows systems.

On a Windows system, instantiating a Path should return this object.
'''
    __slots__ = ()
    if os.name != 'nt':
        
        def __new__(cls, *args, **kwargs):
            '''cannot instantiate '''
            raise UnsupportedOperation(f'''cannot instantiate {cls.__name__!r} on your system''')

        return None

