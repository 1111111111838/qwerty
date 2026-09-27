# Source Generated with Decompyle++
# File: __init__.pyc (Python 3.14)

from __future__ import annotations
import os
import re
import abc
import sys
import json
import email
import types
import inspect
import pathlib
import zipfile
import operator
import textwrap
import warnings
import functools
import itertools
import posixpath
import collections
from . import _meta
from ._collections import FreezableDefaultDict, Pair
from ._functools import method_cache, pass_none
from ._itertools import always_iterable, unique_everseen
from ._meta import PackageMetadata, SimplePath
from contextlib import suppress
from importlib import import_module
from importlib.abc import MetaPathFinder
from itertools import starmap
from typing import Any, Iterable, List, Mapping, Match, Optional, Set, cast
__all__ = [
    'Distribution',
    'DistributionFinder',
    'PackageMetadata',
    'PackageNotFoundError',
    'distribution',
    'distributions',
    'entry_points',
    'files',
    'metadata',
    'packages_distributions',
    'requires',
    'version']

class PackageNotFoundError(ModuleNotFoundError):
    '''The package was not found.'''
    
    def __str__(self):
        '''No package metadata was found for '''
        return f'''No package metadata was found for {self.name}'''

    name = (lambda self: (name,) = self.argsname)()


class Sectioned:
    """
A simple entry point config parser for performance

>>> for item in Sectioned.read(Sectioned._sample):
...     print(item)
Pair(name='sec1', value='# comments ignored')
Pair(name='sec1', value='a = 1')
Pair(name='sec1', value='b = 2')
Pair(name='sec2', value='a = 2')

>>> res = Sectioned.section_pairs(Sectioned._sample)
>>> item = next(res)
>>> item.name
'sec1'
>>> item.value
Pair(name='a', value='1')
>>> item = next(res)
>>> item.value
Pair(name='b', value='2')
>>> item = next(res)
>>> item.name
'sec2'
>>> item.value
Pair(name='a', value='2')
>>> list(res)
[]
"""
    _sample = textwrap.dedent('\n        [sec1]\n        # comments ignored\n        a = 1\n        b = 2\n\n        [sec2]\n        a = 2\n        ').lstrip()
    section_pairs = (lambda cls, text: cls.read(text, filter_ = cls.valid)())()
    read = (lambda text, filter_ = None: lines = filter(filter_, map(str.strip, text.splitlines()))name = Nonefor value in lines:
section_match = value.startswith('[') and value.endswith(']')if section_match:
name = value.strip('[]')continuePair(name, value)lines)()
    valid = (lambda line: line and not line.startswith('#'))()


class EntryPoint:
    """An entry point as defined by Python packaging conventions.

See `the packaging docs on entry points
<https://packaging.python.org/specifications/entry-points/>`_
for more information.

>>> ep = EntryPoint(
...     name=None, group=None, value='package.module:attr [extra1, extra2]')
>>> ep.module
'package.module'
>>> ep.attr
'attr'
>>> ep.extras
['extra1', 'extra2']
"""
    group: 'str' = re.compile('(?P<module>[\\w.]+)\\s*(:\\s*(?P<attr>[\\w.]+)\\s*)?((?P<extras>\\[.*\\])\\s*)?$')
    dist: 'Optional[Distribution]' = None
    
    def __init__(self, name, value, group):
        vars(self).update(name = name, value = value, group = group)

    
    def load(self):
        '''Load the entry point from its definition. If only a module
is indicated by the value, return that module. Otherwise,
return the named object.
'''
        match = cast(Match, self.pattern.match(self.value))
        module = import_module(match.group('module'))
        attrs = filter(None, (match.group('attr') or '').split('.'))
        return functools.reduce(getattr, attrs, module)

    module = (lambda self: match = self.pattern.match(self.value)if match is None:
raise AssertionErrormatch.group('module'))()
    attr = (lambda self: match = self.pattern.match(self.value)if match is None:
raise AssertionErrormatch.group('attr'))()
    extras = (lambda self: match = self.pattern.match(self.value)if match is None:
raise AssertionErrorre.findall('\\w+', match.group('extras') or ''))()
    
    def _for(self, dist):
        vars(self).update(dist = dist)
        return self

    
    def matches(self, **params):
        """
EntryPoint matches the given parameters.

>>> ep = EntryPoint(group='foo', name='bar', value='bing:bong [extra1, extra2]')
>>> ep.matches(group='foo')
True
>>> ep.matches(name='bar', value='bing:bong [extra1, extra2]')
True
>>> ep.matches(group='foo', name='other')
False
>>> ep.matches()
True
>>> ep.matches(extras=['extra1', 'extra2'])
True
>>> ep.matches(module='bing')
True
>>> ep.matches(attr='bong')
True
"""
        attrs = params()
        return all(map(operator.eq, params.values(), attrs))

    
    def _key(self):
        return (self.name, self.value, self.group)

    
    def __lt__(self, other):
        return self._key() < other._key()

    
    def __eq__(self, other):
        return self._key() == other._key()

    
    def __setattr__(self, name, value):
        '''EntryPoint objects are immutable.'''
        raise AttributeError('EntryPoint objects are immutable.')

    
    def __repr__(self):
        '''EntryPoint(name='''
        return f'''EntryPoint(name={self.name!r}, value={self.value!r}, group={self.group!r})'''

    
    def __hash__(self):
        return hash(self._key())



