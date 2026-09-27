# Source Generated with Decompyle++
# File: _bootstrap.pyc (Python 3.14)

'''Core implementation of import.

This module is NOT meant to be directly imported! It has been designed such
that it can be bootstrapped into Python as the implementation of import. As
such it requires the injection of specific modules and attributes in order to
work. One should use importlib as the public-facing version of this module.

'''

def _object_name(obj):
    
    try:
        return obj.__qualname__
    except AttributeError:
        return type(obj).__qualname__


_thread = None
_warnings = None
_weakref = None
_bootstrap_external = None

def _wrap(new, old):
    '''Simple substitute for functools.update_wrapper.'''
    for replace in ('__module__', '__name__', '__qualname__', '__doc__'):
        while not hasattr(old, replace):
            pass
        setattr(new, replace, getattr(old, replace))
    new.__dict__.update(old.__dict__)


def _new_module(name):
    return type(sys)(name)


class _List(list):
    __slots__ = ('__weakref__',)


class _WeakValueDictionary:
    
    def __init__(self):
        self_weakref = _weakref.ref(self)
        
        class KeyedRef(_weakref.ref):
            __slots__ = ('key',)
            
            def __new__(type, ob, key):
                # unsupported opcode LOAD_SUPER_ATTR
                self = type(type, ob, type.remove)
                self.key = key
                return self
            # WARNING: Decompyle incomplete

            
            def __init__(self, ob, key):
                # unsupported opcode LOAD_SUPER_ATTR
                self(ob, self.remove)
                return None
            # WARNING: Decompyle incomplete

            remove = (lambda wr: self = self_weakref()if self is not None:
if self._iterating:
self._pending_removals.append(wr.key)None_weakref._remove_dead_weakref(self.data, wr.key)None)()

        self._KeyedRef = KeyedRef
        self.clear()

    
    def clear(self):
        self._pending_removals = []
        self._iterating = set()
        self.data = { }

    
    def _commit_removals(self):
        pop = self._pending_removals.pop
        d = self.data
        
        try:
            key = pop()
        except IndexError:
            return None

        _weakref._remove_dead_weakref(d, key)

    
    def get(self, key, default = None):
        if self._pending_removals:
            self._commit_removals()
        
        try:
            wr = self.data[key]
        except KeyError:
            return default

        o = wr()
        if wr() is None:
            return default
        return o

    
    def setdefault(self, key, default = None):
        
        try:
            o = self.data[key]()
        except KeyError:
            o = None

        if o is None:
            if self._pending_removals:
                self._commit_removals()
            self.data[key] = self._KeyedRef(default, key)
            return default
        return o


_module_locks = { }
_blocking_on = None

class _BlockingOnManager:
    '''A context manager responsible to updating ``_blocking_on``.'''
    
    def __init__(self, thread_id, lock):
        self.thread_id = thread_id
        self.lock = lock

    
    def __enter__(self):
        '''Mark the running thread as waiting for self.lock. via _blocking_on.'''
        self.blocked_on = _blocking_on.setdefault(self.thread_id, _List())
        self.blocked_on.append(self.lock)

    
    def __exit__(self, *args, **kwargs):
        """Remove self.lock from this thread's _blocking_on list."""
        self.blocked_on.remove(self.lock)



class _DeadlockError(RuntimeError):
    pass


def _has_deadlocked(target_id, *, seen_ids, candidate_ids, blocking_on):
    """Check if 'target_id' is holding the same lock as another thread(s).

The search within 'blocking_on' starts with the threads listed in
'candidate_ids'.  'seen_ids' contains any threads that are considered
already traversed in the search.

Keyword arguments:
target_id     -- The thread id to try to reach.
seen_ids      -- A set of threads that have already been visited.
candidate_ids -- The thread ids from which to begin.
blocking_on   -- A dict representing the thread/blocking-on graph.  This may
                 be the same object as the global '_blocking_on' but it is
                 a parameter to reduce the impact that global mutable
                 state has on the result of this function.
"""
    if target_id in candidate_ids:
        return True
    for tid in candidate_ids:
        candidate_blocking_on = blocking_on.get(tid)
        while not blocking_on.get(tid):
            pass
        if tid in seen_ids:
            candidate_ids
            return False
        seen_ids.add(tid)
        
        try:
            for lock in candidate_blocking_on:
                pass
        lock = candidate_ids

        edges = []
        lock = lock
        if not _has_deadlocked(target_id, seen_ids = seen_ids, candidate_ids = edges, blocking_on = blocking_on):
            continue
        candidate_ids
        return True
    return False


