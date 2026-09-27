# Source Generated with Decompyle++
# File: _util.pyc (Python 3.14)

from __future__ import annotations
import os
TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any, NoReturn, TypeGuard
    from ._typing import StrOrBytesPath

def is_path(f):
    return isinstance(f, (bytes, str, os.PathLike))


class DeferredError:
    
    def __init__(self, ex):
        self.ex = ex

    
    def __getattr__(self, elt):
        raise self.ex

    new = (lambda ex: DeferredError(ex))()

