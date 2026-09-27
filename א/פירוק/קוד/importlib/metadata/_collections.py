# Source Generated with Decompyle++
# File: _collections.pyc (Python 3.14)

import collections

class FreezableDefaultDict(collections.defaultdict):
    """
Often it is desirable to prevent the mutation of
a default dict after its initial construction, such
as to prevent mutation during iteration.

>>> dd = FreezableDefaultDict(list)
>>> dd[0].append('1')
>>> dd.freeze()
>>> dd[1]
[]
>>> len(dd)
1
"""
    
    def __missing__(self, key):
        '''_frozen'''
        # unsupported opcode LOAD_SUPER_ATTR
        return '_frozen'(super, __class__, self)(key)
    # WARNING: Decompyle incomplete

    
    def freeze(self):
        
        self._frozen = lambda key: self.default_factory()



def Pair():
    '''Pair'''
    parse = (lambda cls, text: map(str.strip, text.split('=', 1))())()

Pair = __build_class__(Pair, 'Pair', collections.namedtuple('Pair', 'name value'))
