# Source Generated with Decompyle++
# File: theme_engine.pyc (Python 3.14)


def __annotate__(format):
    if format > 2:
        raise NotImplementedError
    if 0 in __conditional_annotations__:
        pass
    return {
        '_cached_icon_images': Dict[(str, Dict[(int, Image.Image)])] }

__conditional_annotations__ = {}
import os
import struct
import colorsys
import json
from typing import List, Tuple, Dict
from PIL import Image
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
CONFIG_PATH = os.path.join(BASE_DIR, 'assets', 'theme_config.json')
PRESETS = [
    {
        'desc': 'הערכה האדומה המוכחת (ברירת מחדל)',
        'hex': '#B80C10',
        'name': 'אדום קלאסי',
        'id': 'crimson_red' },
    {
        'desc': 'כחול עמוק, יוקרתי ואלגנטי',
        'hex': '#1D4ED8',
        'name': 'כחול רויאל',
        'id': 'royal_blue' },
    {
        'desc': 'ירוק רענן עם ניגודיות גבוהה',
        'hex': '#059669',
        'name': 'ירוק אמרלד',
        'id': 'emerald_green' },
    {
        'desc': 'סגול עשיר ומודרני',
        'hex': '#7C3AED',
        'name': 'סגול מלכותי',
        'id': 'royal_purple' },
    {
        'desc': 'גוון ענבר-זהב יוקרתי',
        'hex': '#D97706',
        'name': 'זהב יוקרתי',
        'id': 'luxury_gold' },
    {
        'desc': 'טורקיז תוסס וטכנולוגי',
        'hex': '#0891B2',
        'name': 'טורקיז עמוק',
        'id': 'deep_cyan' },
    {
        'desc': 'כתום חם ובולט',
        'hex': '#EA580C',
        'name': 'כתום שקיעה',
        'id': 'sunset_orange' },
    {
        'desc': 'כהה סולידי ומלוטש',
        'hex': '#334155',
        'name': 'שחור גרפיט',
        'id': 'graphite_slate' },
    {
        'desc': 'צבעי המפעל המקוריים של המכשיר',
        'hex': '#0284C7',
        'name': 'כחול מפעל מקורי',
        'id': 'stock_cyan' }]

def hex_to_rgb(hex_str):
    '''#'''
    h = hex_str.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    '''#'''
    return f'''#{r:02X}{g:02X}{b:02X}'''


def rgb_to_rgb565(r, g, b):
    r5 = r * 31 // 255
    g6 = g * 63 // 255
    b5 = b * 31 // 255
    return r5 << 11 | g6 << 5 | b5


def rgb565_to_rgb(val):
    r = (val >> 11 & 31) * 255 // 31
    g = (val >> 5 & 63) * 255 // 63
    b = (val & 31) * 255 // 31
    return (r, g, b)


def check_contrast_guard(hex_str):
    (r, g, b) = hex_to_rgb(hex_str)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    if lum > 175:
        return (False, '⚠️ צבע בהיר מדי - טקסט לבן בטלפון עלול להיות פחות קריא')
    return (True, '✔ ניגודיות מצוינת (טקסט לבן קריא וברור)')


def load_theme_config():
    '''r'''
    if os.path.exists(CONFIG_PATH):
        
        try:
            f = open(CONFIG_PATH, 'r', encoding = 'utf-8').__enter__()
            open(CONFIG_PATH, 'r', encoding = 'utf-8').__exit__(None, None, None)
        except Exception:
            pass

        return json.load(f)
    return {
        'name': 'כחול מפעל מקורי',
        'active_hex': '#0284C7' }


def save_theme_config(active_hex, name = 'מותאם אישית'):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok = True)
    with open(CONFIG_PATH, 'w', encoding = 'utf-8') as f:
        json.dump({
            'name': name,
            'active_hex': active_hex }, f, ensure_ascii = False, indent = 2)

_cached_clean_chunks = None

def get_base_red_chunks():
    global _cached_clean_chunks
    if _cached_clean_chunks is not None:
        return _cached_clean_chunks
    with open(CLEAN_REF_DLL, 'rb') as f:
        hook_ref = f.read()
    diff_off = 3631104
    num_chunks = struct.unpack_from('<I', hook_ref, diff_off)[0]
    p = diff_off + 4
    clean_theme_chunks = []
    for i in range(num_chunks):
        off, sz = struct.unpack_from('<II', hook_ref, p)
        data = hook_ref[p + 8:p + 8 + sz]
        p += 8 + sz
        if 39317504 <= off:
            if off <= 40043776:
                continue
        clean_theme_chunks.append((off, sz, data))
    _cached_clean_chunks = clean_theme_chunks
    return _cached_clean_chunks


