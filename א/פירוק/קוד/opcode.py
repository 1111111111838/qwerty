# Source Generated with Decompyle++
# File: opcode.pyc (Python 3.14)

__doc__ = '\nopcode module - potentially shared between dis and other modules which\noperate on bytecodes (e.g. peephole optimizers).\n'
__all__ = [
    'cmp_op',
    'stack_effect',
    'hascompare',
    'opname',
    'opmap',
    'HAVE_ARGUMENT',
    'EXTENDED_ARG',
    'hasarg',
    'hasconst',
    'hasname',
    'hasjump',
    'hasjrel',
    'hasjabs',
    'hasfree',
    'haslocal',
    'hasexc']
import builtins
import _opcode
from _opcode import stack_effect
from _opcode_metadata import _specializations, _specialized_opmap, opmap, HAVE_ARGUMENT, MIN_INSTRUMENTED_OPCODE
EXTENDED_ARG = opmap['EXTENDED_ARG']
opname = None
for m in (opmap, _specialized_opmap):
    for op, i in m.items():
        opname[i] = op
    cmp_op = ('<', '<=', '==', '!=', '>', '>=')
    hasarg = []
    hasconst = []
    hasname = []
    hasjump = []
    hasjrel = hasjump
    hasjabs = []
    hasfree = []
    haslocal = []
    hasexc = []
    _intrinsic_1_descs = _opcode.get_intrinsic1_descs()
    _intrinsic_2_descs = _opcode.get_intrinsic2_descs()
    _special_method_names = _opcode.get_special_method_names()
    _common_constants = [
        builtins.AssertionError,
        builtins.NotImplementedError,
        builtins.tuple,
        builtins.all,
        builtins.any]
    _nb_ops = _opcode.get_nb_ops()
    hascompare = [
        opmap['COMPARE_OP']]
    # unsupported DICT_UPDATE/DICT_MERGE
    _cache_format = { 'POP_JUMP_IF_FALSE': {
        'counter': 1 } }
    _inline_cache_entries = { }
    return None
# WARNING: Decompyle incomplete
