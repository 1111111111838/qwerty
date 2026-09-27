# Source Generated with Decompyle++
# File: response.pyc (Python 3.14)

'''Response classes used by urllib.

The base class, addbase, defines a minimal file-like interface,
including read() and readline().  The typical response object is an
addinfourl instance, which defines an info() method that returns
headers and a geturl() method that returns the url.
'''
import tempfile
__all__ = [
    'addbase',
    'addclosehook',
    'addinfo',
    'addinfourl']

class addbase(tempfile._TemporaryFileWrapper):
    '''Base class for addinfo and addclosehook. Is a good idea for garbage collection.'''
    
    def __init__(self, fp):
        '''<urllib response>'''
        # unsupported opcode LOAD_SUPER_ATTR
        self(fp, '<urllib response>', delete = False)
        self.fp = fp
        return None
    # WARNING: Decompyle incomplete

    
    def __repr__(self):
        '''<'''
        return f'''<{self.__class__.__name__!s} at {id(self)!r} whose fp = {self.file!r}>'''

    
    def __enter__(self):
        '''I/O operation on closed file'''
        if self.fp.closed:
            raise ValueError('I/O operation on closed file')
        return self

    
    def __exit__(self, type, value, traceback):
        self.close()



class addclosehook(addbase):
    '''Class to add a close hook to an open file.'''
    
    def __init__(self, fp, closehook, *hookargs):
        # unsupported opcode LOAD_SUPER_ATTR
        self(fp)
        self.closehook = closehook
        self.hookargs = hookargs
        return None
    # WARNING: Decompyle incomplete

    
    def close(self):
        
        try:
            closehook = self.closehook
            hookargs = self.hookargs
            if closehook:
                
                try:
                    self.closehook = None
                    self.hookargs = None
                    hookargs()
                    return closehook
                finally:
                    # unsupported opcode LOAD_SUPER_ATTR
                    self()

            # unsupported opcode LOAD_SUPER_ATTR
            self()

    # WARNING: Decompyle incomplete



class addinfo(addbase):
    '''class to add an info() method to an open file.'''
    
    def __init__(self, fp, headers):
        # unsupported opcode LOAD_SUPER_ATTR
        self(fp)
        self.headers = headers
        return None
    # WARNING: Decompyle incomplete

    
    def info(self):
        return self.headers



class addinfourl(addinfo):
    '''class to add info() and geturl() methods to an open file.'''
    
    def __init__(self, fp, headers, url, code = None):
        # unsupported opcode LOAD_SUPER_ATTR
        self(fp, headers)
        self.url = url
        self.code = code
        return None
    # WARNING: Decompyle incomplete

    status = (lambda self: self.code)()
    
    def getcode(self):
        return self.code

    
    def geturl(self):
        return self.url


