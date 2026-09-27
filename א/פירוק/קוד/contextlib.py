# Source Generated with Decompyle++
# File: contextlib.pyc (Python 3.14)

'''Utilities for with-statement contexts.  See PEP 343.'''
import abc
import os
import sys
import _collections_abc
from collections import deque
from functools import wraps
from types import MethodType, GenericAlias
__all__ = [
    'asynccontextmanager',
    'contextmanager',
    'closing',
    'nullcontext',
    'AbstractContextManager',
    'AbstractAsyncContextManager',
    'AsyncExitStack',
    'ContextDecorator',
    'ExitStack',
    'redirect_stdout',
    'redirect_stderr',
    'suppress',
    'aclosing',
    'chdir']

class AbstractContextManager(abc.ABC):
    '''An abstract base class for context managers.'''
    __class_getitem__ = classmethod(GenericAlias)
    __slots__ = ()
    
    def __enter__(self):
        '''Return `self` upon entering the runtime context.'''
        return self

    __exit__ = (lambda self, exc_type, exc_value, traceback: pass)()
    __subclasshook__ = (lambda cls, C: _collections_abc._check_methods(C, '__enter__', '__exit__') if cls is AbstractContextManager else NotImplemented)()


class AbstractAsyncContextManager(abc.ABC):
    '''An abstract base class for asynchronous context managers.'''
    __class_getitem__ = classmethod(GenericAlias)
    __slots__ = ()
    
    async def __aenter__(self):
        '''Return `self` upon entering the runtime context.'''
        return self

    __aexit__ = (lambda self, exc_type, exc_value, traceback: pass)()
    __subclasshook__ = (lambda cls, C: _collections_abc._check_methods(C, '__aenter__', '__aexit__') if cls is AbstractAsyncContextManager else NotImplemented)()


class ContextDecorator(object):
    '''A base class or mixin that enables context managers to work as decorators.'''
    
    def _recreate_cm(self):
        '''Return a recreated instance of self.

Allows an otherwise one-shot context manager like
_GeneratorContextManager to support use as
a decorator via implicit recreation.

This is a private interface just for _GeneratorContextManager.
See issue #11647 for details.
'''
        return self

    
    def __call__(self, func):
        inner = (lambda : self._recreate_cm().__enter__()func(None, None, None)self._recreate_cm().__exit__)()
        return inner



class AsyncContextDecorator(object):
    '''A base class or mixin that enables async context managers to work as decorators.'''
    
    def _recreate_cm(self):
        '''Return a recreated instance of self.
        '''
        return self

    
    def __call__(self, func):
        inner = (lambda : # unsupported opcode GET_AWAITABLE# unsupported opcode SENDtry:
None# unsupported opcode CLEANUP_THROWtry:
None# unsupported opcode CLEANUP_THROWtry:
None# unsupported opcode CLEANUP_THROW# unsupported opcode GET_AWAITABLE# unsupported opcode SENDtry:
None# unsupported opcode CLEANUP_THROW# unsupported opcode END_SENDself._recreate_cm().__aenter__()self._recreate_cm().__aexit__Nonetry:
None# unsupported opcode CLEANUP_THROW# unsupported opcode GET_AWAITABLE# unsupported opcode SENDtry:
None# unsupported opcode CLEANUP_THROW# unsupported opcode END_SENDself._recreate_cm().__aenter__()self._recreate_cm().__aexit__None# unsupported opcode END_SENDself._recreate_cm().__aenter__()# unsupported opcode GET_AWAITABLE# unsupported opcode SENDtry:
None# unsupported opcode CLEANUP_THROWtry:
None# unsupported opcode CLEANUP_THROW# unsupported opcode GET_AWAITABLE# unsupported opcode SENDtry:
None# unsupported opcode CLEANUP_THROW# unsupported opcode END_SENDself._recreate_cm().__aenter__()self._recreate_cm().__aexit__Nonetry:
None# unsupported opcode CLEANUP_THROW# unsupported opcode GET_AWAITABLE# unsupported opcode SENDtry:
None# unsupported opcode CLEANUP_THROW# unsupported opcode END_SENDself._recreate_cm().__aenter__()self._recreate_cm().__aexit__None# unsupported opcode END_SEND# unsupported opcode GET_AWAITABLE# unsupported opcode SENDtry:
None# unsupported opcode CLEANUP_THROW# unsupported opcode GET_AWAITABLE# unsupported opcode SENDtry:
None# unsupported opcode CLEANUP_THROW# unsupported opcode END_SENDself._recreate_cm().__aenter__()self._recreate_cm().__aexit__None# unsupported opcode END_SENDfunc(None, None, None)self._recreate_cm().__aexit__# WARNING: Decompyle incomplete
)()
        return inner