class EntryPoints(tuple):
    '''
An immutable collection of selectable EntryPoint objects.
'''
    __slots__ = ()
    
    def __getitem__(self, name):
        '''
Get the EntryPoint in self matching name.
'''
        
        try:
            return next(iter(self.select(name = name)))
        except StopIteration:
            raise KeyError(name)


    
    def __repr__(self):
        '''
Repr with classname and tuple constructor to
signal that we deviate from regular tuple behavior.
'''
        return f'''{self.__class__.__name__!s}({tuple(self)!r})'''

    
    def select(self, **params):
        '''
Select entry points from self that match the
given parameters (typically group and/or name).
'''
        return (lambda .0: for ep in .0:
while not ()(*{
**params }):
passepep.matches)(self())

    names = (lambda self: None# WARNING: Decompyle incomplete
)()
    groups = (lambda self: None# WARNING: Decompyle incomplete
)()
    _from_text_for = (lambda cls, text, dist: (lambda .0: for ep in .0:
ep._for(dist).0)(cls._from_text(text)())
)()
    _from_text = (lambda text: Sectioned.section_pairs(text or '')())()


class PackagePath(pathlib.PurePosixPath):
    dist: 'Distribution' = 'A reference to a path in a package'
    
    def read_text(self, encoding = 'utf-8'):
        return self.locate().read_text(encoding = encoding)

    
    def read_binary(self):
        return self.locate().read_bytes()

    
    def locate(self):
        '''Return a path-like object for this path'''
        return self.dist.locate_file(self)



class FileHash:
    
    def __init__(self, spec):
        '''='''
        _ = (self.mode,)
        return None
    # WARNING: Decompyle incomplete

    
    def __repr__(self):
        '''<FileHash mode: '''
        return f'''<FileHash mode: {self.mode} value: {self.value}>'''



class DeprecatedNonAbstract:
    
    def __new__(cls, *args, **kwargs):
        '''__isabstractmethod__'''
        
        try:
            for subclass in inspect.getmro(cls):
                for name in vars(subclass):
                    pass
        name = all_names
        subclass = None
        
        try:
            for name in all_names:
                while not getattr(getattr(cls, name), '__isabstractmethod__', False):
                    pass
        name = name


        all_names = name
        subclass = None
        name = None
        
        try:
            for name in all_names:
                while not getattr(getattr(cls, name), '__isabstractmethod__', False):
                    pass
        name = name

        abstract = name
        name = None
        if abstract:
            warnings.warn(f'''Unimplemented abstract methods {abstract}''', DeprecationWarning, stacklevel = 2)
        # unsupported opcode LOAD_SUPER_ATTR
        return cls(cls)
    # WARNING: Decompyle incomplete