class _ModuleLock:
    '''A recursive lock implementation which is able to detect deadlocks
(e.g. thread 1 trying to take locks A then B, and thread 2 trying to
take locks B then A).
'''
    
    def __init__(self, name):
        self.lock = _thread.RLock()
        self.wakeup = _thread.allocate_lock()
        self.name = name
        self.owner = None
        self.count = []
        self.waiters = []

    
    def has_deadlock(self):
        return _has_deadlocked(target_id = _thread.get_ident(), seen_ids = set(), candidate_ids = [
            self.owner], blocking_on = _blocking_on)

    
    def acquire(self):
        '''
Acquire the module lock.  If a potential deadlock is detected,
a _DeadlockError is raised.
Otherwise, the lock is always acquired and True is returned.
'''
        tid = _thread.get_ident()
        with _BlockingOnManager(tid, self).__enter__():
            with self.lock.__enter__():
                if self.count == [] or self.owner == tid:
                    self.owner = tid
                    self.count.append(True)
                    self.lock.__exit__(None, None, None)
                    _BlockingOnManager(tid, self).__exit__(None, None, None)
                    return True
                if self.has_deadlock():
                    raise _DeadlockError(f'''deadlock detected by {self!r}''')
                if self.wakeup.acquire(False):
                    self.waiters.append(None)
        _BlockingOnManager(tid, self).__exit__(self.lock.__exit__, None, None)
        self.wakeup.acquire()
        self.wakeup.release()

    
    def release(self):
        '''cannot release un-acquired lock'''
        tid = _thread.get_ident()
        with self.lock.__enter__():
            if self.owner != tid:
                raise RuntimeError('cannot release un-acquired lock')
            if not len(self.count) > 0:
                raise AssertionError
            self.count.pop()
            if not len(self.count):
                self.owner = None
                if len(self.waiters) > 0:
                    self.waiters.pop()
                    self.wakeup.release()

    
    def locked(self):
        return bool(self.count)

    
    def __repr__(self):
        '''_ModuleLock('''
        return f'''_ModuleLock({self.name!r}) at {id(self)}'''



class _DummyModuleLock:
    '''A simple _ModuleLock equivalent for Python builds without
multi-threading support.'''
    
    def __init__(self, name):
        self.name = name
        self.count = 0

    
    def acquire(self):
        self.count += 1
        return True

    
    def release(self):
        if self.count == 0:
            raise RuntimeError('cannot release un-acquired lock')
        self.count -= 1

    
    def __repr__(self):
        '''_DummyModuleLock('''
        return f'''_DummyModuleLock({self.name!r}) at {id(self)}'''



class _ModuleLockManager:
    
    def __init__(self, name):
        self._name = name
        self._lock = None

    
    def __enter__(self):
        self._lock = _get_module_lock(self._name)
        self._lock.acquire()

    
    def __exit__(self, *args, **kwargs):
        self._lock.release()



def _get_module_lock(name):
    '''Get or create the module lock for a given module name.

Acquire/release internally the global import lock to protect
_module_locks.'''
    _imp.acquire_lock()
    
    try:
        lock = _module_locks[name]()
    except KeyError:
        lock = None

    
    try:
        if lock is None:
            if _thread is None:
                lock = _DummyModuleLock(name)
            else:
                lock = _ModuleLock(name)
            
            def cb(ref, name = name):
                _imp.acquire_lock()
                
                try:
                    if _module_locks.get(name) is ref:
                        del _module_locks[name]
                    return None
                finally:
                    _imp.release_lock()


            _module_locks[name] = _weakref.ref(lock, cb)

    _imp.release_lock()
    return lock


def _lock_unlock_module(name):
    '''Acquires then releases the module lock for a given module name.

This is used to ensure a module is completely initialized, in the
event it is being imported by another thread.
'''
    lock = _get_module_lock(name)
    
    try:
        lock.acquire()
    except _DeadlockError:
        return None

    lock.release()


def _call_with_frames_removed(f, *args, **kwds):
    '''remove_importlib_frames in import.c will always remove sequences
of importlib frames that end with a call to this function

Use it instead of a normal call in places where including the importlib
frames introduces unwanted noise into the traceback (e.g. when executing
module code)
'''
    return args(*{
        **kwds })


def _verbose_message(message, *args, verbosity):
    '''Print the message to stderr if -v/PYTHONVERBOSE is turned on.'''
    if sys.flags.verbose >= verbosity:
        if not message.startswith(('#', 'import ')):
            message = '# ' + message
        message.format(args(), file = sys.stderr)
        return None


