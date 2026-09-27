# Source Generated with Decompyle++
# File: _compat_pickle.pyc (Python 3.14)

IMPORT_MAPPING = {
    '__builtin__': 'builtins',
    'copy_reg': 'copyreg',
    'Queue': 'queue',
    'SocketServer': 'socketserver',
    'ConfigParser': 'configparser',
    'repr': 'reprlib',
    'tkFileDialog': 'tkinter.filedialog',
    'tkSimpleDialog': 'tkinter.simpledialog',
    'tkColorChooser': 'tkinter.colorchooser',
    'tkCommonDialog': 'tkinter.commondialog',
    'Dialog': 'tkinter.dialog',
    'Tkdnd': 'tkinter.dnd',
    'tkFont': 'tkinter.font',
    'tkMessageBox': 'tkinter.messagebox',
    'ScrolledText': 'tkinter.scrolledtext',
    'Tkconstants': 'tkinter.constants',
    'ttk': 'tkinter.ttk',
    'Tkinter': 'tkinter',
    'markupbase': '_markupbase',
    '_winreg': 'winreg',
    'thread': '_thread',
    'dummy_thread': '_dummy_thread',
    'dbhash': 'dbm.bsd',
    'dumbdbm': 'dbm.dumb',
    'dbm': 'dbm.ndbm',
    'gdbm': 'dbm.gnu',
    'xmlrpclib': 'xmlrpc.client',
    'SimpleXMLRPCServer': 'xmlrpc.server',
    'httplib': 'http.client',
    'htmlentitydefs': 'html.entities',
    'HTMLParser': 'html.parser',
    'Cookie': 'http.cookies',
    'cookielib': 'http.cookiejar',
    'BaseHTTPServer': 'http.server',
    '_abcoll': 'collections.abc',
    'anydbm': 'dbm',
    'urllib2': 'urllib.request',
    'robotparser': 'urllib.robotparser',
    'urlparse': 'urllib.parse',
    'commands': 'subprocess',
    'test.test_support': 'test.support' }
NAME_MAPPING = {
    ('__builtin__', 'xrange'): ('builtins', 'range'),
    ('__builtin__', 'reduce'): ('functools', 'reduce'),
    ('__builtin__', 'intern'): ('sys', 'intern'),
    ('__builtin__', 'unichr'): ('builtins', 'chr'),
    ('__builtin__', 'unicode'): ('builtins', 'str'),
    ('__builtin__', 'long'): ('builtins', 'int'),
    ('itertools', 'izip'): ('builtins', 'zip'),
    ('itertools', 'imap'): ('builtins', 'map'),
    ('itertools', 'ifilter'): ('builtins', 'filter'),
    ('itertools', 'ifilterfalse'): ('itertools', 'filterfalse'),
    ('itertools', 'izip_longest'): ('itertools', 'zip_longest'),
    ('UserDict', 'IterableUserDict'): ('collections', 'UserDict'),
    ('UserList', 'UserList'): ('collections', 'UserList'),
    ('UserString', 'UserString'): ('collections', 'UserString'),
    ('whichdb', 'whichdb'): ('dbm', 'whichdb'),
    ('_socket', 'fromfd'): ('socket', 'fromfd'),
    ('_multiprocessing', 'Connection'): ('multiprocessing.connection', 'Connection'),
    ('multiprocessing.process', 'Process'): ('multiprocessing.context', 'Process'),
    ('multiprocessing.forking', 'Popen'): ('multiprocessing.popen_fork', 'Popen'),
    ('urllib', 'ContentTooShortError'): ('urllib.error', 'ContentTooShortError'),
    ('urllib', 'getproxies'): ('urllib.request', 'getproxies'),
    ('urllib', 'pathname2url'): ('urllib.request', 'pathname2url'),
    ('urllib', 'quote_plus'): ('urllib.parse', 'quote_plus'),
    ('urllib', 'quote'): ('urllib.parse', 'quote'),
    ('urllib', 'unquote_plus'): ('urllib.parse', 'unquote_plus'),
    ('urllib', 'unquote'): ('urllib.parse', 'unquote'),
    ('urllib', 'url2pathname'): ('urllib.request', 'url2pathname'),
    ('urllib', 'urlcleanup'): ('urllib.request', 'urlcleanup'),
    ('urllib', 'urlencode'): ('urllib.parse', 'urlencode'),
    ('urllib', 'urlopen'): ('urllib.request', 'urlopen'),
    ('urllib', 'urlretrieve'): ('urllib.request', 'urlretrieve'),
    ('urllib2', 'HTTPError'): ('urllib.error', 'HTTPError'),
    ('urllib2', 'URLError'): ('urllib.error', 'URLError') }
PYTHON2_EXCEPTIONS = ('ArithmeticError', 'AssertionError', 'AttributeError', 'BaseException', 'BufferError', 'BytesWarning', 'DeprecationWarning', 'EOFError', 'EnvironmentError', 'Exception', 'FloatingPointError', 'FutureWarning', 'GeneratorExit', 'IOError', 'ImportError', 'ImportWarning', 'IndentationError', 'IndexError', 'KeyError', 'KeyboardInterrupt', 'LookupError', 'MemoryError', 'NameError', 'NotImplementedError', 'OSError', 'OverflowError', 'PendingDeprecationWarning', 'ReferenceError', 'RuntimeError', 'RuntimeWarning', 'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit', 'TabError', 'TypeError', 'UnboundLocalError', 'UnicodeDecodeError', 'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError', 'UnicodeWarning', 'UserWarning', 'ValueError', 'Warning', 'ZeroDivisionError')

