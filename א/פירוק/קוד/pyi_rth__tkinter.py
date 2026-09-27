# Source Generated with Decompyle++
# File: pyi_rth__tkinter.pyc (Python 3.14)


def _pyi_rthook():
    import os
    import sys
    tcldir = os.path.join(sys._MEIPASS, '_tcl_data')
    tkdir = os.path.join(sys._MEIPASS, '_tk_data')
    if os.path.isdir(tcldir):
        os.environ['TCL_LIBRARY'] = tcldir
    if os.path.isdir(tkdir):
        os.environ['TK_LIBRARY'] = tkdir
        return None

_pyi_rthook()
del _pyi_rthook