class _GeneratorContextManagerBase:
    '''Shared functionality for @contextmanager and @asynccontextmanager.'''
    
    def __init__(self, func, args, kwds):
        '''__doc__'''
        self.gen = args(*{
            **kwds })
        self.func = func
        self.args = args
        self.kwds = kwds
        doc = getattr(func, '__doc__', None)
        if doc is None:
            doc = type(self).__doc__
        self.__doc__ = doc

    
    def _recreate_cm(self):
        return self.__class__(self.func, self.args, self.kwds)



class _GeneratorContextManager(ContextDecorator, AbstractContextManager, _GeneratorContextManagerBase):
    '''Helper for @contextmanager decorator.'''
    
    def __enter__(self):
        """generator didn't yield"""
        del self.args
        del self.kwds
        del self.func
        
        try:
            return next(self.gen)
        except StopIteration:
            raise RuntimeError("generator didn't yield") from None


    
    def __exit__(self, typ, value, traceback):
        if typ is None:
            
            try:
                next(self.gen)
            except StopIteration:
                return False

            
            try:
                raise RuntimeError("generator didn't stop")
            
            try:
                raise RuntimeError("generator didn't stop after throw()")


        if value is None:
            value = typ()
        
        try:
            self.gen.throw(value)
        except StopIteration as exc:
            return exc is not value
        except RuntimeError as exc:
            if exc is value:
                exc.__traceback__ = traceback
                return False
            if isinstance(value, StopIteration) and exc.__cause__ is value:
                value.__traceback__ = traceback
                return False
            raise
        except BaseException as exc:
            if exc is not value:
                raise
            exc.__traceback__ = traceback
            return False

        
        try:
            raise RuntimeError("generator didn't stop after throw()")

        
        try:
            raise RuntimeError("generator didn't stop")
        
        try:
            raise RuntimeError("generator didn't stop after throw()")


    # WARNING: Decompyle incomplete



