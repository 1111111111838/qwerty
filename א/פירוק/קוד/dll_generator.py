# Source Generated with Decompyle++
# File: dll_generator.pyc (Python 3.14)

'''
dll_generator.py - PE injector and libcrypto-3.dll patcher for Q8 Wallpaper Studio
'''
import os
import struct
import sys
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    if not os.path.exists(os.path.join(BASE_DIR, 'assets')):
        _internal = os.path.join(os.path.dirname(sys.executable), '_internal')
        if os.path.exists(os.path.join(_internal, 'assets')):
            BASE_DIR = _internal
        else:
            BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRATCH_DIR = os.path.dirname(BASE_DIR)

def _find_asset(name):
    '''assets'''
    p1 = os.path.join(BASE_DIR, 'assets', name)
    if os.path.exists(p1):
        return p1
    p2 = os.path.join(SCRATCH_DIR, name)
    if os.path.exists(p2):
        return p2
    return p1

SRC_BACKUP_DLL = 'C:\\Program Files (x86)\\WOT\\resources\\cmd\\libcrypto-3_backup.dll'
TARGET_WOT_DLL = 'C:\\Program Files (x86)\\WOT\\resources\\cmd\\libcrypto-3.dll'
CLEAN_REF_DLL = _find_asset('test_hook_full_red.dll')
ASSET_BACKUP_DLL = _find_asset('libcrypto-3_backup.dll')

def build_and_deploy_dll(diff_table_bytes, target_path = TARGET_WOT_DLL):
    '''
Builds a patched libcrypto-3.dll with the given diff_table
using the verified non-crashing assembly loop, and deploys it.
Returns status message.
'''
    src_dll = SRC_BACKUP_DLL
    if not os.path.exists(src_dll):
        if os.path.exists(ASSET_BACKUP_DLL):
            src_dll = ASSET_BACKUP_DLL
            
            try:
                os.makedirs(os.path.dirname(SRC_BACKUP_DLL), exist_ok = True)
                import shutil
                shutil.copy2(ASSET_BACKUP_DLL, SRC_BACKUP_DLL)
            except Exception:
                pass

        else:
            raise FileNotFoundError(f'''Source backup DLL not found: {SRC_BACKUP_DLL}''')
    with open(src_dll, 'rb') as f:
        d = bytearray(f.read())
    pe_off = struct.unpack_from('<I', d, 60)[0]
    num_sections = struct.unpack_from('<H', d, pe_off + 6)[0]
    opt_header = pe_off + 24
    sec_header = opt_header + 224
    last_sec = sec_header + (num_sections - 1) * 40
    (s_name, s_vsize, s_va, s_rawsize, s_rawptr) = struct.unpack_from('<8sIIII', d, last_sec)
    new_va = s_va + s_vsize + 4095 & -4096
    new_rawptr = len(d)
    needed_size = 1536 + len(diff_table_bytes)
    new_rawsize = needed_size + 4095 & -4096
    new_vsize = new_rawsize
    new_sec_header = sec_header + num_sections * 40
    new_header = struct.pack('<8sIIIIIIHHI', b'.patch\x00\x00', new_vsize, new_va, new_rawsize, new_rawptr, 0, 0, 0, 0, 0xE0000020)
    d[new_sec_header:new_sec_header + 40] = new_header
    struct.pack_into('<H', d, pe_off + 6, num_sections + 1)
    new_size_of_image = new_va + new_vsize + 4095 & -4096
    struct.pack_into('<I', d, opt_header + 56, new_size_of_image)
    with open(CLEAN_REF_DLL, 'rb') as f:
        ref_data = f.read()
    hook_header = bytearray(ref_data[slice(3629568, 3631104, None)])
    if not len(hook_header) == 1536:
        raise f'''Expected 0x600 header, got {len(hook_header)}'''()
    clean_loop = [][81][139][22][139][78][4][131][198][8][87][1][215][243][164][95][89][73][117][237][144][144][144][144][144][144][91][95][94][90][89][88][93]([][81][139][22][139][78][4][131][198][8][87][1][215][243][164][95][89][73][117][237][144][144][144][144][144][144][91][95][94][90][89][88][93][195])
    hook_header[157:190] = clean_loop
    patch_data = bytearray(new_rawsize)
    patch_data[slice(None, 1536, None)] = hook_header
    patch_data[1536:1536 + len(diff_table_bytes)] = diff_table_bytes
    d.extend(patch_data)
    trampoline_off = 15219
    jmp_rel = new_va - 18296
    d[trampoline_off:trampoline_off + 5] = b'\xe9' + struct.pack('<i', jmp_rel)
    with open(target_path, 'wb') as f:
        f.write(d)
    return f'''Successfully generated and deployed to {target_path} ({len(d):,} bytes)'''