class Distribution(DeprecatedNonAbstract):
    '''
An abstract Python distribution package.

Custom providers may derive from this class and define
the abstract methods to provide a concrete implementation
for their environment. Some providers may opt to override
the default implementation of some properties to bypass
the file-reading mechanism.
'''
    read_text = (lambda self, filename: pass)()
    locate_file = (lambda self, path: pass)()
    from_name = (lambda cls, name: if not name:
raise ValueError('A distribution name is required.')try:
next(iter(cls.discover(name = name)))except StopIteration:
raise PackageNotFoundError(name))()
    discover = (lambda cls, *, context: if context and kwargs:
raise ValueError('cannot accept context and kwargs')context = DistributionFinder.Context or ()(*{
**kwargs })(lambda .0: for resolver in .0:
resolver(context).0)(cls._discover_resolvers()())
)()
    at = (lambda path: PathDistribution(pathlib.Path(path)))()
    _discover_resolvers = (lambda : declared = sys.meta_path()filter(None, declared))()
    metadata = (lambda self: from . import _adaptersopt_text = self.read_text('PKG-INFO') or self.read_text('')text = cast(str, opt_text)_adapters.Message(email.message_from_string(text)))()
    name = (lambda self: self.metadata['Name'])()
    _normalized_name = (lambda self: Prepared.normalize(self.name))()
    version = (lambda self: self.metadata['Version'])()
    entry_points = (lambda self: EntryPoints._from_text_for(self.read_text('entry_points.txt'), self))()
    files = (lambda self: 
def make_file(name, hash = None, size_str = None):
result = PackagePath(name)result.hash = FileHash(hash) if hash else Noneresult.size = int(size_str) if size_str else Noneresult.dist = selfresultmake_files = (lambda lines: import csvstarmap(make_file, csv.reader(lines)))()
        skip_missing_files = (lambda package_paths: list(filter((lambda path: path.locate().exists()), package_paths))
)()
        return make_files(self._read_files_distinfo()(self._read_files_egginfo_installed() or self._read_files_egginfo_sources()))
)()
    
    def _read_files_distinfo(self):
        '''
Read the lines of RECORD.
'''
        text = self.read_text('RECORD')
        return text and text.splitlines()

    
    def _read_files_egginfo_installed(self):
        '''
Read installed-files.txt and return lines in a similar
CSV-parsable format as RECORD: each file must be placed
relative to the site-packages directory and must also be
quoted (since file names can contain literal commas).

This file is written when the package is installed by pip,
but it might not be written for other installation methods.
Assume the file is accurate if it exists.
'''
        text = self.read_text('installed-files.txt')
        subdir = getattr(self, '_path', None)
        if not text or not subdir:
            return None
        paths = text.splitlines()()
        return map('"{}"'.format, paths)

    
    def _read_files_egginfo_sources(self):
        '''
Read SOURCES.txt and return lines in a similar CSV-parsable
format as RECORD: each file name must be quoted (since it
might contain literal commas).

Note that SOURCES.txt is not a reliable source for what
files are installed by a package. This file is generated
for a source archive, and the files that are present
there (e.g. setup.py) may not correctly reflect the files
that are present after the package has been installed.
'''
        text = self.read_text('SOURCES.txt')
        return text and map('"{}"'.format, text.splitlines())

    requires = (lambda self: reqs = self._read_dist_info_reqs() or self._read_egg_info_reqs()reqs and list(reqs))()
    
    def _read_dist_info_reqs(self):
        '''Requires-Dist'''
        return self.metadata.get_all('Requires-Dist')

    
    def _read_egg_info_reqs(self):
        '''requires.txt'''
        source = self.read_text('requires.txt')
        return pass_none(self._deps_from_requires_text)(source)

    _deps_from_requires_text = (lambda cls, source: cls._convert_egg_info_reqs_to_simple_reqs(Sectioned.read(source)))()
    _convert_egg_info_reqs_to_simple_reqs = (lambda sections: 
def make_condition(name):
'''extra == "'''
name and f'''extra == "{name}"'''
def quoted_marker(section):
''
section = section or ''(extra, sep, markers) = section.partition(':')if extra and markers:
markers = f'''({markers})'''conditions = list(filter(None, [
markers,
make_condition(extra)]))if conditions:
'; ' + ' and '.join(conditions)''
def url_req_space(req):
'''
PEP 508 requires a space between the url_spec and the quoted_marker.
Ref python/importlib_metadata#357.
'''
' ' * ('@' in req)for section in sections:
space = url_req_space(section.value)section.value + space + quoted_marker(section.name)sections)()
    origin = (lambda self: self._load_json('direct_url.json'))()
    
    def _load_json(self, filename):
        return pass_none(json.loads)(self.read_text(filename), object_hook = (lambda data: ()(*{
**data })))



class DistributionFinder(MetaPathFinder):
    '''
A MetaPathFinder capable of discovering installed distributions.

Custom providers should implement this interface in order to
supply metadata.
'''
    
    class Context:
        '''
Keyword arguments presented by the caller to
``distributions()`` or ``Distribution.discover()``
to narrow the scope of a search for distributions
in all DistributionFinders.

Each DistributionFinder may expect any parameters
and should attempt to honor the canonical
parameters defined below when appropriate.

This mechanism gives a custom provider a means to
solicit additional details from the caller beyond
"name" and "path" when searching distributions.
For example, imagine a provider that exposes suites
of packages in either a "public" or "private" ``realm``.
A caller may wish to query only for distributions in
a particular realm and could call
``distributions(realm="private")`` to signal to the
custom provider to only include distributions from that
realm.
'''
        name = None
        
        def __init__(self, **kwargs):
            vars(self).update(kwargs)

        path = (lambda self: vars(self).get('path', sys.path))()

    find_distributions = (lambda self, context = Context(): pass)()


