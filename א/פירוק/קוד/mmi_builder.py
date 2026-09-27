# Source Generated with Decompyle++
# File: mmi_builder.pyc (Python 3.14)

'''
mmi_builder.py - MMI Resource and Diff Table generator for Q8 Wallpaper Studio
Clean architectural slot mapping preserving all original stock wallpapers (slots 1..61, 65..70)
and placing custom user wallpapers precisely in their designated slots.
'''
import os
import sys
import struct
import io
from typing import Dict, Tuple, List, Optional, Any
from PIL import Image, ImageFilter
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    if not os.path.exists(os.path.join(BASE_DIR, 'assets')):
        _internal = os.path.join(os.path.dirname(sys.executable), '_internal')
        if os.path.exists(os.path.join(_internal, 'assets')):
            BASE_DIR = _internal
        else:
            BASE_DIR = os.path.dirname(sys.executable)
else:
    # NOTE(recovery): this else belongs to `if frozen` (decompiler mis-nested it);
    # without it BASE_DIR was undefined when run as a plain .py.
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

MMI_DUMP_PATH = _find_asset('mmi_res_dumped.bin')
CLEAN_REF_DLL = _find_asset('test_hook_full_red.dll')
WOT_DLL_PATH = 'C:\\Program Files (x86)\\WOT\\resources\\cmd\\libcrypto-3.dll'
P40 = 39319156
INFO_OFF = 39319260
OFFSETS_OFF = 39320088
NUM_WALLPAPERS = 69

def get_slot_info(orig_bytes):
    '''
Returns list of (abs_offset, size, capacity) for all 69 slots.
'''
    slots = []
    for i in range(NUM_WALLPAPERS):
        rel = struct.unpack_from('<I', orig_bytes, OFFSETS_OFF + i * 4)[0]
        sz = struct.unpack_from('<I', orig_bytes, INFO_OFF + i * 12 + 8)[0]
        abs_off = P40 + rel
        if i < NUM_WALLPAPERS - 1:
            next_rel = struct.unpack_from('<I', orig_bytes, OFFSETS_OFF + (i + 1) * 4)[0]
            cap = P40 + next_rel - abs_off
        else:
            cap = 40042980 - abs_off
        slots.append((abs_off, sz, cap))
    return slots


def encode_sjpg(im, q_idx = 0, blur = 0):
    '''Encodes an image to compact SJPG using quant table 0 and specified blur.'''
    import spd_sjpg
    im_c = spd_sjpg.fit_image(im, 240, 320, mode = 'crop')
    if blur > 0:
        im_c = im_c.filter(ImageFilter.GaussianBlur(radius = blur))
    lum_q = list(spd_sjpg.JPG_LUM_QUANT_TBL[q_idx])
    chr_q = list(spd_sjpg.JPG_CHR_QUANT_TBL[q_idx])
    buf = io.BytesIO()
    im_c.save(buf, format = 'JPEG', qtables = [
        lum_q,
        chr_q], subsampling = '4:2:2', optimize = False)
    jpg_bytes = buf.getvalue()
    sos_idx = jpg_bytes.find(b'\xff\xda\x00\x0c')
    scan_data = jpg_bytes[sos_idx + 14:-2]
    return b'SJPG' + struct.pack('>HHHH', 320, 240, 3, q_idx) + scan_data


def encode_slot_sjpg(im, slot):
    '''Helper for single slot encoding with crisp Q0 quality.'''
    return encode_sjpg(im, q_idx = 0, blur = 0)


def encode_q0(im, blur = 0):
    '''Encodes an image to compact SJPG using quant table 0.'''
    return encode_sjpg(im, q_idx = 0, blur = blur)

