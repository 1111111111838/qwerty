# Source Generated with Decompyle++
# File: _adapters.pyc (Python 3.14)

import functools
import warnings
import re
import textwrap
import email.message as email
from ._text import FoldedCase
_warn = functools.partial(warnings.warn, 'Implicit None on return values is deprecated and will raise KeyErrors.', DeprecationWarning, stacklevel = 2)

class Message(email.message.Message):
    multiple_use_keys = set(map(FoldedCase, [
        'Classifier',
        'Obsoletes-Dist',
        'Platform',
        'Project-URL',
        'Provides-Dist',
        'Provides-Extra',
        'Requires-Dist',
        'Requires-External',
        'Supported-Platform',
        'Dynamic']))
    
    def __new__(cls, orig):
        # unsupported opcode LOAD_SUPER_ATTR
        res = cls(cls)
        vars(res).update(vars(orig))
        return res
    # WARNING: Decompyle incomplete

    
    def __init__(self, *args, **kwargs):
        self._headers = self._repair_headers()

    
    def __iter__(self):
        # unsupported opcode LOAD_SUPER_ATTR
        return self()
    # WARNING: Decompyle incomplete

    
    def __getitem__(self, item):
        '''
Warn users that a ``KeyError`` can be expected when a
missing key is supplied. Ref python/importlib_metadata#371.
'''
        # unsupported opcode LOAD_SUPER_ATTR
        res = self(item)
        if res is None:
            _warn()
        return res
    # WARNING: Decompyle incomplete

    
    def _repair_headers(self):
        
        def redent(value):
            '''Correct for RFC822 indentation'''
            if not value or '\n' not in value:
                return value
            return textwrap.dedent('        ' + value)

        
        try:
            for key, value in vars(self)['_headers']:
                pass
        value = vars(self)['_headers']
        key = value

        headers = []
        key = key
        value = value
        if self._payload:
            headers.append(('Description', self.get_payload()))
        return headers
    # WARNING: Decompyle incomplete

    json = (lambda self: 
def transform(key):
'''Keywords'''
value = self.get_all(key) if key in self.multiple_use_keys else self[key]if key == 'Keywords':
value = re.split('\\s+', value)tk = key.lower().replace('-', '_')(tk, value)dict(map(transform, map(FoldedCase, self))))()