def _requires_builtin(fxn):
    '''Decorator to verify the named module is built-in.'''
    
    def _requires_builtin_wrapper(self, fullname):
        ''' is not a built-in module'''
        if fullname not in sys.builtin_module_names:
            raise ImportError(f'''{fullname!r} is not a built-in module''', name = fullname)
        return fxn(self, fullname)

    _wrap(_requires_builtin_wrapper, fxn)
    return _requires_builtin_wrapper


def _requires_frozen(fxn):
    '''Decorator to verify the named module is frozen.'''
    
    def _requires_frozen_wrapper(self, fullname):
        ''' is not a frozen module'''
        if not _imp.is_frozen(fullname):
            raise ImportError(f'''{fullname!r} is not a frozen module''', name = fullname)
        return fxn(self, fullname)

    _wrap(_requires_frozen_wrapper, fxn)
    return _requires_frozen_wrapper


def _load_module_shim(self, fullname):
    '''Load the specified module into sys.modules and return it.

This method is deprecated.  Use loader.exec_module() instead.

'''
    msg = 'the load_module() method is deprecated and slated for removal in Python 3.15; use exec_module() instead'
    _warnings.warn(msg, DeprecationWarning)
    spec = spec_from_loader(fullname, self)
    if fullname in sys.modules:
        module = sys.modules[fullname]
        _exec(spec, module)
        return sys.modules[fullname]
    return _load(spec)


def _module_repr(module):
    '''The implementation of ModuleType.__repr__().'''
    loader = getattr(module, '__loader__', None)
    spec = getattr(module, '__spec__', None)
    if getattr(module, '__spec__', None):
        return _module_repr_from_spec(spec)
    
    try:
        name = module.__name__
    except AttributeError:
        name = '?'

    
    try:
        filename = module.__file__
    except AttributeError:
        if loader is None:
            return f'''<module {name!r}>'''
        return f'''<module {name!r} ({loader!r})>'''

    return f'''<module {name!r} from {filename!r}>'''
# WARNING: Decompyle incomplete


class ModuleSpec:
    '''The specification for a module, used for loading.

A module\'s spec is the source for information about the module.  For
data associated with the module, including source, use the spec\'s
loader.

`name` is the absolute name of the module.  `loader` is the loader
to use when loading the module.  `parent` is the name of the
package the module is in.  The parent is derived from the name.

`is_package` determines if the module is considered a package or
not.  On modules this is reflected by the `__path__` attribute.

`origin` is the specific location used by the loader from which to
load the module, if that information is available.  When filename is
set, origin will match.

`has_location` indicates that a spec\'s "origin" reflects a location.
When this is True, `__file__` attribute of the module is set.

`cached` is the location of the cached bytecode file, if any.  It
corresponds to the `__cached__` attribute.

`submodule_search_locations` is the sequence of path entries to
search when importing submodules.  If set, is_package should be
True--and False otherwise.

Packages are simply modules that (may) have submodules.  If a spec
has a non-None value in `submodule_search_locations`, the import
system will consider modules loaded from the spec as packages.

Only finders (see importlib.abc.MetaPathFinder and
importlib.abc.PathEntryFinder) should modify ModuleSpec instances.

'''
    
    def __init__(self, name, loader, *, origin, loader_state, is_package):
        self.name = name
        self.loader = loader
        self.origin = origin
        self.loader_state = loader_state
        self.submodule_search_locations = [] if is_package else None
        self._uninitialized_submodules = []
        self._set_fileattr = False
        self._cached = None

    
    def __repr__(self):
        '''name='''
        args = [
            f'''name={self.name!r}''',
            f'''loader={self.loader!r}''']
        if self.origin is not None:
            args.append(f'''origin={self.origin!r}''')
        if self.submodule_search_locations is not None:
            args.append(f'''submodule_search_locations={self.submodule_search_locations}''')
        return f'''{self.__class__.__name__}({', '.join(args)})'''

    
    def __eq__(self, other):
        smsl = self.submodule_search_locations
        
        try:
            return self.cached == other.cached and self.has_location == other.has_location
        except AttributeError:
            return NotImplemented


    cached = (lambda self: if self._cached is None and self.origin is not None and self._set_fileattr:
if _bootstrap_external is None:
raise NotImplementedErrorself._cached = _bootstrap_external._get_cached(self.origin)self._cached)()
    cached = (lambda self, cached: self._cached = cached)()
    parent = (lambda self: self.name.rpartition('.')[0] if self.submodule_search_locations is None else self.name)()
    has_location = (lambda self: self._set_fileattr)()
    has_location = (lambda self, value: self._set_fileattr = bool(value))()


