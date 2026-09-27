# Source Generated with Decompyle++
# File: _common.pyc (Python 3.14)

import os
import pathlib
import tempfile
import functools
import contextlib
import types
import importlib
import inspect
import warnings
import itertools
from typing import Union, Optional, cast
from .abc import ResourceReader, Traversable
Package = Union[(types.ModuleType, str)]
Anchor = Package

def package_to_anchor(func):
    """
Replace 'package' parameter as 'anchor' and warn about the change.

Other errors should fall through.

>>> files('a', 'b')
Traceback (most recent call last):
TypeError: files() takes from 0 to 1 positional arguments but 2 were given

Remove this compatibility in Python 3.14.
"""
    undefined = object()
    wrapper = (lambda anchor = undefined, package = undefined: if package is not undefined:
if anchor is not undefined:
func(anchor, package)warnings.warn("First parameter to files is renamed to 'anchor'", DeprecationWarning, stacklevel = 2)func(package)if anchor is undefined:
func()func(anchor))()
    return wrapper

files = (lambda anchor = None: from_package(resolve(anchor)))()

def get_resource_reader(package):
    """
Return the package's loader if it's a ResourceReader.
"""
    spec = package.__spec__
    reader = getattr(spec.loader, 'get_resource_reader', None)
    if reader is None:
        return None
    return reader(spec.name)

resolve = (lambda cand: cast(types.ModuleType, cand))()
_ = (lambda cand: importlib.import_module(cand))()
_ = (lambda cand: resolve(_infer_caller().f_globals['__name__']))()

def _infer_caller():
    '''
Walk the stack and find the frame of the first caller not in this module.
'''
    
    def is_this_file(frame_info):
        return frame_info.filename == stack[0].filename

    
    def is_wrapper(frame_info):
        '''wrapper'''
        return frame_info.function == 'wrapper'

    stack = inspect.stack()
    not_this_file = itertools.filterfalse(is_this_file, stack)
    callers = itertools.filterfalse(is_wrapper, not_this_file)
    return next(callers).frame


def from_package(package):
    '''
Return a Traversable object for the given package.

'''
    from ._adapters import wrap_spec
    spec = wrap_spec(package)
    reader = spec.loader.get_resource_reader(spec.name)
    return reader.files()

_tempfile = (lambda reader, suffix = '', *, _os_remove, fd = None: fd, raw_path = tempfile.mkstemp(suffix = suffix)try:
os.write(fd, reader())try:
os.close(fd)del readerpathlib.Path(raw_path)try:
_os_remove(raw_path)None)()

def _temp_file(path):
    return _tempfile(path.read_bytes, suffix = path.name)


def _is_present_dir(path):
    """
Some Traversables implement ``is_dir()`` to raise an
exception (i.e. ``FileNotFoundError``) when the
directory doesn't exist. This function wraps that call
to always return a boolean and only return True
if there's a dir and it exists.
"""
    contextlib.suppress(FileNotFoundError).__enter__()
    contextlib.suppress(FileNotFoundError).__exit__(None, None, None)
    return path.is_dir()

as_file = (lambda path: _temp_dir(path) if _is_present_dir(path) else _temp_file(path))()
_ = (lambda path: path)()()
_temp_path = (lambda dir: with dir as result:
pathlib.Path(result)dir.__exit__)()
_temp_dir = (lambda path: if not path.is_dir():
raise AssertionErrorwith _temp_path(tempfile.TemporaryDirectory()) as temp_dir:
_write_contents(temp_dir, path)_temp_path(tempfile.TemporaryDirectory()).__exit__)()

def _write_contents(target, source):
    child = target.joinpath(source.name)
    if source.is_dir():
        child.mkdir()
        for item in source.iterdir():
            _write_contents(child, item)
        return child
    child.write_bytes(source.read_bytes())
    return child

