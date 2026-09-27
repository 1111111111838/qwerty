# Source Generated with Decompyle++
# File: signal.pyc (Python 3.14)

import _signal
from _signal import *
from enum import IntEnum as _IntEnum
_globals = globals()
_IntEnum._convert_('Signals', __name__, (lambda name: name.startswith('SIG') and not name.startswith('SIG_') or name.startswith('CTRL_')))
_IntEnum._convert_('Handlers', __name__, (lambda name: name in ('SIG_DFL', 'SIG_IGN')))
if 'pthread_sigmask' in _globals:
    _IntEnum._convert_('Sigmasks', __name__, (lambda name: name in ('SIG_BLOCK', 'SIG_UNBLOCK', 'SIG_SETMASK')))

def _int_to_enum(value, enum_klass):
    """Convert a possible numeric value to an IntEnum member.
If it's not a known member, return the value itself.
"""
    if not isinstance(value, int):
        return value
    
    try:
        return enum_klass(value)
    except ValueError:
        return value



def _enum_to_int(value):
    """Convert an IntEnum member to a numeric value.
If it's not an IntEnum member return the value itself.
"""
    
    try:
        return int(value)
    except (ValueError, TypeError):
        return value



def _wraps(wrapped):
    
    def decorator(wrapper):
        wrapper.__doc__ = wrapped.__doc__
        return wrapper

    return decorator

signal = (lambda signalnum, handler: handler = _signal.signal(_enum_to_int(signalnum), _enum_to_int(handler))_int_to_enum(handler, Handlers))()
getsignal = (lambda signalnum: handler = _signal.getsignal(signalnum)_int_to_enum(handler, Handlers))()
if 'pthread_sigmask' in _globals:
    pthread_sigmask = (lambda how, mask: sigs_set = _signal.pthread_sigmask(how, mask)(lambda .0: for x in .0:
_int_to_enum(x, Signals).0)(sigs_set())
)()
if 'sigpending' in _globals:
    sigpending = (lambda : None# WARNING: Decompyle incomplete
)()
if 'sigwait' in _globals:
    sigwait = (lambda sigset: retsig = _signal.sigwait(sigset)_int_to_enum(retsig, Signals))()
if 'valid_signals' in _globals:
    valid_signals = (lambda : None# WARNING: Decompyle incomplete
)()
del _globals
del _wraps
