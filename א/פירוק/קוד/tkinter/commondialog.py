# Source Generated with Decompyle++
# File: commondialog.pyc (Python 3.14)

'''Base class for the Tk common dialogs.'''
__all__ = [
    'Dialog']
from tkinter import _get_temp_root, _destroy_temp_root

class Dialog:
    command = None
    
    def __init__(self, master = None, **options):
        if master is None:
            master = options.get('parent')
        self.master = master
        self.options = options

    
    def _fixoptions(self):
        pass

    
    def _fixresult(self, widget, result):
        return result

    
    def show(self, **options):
        for k, v in options.items():
            self.options[k] = v
        self._fixoptions()
        master = self.master
        if master is None:
            master = _get_temp_root()
        
        try:
            self._test_callback(master)
            # unsupported CALL_INTRINSIC_1 6
            s = master.tk.call()
            s = self._fixresult(master, s)
            return s
        finally:
            _destroy_temp_root(master)

    # WARNING: Decompyle incomplete

    
    def _test_callback(self, master):
        pass