class _AsyncGeneratorContextManager(AsyncContextDecorator, AbstractAsyncContextManager, _GeneratorContextManagerBase):
    '''Helper for @asynccontextmanager decorator.'''
    
    async def __aenter__(self):
        del self.args
        del self.kwds
        del self.func
        
        try:
            # unsupported opcode GET_AWAITABLE
            # unsupported opcode SEND
            
            try:
                yield None
            # unsupported opcode CLEANUP_THROW

            # unsupported opcode END_SEND
        except StopAsyncIteration:
            raise RuntimeError("generator didn't yield") from None

        return anext(self.gen)
    # WARNING: Decompyle incomplete

    
    async def __aexit__(self, typ, value, traceback):
        if typ is None:
            
            try:
                # unsupported opcode GET_AWAITABLE
                # unsupported opcode SEND
                
                try:
                    yield None
                # unsupported opcode CLEANUP_THROW
                
                try:
                    raise RuntimeError("generator didn't stop")
                # unsupported opcode GET_AWAITABLE
                # unsupported opcode SEND
                try:
                    yield None
                # unsupported opcode CLEANUP_THROW
                # unsupported opcode END_SEND
                
                try:
                    yield None
                # unsupported opcode CLEANUP_THROW
                
                try:
                    raise RuntimeError("generator didn't stop after athrow()")
                # unsupported opcode GET_AWAITABLE
                # unsupported opcode SEND
                try:
                    yield None
                # unsupported opcode CLEANUP_THROW
                # unsupported opcode END_SEND

                
                try:
                    raise RuntimeError("generator didn't stop after athrow()")
                # unsupported opcode GET_AWAITABLE
                # unsupported opcode SEND
                try:
                    yield None
                # unsupported opcode CLEANUP_THROW
                # unsupported opcode END_SEND



                
                try:
                    raise RuntimeError("generator didn't stop")
                # unsupported opcode GET_AWAITABLE
                # unsupported opcode SEND
                try:
                    yield None
                # unsupported opcode CLEANUP_THROW
                # unsupported opcode END_SEND
                
                try:
                    yield None
                # unsupported opcode CLEANUP_THROW
                
                try:
                    raise RuntimeError("generator didn't stop after athrow()")
                # unsupported opcode GET_AWAITABLE
                # unsupported opcode SEND
                try:
                    yield None
                # unsupported opcode CLEANUP_THROW
                # unsupported opcode END_SEND

                
                try:
                    raise RuntimeError("generator didn't stop after athrow()")
                # unsupported opcode GET_AWAITABLE
                # unsupported opcode SEND
                try:
                    yield None
                # unsupported opcode CLEANUP_THROW
                # unsupported opcode END_SEND




                # unsupported opcode END_SEND
                anext(self.gen)
            except StopAsyncIteration:
                return False

            
            try:
                raise RuntimeError("generator didn't stop")
            # unsupported opcode GET_AWAITABLE
            # unsupported opcode SEND
            try:
                yield None
            # unsupported opcode CLEANUP_THROW
            # unsupported opcode END_SEND
            
            try:
                yield None
            # unsupported opcode CLEANUP_THROW
            
            try:
                raise RuntimeError("generator didn't stop after athrow()")
            # unsupported opcode GET_AWAITABLE
            # unsupported opcode SEND
            try:
                yield None
            # unsupported opcode CLEANUP_THROW
            # unsupported opcode END_SEND

            
            try:
                raise RuntimeError("generator didn't stop after athrow()")
            # unsupported opcode GET_AWAITABLE
            # unsupported opcode SEND
            try:
                yield None
            # unsupported opcode CLEANUP_THROW
            # unsupported opcode END_SEND



        if value is None:
            value = typ()
        
        try:
            # unsupported opcode GET_AWAITABLE
            # unsupported opcode SEND
            
            try:
                yield None
            # unsupported opcode CLEANUP_THROW
            
            try:
                raise RuntimeError("generator didn't stop after athrow()")
            # unsupported opcode GET_AWAITABLE
            # unsupported opcode SEND
            try:
                yield None
            # unsupported opcode CLEANUP_THROW
            # unsupported opcode END_SEND

            
            try:
                raise RuntimeError("generator didn't stop after athrow()")
            # unsupported opcode GET_AWAITABLE
            # unsupported opcode SEND
            try:
                yield None
            # unsupported opcode CLEANUP_THROW
            # unsupported opcode END_SEND


            # unsupported opcode END_SEND
            self.gen.athrow(value)
        except StopAsyncIteration as exc:
            return exc is not value
        except RuntimeError as exc:
            if exc is value:
                exc.__traceback__ = traceback
                return False
            if isinstance(value, (StopIteration, StopAsyncIteration)) and exc.__cause__ is value:
                value.__traceback__ = traceback
                return False
            raise
        except BaseException as exc:
            if exc is not value:
                raise
            exc.__traceback__ = traceback
            return False

        
        try:
            raise RuntimeError("generator didn't stop after athrow()")
        # unsupported opcode GET_AWAITABLE
        # unsupported opcode SEND
        try:
            yield None
        # unsupported opcode CLEANUP_THROW
        # unsupported opcode END_SEND

        
        try:
            yield None
        # unsupported opcode CLEANUP_THROW
        
        try:
            raise RuntimeError("generator didn't stop")
        # unsupported opcode GET_AWAITABLE
        # unsupported opcode SEND
        try:
            yield None
        # unsupported opcode CLEANUP_THROW
        # unsupported opcode END_SEND
        
        try:
            yield None
        # unsupported opcode CLEANUP_THROW
        
        try:
            raise RuntimeError("generator didn't stop after athrow()")
        # unsupported opcode GET_AWAITABLE
        # unsupported opcode SEND
        try:
            yield None
        # unsupported opcode CLEANUP_THROW
        # unsupported opcode END_SEND

        
        try:
            raise RuntimeError("generator didn't stop after athrow()")
        # unsupported opcode GET_AWAITABLE
        # unsupported opcode SEND
        try:
            yield None
        # unsupported opcode CLEANUP_THROW
        # unsupported opcode END_SEND



        
        try:
            raise RuntimeError("generator didn't stop")
        # unsupported opcode GET_AWAITABLE
        # unsupported opcode SEND
        try:
            yield None
        # unsupported opcode CLEANUP_THROW
        # unsupported opcode END_SEND
        
        try:
            yield None
        # unsupported opcode CLEANUP_THROW
        
        try:
            raise RuntimeError("generator didn't stop after athrow()")
        # unsupported opcode GET_AWAITABLE
        # unsupported opcode SEND
        try:
            yield None
        # unsupported opcode CLEANUP_THROW
        # unsupported opcode END_SEND

        
        try:
            raise RuntimeError("generator didn't stop after athrow()")
        # unsupported opcode GET_AWAITABLE
        # unsupported opcode SEND
        try:
            yield None
        # unsupported opcode CLEANUP_THROW
        # unsupported opcode END_SEND




    # WARNING: Decompyle incomplete



