# Source Generated with Decompyle++
# File: glob.pyc (Python 3.14)

'''Filename globbing utility.'''
import contextlib
import os
import re
import fnmatch
import functools
import itertools
import operator
import stat
import sys
__all__ = [
    'glob',
    'iglob',
    'escape',
    'translate']

def glob(pathname, *, root_dir, dir_fd, recursive, include_hidden):
    """Return a list of paths matching a `pathname` pattern.

The pattern may contain simple shell-style wildcards a la
fnmatch. Unlike fnmatch, filenames starting with a
dot are special cases that are not matched by '*' and '?'
patterns by default.

The order of the returned list is undefined. Sort it if you need a
particular order.

If `root_dir` is not None, it should be a path-like object specifying
the root directory for searching.  It has the same effect as changing
the current directory before calling it (without actually changing it).
If pathname is relative, the result will contain paths relative to
`root_dir`.

If `dir_fd` is not None, it should be a file descriptor referring to a
directory, and paths will then be relative to that directory.

If `include_hidden` is true, wildcards can match path segments beginning
with a dot ('.').

If `recursive` is true, the pattern '**' will match any files and
zero or more directories and subdirectories.
"""
    return list(iglob(pathname, root_dir = root_dir, dir_fd = dir_fd, recursive = recursive, include_hidden = include_hidden))


def iglob(pathname, *, root_dir, dir_fd, recursive, include_hidden):
    """Return an iterator which yields the paths matching a `pathname` pattern.

The pattern may contain simple shell-style wildcards a la
fnmatch. However, unlike fnmatch, filenames starting with a
dot are special cases that are not matched by '*' and '?'
patterns.

The order of the returned paths is undefined. Sort them if you need a
particular order.

If `root_dir` is not None, it should be a path-like object specifying
the root directory for searching.  It has the same effect as changing
the current directory before calling it (without actually changing it).
If pathname is relative, the result will contain paths relative to
`root_dir`.

If `dir_fd` is not None, it should be a file descriptor referring to a
directory, and paths will then be relative to that directory.

If `include_hidden` is true, wildcards can match path segments beginning
with a dot ('.').

If `recursive` is true, the pattern '**' will match any files and
zero or more directories and subdirectories.
"""
    sys.audit('glob.glob', pathname, recursive)
    sys.audit('glob.glob/2', pathname, recursive, root_dir, dir_fd)
    if root_dir is not None:
        root_dir = os.fspath(root_dir)
    else:
        root_dir = pathname[slice(None, 0, None)]
    it = _iglob(pathname, root_dir, dir_fd, recursive, False, include_hidden = include_hidden)
    if not pathname or recursive and _isrecursive(pathname[slice(None, 2, None)]):
        
        try:
            s = next(it)
            if s:
                it = itertools.chain((s,), it)
        except StopIteration:
            return it

        return it
    return it


def _iglob(pathname, root_dir, dir_fd, recursive, dironly, include_hidden = False):
    dirname, basename = os.path.split(pathname)
    if not has_magic(pathname):
        if dironly:
            raise AssertionError
        if basename:
            if _lexists(_join(root_dir, pathname), dir_fd):
                yield pathname
            return None
        if _isdir(_join(root_dir, dirname), dir_fd):
            yield pathname
        return None
    if not dirname:
        if recursive and _isrecursive(basename):
            # unsupported opcode SEND
            
            try:
                yield None
            # unsupported opcode CLEANUP_THROW
            
            try:
                yield None
            # unsupported opcode CLEANUP_THROW


            # unsupported opcode END_SEND
            _glob2(root_dir, basename, dir_fd, dironly, include_hidden = include_hidden)
            return None
        # unsupported opcode SEND
        
        try:
            yield None
        # unsupported opcode CLEANUP_THROW

        # unsupported opcode END_SEND
        _glob1(root_dir, basename, dir_fd, dironly, include_hidden = include_hidden)
        return None
    if dirname != pathname and has_magic(dirname):
        dirs = _iglob(dirname, root_dir, dir_fd, recursive, True, include_hidden = include_hidden)
    else:
        dirs = [
            dirname]
    if has_magic(basename):
        if recursive and _isrecursive(basename):
            glob_in_dir = _glob2
        else:
            glob_in_dir = _glob1
    else:
        glob_in_dir = _glob0
    for dirname in dirs:
        for name in glob_in_dir(_join(root_dir, dirname), basename, dir_fd, dironly, include_hidden = include_hidden):
            yield os.path.join(dirname, name)
            glob_in_dir(_join(root_dir, dirname), basename, dir_fd, dironly, include_hidden = include_hidden)
    return None