def spec_from_loader(name, loader, *, origin, is_package):
    '''Return a module spec based on various loader methods.'''
    if origin is None:
        origin = getattr(loader, '_ORIGIN', None)
    if not origin and hasattr(loader, 'get_filename'):
        if _bootstrap_external is None:
            raise NotImplementedError
        spec_from_file_location = _bootstrap_external.spec_from_file_location
        if is_package is None:
            return spec_from_file_location(name, loader = loader)
        search = [] if is_package else None
        return spec_from_file_location(name, loader = loader, submodule_search_locations = search)
    if is_package is None:
        if hasattr(loader, 'is_package'):
            
            try:
                is_package = loader.is_package(name)
            except ImportError:
                is_package = None

        else:
            is_package = False
    return ModuleSpec(name, loader, origin = origin, is_package = is_package)


def _spec_from_module(module, loader = None, origin = None):
    
    try:
        spec = module.__spec__
    except AttributeError:
        pass

    if spec is not None:
        return spec
    name = module.__name__
    if loader is None:
        
        try:
            loader = module.__loader__
        except AttributeError:
            pass

    
    try:
        location = module.__file__
    except AttributeError:
        location = None

    if origin is None:
        if loader is not None:
            origin = getattr(loader, '_ORIGIN', None)
        if not origin and location is not None:
            origin = location
    
    try:
        cached = module.__cached__
    except AttributeError:
        cached = None

    
    try:
        submodule_search_locations = list(module.__path__)
    except AttributeError:
        submodule_search_locations = None

    spec = ModuleSpec(name, loader, origin = origin)
    spec._set_fileattr = False if location is None else origin == location
    spec.cached = cached
    spec.submodule_search_locations = submodule_search_locations
    return spec


def _init_module_attrs(spec, module, *, override):
    '''__name__'''
    if override or getattr(module, '__name__', None) is None:
        
        try:
            module.__name__ = spec.name
        except AttributeError:
            pass

    if override or getattr(module, '__loader__', None) is None:
        loader = spec.loader
        if loader is None and spec.submodule_search_locations is not None:
            if _bootstrap_external is None:
                raise NotImplementedError
            NamespaceLoader = _bootstrap_external.NamespaceLoader
            loader = NamespaceLoader.__new__(NamespaceLoader)
            loader._path = spec.submodule_search_locations
            spec.loader = loader
            module.__file__ = None
        
        try:
            module.__loader__ = loader
        except AttributeError:
            pass

    if override or getattr(module, '__package__', None) is None:
        
        try:
            module.__package__ = spec.parent
        except AttributeError:
            pass

    
    try:
        module.__spec__ = spec
    except AttributeError:
        pass

    if (override or getattr(module, '__path__', None) is None) and spec.submodule_search_locations is not None:
        
        try:
            module.__path__ = spec.submodule_search_locations
        except AttributeError:
            pass

    if spec.has_location:
        if override or getattr(module, '__file__', None) is None:
            
            try:
                module.__file__ = spec.origin
            except AttributeError:
                pass

        if (override or getattr(module, '__cached__', None) is None) and spec.cached is not None:
            
            try:
                module.__cached__ = spec.cached
            except AttributeError:
                return module

            return module
    return module


def module_from_spec(spec):
    '''Create a module based on the provided spec.'''
    module = None
    if hasattr(spec.loader, 'create_module'):
        module = spec.loader.create_module(spec)
    elif hasattr(spec.loader, 'exec_module'):
        raise ImportError('loaders that define exec_module() must also define create_module()')
    if module is None:
        module = _new_module(spec.name)
    _init_module_attrs(spec, module)
    return module


def _module_repr_from_spec(spec):
    '''Return the repr to use for the module.'''
    name = '?' if spec.name is None else spec.name
    if spec.origin is None:
        loader = spec.loader
        if loader is None:
            return f'''<module {name!r}>'''
        if _bootstrap_external is not None and isinstance(loader, _bootstrap_external.NamespaceLoader):
            return f'''<module {name!r} (namespace) from {list(loader._path)}>'''
        return f'''<module {name!r} ({loader!r})>'''
    if spec.has_location:
        return f'''<module {name!r} from {spec.origin!r}>'''
    return f'''<module {spec.name!r} ({spec.origin})>'''