class FastPath:
    """
Micro-optimized class for searching a root for children.

Root is a path on the file system that may contain metadata
directories either as natural directories or within a zip file.

>>> FastPath('').children()
['...']

FastPath objects are cached and recycled for any given root.

>>> FastPath('foobar') is FastPath('foobar')
True
"""
    __new__ = (lambda cls, root: # unsupported opcode LOAD_SUPER_ATTRcls(cls)# WARNING: Decompyle incomplete
)()
    
    def __init__(self, root):
        self.root = root

    
    def joinpath(self, child):
        return pathlib.Path(self.root, child)

    
    def children(self):
        '''.'''
        suppress(Exception).__enter__()
        suppress(Exception).__exit__(None, None, None)
        return os.listdir(self.root or '.')
    # WARNING: Decompyle incomplete

    
    def zip_children(self):
        zip_path = zipfile.Path(self.root)
        names = zip_path.root.namelist()
        self.joinpath = zip_path.joinpath
        return (lambda .0: for child in .0:
child.split(posixpath.sep, 1)[0].0)(names())

    
    def search(self, name):
        return self.lookup(self.mtime).search(name)

    mtime = (lambda self: suppress(OSError).__enter__()suppress(OSError).__exit__(None, None, None)os.stat(self.root).st_mtime# WARNING: Decompyle incomplete
)()
    lookup = (lambda self, mtime: Lookup(self))()


class Lookup:
    '''
A micro-optimized class for searching a (fast) path for metadata.
'''
    
    def __init__(self, path):
        '''
Calculate all of the children representing metadata.

From the children in the path, calculate early all of the
children that appear to represent metadata (infos) or legacy
metadata (eggs).
'''
        base = os.path.basename(path.root).lower()
        base_is_egg = base.endswith('.egg')
        self.infos = FreezableDefaultDict(list)
        self.eggs = FreezableDefaultDict(list)
        for child in path.children():
            low = child.lower()
            if low.endswith(('.dist-info', '.egg-info')):
                name = low.rpartition('.')[0].partition('-')[0]
                normalized = Prepared.normalize(name)
                self.infos[normalized].append(path.joinpath(child))
                continue
            if not base_is_egg:
                continue
            if not low == 'egg-info':
                continue
            name = base.rpartition('.')[0].partition('-')[0]
            legacy_normalized = Prepared.legacy_normalize(name)
            self.eggs[legacy_normalized].append(path.joinpath(child))
        self.infos.freeze()
        self.eggs.freeze()

    
    def search(self, prepared):
        '''
Yield all infos and eggs matching the Prepared query.
'''
        infos = self.infos[prepared.normalized] if prepared else itertools.chain.from_iterable(self.infos.values())
        eggs = self.eggs[prepared.legacy_normalized] if prepared else itertools.chain.from_iterable(self.eggs.values())
        return itertools.chain(infos, eggs)



class Prepared:
    """
A prepared search query for metadata on a possibly-named package.

Pre-calculates the normalization to prevent repeated operations.

>>> none = Prepared(None)
>>> none.normalized
>>> none.legacy_normalized
>>> bool(none)
False
>>> sample = Prepared('Sample__Pkg-name.foo')
>>> sample.normalized
'sample_pkg_name_foo'
>>> sample.legacy_normalized
'sample__pkg_name.foo'
>>> bool(sample)
True
"""
    normalized = None
    legacy_normalized = None
    
    def __init__(self, name):
        self.name = name
        if name is None:
            return None
        self.normalized = self.normalize(name)
        self.legacy_normalized = self.legacy_normalize(name)

    normalize = (lambda name: re.sub('[-_.]+', '-', name).lower().replace('-', '_'))()
    legacy_normalize = (lambda name: name.lower().replace('-', '_'))()
    
    def __bool__(self):
        return bool(self.name)



class MetadataPathFinder(DistributionFinder):
    find_distributions = (lambda cls, context = DistributionFinder.Context(): found = cls._search_paths(context.name, context.path)map(PathDistribution, found))()
    _search_paths = (lambda cls, name, paths: prepared = Prepared(name)(lambda .0: for path in .0:
path.search(prepared).0)(map(FastPath, paths)())
)()
    invalidate_caches = (lambda cls: FastPath.__new__.cache_clear())()