LIST0_P0 = 1112
LIST0_INFO_OFF = 1216
LIST0_OFFSETS_OFF = 10036
UNISOC_ICON_MAPPING = [(227, 222), (228, 274), (229, 226), (230, 283), (231, 212), (232, 278), (233, 265), (234, 286), (235, 301), (236, 270), (237, 295), (238, 275), (239, 202), (240, 271), (241, 203), (242, 273), (243, 217), (244, 285), (245, 219), (246, 287), (247, 207), (248, 272), (249, 200), (250, 280), (251, 201), (252, 269), (253, 224), (254, 292), (255, 216), (256, 284), (257, 264), (258, 268), (259, 220), (260, 276), (261, 210), (262, 277)]

def prepare_slots_pool(custom_wallpapers, orig_mmi, preferred_start_slot = 38):
    '''
Adaptively packs slots into the dedicated pool ending at 0x26301E4.
Starts at preferred_start_slot (e.g. 38) where re-encoding stock slots with quant 0
frees up over 60,000 bytes, guaranteeing all custom wallpapers fit
with 100% crystal-clear clarity (blur = 0.0, ZERO blur).
'''
    import spd_sjpg
    end_off = 40042980
    start_slot = preferred_start_slot
    while start_slot >= 20:
        start_idx = start_slot - 2
        start_rel = struct.unpack_from('<I', orig_mmi, OFFSETS_OFF + start_idx * 4)[0]
        start_off = P40 + start_rel
        pool_capacity = end_off - start_off
        packed = { }
        for s in range(start_slot, 71):
            idx = s - 2
            val = custom_wallpapers.get(s)
            # NOTE(recovery): decompiler emitted `while val:` here; restored to `if/else`
            # (the `while` form would loop forever). Verify against original source.
            if val:
                if isinstance(val, bytes):
                    packed[s] = val
                    continue
                packed[s] = encode_sjpg(val, q_idx = 0, blur = 0)
                continue
            rel = struct.unpack_from('<I', orig_mmi, OFFSETS_OFF + idx * 4)[0]
            sz = struct.unpack_from('<I', orig_mmi, INFO_OFF + idx * 12 + 8)[0]
            abs_p = P40 + rel
            stock_im = spd_sjpg.sjpg_to_image(orig_mmi[abs_p:abs_p + sz])
            packed[s] = encode_sjpg(stock_im, q_idx = 0, blur = 0)
        tot = sum((len(d) + 3 & -4) for d in packed.values())
        if tot <= pool_capacity:
            return (start_slot, start_off, packed)
        start_slot -= 2
    start_slot += 2
    start_idx = start_slot - 2
    start_rel = struct.unpack_from('<I', orig_mmi, OFFSETS_OFF + start_idx * 4)[0]
    start_off = P40 + start_rel
    pool_capacity = end_off - start_off
    # NOTE(recovery): the fallback packing block below was heavily corrupted by the
    # decompiler (lost control flow: bare `try`, `while not ... : pass`, `s = sum`).
    # Reconstructed from context/intent: re-pack the widest pool, then progressively
    # add blur to the largest custom wallpaper until everything fits. VERIFY against
    # the original source before treating this branch as authoritative.
    packed = { }
    blurs = { }
    for s in range(start_slot, 71):
        idx = s - 2
        val = custom_wallpapers.get(s)
        if val:
            if isinstance(val, bytes):
                packed[s] = val
                continue
            blurs[s] = 0.0
            packed[s] = encode_sjpg(val, q_idx = 0, blur = 0)
            continue
        rel = struct.unpack_from('<I', orig_mmi, OFFSETS_OFF + idx * 4)[0]
        sz = struct.unpack_from('<I', orig_mmi, INFO_OFF + idx * 12 + 8)[0]
        abs_p = P40 + rel
        stock_im = spd_sjpg.sjpg_to_image(orig_mmi[abs_p:abs_p + sz])
        packed[s] = encode_sjpg(stock_im, q_idx = 0, blur = 0)
    while sum((len(d) + 3 & -4) for d in packed.values()) > pool_capacity and blurs:
        largest_s = max(blurs.keys(), key = (lambda s: len(packed[s])))
        blurs[largest_s] += 0.05
        packed[largest_s] = encode_sjpg(custom_wallpapers[largest_s], q_idx = 0, blur = blurs[largest_s])
    tot = sum((len(d) + 3 & -4) for d in packed.values())
    if not tot <= pool_capacity:
        raise Exception(f'''Wallpapers exceeded pool capacity: {tot} > {pool_capacity}''')
    return (start_slot, start_off, packed)