def contextmanager(func):
    '''@contextmanager decorator.

Typical usage:

    @contextmanager
    def some_generator(<arguments>):
        <setup>
        try:
            yield <value>
        finally:
            <cleanup>

This makes this:

    with some_generator(<arguments>) as <variable>:
        <body>

equivalent to this:

    <setup>
    try:
        <variable> = <value>
        <body>
    finally:
        <cleanup>
'''
    helper = (lambda : _GeneratorContextManager(func, args, kwds))()
    return helper


def asynccontextmanager(func):
    '''@asynccontextmanager decorator.

Typical usage:

    @asynccontextmanager
    async def some_async_generator(<arguments>):
        <setup>
        try:
            yield <value>
        finally:
            <cleanup>

This makes this:

    async with some_async_generator(<arguments>) as <variable>:
        <body>

equivalent to this:

    <setup>
    try:
        <variable> = <value>
        <body>
    finally:
        <cleanup>
'''
    helper = (lambda : _AsyncGeneratorContextManager(func, args, kwds))()
    return helper


class closing(AbstractContextManager):
    '''Context to automatically close something at the end of a block.

Code like this:

    with closing(<module>.open(<arguments>)) as f:
        <block>

is equivalent to this:

    f = <module>.open(<arguments>)
    try:
        <block>
    finally:
        f.close()

'''
    
    def __init__(self, thing):
        self.thing = thing

    
    def __enter__(self):
        return self.thing

    
    def __exit__(self, *exc_info):
        self.thing.close()



class aclosing(AbstractAsyncContextManager):
    '''Async context manager for safely finalizing an asynchronously cleaned-up
resource such as an async generator, calling its ``aclose()`` method.

Code like this:

    async with aclosing(<module>.fetch(<arguments>)) as agen:
        <block>

is equivalent to this:

    agen = <module>.fetch(<arguments>)
    try:
        <block>
    finally:
        await agen.aclose()

'''
    
    def __init__(self, thing):
        self.thing = thing

    
    async def __aenter__(self):
        return self.thing

    
    async def __aexit__(self, *exc_info):
        # unsupported opcode GET_AWAITABLE
        # unsupported opcode SEND
        
        try:
            yield None
        # unsupported opcode CLEANUP_THROW

        # unsupported opcode END_SEND
        self.thing.aclose()
        return None
    # WARNING: Decompyle incomplete