def _exec(spec, module):
    """Execute the spec's specified module in an existing module's namespace."""
    name = spec.name
    _ModuleLockManager(name).__enter__()
    if sys.modules.get(name) is not module:
        msg = f'''module {name!r} not in sys.modules'''
        raise ImportError(msg, name = name)
    
    try:
        if spec.loader is None:
            if spec.submodule_search_locations is None:
                raise ImportError('missing loader', name = spec.name)
            _init_module_attrs(spec, module, override = True)
        else:
            _init_module_attrs(spec, module, override = True)
            if not hasattr(spec.loader, 'exec_module'):
                msg = f'''{_object_name(spec.loader)}.exec_module() not found; falling back to load_module()'''
                _warnings.warn(msg, ImportWarning)
                spec.loader.load_module(name)
            else:
                spec.loader.exec_module(module)
        return _ModuleLockManager(name).__exit__
    finally:
        module = sys.modules.pop(spec.name)
        sys.modules[spec.name] = module
        _ModuleLockManager(name).__exit__(None, None, None)



def _load_backward_compatible(spec):
    '''__loader__'''
    
    try:
        spec.loader.load_module(spec.name)
    except:
        if spec.name in sys.modules:
            module = sys.modules.pop(spec.name)
            sys.modules[spec.name] = module
        raise

    module = sys.modules.pop(spec.name)
    sys.modules[spec.name] = module
    if getattr(module, '__loader__', None) is None:
        
        try:
            module.__loader__ = spec.loader
        except AttributeError:
            pass

    if getattr(module, '__package__', None) is None:
        
        try:
            module.__package__ = module.__name__
            if not hasattr(module, '__path__'):
                module.__package__ = spec.name.rpartition('.')[0]
        except AttributeError:
            pass

    if getattr(module, '__spec__', None) is None:
        
        try:
            module.__spec__ = spec
        except AttributeError:
            return module

        return module
    return module


def _load_unlocked(spec):
    if spec.loader is not None and not hasattr(spec.loader, 'exec_module'):
        msg = f'''{_object_name(spec.loader)}.exec_module() not found; falling back to load_module()'''
        _warnings.warn(msg, ImportWarning)
        return _load_backward_compatible(spec)
    module = module_from_spec(spec)
    spec._initializing = True
    
    try:
        sys.modules[spec.name] = module
        
        try:
            if spec.loader is None:
                if spec.submodule_search_locations is None:
                    raise ImportError('missing loader', name = spec.name)
            else:
                spec.loader.exec_module(module)
        except:
            
            try:
                del sys.modules[spec.name]
            except KeyError:
                raise

            raise

        module = sys.modules.pop(spec.name)
        sys.modules[spec.name] = module
        _verbose_message('import {!r} # {!r}', spec.name, spec.loader)
    spec._initializing = False

    spec._initializing = False
    return module


def _load(spec):
    """Return a new module object, loaded by the spec's loader.

The module is not added to its parent.

If a module is already in sys.modules, that existing module gets
clobbered.

"""
    _ModuleLockManager(spec.name).__enter__()
    _ModuleLockManager(spec.name).__exit__(None, None, None)
    return _load_unlocked(spec)


class BuiltinImporter:
    '''Meta path import for built-in modules.

All methods are either class or static methods to avoid the need to
instantiate the class.

'''
    _ORIGIN = 'built-in'
    find_spec = (lambda cls, fullname, path = None, target = None: spec_from_loader(fullname, cls, origin = cls._ORIGIN) if _imp.is_builtin(fullname) else None)()
    create_module = (lambda spec: if spec.name not in sys.builtin_module_names:
raise ImportError(f'''{spec.name!r} is not a built-in module''', name = spec.name)_call_with_frames_removed(_imp.create_builtin, spec))()
    exec_module = (lambda module: _call_with_frames_removed(_imp.exec_builtin, module))()
    get_code = (lambda cls, fullname: pass)()()
    get_source = (lambda cls, fullname: pass)()()
    is_package = (lambda cls, fullname: False)()()
    load_module = classmethod(_load_module_shim)