def prepare_slots_61_70(slot_inputs, orig_mmi):
    '''Compatibility wrapper redirecting to prepare_slots_pool.'''
    return prepare_slots_pool(slot_inputs, orig_mmi, preferred_start_slot = 38)


def build_modified_mmi(custom_wallpapers, theme_hex = None, use_unisoc_icons = False):
    '''
Builds patched MMI binary respecting exact user customization choices:
- Guaranteed ZERO Gaussian blur (blur = 0.0) for all custom wallpapers.
- Dynamically packs into high-efficiency pool (up to 0x26301E4).
- Theme colors applied via theme_engine.
Guaranteed zero bootloop and zero overflow beyond List 40 limit (0x26301E4).
'''
    import theme_engine
    with open(MMI_DUMP_PATH, 'rb') as f:
        orig = f.read()
    if theme_hex is None:
        cfg = theme_engine.load_theme_config()
        theme_hex = cfg.get('active_hex', '#0284C7')
    modified = bytearray(orig)
    clean_theme_chunks = theme_engine.recolor_all_chunks(theme_hex)
    for off, sz, data in clean_theme_chunks:
        modified[off:off + sz] = data
    if 1 in custom_wallpapers and custom_wallpapers[1] is not None:
        val1 = custom_wallpapers[1]
        if isinstance(val1, Image.Image):
            blur = 0
            sjpg1 = encode_sjpg(val1, q_idx = 0, blur = blur)
            while len(sjpg1) > 2551:
                blur += 0.1
                sjpg1 = encode_sjpg(val1, q_idx = 0, blur = blur)
        else:
            sjpg1 = val1
        if not len(sjpg1) <= 2551:
            raise Exception(f'''Slot 1 exceeds 2551 bytes: {len(sjpg1)}''')
        modified[892172:892172 + len(sjpg1)] = sjpg1
        if len(sjpg1) < 2551:
            modified[892172 + len(sjpg1):894723] = b'\x00' * (2551 - len(sjpg1))
    else:
        modified[892172:894723] = orig[892172:894723]
    
    # NOTE(recovery): decompiler corrupted this into bare `try`/`while ...: pass`.
    # Reconstructed as the list of slots (>= 2) that carry a real custom wallpaper.
    custom_slots = [s for s in custom_wallpapers.keys() if s >= 2 and custom_wallpapers[s]]
    min_custom_slot = min(custom_slots) if custom_slots else 70
    preferred_start = 38
    if min_custom_slot < 38:
        preferred_start = max(20, min_custom_slot)
    (start_slot, start_off, packed) = prepare_slots_pool(custom_wallpapers, orig, preferred_start_slot = preferred_start)
    for s in range(2, start_slot):
        idx = s - 2
        orig_rel = struct.unpack_from('<I', orig, OFFSETS_OFF + idx * 4)[0]
        orig_sz = struct.unpack_from('<I', orig, INFO_OFF + idx * 12 + 8)[0]
        abs_off = P40 + orig_rel
        if idx < 68:
            next_rel = struct.unpack_from('<I', orig, OFFSETS_OFF + (idx + 1) * 4)[0]
            cap = P40 + next_rel - abs_off
        else:
            cap = orig_sz
        if s in custom_wallpapers and custom_wallpapers[s] is not None:
            val = custom_wallpapers[s]
            if isinstance(val, Image.Image):
                sjpg = encode_sjpg(val, q_idx = 0, blur = 0)
            else:
                sjpg = val
            if not len(sjpg) <= cap:
                raise Exception(f'''Slot {s} exceeds capacity {cap}: {len(sjpg)}''')
            modified[abs_off:abs_off + len(sjpg)] = sjpg
            struct.pack_into('<HHII', modified, INFO_OFF + idx * 12, 240, 320, 522, len(sjpg))
            struct.pack_into('<I', modified, OFFSETS_OFF + idx * 4, abs_off - P40)
            continue
        modified[INFO_OFF + idx * 12:INFO_OFF + (idx + 1) * 12] = orig[INFO_OFF + idx * 12:INFO_OFF + (idx + 1) * 12]
        modified[OFFSETS_OFF + idx * 4:OFFSETS_OFF + (idx + 1) * 4] = orig[OFFSETS_OFF + idx * 4:OFFSETS_OFF + (idx + 1) * 4]
        modified[abs_off:abs_off + orig_sz] = orig[abs_off:abs_off + orig_sz]
    curr_off = start_off
    for s in range(start_slot, 71):
        idx = s - 2
        data = packed[s]
        modified[curr_off:curr_off + len(data)] = data
        struct.pack_into('<HHII', modified, INFO_OFF + idx * 12, 240, 320, 522, len(data))
        struct.pack_into('<I', modified, OFFSETS_OFF + idx * 4, curr_off - P40)
        curr_off = curr_off + len(data) + 3 & -4
    if not curr_off <= 40042980:
        raise Exception(f'''CRITICAL: Slots overflowed pool: 0x{curr_off:X} > 0x26301E4''')
    if curr_off < 40042980:
        modified[curr_off:40042980] = b'\x00' * (40042980 - curr_off)
    if use_unisoc_icons:
        for qlyx_idx, orig_idx in UNISOC_ICON_MAPPING:
            modified[LIST0_INFO_OFF + qlyx_idx * 12:LIST0_INFO_OFF + (qlyx_idx + 1) * 12] = orig[LIST0_INFO_OFF + orig_idx * 12:LIST0_INFO_OFF + (orig_idx + 1) * 12]
            modified[LIST0_OFFSETS_OFF + qlyx_idx * 4:LIST0_OFFSETS_OFF + (qlyx_idx + 1) * 4] = orig[LIST0_OFFSETS_OFF + orig_idx * 4:LIST0_OFFSETS_OFF + (orig_idx + 1) * 4]
    
    try:
        import text_engine
        modified = text_engine.apply_text_patches(modified)
    except Exception as e:
        print(f'''Warning: could not apply text patches: {e}''')

    return (bytes(orig), bytes(modified))


