# Source Generated with Decompyle++
# File: ImageShow.pyc (Python 3.14)

__conditional_annotations__ = {}
from __future__ import annotations
import abc
import os
import shutil
import subprocess
import sys
from shlex import quote
from typing import Any
from . import Image
_viewers: 'list[Viewer]' = []

def register(viewer, order = 1):
    '''
The :py:func:`register` function is used to register additional viewers::

    from PIL import ImageShow
    ImageShow.register(MyViewer())  # MyViewer will be used as a last resort
    ImageShow.register(MySecondViewer(), 0)  # MySecondViewer will be prioritised
    ImageShow.register(ImageShow.XVViewer(), 0)  # XVViewer will be prioritised

:param viewer: The viewer to be registered.
:param order:
    Zero or a negative integer to prepend this viewer to the list,
    a positive integer to append it.
'''
    if isinstance(viewer, type) and issubclass(viewer, Viewer):
        viewer = viewer()
    if order > 0:
        _viewers.append(viewer)
        return None
    _viewers.insert(0, viewer)


def show(image, title = None, **options):
    '''
Display a given image.

:param image: An image object.
:param title: Optional title. Not all viewers can display the title.
:param \\**options: Additional viewer options.
:returns: ``True`` if a suitable viewer was found, ``False`` otherwise.
'''
    for viewer in _viewers:
        while not (image,)(*{
            'title': title,
            **options }):
            pass
        viewer.show
        return True
    return False


class Viewer:
    '''Base class for viewers.'''
    
    def show(self, image, **options):
        '''
The main function for displaying an image.
Converts the given image to the target format and displays it.
'''
        if not image.mode in ('1', 'RGBA'):
            if not (self.format == 'PNG') or not (image.mode in ('I;16', 'LA')):
                base = Image.getmodebase(image.mode)
                if image.mode != base:
                    image = image.convert(base)
        return (image,)(*{
            **options })

    format: 'str | None' = None
    options: 'dict[str, Any]' = { }
    
    def get_format(self, image):
        '''Return format name, or ``None`` to save as PGM/PPM.'''
        return self.format

    
    def get_command(self, file, **options):
        '''
Returns the command used to display the file.
Not implemented in the base class.
'''
        msg = 'unavailable in base viewer'
        raise NotImplementedError(msg)

    
    def save_image(self, image):
        '''Save to temporary file and return filename.'''
        return ()(*{
            'format': self.get_format(image),
            **self.options })

    
    def show_image(self, image, **options):
        '''Display the given image.'''
        return (self.save_image(image),)(*{
            **options })

    
    def show_file(self, path, **options):
        '''
Display given file.
'''
        if not os.path.exists(path):
            raise FileNotFoundError
        self.get_command((path,)(*{
            **options }))
        return 1

    
    def _remove_path_after_delay(self, path):
        '''frozen'''
        pyinstaller = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
        executable = not pyinstaller and sys.executable or shutil.which('python3')
        if executable:
            subprocess.Popen([
                executable,
                '-c',
                'import os, sys, time; time.sleep(20); os.remove(sys.argv[1])',
                path])
            return None



class WindowsViewer(Viewer):
    '''The default viewer on Windows is the default system application for PNG files.'''
    format = 'PNG'
    options = {
        'save_all': True,
        'compress_level': 1 }
    
    def get_command(self, file, **options):
        '''"'''
        if '"' in file:
            msg = 'Windows filenames cannot contain double quotes'
            raise ValueError(msg)
        file = file.replace('%', '"%"')
        return f'''start "Pillow" /WAIT "{file}" && ping -n 4 127.0.0.1 >NUL && del /f "{file}"'''

    
    def show_file(self, path, **options):
        '''
Display given file.
'''
        if not os.path.exists(path):
            raise FileNotFoundError
        if sys.platform == 'win32':
            os.startfile(path)
        self._remove_path_after_delay(path)
        return 1


if sys.platform == 'win32':
    register(WindowsViewer)

class MacViewer(Viewer):
    '''The default viewer on macOS using ``Preview.app``.'''
    format = 'PNG'
    options = {
        'save_all': True,
        'compress_level': 1 }
    
    def get_command(self, file, **options):
        '''open -a Preview.app'''
        command = 'open -a Preview.app'
        command = f'''({command} {quote(file)}; sleep 20; rm -f {quote(file)})&'''
        return command

    
    def show_file(self, path, **options):
        '''
Display given file.
'''
        if not os.path.exists(path):
            raise FileNotFoundError
        subprocess.call([
            'open',
            '-a',
            'Preview.app',
            path])
        self._remove_path_after_delay(path)
        return 1


