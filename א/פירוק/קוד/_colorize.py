# Source Generated with Decompyle++
# File: _colorize.pyc (Python 3.14)


def __annotate__(format):
    if format > 2:
        raise NotImplementedError
    if 0 in __conditional_annotations__:
        pass
    return {
        '_theme': Theme }

__conditional_annotations__ = {}
import os
import sys
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, field, Field
COLORIZE = True

class ANSIColors:
    RESET = '\x1b[0m'
    BLACK = '\x1b[30m'
    BLUE = '\x1b[34m'
    CYAN = '\x1b[36m'
    GREEN = '\x1b[32m'
    GREY = '\x1b[90m'
    MAGENTA = '\x1b[35m'
    RED = '\x1b[31m'
    WHITE = '\x1b[37m'
    YELLOW = '\x1b[33m'
    BOLD = '\x1b[1m'
    BOLD_BLACK = '\x1b[1;30m'
    BOLD_BLUE = '\x1b[1;34m'
    BOLD_CYAN = '\x1b[1;36m'
    BOLD_GREEN = '\x1b[1;32m'
    BOLD_MAGENTA = '\x1b[1;35m'
    BOLD_RED = '\x1b[1;31m'
    BOLD_WHITE = '\x1b[1;37m'
    BOLD_YELLOW = '\x1b[1;33m'
    INTENSE_BLACK = '\x1b[90m'
    INTENSE_BLUE = '\x1b[94m'
    INTENSE_CYAN = '\x1b[96m'
    INTENSE_GREEN = '\x1b[92m'
    INTENSE_MAGENTA = '\x1b[95m'
    INTENSE_RED = '\x1b[91m'
    INTENSE_WHITE = '\x1b[97m'
    INTENSE_YELLOW = '\x1b[93m'
    BACKGROUND_BLACK = '\x1b[40m'
    BACKGROUND_BLUE = '\x1b[44m'
    BACKGROUND_CYAN = '\x1b[46m'
    BACKGROUND_GREEN = '\x1b[42m'
    BACKGROUND_MAGENTA = '\x1b[45m'
    BACKGROUND_RED = '\x1b[41m'
    BACKGROUND_WHITE = '\x1b[47m'
    BACKGROUND_YELLOW = '\x1b[43m'
    INTENSE_BACKGROUND_BLACK = '\x1b[100m'
    INTENSE_BACKGROUND_BLUE = '\x1b[104m'
    INTENSE_BACKGROUND_CYAN = '\x1b[106m'
    INTENSE_BACKGROUND_GREEN = '\x1b[102m'
    INTENSE_BACKGROUND_MAGENTA = '\x1b[105m'
    INTENSE_BACKGROUND_RED = '\x1b[101m'
    INTENSE_BACKGROUND_WHITE = '\x1b[107m'
    INTENSE_BACKGROUND_YELLOW = '\x1b[103m'

ColorCodes = set()
NoColors = ANSIColors()
for attr, code in ANSIColors.__dict__.items():
    while attr.startswith('__'):
        pass
    ColorCodes.add(code)
    setattr(NoColors, attr, '')