class PathDistribution(Distribution):
    
    def __init__(self, path):
        '''Construct a distribution.

:param path: SimplePath indicating the metadata directory.
'''
        self._path = path

    
    def read_text(self, filename):
        '''utf-8'''
        suppress(FileNotFoundError, IsADirectoryError, KeyError, NotADirectoryError, PermissionError).__enter__()
        suppress(FileNotFoundError, IsADirectoryError, KeyError, NotADirectoryError, PermissionError).__exit__(None, None, None)
        return self._path.joinpath(filename).read_text(encoding = 'utf-8')

    read_text.__doc__ = Distribution.read_text.__doc__
    
    def locate_file(self, path):
        return self._path.parent / path

    _normalized_name = (lambda self: stem = os.path.basename(str(self._path))# unsupported opcode LOAD_SUPER_ATTR__class__ or self# WARNING: Decompyle incomplete
)()
    _name_from_stem = (lambda stem: filename, ext = os.path.splitext(stem)if ext not in ('.dist-info', '.egg-info'):
None(name, sep, rest) = filename.partition('-')name)()


def distribution(distribution_name):
    '''Get the ``Distribution`` instance for the named package.

:param distribution_name: The name of the distribution package as a string.
:return: A ``Distribution`` instance (or subclass thereof).
'''
    return Distribution.from_name(distribution_name)


def distributions(**kwargs):
    '''Get all ``Distribution`` instances in the current environment.

:return: An iterable of ``Distribution`` instances.
'''
    return ()(*{
        **kwargs })


def metadata(distribution_name):
    '''Get the metadata for the named package.

:param distribution_name: The name of the distribution package to query.
:return: A PackageMetadata containing the parsed metadata.
'''
    return Distribution.from_name(distribution_name).metadata


def version(distribution_name):
    '''Get the version string for the named package.

:param distribution_name: The name of the distribution package to query.
:return: The version string for the package as defined in the package\'s
    "Version" metadata key.
'''
    return distribution(distribution_name).version

_unique = functools.partial(unique_everseen, key = operator.attrgetter('_normalized_name'))

def entry_points(**params):
    '''Return EntryPoint objects for all installed packages.

Pass selection parameters (group or name) to filter the
result to entry points matching those properties (see
EntryPoints.select()).

:return: EntryPoints for all installed packages.
'''
    eps = (lambda .0: for dist in .0:
dist.entry_points.0)(_unique(distributions())())
    return ()(*{
        **params })


def files(distribution_name):
    '''Return a list of files for the named package.

:param distribution_name: The name of the distribution package to query.
:return: List of files composing the distribution.
'''
    return distribution(distribution_name).files


def requires(distribution_name):
    '''
Return a list of requirements for the named package.

:return: An iterable of requirements, suitable for
    packaging.requirement.Requirement.
'''
    return distribution(distribution_name).requires


def packages_distributions():
    '''
Return a mapping of top-level packages to their
distributions.

>>> import collections.abc
>>> pkgs = packages_distributions()
>>> all(isinstance(dist, collections.abc.Sequence) for dist in pkgs.values())
True
'''
    pkg_to_dist = collections.defaultdict(list)
    for dist in distributions():
        for pkg in _top_level_declared(dist) or _top_level_inferred(dist):
            pkg_to_dist[pkg].append(dist.metadata['Name'])
    return dict(pkg_to_dist)


def _top_level_declared(dist):
    '''top_level.txt'''
    return (dist.read_text('top_level.txt') or '').split()


def _topmost(name):
    '''
Return the top-most parent as long as there is a parent.
'''
    top, rest = name.parts
    if rest:
        return top


def _get_toplevel_name(name):
    """
Infer a possibly importable module name from a name presumed on
sys.path.

>>> _get_toplevel_name(PackagePath('foo.py'))
'foo'
>>> _get_toplevel_name(PackagePath('foo'))
'foo'
>>> _get_toplevel_name(PackagePath('foo.pyc'))
'foo'
>>> _get_toplevel_name(PackagePath('foo/__init__.py'))
'foo'
>>> _get_toplevel_name(PackagePath('foo.pth'))
'foo.pth'
>>> _get_toplevel_name(PackagePath('foo.dist-info'))
'foo.dist-info'
"""
    return inspect.getmodulename(name) or str(name)


def _top_level_inferred(dist):
    opt_names = set(map(_get_toplevel_name, always_iterable(dist.files)))
    
    def importable_name(name):
        '''.'''
        return '.' not in name

    return filter(importable_name, opt_names)