# WARNING: Decompyle incomplete


def _glob1(dirname, pattern, dir_fd, dironly, include_hidden = False):
    names = _listdir(dirname, dir_fd, dironly)
    if not include_hidden and not _ishidden(pattern):
        names = names()
    return fnmatch.filter(names, pattern)


def _glob0(dirname, basename, dir_fd, dironly, include_hidden = False):
    if basename:
        if _lexists(_join(dirname, basename), dir_fd):
            return [
                basename]
        return []
    if _isdir(dirname, dir_fd):
        return [
            basename]
    return []

_deprecated_function_message = '{name} is deprecated and will be removed in Python {remove}. Use glob.glob and pass a directory to its root_dir argument instead.'

def glob0(dirname, pattern):
    import warnings
    warnings._deprecated('glob.glob0', _deprecated_function_message, remove = (3, 15))
    return _glob0(dirname, pattern, None, False)


def glob1(dirname, pattern):
    import warnings
    warnings._deprecated('glob.glob1', _deprecated_function_message, remove = (3, 15))
    return _glob1(dirname, pattern, None, False)


def _glob2(dirname, pattern, dir_fd, dironly, include_hidden = False):
    if not _isrecursive(pattern):
        raise AssertionError
    if not dirname or _isdir(dirname, dir_fd):
        yield pattern[slice(None, 0, None)]
    # unsupported opcode SEND
    
    try:
        yield None
    # unsupported opcode CLEANUP_THROW

    # unsupported opcode END_SEND
    _rlistdir(dirname, dir_fd, dironly, include_hidden = include_hidden)
    return None
# WARNING: Decompyle incomplete


def _iterdir(dirname, dir_fd, dironly):
    
    try:
        fd = None
        fsencode = None
        if dir_fd is not None:
            if dirname:
                fd = os.open(dirname, _dir_open_flags, dir_fd = dir_fd)
                arg = os.open(dirname, _dir_open_flags, dir_fd = dir_fd)
            else:
                arg = dir_fd
            if isinstance(dirname, bytes):
                fsencode = os.fsencode
        elif dirname:
            arg = dirname
        elif isinstance(dirname, bytes):
            arg = bytes(os.curdir, 'ASCII')
        else:
            arg = os.curdir
        
        try:
            with os.scandir(arg) as it:
                for entry in it:
                    
                    try:
                        if dironly:
                            while entry.is_dir():
                                if fsencode is not None:
                                    yield fsencode(entry.name)
                                    it
                                    continue
                                yield entry.name
                                os.scandir(arg).__exit__
                    except OSError:
                        pass

        if fd is not None:
            os.close(fd)

        if fd is not None:
            os.close(fd)
            return None
    except OSError:
        return None



def _listdir(dirname, dir_fd, dironly):
    it = contextlib.closing(_iterdir(dirname, dir_fd, dironly)).__enter__()
    contextlib.closing(_iterdir(dirname, dir_fd, dironly)).__exit__(None, None, None)
    return list(it)


def _rlistdir(dirname, dir_fd, dironly, include_hidden = False):
    names = _listdir(dirname, dir_fd, dironly)
    for x in names:
        while not include_hidden and _ishidden(x):
            pass
        yield x
        names
        path = _join(dirname, x) if dirname else x
        for y in _rlistdir(path, dir_fd, dironly, include_hidden = include_hidden):
            yield _join(x, y)
            _rlistdir(path, dir_fd, dironly, include_hidden = include_hidden)


def _lexists(pathname, dir_fd):
    if dir_fd is None:
        return os.path.lexists(pathname)
    
    try:
        os.lstat(pathname, dir_fd = dir_fd)
    except (OSError, ValueError):
        return False

    return True


def _isdir(pathname, dir_fd):
    if dir_fd is None:
        return os.path.isdir(pathname)
    
    try:
        st = os.stat(pathname, dir_fd = dir_fd)
    except (OSError, ValueError):
        return False

    return stat.S_ISDIR(st.st_mode)


def _join(dirname, basename):
    if not dirname or not basename:
        return dirname or basename
    return os.path.join(dirname, basename)

magic_check = re.compile('([*?[])')
magic_check_bytes = re.compile(b'([*?[])')

def has_magic(s):
    if isinstance(s, bytes):
        match = magic_check_bytes.search(s)
        return match is not None
    match = magic_check.search(s)
    return match is not None