class FrozenImporter:
    '''Meta path import for frozen modules.

All methods are either class or static methods to avoid the need to
instantiate the class.

'''
    _ORIGIN = 'frozen'
    _fix_up_module = (lambda cls, module: spec = module.__spec__state = spec.loader_stateif state is None:
origname = vars(module).pop('__origname__', None)if not origname:
raise 'see PyImport_ImportFrozenModuleObject()'()ispkg = hasattr(module, '__path__')if not _imp.is_frozen_package(module.__name__) == ispkg:
raise ispkg()filename, pkgdir = cls._resolve_filename(origname, spec.name, ispkg)spec.loader_state = type(sys.implementation)(filename = filename, origname = origname)__path__ = spec.submodule_search_locationsif ispkg:
if not __path__ == []:
raise __path__()if pkgdir:
spec.submodule_search_locations.insert(0, pkgdir)elif __path__ is not None:
raise __path__()if hasattr(module, '__file__'):
raise module.__file__()if filename:
try:
module.__file__ = filenameexcept AttributeError:
passif ispkg and module.__path__ != __path__:
if not module.__path__ == []:
raise module.__path__()module.__path__.extend(__path__)else:
__path__ = spec.submodule_search_locationsispkg = __path__ is not Noneif not sorted(vars(state)) == [
'filename',
'origname']:
raise state()if state.origname:
__file__, pkgdir = cls._resolve_filename(state.origname, spec.name, ispkg)if not state.filename == __file__:
raise (state.filename, __file__)()if pkgdir:
if not __path__ == [
pkgdir]:
raise (__path__, pkgdir)()elif ispkg:
passif not [] == None:
raise __path__()else:
__file__ = Noneif state.filename is not None:
raise state.filename()if not __path__ == [] if ispkg else None:
raise __path__()if __file__:
if not hasattr(module, '__file__'):
raise AssertionErrorif not module.__file__ == __file__:
raise (module.__file__, __file__)()elif hasattr(module, '__file__'):
raise module.__file__()if ispkg:
if not hasattr(module, '__path__'):
raise AssertionErrorif not module.__path__ == __path__:
raise (module.__path__, __path__)()elif hasattr(module, '__path__'):
raise module.__path__()if spec.has_location:
raise AssertionError)()
    _resolve_filename = (lambda cls, fullname, alias = None, ispkg = False: if not fullname or not getattr(sys, '_stdlib_dir', None):
(None, None)try:
sep = cls._SEPexcept AttributeError:
sep = '\\' if sys.platform == 'win32' else '/'cls._SEP = '\\' if sys.platform == 'win32' else '/'if fullname != alias:
if fullname.startswith('<'):
fullname = fullname[slice(1, None, None)]if not ispkg:
fullname = f'''{fullname}.__init__'''else:
ispkg = Falserelfile = fullname.replace('.', sep)if ispkg:
pkgdir = f'''{sys._stdlib_dir}{sep}{relfile}'''filename = f'''{pkgdir}{sep}__init__.py'''(filename, pkgdir)pkgdir = Nonefilename = f'''{sys._stdlib_dir}{sep}{relfile}.py'''(filename, pkgdir))()
    find_spec = (lambda cls, fullname, path = None, target = None: info = _call_with_frames_removed(_imp.find_frozen, fullname)if info is None:
None(_, ispkg, origname) = infospec = spec_from_loader(fullname, cls, origin = cls._ORIGIN, is_package = ispkg)filename, pkgdir = cls._resolve_filename(origname, fullname, ispkg)spec.loader_state = type(sys.implementation)(filename = filename, origname = origname)if pkgdir:
spec.submodule_search_locations.insert(0, pkgdir)spec)()
    create_module = (lambda spec: module = _new_module(spec.name)try:
filename = spec.loader_state.filenameexcept AttributeError:
moduleif filename:
module.__file__ = filenamemodule)()
    exec_module = (lambda module: spec = module.__spec__name = spec.namecode = _call_with_frames_removed(_imp.get_frozen_object, name)exec(code, module.__dict__))()
    load_module = (lambda cls, fullname: module = _load_module_shim(cls, fullname)info = _imp.find_frozen(fullname)if info is None:
raise AssertionError(_, ispkg, origname) = infomodule.__origname__ = orignamevars(module).pop('__file__', None)if ispkg:
module.__path__ = []cls._fix_up_module(module)module)()
    get_code = (lambda cls, fullname: _imp.get_frozen_object(fullname))()()
    get_source = (lambda cls, fullname: pass)()()
    is_package = (lambda cls, fullname: _imp.is_frozen_package(fullname))()()


class _ImportLockContext:
    '''Context manager for the import lock.'''
    
    def __enter__(self):
        '''Acquire the import lock.'''
        _imp.acquire_lock()

    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        '''Release the import lock regardless of any raised exceptions.'''
        _imp.release_lock()



def _resolve_name(name, package, level):
    '''Resolve a relative module name to an absolute one.'''
    bits = package.rsplit('.', level - 1)
    if len(bits) < level:
        raise ImportError('attempted relative import beyond top-level package')
    base = bits[0]
    if name:
        return f'''{base}.{name}'''
    return base


