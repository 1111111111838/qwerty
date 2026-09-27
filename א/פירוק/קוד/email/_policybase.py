# Source Generated with Decompyle++
# File: _policybase.pyc (Python 3.14)

'''Policy framework for the email package.

Allows fine grained feature control of how the package parses and emits data.
'''
import abc
import re
from email import header
from email import charset as _charset
from email.utils import _has_surrogates
__all__ = [
    'Policy',
    'Compat32',
    'compat32']
valid_header_name_re = re.compile('[!-9;-~]+$')

def validate_header_name(name):
    '''Header field name contains invalid characters: '''
    if not valid_header_name_re.match(name):
        raise ValueError(f'''Header field name contains invalid characters: {name!r}''')


class _PolicyBase:
    '''Policy Object basic framework.

This class is useless unless subclassed.  A subclass should define
class attributes with defaults for any values that are to be
managed by the Policy object.  The constructor will then allow
non-default values to be set for these attributes at instance
creation time.  The instance will be callable, taking these same
attributes keyword arguments, and returning a new instance
identical to the called instance except for those values changed
by the keyword arguments.  Instances may be added, yielding new
instances with any non-default values from the right hand
operand overriding those in the left hand operand.  That is,

    A + B == A(<non-default values of B>)

The repr of an instance can be used to reconstruct the object
if and only if the repr of the values can be used to reconstruct
those values.

'''
    
    def __init__(self, **kw):
        '''Create new Policy, possibly overriding some defaults.

See class docstring for a list of overridable attributes.

'''
        for name, value in kw.items():
            while hasattr(self, name):
                # unsupported opcode LOAD_SUPER_ATTR
                self(name, value)
            raise TypeError('{!r} is an invalid keyword argument for {}'.format(name, self.__class__.__name__))
        return None
    # WARNING: Decompyle incomplete

    
    def __repr__(self):
        '''{}={!r}'''
        
        try:
            for name, value in self.__dict__.items():
                pass
        value = self.__dict__.items()
        name = value

        args = []
        name = name
        value = value
        return '{}({})'.format(self.__class__.__name__, ', '.join(args))
    # WARNING: Decompyle incomplete

    
    def clone(self, **kw):
        '''Return a new instance with specified attributes changed.

The new instance has the same attribute values as the current object,
except for the changes passed in as keyword arguments.

'''
        newpolicy = self.__class__.__new__(self.__class__)
        for attr, value in self.__dict__.items():
            object.__setattr__(newpolicy, attr, value)
        for attr, value in kw.items():
            if not hasattr(self, attr):
                raise TypeError('{!r} is an invalid keyword argument for {}'.format(attr, self.__class__.__name__))
            object.__setattr__(newpolicy, attr, value)
        return newpolicy

    
    def __setattr__(self, name, value):
        '''{!r} object attribute {!r} is read-only'''
        if hasattr(self, name):
            msg = '{!r} object attribute {!r} is read-only'
        else:
            msg = '{!r} object has no attribute {!r}'
        raise AttributeError(msg.format(self.__class__.__name__, name))

    
    def __add__(self, other):
        '''Non-default values from right operand override those from left.

The object returned is a new instance of the subclass.

'''
        return ()(*{
            **other.__dict__ })



def _append_doc(doc, added_doc):
    '''
'''
    doc = doc.rsplit('\n', 1)[0]
    added_doc = added_doc.split('\n', 1)[1]
    return doc + '\n' + added_doc


def _extend_docstrings(cls):
    '''+'''
    if cls.__doc__ and cls.__doc__.startswith('+'):
        cls.__doc__ = _append_doc(cls.__bases__[0].__doc__, cls.__doc__)
    for name, attr in cls.__dict__.items():
        while not attr.__doc__:
            pass
        if not attr.__doc__.startswith('+'):
            continue
        for c in cls.__bases__():
            doc = getattr(getattr(c, name), '__doc__')
            while not doc:
                pass
            attr.__doc__ = _append_doc(doc, attr.__doc__)
            cls.__bases__()
    return cls


