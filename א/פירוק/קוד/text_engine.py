# Source Generated with Decompyle++
# File: text_engine.pyc (Python 3.14)

'''
text_engine.py - Q8 String and About Screen Customization Engine
Handles live preview and binary patching for:
1. "About" Screen (מסך אודות): Title, custom version note, credits/dedication, contact info.
2. Menu and System Strings: Search and safe in-place replacement.
'''
import os
import json
from typing import Dict, List, Tuple, Optional
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

MMI_DUMP_PATH = _find_asset('mmi_res_dumped.bin')
TEXT_CONFIG_PATH = os.path.join(BASE_DIR, 'assets', 'text_config.json')
ABOUT_TITLE_OFF = 11240480
ABOUT_TITLE_MAX_BYTES = 20
ABOUT_BODY_OFF = 11240504
ABOUT_BODY_MAX_BYTES = 192
DEFAULT_ABOUT_TITLE = 'מספר גרסה:'
DEFAULT_ABOUT_BODY = 'כל הזכויות שמורות©\nאין להעתיק ו/או לשכפל ו/או לצלם או לעבד נתונים מהגרסה. Support@qlyx-tech.com\n'
STR_REGION_START = 11018006
STR_REGION_END = 11272192

def load_text_config():
    '''Loads saved text configuration or returns factory defaults.'''
    if os.path.exists(TEXT_CONFIG_PATH):
        
        try:
            f = open(TEXT_CONFIG_PATH, 'r', encoding = 'utf-8').__enter__()
            open(TEXT_CONFIG_PATH, 'r', encoding = 'utf-8').__exit__(None, None, None)
        except Exception:
            pass

        return json.load(f)
    default_cfg = {
        'replacements': { },
        'about_body': DEFAULT_ABOUT_BODY,
        'about_title': DEFAULT_ABOUT_TITLE }
    save_text_config(default_cfg)
    return default_cfg


def save_text_config(cfg):
    '''Saves text configuration to JSON.'''
    os.makedirs(os.path.dirname(TEXT_CONFIG_PATH), exist_ok = True)
    with open(TEXT_CONFIG_PATH, 'w', encoding = 'utf-8') as f:
        json.dump(cfg, f, ensure_ascii = False, indent = 2)


def apply_text_patches(mmi_bytes, cfg = None):
    '''
Applies custom text patches directly into MMI bytearray:
- Guaranteed zero pointer corruption: all replacements fit exact existing byte allocations.
- Zero offset shifting.
'''
    if cfg is None:
        cfg = load_text_config()
    about_title = cfg.get('about_title', DEFAULT_ABOUT_TITLE)
    about_body = cfg.get('about_body', DEFAULT_ABOUT_BODY)
    replacements = cfg.get('replacements', { })
    if about_title:
        title_enc = about_title.encode('utf-16le')
        if len(title_enc) > ABOUT_TITLE_MAX_BYTES:
            title_enc = title_enc[:ABOUT_TITLE_MAX_BYTES]
        else:
            title_enc = title_enc + b'\x00' * (ABOUT_TITLE_MAX_BYTES - len(title_enc))
        mmi_bytes[ABOUT_TITLE_OFF + 4:ABOUT_TITLE_OFF + 4 + ABOUT_TITLE_MAX_BYTES] = title_enc
    if about_body:
        body_enc = about_body.encode('utf-16le')
        if len(body_enc) > ABOUT_BODY_MAX_BYTES:
            body_enc = body_enc[:ABOUT_BODY_MAX_BYTES]
        else:
            body_enc = body_enc + b'\x00' * (ABOUT_BODY_MAX_BYTES - len(body_enc))
        mmi_bytes[ABOUT_BODY_OFF + 4:ABOUT_BODY_OFF + 4 + ABOUT_BODY_MAX_BYTES] = body_enc
    for orig_text, new_text in replacements.items():
        if orig_text and new_text:
            while orig_text == new_text:
                pass
        orig_enc = orig_text.encode('utf-16le')
        new_enc = new_text.encode('utf-16le')
        p = STR_REGION_START
        if not p < STR_REGION_END - 4:
            continue
        flag = int.from_bytes(mmi_bytes[p:p + 2], 'little')
        if flag == 128:
            length = int.from_bytes(mmi_bytes[p + 2:p + 4], 'little')
            if length >= len(new_enc) and length <= 400:
                curr_enc = mmi_bytes[p + 4:p + 4 + length]
                if curr_enc.startswith(orig_enc):
                    padded_new = new_enc + b'\x00' * (length - len(new_enc))
                    mmi_bytes[p + 4:p + 4 + length] = padded_new
                    continue
            p += 4 + length
            continue
        p += 2
    return mmi_bytes


def search_hebrew_strings(query, limit = 40):
    """
Searches Hebrew strings in MMI resource dump.
Returns list of dicts: {'offset': int, 'text': str, 'max_chars': int}
"""
    if not os.path.exists(MMI_DUMP_PATH) or not query.strip():
        return []
    with open(MMI_DUMP_PATH, 'rb') as f:
        d = f.read()
    results = []
    p = STR_REGION_START
    query_clean = query.strip()
    while p < STR_REGION_END - 4:
        flag = int.from_bytes(d[p:p + 2], 'little')
        if flag == 128:
            length = int.from_bytes(d[p + 2:p + 4], 'little')
            if 2 <= length and length <= 300 and p + 4 + length <= STR_REGION_END:
                raw = d[p + 4:p + 4 + length]
                
                try:
                    txt = raw.decode('utf-16le').rstrip('\x00')
                    if query_clean in txt:
                        results.append({
                            'byte_length': length,
                            'max_chars': length // 2,
                            'text': txt,
                            'offset': p + 4 })
                        if len(results) >= limit:
                            return results
                    p += 4 + length
                except Exception:
                    pass

                continue
        p += 2
    return results