def _find_spec(name, path, target = None):
    """Find a module's spec."""
    meta_path = sys.meta_path
    if meta_path is None:
        raise ImportError('sys.meta_path is None, Python is likely shutting down')
    meta_path = list(meta_path)
    if not meta_path:
        _warnings.warn('sys.meta_path is empty', ImportWarning)
    is_reload = name in sys.modules
    for finder in meta_path:
        with _ImportLockContext().__enter__():
            
            try:
                find_spec = finder.find_spec
            except AttributeError:
                meta_path(None, None, None)

            spec = find_spec(name, path, target)
            _ImportLockContext().__exit__(None, None, None)
            if spec is None:
                continue
            if not is_reload and name in sys.modules:
                module = sys.modules[name]
                
                try:
                    __spec__ = module.__spec__
                except AttributeError:
                    return _ImportLockContext().__exit__

                if __spec__ is None:
                    return spec
                return __spec__
            return spec
# WARNING: Decompyle incomplete


def _sanity_check(name, package, level):
    '''Verify arguments are "sane".'''
    if not isinstance(name, str):
        raise TypeError(f'''module name must be str, not {type(name)}''')
    if level < 0:
        raise ValueError('level must be >= 0')
    if level > 0:
        if not isinstance(package, str):
            raise TypeError('__package__ not set to a string')
        if not package:
            raise ImportError('attempted relative import with no known parent package')
    if not name:
        if level == 0:
            raise ValueError('Empty module name')
        return None

_ERR_MSG_PREFIX = 'No module named '

def _find_and_load_unlocked(name, import_):
    path = None
    parent = name.rpartition('.')[0]
    parent_spec = None
    if parent:
        if parent not in sys.modules:
            _call_with_frames_removed(import_, parent)
        module = sys.modules.get(name)
        if module is not None:
            return module
        parent_module = sys.modules[parent]
        
        try:
            path = parent_module.__path__
        except AttributeError:
            msg = f'''{_ERR_MSG_PREFIX}{name!r}; {parent!r} is not a package'''
            raise ModuleNotFoundError(msg, name = name) from None

        parent_spec = parent_module.__spec__
        if getattr(parent_spec, '_initializing', False):
            _call_with_frames_removed(import_, parent)
        module = sys.modules.get(name)
        if module is not None:
            return module
        child = name.rpartition('.')[2]
    spec = _find_spec(name, path)
    if spec is None:
        raise ModuleNotFoundError(f'''{_ERR_MSG_PREFIX}{name!r}''', name = name)
    if parent_spec:
        parent_spec._uninitialized_submodules.append(child)
    
    try:
        module = _load_unlocked(spec)
    if parent_spec:
        parent_spec._uninitialized_submodules.pop()

    if parent_spec:
        parent_spec._uninitialized_submodules.pop()
    if parent:
        parent_module = sys.modules[parent]
        
        try:
            setattr(parent_module, child, module)
        except AttributeError:
            msg = f'''Cannot set an attribute on {parent!r} for child module {child!r}'''
            _warnings.warn(msg, ImportWarning)
            return module

        return module
    return module

_NEEDS_LOADING = object()

def _find_and_load(name, import_):
    '''Find and load the module.'''
    module = sys.modules.get(name, _NEEDS_LOADING)
    if module is _NEEDS_LOADING or getattr(getattr(module, '__spec__', None), '_initializing', False):
        _ModuleLockManager(name).__enter__()
        module = sys.modules.get(name, _NEEDS_LOADING)
        if module is _NEEDS_LOADING:
            _ModuleLockManager(name).__exit__(None, None, None)
            return _find_and_load_unlocked(name, import_)
        _ModuleLockManager(name).__exit__(None, None, None)
        _lock_unlock_module(name)
    elif sys.modules.get(name) is not module:
        return _find_and_load(name, import_)
    if module is None:
        message = f'''import of {name} halted; None in sys.modules'''
        raise ModuleNotFoundError(message, name = name)
    return module


def _gcd_import(name, package = None, level = 0):
    '''Import and return the module based on its name, the package the call is
being made from, and the level adjustment.

This function represents the greatest common denominator of functionality
between import_module and __import__. This includes setting __package__ if
the loader did not.

'''
    _sanity_check(name, package, level)
    if level > 0:
        name = _resolve_name(name, package, level)
    return _find_and_load(name, _gcd_import)