try:
    WindowsError
except NameError:
    pass

PYTHON2_EXCEPTIONS += ('WindowsError',)
for excname in PYTHON2_EXCEPTIONS:
    NAME_MAPPING[('exceptions', excname)] = ('builtins', excname)
MULTIPROCESSING_EXCEPTIONS = ('AuthenticationError', 'BufferTooShort', 'ProcessError', 'TimeoutError')
for excname in MULTIPROCESSING_EXCEPTIONS:
    NAME_MAPPING[('multiprocessing', excname)] = ('multiprocessing.context', excname)
REVERSE_IMPORT_MAPPING = (lambda .0: for k, v in .0:
(v, k).0)(IMPORT_MAPPING.items()())
if not len(REVERSE_IMPORT_MAPPING) == len(IMPORT_MAPPING):
    raise AssertionError
REVERSE_NAME_MAPPING = (lambda .0: for k, v in .0:
(v, k).0)(NAME_MAPPING.items()())
if not len(REVERSE_NAME_MAPPING) == len(NAME_MAPPING):
    raise AssertionError
IMPORT_MAPPING.update({
    'cStringIO': 'io',
    'StringIO': 'io',
    'whichdb': 'dbm',
    'UserString': 'collections',
    'UserList': 'collections',
    'UserDict': 'collections',
    'CGIHTTPServer': 'http.server',
    'SimpleHTTPServer': 'http.server',
    'DocXMLRPCServer': 'xmlrpc.server',
    'SimpleDialog': 'tkinter.simpledialog',
    'FileDialog': 'tkinter.filedialog',
    '_elementtree': 'xml.etree.ElementTree',
    'cPickle': 'pickle' })
REVERSE_IMPORT_MAPPING.update({
    '_pickle': 'pickle',
    '_gdbm': 'gdbm',
    '_functools': 'functools',
    '_dbm': 'dbm',
    '_bz2': 'bz2' })
NAME_MAPPING.update({
    ('socket', '_socketobject'): ('socket', 'SocketType'),
    ('UserDict', 'UserDict'): ('collections', 'UserDict'),
    ('exceptions', 'StandardError'): ('builtins', 'Exception'),
    ('__builtin__', 'basestring'): ('builtins', 'str') })
REVERSE_NAME_MAPPING.update({
    ('_socket', 'socket'): ('socket', '_socketobject'),
    ('http.server', 'CGIHTTPRequestHandler'): ('CGIHTTPServer', 'CGIHTTPRequestHandler'),
    ('http.server', 'SimpleHTTPRequestHandler'): ('SimpleHTTPServer', 'SimpleHTTPRequestHandler'),
    ('xmlrpc.server', 'DocCGIXMLRPCRequestHandler'): ('DocXMLRPCServer', 'DocCGIXMLRPCRequestHandler'),
    ('xmlrpc.server', 'DocXMLRPCServer'): ('DocXMLRPCServer', 'DocXMLRPCServer'),
    ('xmlrpc.server', 'DocXMLRPCRequestHandler'): ('DocXMLRPCServer', 'DocXMLRPCRequestHandler'),
    ('xmlrpc.server', 'XMLRPCDocGenerator'): ('DocXMLRPCServer', 'XMLRPCDocGenerator'),
    ('xmlrpc.server', 'ServerHTMLDoc'): ('DocXMLRPCServer', 'ServerHTMLDoc'),
    ('tkinter.simpledialog', 'SimpleDialog'): ('SimpleDialog', 'SimpleDialog'),
    ('tkinter.filedialog', 'SaveFileDialog'): ('FileDialog', 'SaveFileDialog'),
    ('tkinter.filedialog', 'LoadFileDialog'): ('FileDialog', 'LoadFileDialog'),
    ('tkinter.filedialog', 'FileDialog'): ('FileDialog', 'FileDialog'),
    ('_functools', 'reduce'): ('__builtin__', 'reduce') })
PYTHON3_OSERROR_EXCEPTIONS = ('BrokenPipeError', 'ChildProcessError', 'ConnectionAbortedError', 'ConnectionError', 'ConnectionRefusedError', 'ConnectionResetError', 'FileExistsError', 'FileNotFoundError', 'InterruptedError', 'IsADirectoryError', 'NotADirectoryError', 'PermissionError', 'ProcessLookupError', 'TimeoutError')
for excname in PYTHON3_OSERROR_EXCEPTIONS:
    REVERSE_NAME_MAPPING[('builtins', excname)] = ('exceptions', 'OSError')
PYTHON3_IMPORTERROR_EXCEPTIONS = ('ModuleNotFoundError',)
for excname in PYTHON3_IMPORTERROR_EXCEPTIONS:
    REVERSE_NAME_MAPPING[('builtins', excname)] = ('exceptions', 'ImportError')
del excname
