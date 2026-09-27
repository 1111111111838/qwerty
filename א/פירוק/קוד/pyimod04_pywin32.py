# Source Generated with Decompyle++
# File: pyimod04_pywin32.pyc (Python 3.14)

'''
Set search path for pywin32 DLLs. Due to the large number of pywin32 modules, we use a single loader-level script
instead of per-module runtime hook scripts.
'''
import os
import sys

def install():
    '''win32'''
    pywin32_ext_paths = ('win32', 'pythonwin')
    
    try:
        for pywin32_ext_path in pywin32_ext_paths:
            pass
    pywin32_ext_path = pywin32_ext_paths
    
    try:
        for path in pywin32_ext_paths:
            if not os.path.isdir(path):
                continue
    path = pywin32_ext_paths


    pywin32_ext_paths = []
    pywin32_ext_path = pywin32_ext_path
    
    try:
        for path in pywin32_ext_paths:
            if not os.path.isdir(path):
                continue
    path = pywin32_ext_paths

    pywin32_ext_paths = []
    path = path
    sys.path.extend(pywin32_ext_paths)
    pywin32_system32_path = os.path.join(sys._MEIPASS, 'pywin32_system32')
    if not os.path.isdir(pywin32_system32_path):
        return None
    sys.path.append(pywin32_system32_path)
    os.add_dll_directory(pywin32_system32_path)
    path = os.environ.get('PATH', None)
    if not path:
        path = pywin32_system32_path
    else:
        path = pywin32_system32_path + os.pathsep + path
    os.environ['PATH'] = path
    return None
# WARNING: Decompyle incomplete

