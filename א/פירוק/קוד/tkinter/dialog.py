# Source Generated with Decompyle++
# File: dialog.pyc (Python 3.14)

'''Classic Tk dialog box, wrapping the tk_dialog script.'''
from tkinter import _cnfmerge, Widget, TclError, Button, Pack
__all__ = [
    'Dialog']
DIALOG_ICON = 'questhead'

class Dialog(Widget):
    '''A modal dialog box built from the classic (non-themed) Tk widgets.'''
    
    def __init__(self, master = None, cnf = { }, **kw):
        '''__dialog__'''
        cnf = _cnfmerge((cnf, kw))
        self.widgetName = '__dialog__'
        self._setup(master, cnf)
        # unsupported CALL_INTRINSIC_1 6
        self.num = self.tk.getint(self.tk.call())
        
        try:
            Widget.destroy(self)
        except TclError:
            return None

        return None
    # WARNING: Decompyle incomplete

    
    def destroy(self):
        '''Do nothing; the dialog window is already destroyed.'''
        pass



def _test():
    d = Dialog(None, {
        'strings': ('Save File', 'Discard Changes', 'Return to Editor'),
        'default': 0,
        'bitmap': DIALOG_ICON,
        'text': 'File "Python.h" has been modified since the last time it was saved. Do you want to save it before exiting the application.',
        'title': 'File Modified' })
    print(d.num)

if __name__ == '__main__':
    t = Button(None, {
        Pack: { },
        'command': _test,
        'text': 'Test' })
    q = Button(None, {
        Pack: { },
        'command': t.quit,
        'text': 'Quit' })
    t.mainloop()