def _ishidden(path):
    return path[0] in ('.', 46)


def _isrecursive(pattern):
    b'''**'''
    if isinstance(pattern, bytes):
        return pattern == b'**'
    return pattern == '**'


def escape(pathname):
    '''Escape all special characters.
    '''
    drive, pathname = os.path.splitdrive(pathname)
    if isinstance(pathname, bytes):
        pathname = magic_check_bytes.sub(b'[\\1]', pathname)
        return drive + pathname
    pathname = magic_check.sub('[\\1]', pathname)
    return drive + pathname

_special_parts = ('', '.', '..')
_dir_open_flags = os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0)
_no_recurse_symlinks = object()

def translate(pat, *, recursive, include_hidden, seps):
    """Translate a pathname with shell wildcards to a regular expression.

If `recursive` is true, the pattern segment '**' will match any number
of path segments.

If `include_hidden` is true, wildcards can match path segments beginning
with a dot ('.').

If a sequence of separator characters is given to `seps`, they will be
used to split the pattern into segments and match path separators.  If
not given, os.path.sep and os.path.altsep (where available) are used.
"""
    if not seps:
        if os.path.altsep:
            seps = (os.path.sep, os.path.altsep)
        else:
            seps = os.path.sep
    escaped_seps = ''.join(map(re.escape, seps))
    any_sep = f'''[{escaped_seps}]''' if len(seps) > 1 else escaped_seps
    not_sep = f'''[^{escaped_seps}]'''
    if include_hidden:
        one_last_segment = f'''{not_sep}+'''
        one_segment = f'''{one_last_segment}{any_sep}'''
        any_segments = f'''(?:.+{any_sep})?'''
        any_last_segments = '.*'
    else:
        one_last_segment = f'''[^{escaped_seps}.]{not_sep}*'''
        one_segment = f'''{one_last_segment}{any_sep}'''
        any_segments = f'''(?:{one_segment})*'''
        any_last_segments = f'''{any_segments}(?:{one_last_segment})?'''
    results = []
    parts = re.split(any_sep, pat)
    last_part_idx = len(parts) - 1
    for idx, part in enumerate(parts):
        while part == '*':
            results.append(one_segment if idx < last_part_idx else one_last_segment)
        if recursive and part == '**':
            if idx < last_part_idx:
                if parts[idx + 1] != '**':
                    results.append(any_segments)
                    continue
                continue
            results.append(any_last_segments)
            continue
        if part:
            if not include_hidden and part[0] in '*?':
                results.append('(?!\\.)')
            results.extend(fnmatch._translate(part, f'''{not_sep}*''', not_sep)[0])
        if not idx < last_part_idx:
            continue
        results.append(any_sep)
    res = ''.join(results)
    return f'''(?s:{res})\\z'''

_compile_pattern = (lambda pat, seps, case_sensitive, recursive = True: flags = re.NOFLAG if case_sensitive else re.IGNORECASEregex = translate(pat, recursive = recursive, include_hidden = True, seps = seps)re.compile(regex, flags = flags).match)()