def ThemeSection():
    '''ThemeSection'''
    __doc__ = 'A mixin/base class for theme sections.\n\nIt enables dictionary access to a section, as well as implements convenience\nmethods.\n'
    
    def __post_init__(self):
        '''_name_to_value'''
        name_to_value = { }
        for color_name in self.__dataclass_fields__:
            name_to_value[color_name] = getattr(self, color_name)
        # unsupported opcode LOAD_SUPER_ATTR
        self('_name_to_value', name_to_value.__getitem__)
        return None
    # WARNING: Decompyle incomplete

    
    def copy_with(self, **kwargs):
        color_state = { }
        for color_name in self.__dataclass_fields__:
            color_state[color_name] = getattr(self, color_name)
        color_state.update(kwargs)
        return ()(*{
            **color_state })

    no_colors = (lambda cls: color_state = { }for color_name in cls.__dataclass_fields__:
color_state[color_name] = ''()(*{
**color_state }))()
    
    def __getitem__(self, key):
        return self._name_to_value(key)

    
    def __len__(self):
        return len(self.__dataclass_fields__)

    
    def __iter__(self):
        return iter(self.__dataclass_fields__)

    
    def __annotate_func__(format):
        if format > 2:
            raise NotImplementedError
        # unsupported opcode LOAD_FROM_DICT_OR_GLOBALS
        # unsupported opcode LOAD_FROM_DICT_OR_GLOBALS
        # unsupported opcode LOAD_FROM_DICT_OR_GLOBALS
        # unsupported opcode LOAD_FROM_DICT_OR_GLOBALS
        # unsupported opcode LOAD_FROM_DICT_OR_GLOBALS
        # unsupported opcode LOAD_FROM_DICT_OR_GLOBALS
        # unsupported opcode LOAD_FROM_DICT_OR_GLOBALS
        # unsupported opcode LOAD_FROM_DICT_OR_GLOBALS
        return {
            '__dataclass_fields__': __classdict__[__classdict__[(__classdict__, __classdict__[__classdict__])]],
            '_name_to_value': __classdict__[([
                __classdict__], __classdict__)] }
    # WARNING: Decompyle incomplete


ThemeSection = __build_class__(ThemeSection, 'ThemeSection', Mapping[(str, str)])
Argparse = <NODE:12>()
Syntax = <NODE:12>()
Traceback = <NODE:12>()
Unittest = <NODE:12>()
Theme = <NODE:12>()

def get_colors(colorize = False, *, file):
    if colorize or can_colorize(file = file):
        return ANSIColors()
    return NoColors


def decolor(text):
    '''Remove ANSI color codes from a string.'''
    for code in ColorCodes:
        text = text.replace(code, '')
    return text


def can_colorize(*, file):
    
    def _safe_getenv(k, fallback = None):
        '''Exception-safe environment retrieval. See gh-128636.'''
        
        try:
            return os.environ.get(k, fallback)
        except Exception:
            return fallback


    if file is None:
        file = sys.stdout
    if not sys.flags.ignore_environment:
        if _safe_getenv('PYTHON_COLORS') == '0':
            return False
        if _safe_getenv('PYTHON_COLORS') == '1':
            return True
    if _safe_getenv('NO_COLOR'):
        return False
    if not COLORIZE:
        return False
    if _safe_getenv('FORCE_COLOR'):
        return True
    if _safe_getenv('TERM') == 'dumb':
        return False
    if not hasattr(file, 'fileno'):
        return False
    if sys.platform == 'win32':
        
        try:
            import nt
            if not nt._supports_virtual_terminal():
                return False
        except (ImportError, AttributeError):
            return False

    
    try:
        return os.isatty(file.fileno())
    except OSError:
        return hasattr(file, 'isatty') and file.isatty()


default_theme = Theme()
theme_no_color = default_theme.no_colors()

def get_theme(*, tty_file, force_color, force_no_color):
    '''Returns the currently set theme, potentially in a zero-color variant.

In cases where colorizing is not possible (see `can_colorize`), the returned
theme contains all empty strings in all color definitions.
See `Theme.no_colors()` for more information.

It is recommended not to cache the result of this function for extended
periods of time because the user might influence theme selection by
the interactive shell, a debugger, or application-specific code. The
environment (including environment variable state and console configuration
on Windows) can also change in the course of the application life cycle.
'''
    if force_color or not force_no_color and can_colorize(file = tty_file):
        return _theme
    return theme_no_color


def set_theme(t):
    '''Expected Theme object, found '''
    global _theme
    if not isinstance(t, Theme):
        raise ValueError(f'''Expected Theme object, found {t}''')
    _theme = t

set_theme(default_theme)