class _RedirectStream(AbstractContextManager):
    _stream = None
    
    def __init__(self, new_target):
        self._new_target = new_target
        self._old_targets = []

    
    def __enter__(self):
        self._old_targets.append(getattr(sys, self._stream))
        setattr(sys, self._stream, self._new_target)
        return self._new_target

    
    def __exit__(self, exctype, excinst, exctb):
        setattr(sys, self._stream, self._old_targets.pop())



class redirect_stdout(_RedirectStream):
    """Context manager for temporarily redirecting stdout to another file.

# How to send help() to stderr
with redirect_stdout(sys.stderr):
    help(dir)

# How to write help() to a file
with open('help.txt', 'w') as f:
    with redirect_stdout(f):
        help(pow)
"""
    _stream = 'stdout'


class redirect_stderr(_RedirectStream):
    '''Context manager for temporarily redirecting stderr to another file.'''
    _stream = 'stderr'


class suppress(AbstractContextManager):
    '''Context manager to suppress specified exceptions

After the exception is suppressed, execution proceeds with the next
statement following the with statement.

     with suppress(FileNotFoundError):
         os.remove(somefile)
     # Execution still resumes here if the file was already removed
'''
    
    def __init__(self, *exceptions):
        self._exceptions = exceptions

    
    def __enter__(self):
        pass

    
    def __exit__(self, exctype, excinst, exctb):
        if exctype is None:
            return None
        if issubclass(exctype, self._exceptions):
            return True
        if issubclass(exctype, BaseExceptionGroup):
            match, rest = excinst.split(self._exceptions)
            if rest is None:
                return True
            raise rest
        return False



class _BaseExitStack:
    '''A base class for ExitStack and AsyncExitStack.'''
    _create_exit_wrapper = (lambda cm, cm_exit: MethodType(cm_exit, cm))()
    _create_cb_wrapper = (lambda callback: 
def _exit_wrapper(exc_type, exc, tb):
args(*{
**kwds })_exit_wrapper)()
    
    def __init__(self):
        self._exit_callbacks = deque()

    
    def pop_all(self):
        '''Preserve the context stack by transferring it to a new instance.'''
        new_stack = type(self)()
        new_stack._exit_callbacks = self._exit_callbacks
        self._exit_callbacks = deque()
        return new_stack

    
    def push(self, exit):
        '''Registers a callback with the standard __exit__ method signature.

Can suppress exceptions the same way __exit__ method can.
Also accepts any object with an __exit__ method (registering a call
to the method instead of the object itself).
'''
        _cb_type = type(exit)
        
        try:
            exit_method = _cb_type.__exit__
        except AttributeError:
            self._push_exit_callback(exit)
            return exit

        self._push_cm_exit(exit, exit_method)
        return exit

    
    def enter_context(self, cm):
        '''Enters the supplied context manager.

If successful, also pushes its __exit__ method as a callback and
returns the result of the __enter__ method.
'''
        cls = type(cm)
        
        try:
            _enter = cls.__enter__
            _exit = cls.__exit__
        except AttributeError:
            raise TypeError(f'''\'{cls.__module__}.{cls.__qualname__}\' object does not support the context manager protocol''') from None

        result = _enter(cm)
        self._push_cm_exit(cm, _exit)
        return result

    
    def callback(self, callback, *args, **kwds):
        '''Registers an arbitrary callback and arguments.

Cannot suppress exceptions.
'''
        # unsupported CALL_INTRINSIC_1 6
        _exit_wrapper = self._create_cb_wrapper(*{
            **kwds })
        _exit_wrapper.__wrapped__ = callback
        self._push_exit_callback(_exit_wrapper)
        return callback
    # WARNING: Decompyle incomplete

    
    def _push_cm_exit(self, cm, cm_exit):
        '''Helper to correctly register callbacks to __exit__ methods.'''
        _exit_wrapper = self._create_exit_wrapper(cm, cm_exit)
        self._push_exit_callback(_exit_wrapper, True)

    
    def _push_exit_callback(self, callback, is_sync = True):
        self._exit_callbacks.append((is_sync, callback))