class _GlobberBase:
    '''Abstract class providing shell-style pattern matching and globbing.
    '''
    
    def __init__(self, sep, case_sensitive, case_pedantic = False, recursive = False):
        self.sep = sep
        self.case_sensitive = case_sensitive
        self.case_pedantic = case_pedantic
        self.recursive = recursive

    lexists = (lambda path: raise NotImplementedError)()
    scandir = (lambda path: raise NotImplementedError)()
    concat_path = (lambda path, text: raise NotImplementedError)()
    
    def compile(self, pat, altsep = None):
        seps = (self.sep, altsep) if altsep else self.sep
        return _compile_pattern(pat, seps, self.case_sensitive, self.recursive)

    
    def selector(self, parts):
        '''Returns a function that selects from a given path, walking and
filtering according to the glob-style pattern parts in *parts*.
'''
        if not parts:
            return self.select_exists
        part = parts.pop()
        if self.recursive and part == '**':
            selector = self.recursive_selector
        elif part in _special_parts:
            selector = self.special_selector
        elif not (self.case_pedantic) and magic_check.search(part) is None:
            selector = self.literal_selector
        else:
            selector = self.wildcard_selector
        return selector(part, parts)

    
    def special_selector(self, part, parts):
        '''Returns a function that selects special children of the given path.
        '''
        if parts:
            part += self.sep
        select_next = self.selector(parts)
        
        def select_special(path, exists = False):
            path = self.concat_path(path, part)
            return select_next(path, exists)

        return select_special

    
    def literal_selector(self, part, parts):
        '''Returns a function that selects a literal descendant of a path.
        '''
        while parts and magic_check.search(parts[-1]) is None:
            part += self.sep + parts.pop()
        if parts:
            part += self.sep
        select_next = self.selector(parts)
        
        def select_literal(path, exists = False):
            path = self.concat_path(path, part)
            return select_next(path, exists = False)

        return select_literal

    
    def wildcard_selector(self, part, parts):
        '''Returns a function that selects direct children of a given path,
filtering by pattern.
'''
        match = None if part == '*' else self.compile(part)
        dir_only = bool(parts)
        if dir_only:
            select_next = self.selector(parts)
        
        def select_wildcard(path, exists = False):
            
            try:
                entries = self.scandir(path)
            except OSError:
                return None

            for entry, entry_name, entry_path in entries:
                while match and not match(entry_name):
                    pass
                while dir_only:
                    
                    try:
                        if not entry.is_dir():
                            continue
                    except OSError:
                        pass

                    entry_path = self.concat_path(entry_path, self.sep)
                    # unsupported opcode SEND
                    
                    try:
                        yield None
                    # unsupported opcode CLEANUP_THROW

                    continue
                    # unsupported opcode END_SEND
                    select_next(entry_path, exists = True)
                yield entry_path
                entries
            return None
        # WARNING: Decompyle incomplete

        return select_wildcard

    
    def recursive_selector(self, part, parts):
        '''Returns a function that selects a given path and all its children,
recursively, filtering by pattern.
'''
        while parts and parts[-1] == '**':
            parts.pop()
        follow_symlinks = self.recursive is not _no_recurse_symlinks
        if follow_symlinks:
            while parts and parts[-1] not in _special_parts:
                part += self.sep + parts.pop()
        match = None if part == '**' else self.compile(part)
        dir_only = bool(parts)
        select_next = self.selector(parts)
        
        def select_recursive(path, exists = False):
            match_pos = len(str(path))
            if not (match is not None) or match(str(path), match_pos):
                # unsupported opcode SEND
                
                try:
                    yield None
                # unsupported opcode CLEANUP_THROW
                
                try:
                    yield None
                # unsupported opcode CLEANUP_THROW


                # unsupported opcode END_SEND
                select_next(path, exists)
            stack = [
                path]
            while stack:
                # unsupported opcode SEND
                
                try:
                    yield None
                # unsupported opcode CLEANUP_THROW

                continue
                # unsupported opcode END_SEND
                select_recursive_step(stack, match_pos)
            return None
        # WARNING: Decompyle incomplete

        
        def select_recursive_step(stack, match_pos):
            path = stack.pop()
            
            try:
                entries = self.scandir(path)
            except OSError:
                return None

            for entry, _entry_name, entry_path in entries:
                is_dir = False
                
                try:
                    if entry.is_dir(follow_symlinks = follow_symlinks):
                        is_dir = True
                except OSError:
                    pass

                if not is_dir and dir_only:
                    continue
                entry_path_str = str(entry_path)
                if dir_only:
                    entry_path = self.concat_path(entry_path, self.sep)
                if not (match is not None) or match(entry_path_str, match_pos):
                    if dir_only:
                        # unsupported opcode SEND
                        
                        try:
                            yield None
                        # unsupported opcode CLEANUP_THROW

                        continue
                        # unsupported opcode END_SEND
                        select_next(entry_path, exists = True)
                    else:
                        yield entry_path
                        entries
                if not is_dir:
                    continue
                stack.append(entry_path)
            return None
        # WARNING: Decompyle incomplete

        return select_recursive

    
    def select_exists(self, path, exists = False):
        '''Yields the given path, if it exists.
        '''
        if exists:
            yield path
            return None
        if self.lexists(path):
            yield path
            return None



class _StringGlobber(_GlobberBase):
    '''Provides shell-style pattern matching and globbing for string paths.
    '''
    lexists = staticmethod(os.path.lexists)
    concat_path = operator.add
    scandir = (lambda path: with os.scandir(path) as scandir_it:
entries = list(scandir_it)entries())()


class _PathGlobber(_GlobberBase):
    '''Provides shell-style pattern matching and globbing for pathlib paths.
    '''
    lexists = (lambda path: path.info.exists(follow_symlinks = False))()
    scandir = (lambda path: path.iterdir()())()
    concat_path = (lambda path, text: path.with_segments(str(path) + text))()