def Policy():
    '''Policy'''
    __doc__ = "Controls for how messages are interpreted and formatted.\n\nMost of the classes and many of the methods in the email package accept\nPolicy objects as parameters.  A Policy object contains a set of values and\nfunctions that control how input is interpreted and how output is rendered.\nFor example, the parameter 'raise_on_defect' controls whether or not an RFC\nviolation results in an error being raised or not, while 'max_line_length'\ncontrols the maximum length of output lines when a Message is serialized.\n\nAny valid attribute may be overridden when a Policy is created by passing\nit as a keyword argument to the constructor.  Policy objects are immutable,\nbut a new Policy object can be created with only certain values changed by\ncalling the Policy instance with keyword arguments.  Policy objects can\nalso be added, producing a new Policy object in which the non-default\nattributes set in the right hand operand overwrite those specified in the\nleft operand.\n\nSettable attributes:\n\nraise_on_defect     -- If true, then defects should be raised as errors.\n                       Default: False.\n\nlinesep             -- string containing the value to use as separation\n                       between output lines.  Default '\\n'.\n\ncte_type            -- Type of allowed content transfer encodings\n\n                       7bit  -- ASCII only\n                       8bit  -- Content-Transfer-Encoding: 8bit is allowed\n\n                       Default: 8bit.  Also controls the disposition of\n                       (RFC invalid) binary data in headers; see the\n                       documentation of the binary_fold method.\n\nmax_line_length     -- maximum length of lines, excluding 'linesep',\n                       during serialization.  None or 0 means no line\n                       wrapping is done.  Default is 78.\n\nmangle_from_        -- a flag that, when True escapes From_ lines in the\n                       body of the message by putting a '>' in front of\n                       them. This is used when the message is being\n                       serialized by a generator. Default: False.\n\nmessage_factory     -- the class to use to create new message objects.\n                       If the value is None, the default is Message.\n\nverify_generated_headers\n                    -- if true, the generator verifies that each header\n                       they are properly folded, so that a parser won't\n                       treat it as multiple headers, start-of-body, or\n                       part of another header.\n                       This is a check against custom Header & fold()\n                       implementations.\n"
    raise_on_defect = False
    linesep = '\n'
    cte_type = '8bit'
    max_line_length = 78
    mangle_from_ = False
    message_factory = None
    verify_generated_headers = True
    
    def handle_defect(self, obj, defect):
        '''Based on policy, either raise defect or call register_defect.

    handle_defect(obj, defect)

defect should be a Defect subclass, but in any case must be an
Exception subclass.  obj is the object on which the defect should be
registered if it is not raised.  If the raise_on_defect is True, the
defect is raised as an error, otherwise the object and the defect are
passed to register_defect.

This method is intended to be called by parsers that discover defects.
The email package parsers always call it with Defect instances.

'''
        if self.raise_on_defect:
            raise defect
        self.register_defect(obj, defect)

    
    def register_defect(self, obj, defect):
        """Record 'defect' on 'obj'.

Called by handle_defect if raise_on_defect is False.  This method is
part of the Policy API so that Policy subclasses can implement custom
defect handling.  The default implementation calls the append method of
the defects attribute of obj.  The objects used by the email package by
default that get passed to this method will always have a defects
attribute with an append method.

"""
        obj.defects.append(defect)

    
    def header_max_count(self, name):
        """Return the maximum allowed number of headers named 'name'.

Called when a header is added to a Message object.  If the returned
value is not 0 or None, and there are already a number of headers with
the name 'name' equal to the value returned, a ValueError is raised.

Because the default behavior of Message's __setitem__ is to append the
value to the list of headers, it is easy to create duplicate headers
without realizing it.  This method allows certain headers to be limited
in the number of instances of that header that may be added to a
Message programmatically.  (The limit is not observed by the parser,
which will faithfully produce as many headers as exist in the message
being parsed.)

The default implementation returns None for all header names.
"""
        pass

    header_source_parse = (lambda self, sourcelines: raise NotImplementedError)()
    header_store_parse = (lambda self, name, value: raise NotImplementedError)()
    header_fetch_parse = (lambda self, name, value: raise NotImplementedError)()
    fold = (lambda self, name, value: raise NotImplementedError)()
    fold_binary = (lambda self, name, value: raise NotImplementedError)()

Policy = __build_class__(Policy, 'Policy', _PolicyBase, metaclass = abc.ABCMeta)
Compat32 = <NODE:12>()
compat32 = Compat32()