def generate_diff_table(orig, modified, max_gap = 64):
    '''Generates contiguous diff chunks between original and modified binaries.'''
    # NOTE(recovery): decompiler corrupted the diff scan and grouping into bare
    # `try`/`while ...: pass`. Reconstructed from intent; verify against original.
    diff_indices = [i for i in range(len(orig)) if orig[i] != modified[i]]
    if not diff_indices:
        return bytearray(struct.pack('<I', 0))
    chunks = []
    start = diff_indices[0]
    prev = diff_indices[0]
    for d in diff_indices[slice(1, None, None)]:
        if d - prev <= max_gap:
            prev = d
        else:
            chunks.append((start, (prev - start) + 1))
            start = d
            prev = d
    chunks.append((start, (prev - start) + 1))
    for start, length in chunks:
        if 39317504 <= start <= 40043776:
            if start + length <= 40042980:
                continue
            raise Exception(f'''CRITICAL: Wallpaper chunk at 0x{start:X} exceeded pool (0x{start + length:X} > 0x26301E4)''')
    diff_table = bytearray(struct.pack('<I', len(chunks)))
    for start, length in chunks:
        diff_table.extend(struct.pack('<II', start, length))
        diff_table.extend(modified[start:start + length])
    return diff_table


def load_live_wot_state():
    '''
Reads directly from live WOT libcrypto-3.dll (or reference DLL)
and reconstructs:
1. Wallpaper slots dict (1..70)
2. Live theme hex (#RRGGBB)
3. Live about title string
4. Live about body string
'''
    import spd_sjpg
    import text_engine
    with open(MMI_DUMP_PATH, 'rb') as f:
        orig = f.read()
    source_dll = WOT_DLL_PATH if os.path.exists(WOT_DLL_PATH) else CLEAN_REF_DLL
    with open(source_dll, 'rb') as f:
        dll_data = f.read()
    diff_off = 3631104
    if len(dll_data) > diff_off + 4:
        num_chunks = struct.unpack_from('<I', dll_data, diff_off)[0]
    else:
        num_chunks = 0
    mod = bytearray(orig)
    if num_chunks > 0:
        p = diff_off + 4
        for _ in range(num_chunks):
            off, sz = struct.unpack_from('<II', dll_data, p)
            p += 8
            mod[off:off + sz] = dll_data[p:p + sz]
            p += sz
    CUSTOM_WP_DIR = os.path.join(BASE_DIR, 'assets', 'custom_user_wp')
    results = { }
    for slot in range(1, 71):
        png_p = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.png''')
        if slot == 1:
            data_mod = bytes(mod[892172:894723])
            data_orig = orig[892172:894723]
            is_custom = num_chunks > 0 and data_mod != data_orig
        else:
            idx = slot - 2
            rel_mod = struct.unpack_from('<I', mod, OFFSETS_OFF + idx * 4)[0]
            sz_mod = struct.unpack_from('<I', mod, INFO_OFF + idx * 12 + 8)[0]
            abs_mod = P40 + rel_mod
            data_mod = bytes(mod[abs_mod:abs_mod + sz_mod])
            rel_orig = struct.unpack_from('<I', orig, OFFSETS_OFF + idx * 4)[0]
            sz_orig = struct.unpack_from('<I', orig, INFO_OFF + idx * 12 + 8)[0]
            abs_orig = P40 + rel_orig
            data_orig = bytes(orig[abs_orig:abs_orig + sz_orig])
            is_custom = slot >= 60 and data_mod != data_orig
        if is_custom and os.path.exists(png_p):
            
            try:
                im = Image.open(png_p).convert('RGB')
            except Exception:
                im = spd_sjpg.sjpg_to_image(data_mod)

        else:
            im = spd_sjpg.sjpg_to_image(data_mod)
        results[slot] = {
            'is_custom': is_custom,
            'sjpg': data_mod,
            'image': im }
    if num_chunks == 0:
        live_theme_hex = '#0284C7'
        live_about_title = text_engine.DEFAULT_ABOUT_TITLE
        live_about_body = text_engine.DEFAULT_ABOUT_BODY
    else:
        banner_val = struct.unpack_from('>H', mod, 433980)[0]
        r = (banner_val >> 11 & 31) * 255 // 31
        g = (banner_val >> 5 & 63) * 255 // 63
        b = (banner_val & 31) * 255 // 31
        live_theme_hex = f'''#{r:02X}{g:02X}{b:02X}'''
        t_bytes = mod[text_engine.ABOUT_TITLE_OFF + 4:text_engine.ABOUT_TITLE_OFF + 4 + text_engine.ABOUT_TITLE_MAX_BYTES]
        live_about_title = t_bytes.decode('utf-16le', errors = 'ignore').rstrip('\x00')
        b_bytes = mod[text_engine.ABOUT_BODY_OFF + 4:text_engine.ABOUT_BODY_OFF + 4 + text_engine.ABOUT_BODY_MAX_BYTES]
        live_about_body = b_bytes.decode('utf-16le', errors = 'ignore').rstrip('\x00')
    return (results, live_theme_hex, live_about_title, live_about_body)


def load_live_wot_wallpapers():
    '''Compatibility wrapper returning wallpaper dictionary.'''
    return load_live_wot_state()[0]

