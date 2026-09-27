# Source Generated with Decompyle++
# File: codeop.pyc (Python 3.14)

__doc__ = "Utilities to compile possibly incomplete Python source code.\n\nThis module provides two interfaces, broadly similar to the builtin\nfunction compile(), which take program text, a filename and a 'mode'\nand:\n\n- Return code object if the command is complete and valid\n- Return None if the command is incomplete\n- Raise SyntaxError, ValueError or OverflowError if the command is a\n  syntax error (OverflowError and ValueError can be produced by\n  malformed literals).\n\nThe two interfaces are:\n\ncompile_command(source, filename, symbol):\n\n    Compiles a single command in the manner described above.\n\nCommandCompiler():\n\n    Instances of this class have __call__ methods identical in\n    signature to compile_command; the difference is that if the\n    instance compiles program text containing a __future__ statement,\n    the instance 'remembers' and compiles all subsequent program texts\n    with the statement in force.\n\nThe module also provides another class:\n\nCompile():\n\n    Instances of this class act like the built-in function compile,\n    but with 'memory' in the sense described above.\n"
import __future__
import warnings
_features = None
__all__ = [
    'compile_command',
    'Compile',
    'CommandCompiler']
PyCF_DONT_IMPLY_DEDENT = 512
PyCF_ONLY_AST = 1024
PyCF_ALLOW_INCOMPLETE_INPUT = 16384

def _maybe_compile(compiler, source, filename, symbol, flags):
    '''
'''
    for line in source.split('\n'):
        line = line.strip()
        while not line:
            pass
        if not line[0] != '#':
            continue
        source.split('\n')
    if symbol != 'eval':
        source = 'pass'
    with warnings.catch_warnings().__enter__():
        warnings.simplefilter('ignore', (SyntaxWarning, DeprecationWarning))
        
        try:
            compiler(source, filename, symbol, flags = flags)
        while <exception value><EXCEPTION MATCH>SyntaxError:
            
            try:
                compiler(source + '\n', filename, symbol, flags = flags)
            except _IncompleteInputError as e:
                warnings.catch_warnings().__exit__(None, None, None)
                return None
            except SyntaxError as e:
                pass

            warnings.catch_warnings().__exit__(None, None, None)
            return None

        warnings.catch_warnings().__exit__(None, None, None)
        return compiler(source, filename, symbol, incomplete_input = False)


def _compile(source, filename, symbol, incomplete_input = True, *, flags):
    if incomplete_input:
        flags |= PyCF_ALLOW_INCOMPLETE_INPUT
        flags |= PyCF_DONT_IMPLY_DEDENT
    return compile(source, filename, symbol, flags)


def compile_command(source, filename = '<input>', symbol = 'single', flags = 0):
    '''Compile a command and determine whether it is incomplete.

Arguments:

source -- the source string; may contain \\n characters
filename -- optional filename from which source was read; default
            "<input>"
symbol -- optional grammar start symbol; "single" (default), "exec"
          or "eval"

Return value / exceptions raised:

- Return a code object if the command is complete and valid
- Return None if the command is incomplete
- Raise SyntaxError, ValueError or OverflowError if the command is a
  syntax error (OverflowError and ValueError can be produced by
  malformed literals).
'''
    return _maybe_compile(_compile, source, filename, symbol, flags)


class Compile:
    '''Instances of this class behave much like the built-in compile
function, but if one is used to compile text containing a future
statement, it "remembers" and compiles all subsequent program texts
with the statement in force.'''
    
    def __init__(self):
        self.flags = PyCF_DONT_IMPLY_DEDENT | PyCF_ALLOW_INCOMPLETE_INPUT

    
    def __call__(self, source, filename, symbol, flags = 0, **kwargs):
        '''incomplete_input'''
        flags |= self.flags
        if kwargs.get('incomplete_input', True) is False:
            flags &= ~PyCF_DONT_IMPLY_DEDENT
            flags &= ~PyCF_ALLOW_INCOMPLETE_INPUT
        codeob = compile(source, filename, symbol, flags, True)
        if flags & PyCF_ONLY_AST:
            return codeob
        for feature in _features:
            if not codeob.co_flags & feature.compiler_flag:
                continue
            self.flags |= feature.compiler_flag
        return codeob



class CommandCompiler:
    """Instances of this class have __call__ methods identical in
signature to compile_command; the difference is that if the
instance compiles program text containing a __future__ statement,
the instance 'remembers' and compiles all subsequent program texts
with the statement in force."""
    
    def __init__(self):
        self.compiler = Compile()

    
    def __call__(self, source, filename = '<input>', symbol = 'single'):
        '''Compile a command and determine whether it is incomplete.

Arguments:

source -- the source string; may contain \\n characters
filename -- optional filename from which source was read;
            default "<input>"
symbol -- optional grammar start symbol; "single" (default) or
          "eval"

Return value / exceptions raised:

- Return a code object if the command is complete and valid
- Return None if the command is incomplete
- Raise SyntaxError, ValueError or OverflowError if the command is a
  syntax error (OverflowError and ValueError can be produced by
  malformed literals).
'''
        return _maybe_compile(self.compiler, source, filename, symbol, flags = self.compiler.flags)


return None
# WARNING: Decompyle incomplete