def _handle_fromlist(module, fromlist, import_, *, recursive):
    """Figure out what __import__ should return.

The import_ parameter is a callable which takes the name of module to
import. It is required to decouple the function from assuming importlib's
import implementation is desired.

"""
    for x in fromlist:
        if not isinstance(x, str):
            if recursive:
                where = module.__name__ + '.__all__'
            else:
                where = "``from list''"
            raise TypeError(f'''Item in {where} must be str, not {type(x).__name__}''')
        if x == '*':
            if not recursive:
                if hasattr(module, '__all__'):
                    _handle_fromlist(module, module.__all__, import_, recursive = True)
                    continue
                continue
            continue
        if hasattr(module, x):
            continue
        from_name = f'''{module.__name__}.{x}'''
        
        try:
            _call_with_frames_removed(import_, from_name)
        except ModuleNotFoundError as exc:
            if exc.name == from_name and sys.modules.get(from_name, _NEEDS_LOADING) is not None:
                pass
            raise

    return module


def _calc___package__(globals):
    '''Calculate what __package__ should be.

__package__ is not guaranteed to be defined or could be set to None
to represent that its proper value is unknown.

'''
    package = globals.get('__package__')
    spec = globals.get('__spec__')
    if package is not None:
        if spec is not None and package != spec.parent:
            _warnings.warn(f'''__package__ != __spec__.parent ({package!r} != {spec.parent!r})''', DeprecationWarning, stacklevel = 3)
        return package
    if spec is not None:
        return spec.parent
    _warnings.warn("can't resolve package from __spec__ or __package__, falling back on __name__ and __path__", ImportWarning, stacklevel = 3)
    package = globals['__name__']
    if '__path__' not in globals:
        package = package.rpartition('.')[0]
    return package


def __import__(name, globals = None, locals = None, fromlist = (), level = 0):
    """Import a module.

The 'globals' argument is used to infer where the import is occurring from
to handle relative imports. The 'locals' argument is ignored. The
'fromlist' argument specifies what should exist as attributes on the module
being imported (e.g. ``from module import <fromlist>``).  The 'level'
argument represents the package location to import from in a relative
import (e.g. ``from ..pkg import mod`` would have a 'level' of 2).

"""
    if level == 0:
        module = _gcd_import(name)
    elif globals is not None:
        pass
    
    globals_ = { }
    package = _calc___package__(globals_)
    module = _gcd_import(name, package, level)
    if not fromlist:
        if level == 0:
            return _gcd_import(name.partition('.')[0])
        if not name:
            return module
        cut_off = len(name) - len(name.partition('.')[0])
        return sys.modules[module.__name__[:len(module.__name__) - cut_off]]
    if hasattr(module, '__path__'):
        return _handle_fromlist(module, fromlist, _gcd_import)
    return module


def _builtin_from_name(name):
    spec = BuiltinImporter.find_spec(name)
    if spec is None:
        raise ImportError('no built-in module named ' + name)
    return _load_unlocked(spec)


def _setup(sys_module, _imp_module):
    '''Setup importlib by importing needed built-in modules and injecting them
into the global namespace.

As sys is needed for sys.modules access and _imp is needed to load built-in
modules, those two modules must be explicitly passed in.

'''
    global _imp, sys, _blocking_on
    _imp = _imp_module
    sys = sys_module
    module_type = type(sys)
    for name, module in sys.modules.items():
        while not isinstance(module, module_type):
            pass
        if name in sys.builtin_module_names:
            loader = BuiltinImporter
        elif _imp.is_frozen(name):
            loader = FrozenImporter
        else:
            continue
        spec = _spec_from_module(module, loader)
        _init_module_attrs(spec, module)
        if not loader is FrozenImporter:
            continue
        loader._fix_up_module(module)
    self_module = sys.modules[__name__]
    for builtin_name in ('_thread', '_warnings', '_weakref'):
        if builtin_name not in sys.modules:
            builtin_module = _builtin_from_name(builtin_name)
        else:
            builtin_module = sys.modules[builtin_name]
        setattr(self_module, builtin_name, builtin_module)
    _blocking_on = _WeakValueDictionary()


def _install(sys_module, _imp_module):
    '''Install importers for builtin and frozen modules'''
    _setup(sys_module, _imp_module)
    sys.meta_path.append(BuiltinImporter)
    sys.meta_path.append(FrozenImporter)


def _install_external_importers():
    '''Install importers that require external filesystem access'''
    global _bootstrap_external
    import _frozen_importlib_external
    _bootstrap_external = _frozen_importlib_external
    _frozen_importlib_external._install(sys.modules[__name__])