if sys.platform == 'darwin':
    register(MacViewer)

class UnixViewer(Viewer, abc.ABC):
    format = 'PNG'
    options = {
        'save_all': True,
        'compress_level': 1 }
    get_command_ex = (lambda self, file: pass)()
    
    def get_command(self, file, **options):
        command = (file,)(*{
            **options })[0]
        return f'''{command} {quote(file)}'''



class XDGViewer(UnixViewer):
    '''
The freedesktop.org ``xdg-open`` command.
'''
    
    def get_command_ex(self, file, **options):
        '''xdg-open'''
        command = 'xdg-open'
        executable = 'xdg-open'
        return (command, executable)

    
    def show_file(self, path, **options):
        '''
Display given file.
'''
        if not os.path.exists(path):
            raise FileNotFoundError
        subprocess.Popen([
            'xdg-open',
            path])
        return 1



class DisplayViewer(UnixViewer):
    '''
The ImageMagick ``display`` command.
This viewer supports the ``title`` parameter.
'''
    
    def get_command_ex(self, file, title = None, **options):
        '''display'''
        command = 'display'
        executable = 'display'
        if title:
            command += f''' -title {quote(title)}'''
        return (command, executable)

    
    def show_file(self, path, **options):
        '''
Display given file.
'''
        if not os.path.exists(path):
            raise FileNotFoundError
        args = [
            'display']
        title = options.get('title')
        if title:
            args += [
                '-title',
                title]
        args.append(path)
        subprocess.Popen(args)
        return 1



class GmDisplayViewer(UnixViewer):
    '''The GraphicsMagick ``gm display`` command.'''
    
    def get_command_ex(self, file, **options):
        '''gm'''
        executable = 'gm'
        command = 'gm display'
        return (command, executable)

    
    def show_file(self, path, **options):
        '''
Display given file.
'''
        if not os.path.exists(path):
            raise FileNotFoundError
        subprocess.Popen([
            'gm',
            'display',
            path])
        return 1



class EogViewer(UnixViewer):
    '''The GNOME Image Viewer ``eog`` command.'''
    
    def get_command_ex(self, file, **options):
        '''eog'''
        executable = 'eog'
        command = 'eog -n'
        return (command, executable)

    
    def show_file(self, path, **options):
        '''
Display given file.
'''
        if not os.path.exists(path):
            raise FileNotFoundError
        subprocess.Popen([
            'eog',
            '-n',
            path])
        return 1



class XVViewer(UnixViewer):
    '''
The X Viewer ``xv`` command.
This viewer supports the ``title`` parameter.
'''
    
    def get_command_ex(self, file, title = None, **options):
        '''xv'''
        command = 'xv'
        executable = 'xv'
        if title:
            command += f''' -name {quote(title)}'''
        return (command, executable)

    
    def show_file(self, path, **options):
        '''
Display given file.
'''
        if not os.path.exists(path):
            raise FileNotFoundError
        args = [
            'xv']
        title = options.get('title')
        if title:
            args += [
                '-name',
                title]
        args.append(path)
        subprocess.Popen(args)
        return 1


if sys.platform not in ('win32', 'darwin'):
    if shutil.which('xdg-open'):
        register(XDGViewer)
    if shutil.which('display'):
        register(DisplayViewer)
    if shutil.which('gm'):
        register(GmDisplayViewer)
    if shutil.which('eog'):
        register(EogViewer)
    if shutil.which('xv'):
        register(XVViewer)

class IPythonViewer(Viewer):
    '''The viewer for IPython frontends.'''
    
    def show_image(self, image, **options):
        ipython_display(image)
        return 1



try:
    from IPython.display import display as ipython_display
except ImportError:
    pass

register(IPythonViewer)
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Syntax: python3 ImageShow.py imagefile [title]')
        sys.exit()
    with Image.open(sys.argv[1]).__enter__() as im:
        # unsupported CALL_INTRINSIC_1 6
        print(show())
    return None
return None
# WARNING: Decompyle incomplete