def recolor_all_chunks(target_hex):
    '''#B80C10'''
    base_chunks = get_base_red_chunks()
    if target_hex.upper() == '#B80C10':
        return base_chunks
    if target_hex.upper() == '#0284C7':
        return []
    (r_t, g_t, b_t) = hex_to_rgb(target_hex)
    (h_t, s_t, v_t) = colorsys.rgb_to_hsv(r_t / 255, g_t / 255, b_t / 255)
    c_target_565 = rgb_to_rgb565(r_t, g_t, b_t)
    target_565_bytes = struct.pack('>H', c_target_565)
    recolored = []
    for off, sz, data in base_chunks:
        # NOTE(recovery): decompiler rendered this `if` as `while`, causing an
        # infinite append -> MemoryError. Restored to `if ...: continue`.
        if off in (433980, 891744):
            new_banner = target_565_bytes * (sz // 2)
            recolored.append((off, sz, new_banner))
            continue
        if sz == 2:
            recolored.append((off, sz, target_565_bytes))
            continue
        if sz % 2 != 0:
            recolored.append((off, sz, data))
            continue
        out = bytearray(data)
        for j in range(0, sz, 2):
            c_red = struct.unpack_from('>H', data, j)[0]
            (r, g, b) = rgb565_to_rgb(c_red)
            (h, s, v) = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if not s > 0.12:
                continue
            if not (h < 0.12) and not (h > 0.88):
                continue
            (rn, gn, bn) = colorsys.hsv_to_rgb(h_t, min(1, s * s_t * 1.05), v)
            c_new = rgb_to_rgb565(int(rn * 255), int(gn * 255), int(bn * 255))
            struct.pack_into('>H', out, j, c_new)
        recolored.append((off, sz, bytes(out)))
    return recolored

_cached_icon_images = { }
_fast_icon_meta = None

def _get_fast_icon_meta():
    global _fast_icon_meta
    if _fast_icon_meta is not None:
        return _fast_icon_meta
    with open(MMI_DUMP_PATH, 'rb') as f:
        orig = f.read()
    base_chunks = get_base_red_chunks()
    icons = [
        227,
        229,
        231,
        233,
        235,
        237,
        241,
        243,
        251]
    meta = []
    for idx in icons:
        rel = int.from_bytes(orig[10036 + idx * 4:10036 + (idx + 1) * 4], 'little')
        sz = int.from_bytes(orig[1216 + idx * 12 + 8:1216 + idx * 12 + 12], 'little')
        abs_off = 1112 + rel
        for off, csz, data in base_chunks:
            # NOTE(recovery): decompiler corrupted this overlap test into an
            # infinite `while` with stray statements. Restored to a range check.
            if abs_off <= off < abs_off + sz:
                meta.append((idx, abs_off, sz, off, csz, data))
    _fast_icon_meta = meta
    return _fast_icon_meta


def get_menu_icon_images(target_hex):
    key = target_hex.upper()
    if key in _cached_icon_images:
        return _cached_icon_images[key]
    
    try:
        import sprd_abm
    except ImportError:
        import sys
        spd_tools = os.path.join(SCRATCH_DIR, 'tools', 'chinamobiletools-main', 'spd')
        if spd_tools not in sys.path:
            sys.path.append(spd_tools)
        import sprd_abm

    with open(MMI_DUMP_PATH, 'rb') as f:
        orig = f.read()
    meta = _get_fast_icon_meta()
    if key == '#0284C7':
        res = { }
        for idx, abs_off, sz, off, csz, data in meta:
            
            try:
                (im, _) = sprd_abm.decompress(orig[abs_off:abs_off + sz])
                res[idx] = im.resize((48, 46), Image.Resampling.LANCZOS)
            except Exception:
                pass

        _cached_icon_images[key] = res
        return res
    (r_t, g_t, b_t) = hex_to_rgb(target_hex)
    (h_t, s_t, v_t) = colorsys.rgb_to_hsv(r_t / 255, g_t / 255, b_t / 255)
    is_red = key == '#B80C10'
    res = { }
    for idx, abs_off, sz, off, csz, data in meta:
        if is_red:
            item_bytes = bytearray(orig[abs_off:abs_off + sz])
            item_bytes[off - abs_off:(off - abs_off) + csz] = data
        else:
            out = bytearray(data)
            for j in range(0, csz, 2):
                c_red = struct.unpack_from('>H', data, j)[0]
                (r, g, b) = rgb565_to_rgb(c_red)
                (h, s, v) = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                if not s > 0.12:
                    continue
                if not (h < 0.12) and not (h > 0.88):
                    continue
                (rn, gn, bn) = colorsys.hsv_to_rgb(h_t, min(1, s * s_t * 1.05), v)
                c_new = rgb_to_rgb565(int(rn * 255), int(gn * 255), int(bn * 255))
                struct.pack_into('>H', out, j, c_new)
            item_bytes = bytearray(orig[abs_off:abs_off + sz])
            item_bytes[off - abs_off:(off - abs_off) + csz] = out
        
        try:
            (im, _) = sprd_abm.decompress(bytes(item_bytes))
            res[idx] = im.resize((48, 46), Image.Resampling.LANCZOS)
        except Exception:
            pass

    _cached_icon_images[key] = res
    return res