class ExitStack(AbstractContextManager, _BaseExitStack):
    '''Context manager for dynamic management of a stack of exit callbacks.

For example:
    with ExitStack() as stack:
        files = [stack.enter_context(open(fname)) for fname in filenames]
        # All opened files will automatically be closed at the end of
        # the with statement, even if attempts to open files later
        # in the list raise an exception.
'''
    
    def __enter__(self):
        return self

    
    def __exit__(self, *exc_details):
        exc = exc_details[1]
        received_exc = exc is not None
        frame_exc = sys.exception()
        
        def _fix_exception_context(new_exc, old_exc):
            exc_context = new_exc.__context__
            if not (exc_context is not None) or exc_context is old_exc:
                return None
            if exc_context is frame_exc:
                pass
            else:
                new_exc = exc_context
            new_exc.__context__ = old_exc

        suppressed_exc = False
        pending_raise = False
        while self._exit_callbacks:
            is_sync, cb = self._exit_callbacks.pop()
            if not is_sync:
                raise AssertionError
            
            try:
                if exc is None:
                    exc_details = (None, None, None)
                else:
                    exc_details = (type(exc), exc, exc.__traceback__)
                if exc_details():
                    suppressed_exc = True
                    pending_raise = False
                    exc = None
                    continue
            except BaseException as new_exc:
                _fix_exception_context(new_exc, exc)
                pending_raise = True
                exc = new_exc

        if pending_raise:
            
            try:
                fixed_ctx = exc.__context__
                raise exc
            except BaseException:
                exc.__context__ = fixed_ctx
                raise

        return received_exc and suppressed_exc

    
    def close(self):
        '''Immediately unwind the context stack.'''
        self.__exit__(None, None, None)



class AsyncExitStack(AbstractAsyncContextManager, _BaseExitStack):
    '''Async context manager for dynamic management of a stack of exit
callbacks.

For example:
    async with AsyncExitStack() as stack:
        connections = [await stack.enter_async_context(get_connection())
            for i in range(5)]
        # All opened connections will automatically be released at the
        # end of the async with statement, even if attempts to open a
        # connection later in the list raise an exception.
'''
    _create_async_exit_wrapper = (lambda cm, cm_exit: MethodType(cm_exit, cm))()
    _create_async_cb_wrapper = (lambda callback: 
async def _exit_wrapper(exc_type, exc, tb):
# unsupported opcode GET_AWAITABLE# unsupported opcode SENDtry:
None# unsupported opcode CLEANUP_THROW# unsupported opcode END_SENDargs(*{
**kwds })None# WARNING: Decompyle incomplete
_exit_wrapper)()
    
    async def enter_async_context(self, cm):
        '''Enters the supplied async context manager.

If successful, also pushes its __aexit__ method as a callback and
returns the result of the __aenter__ method.
'''
        cls = type(cm)
        
        try:
            _enter = cls.__aenter__
            _exit = cls.__aexit__
        except AttributeError:
            raise TypeError(f'''\'{cls.__module__}.{cls.__qualname__}\' object does not support the asynchronous context manager protocol''') from None

        # unsupported opcode GET_AWAITABLE
        # unsupported opcode SEND
        
        try:
            yield None
        # unsupported opcode CLEANUP_THROW

        # unsupported opcode END_SEND
        result = _enter(cm)
        self._push_async_cm_exit(cm, _exit)
        return result
    # WARNING: Decompyle incomplete

    
    def push_async_exit(self, exit):
        '''Registers a coroutine function with the standard __aexit__ method
signature.

Can suppress exceptions the same way __aexit__ method can.
Also accepts any object with an __aexit__ method (registering a call
to the method instead of the object itself).
'''
        _cb_type = type(exit)
        
        try:
            exit_method = _cb_type.__aexit__
        except AttributeError:
            self._push_exit_callback(exit, False)
            return exit

        self._push_async_cm_exit(exit, exit_method)
        return exit

    
    def push_async_callback(self, callback, *args, **kwds):
        '''Registers an arbitrary coroutine function and arguments.

Cannot suppress exceptions.
'''
        # unsupported CALL_INTRINSIC_1 6
        _exit_wrapper = self._create_async_cb_wrapper(*{
            **kwds })
        _exit_wrapper.__wrapped__ = callback
        self._push_exit_callback(_exit_wrapper, False)
        return callback
    # WARNING: Decompyle incomplete

    
    async def aclose(self):
        '''Immediately unwind the context stack.'''
        # unsupported opcode GET_AWAITABLE
        # unsupported opcode SEND
        
        try:
            yield None
        # unsupported opcode CLEANUP_THROW

        # unsupported opcode END_SEND
        self.__aexit__(None, None, None)
        return None
    # WARNING: Decompyle incomplete

    
    def _push_async_cm_exit(self, cm, cm_exit):
        '''Helper to correctly register coroutine function to __aexit__
method.'''
        _exit_wrapper = self._create_async_exit_wrapper(cm, cm_exit)
        self._push_exit_callback(_exit_wrapper, False)

    
    async def __aenter__(self):
        return self

    
    async def __aexit__(self, *exc_details):
        exc = exc_details[1]
        received_exc = exc is not None
        frame_exc = sys.exception()
        
        def _fix_exception_context(new_exc, old_exc):
            exc_context = new_exc.__context__
            if not (exc_context is not None) or exc_context is old_exc:
                return None
            if exc_context is frame_exc:
                pass
            else:
                new_exc = exc_context
            new_exc.__context__ = old_exc

        suppressed_exc = False
        pending_raise = False
        while self._exit_callbacks:
            is_sync, cb = self._exit_callbacks.pop()
            
            try:
                if exc is None:
                    exc_details = (None, None, None)
                else:
                    exc_details = (type(exc), exc, exc.__traceback__)
                if is_sync:
                    cb_suppress = exc_details()
                else:
                    # unsupported opcode GET_AWAITABLE
                    # unsupported opcode SEND
                    
                    try:
                        yield None
                    # unsupported opcode CLEANUP_THROW

                    continue
                    # unsupported opcode END_SEND
                    cb_suppress = exc_details()
                if cb_suppress:
                    suppressed_exc = True
                    pending_raise = False
                    exc = None
                    continue
            except BaseException as new_exc:
                _fix_exception_context(new_exc, exc)
                pending_raise = True
                exc = new_exc

        if pending_raise:
            
            try:
                fixed_ctx = exc.__context__
                raise exc
            except BaseException:
                exc.__context__ = fixed_ctx
                raise

        return received_exc and suppressed_exc
    # WARNING: Decompyle incomplete



class nullcontext(AbstractAsyncContextManager, AbstractContextManager):
    '''Context manager that does no additional processing.

Used as a stand-in for a normal context manager, when a particular
block of code is only sometimes used with a normal context manager:

cm = optional_cm if condition else nullcontext()
with cm:
    # Perform operation, using optional_cm if condition is True
'''
    
    def __init__(self, enter_result = None):
        self.enter_result = enter_result

    
    def __enter__(self):
        return self.enter_result

    
    def __exit__(self, *excinfo):
        pass

    
    async def __aenter__(self):
        return self.enter_result

    
    async def __aexit__(self, *excinfo):
        pass



class chdir(AbstractContextManager):
    '''Non thread-safe context manager to change the current working directory.'''
    
    def __init__(self, path):
        self.path = path
        self._old_cwd = []

    
    def __enter__(self):
        self._old_cwd.append(os.getcwd())
        os.chdir(self.path)

    
    def __exit__(self, *excinfo):
        os.chdir(self._old_cwd.pop())


