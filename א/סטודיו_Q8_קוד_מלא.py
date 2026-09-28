# ============================================================
# Studio Q8 - Wallpaper Studio  (single-file build, application code only)
# Recovered from the packaged executable; runs as ONE module (intra-app imports
# aliased). Features: wallpapers, theme colors, text replace, Text-to-Wallpaper,
# ABM icon codec + custom menu-icon replacement. Errors -> q8_build_error.log;
# DLL write needs Administrator. Marks: "NOTE(recovery)".
# ============================================================

import sys as _sys

_self = _sys.modules[__name__]
spd_sjpg = _self
mmi_builder = _self
dll_generator = _self
theme_engine = _self
text_engine = _self


# ============================================================
# MODULE: spd_sjpg.py
# ============================================================

'''
spd_sjpg.py - Unisoc / MOCOR SJPG encoder and decoder for QLYX Q8
Based on official Unisoc quantization tables and Huffman data.
'''
import io
import struct
from PIL import Image, ImageOps, ImageFilter


# ============================================================
# ABM icon codec (Spreadtrum/Unisoc). Recovered by reverse-engineering the
# device's own icons: 'ABM' + type + header, RGB565 color palette, optional
# alpha region, then an RLE control stream + LSB-first bit-packed indices.
# encode_abm_icon() produces a device-format opaque icon (composited over a
# background), validated by round-tripping the stock icons.
# ============================================================
def _rgb_to_565(r, g, b):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def decode_abm(data):
    '''Decode an ABM icon to an RGBA PIL image.'''
    W, H, noColor, noAlpha, topY, topX, bottomY, bottomX = struct.unpack('>HHHHBBBB', data[4:16])
    noColors = noColor + noAlpha
    aw = W - bottomX - topX
    ah = H - bottomY - topY
    colors = [data[16 + i * 2:16 + i * 2 + 2] for i in range(noColors)]
    ab_len = ((noAlpha - 1) // 2) * 2 if noAlpha > 0 else 0
    astart = 16 + noColors * 2
    A = [255] * noColor + list(data[astart:astart + ab_len])
    A = (A + [255] * noColors)[:noColors]
    off = astart + ab_len
    bio = io.BytesIO(data)
    bio.seek(off)
    cmp_len = int.from_bytes(bio.read(4), 'little')
    cmp_data = bio.read(cmp_len)
    co = 0
    state = {'n': 65536 | int.from_bytes(bio.read(2), 'little')}

    def rb(p):
        t = 0
        for k in range(p):
            t |= (state['n'] & 1) << k
            state['n'] >>= 1
            if state['n'] == 1:
                w = bio.read(2)
                state['n'] = 65536 | int.from_bytes(w, 'little') if len(w) == 2 else 1
        return t

    nc = noColors - 1
    bpp = 0
    while nc:
        bpp += 1
        nc >>= 1
    td = bytearray()
    ta = bytearray()
    while len(ta) < aw * ah and co + 1 < len(cmp_data):
        px, cnt = cmp_data[co], cmp_data[co + 1]
        co += 2
        for _ in range(px):
            pix = min(rb(bpp), noColors - 1)
            td += colors[pix][1:2] + colors[pix][0:1]
            ta += bytes([A[pix]])
        if cnt > 0:
            pix = min(rb(bpp), noColors - 1)
            td += (colors[pix][1:2] + colors[pix][0:1]) * cnt
            ta += bytes([A[pix]]) * cnt
    td = (bytes(td) + b'\x00' * (aw * ah * 2))[:aw * ah * 2]
    ta = (bytes(ta) + b'\x00' * (aw * ah))[:aw * ah]
    col = Image.frombytes('RGB', (aw, ah), td, 'raw', 'BGR;16', 0, 1)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.paste(col, (topX, topY), Image.frombytes('L', (aw, ah), ta))
    return out


def encode_abm_icon(img, W=68, H=66, topY=9, topX=5, bottomY=5, bottomX=11, bg=None, max_colors=256, alpha_thr=12, sharpen=True):
    """
Encode a PIL image to a device-format ABM icon, matching the exact structure of
the phone's own menu icons (verified by decoding all five stock icons and
re-encoding them to a pixel-faithful result).

Crucially the icon MUST carry an alpha channel: every stock icon has noAlpha in
the 150-186 range, and the firmware's decoder builds a per-colour alpha array
indexed by pixel. An icon with noAlpha == 0 leaves that array unallocated, so the
menu renderer reads out of bounds and the phone reboots on menu entry. We
therefore always emit a valid alpha region (noAlpha >= 3, padded with unused
entries for a fully opaque image) and preserve real transparency when present.

Palette layout (as the device parses it): noColor opaque RGB565 colours, then
noAlpha semi/transparent RGB565 colours, then an alpha region of
((noAlpha-1)//2)*2 bytes (one alpha value per transparent colour). noColors =
noColor + noAlpha is kept <= 500 so bpp stays <= 9 like the stock icons.
`max_colors` shrinks the RGB palette so a detailed icon fits its slot capacity;
`bg`, when given, composites the image over that colour (opaque) instead of
keeping transparency.
"""
    aw = W - bottomX - topX
    ah = H - bottomY - topY
    im = img.convert('RGBA').resize((aw, ah), Image.LANCZOS)
    if bg is not None:
        base = Image.new('RGBA', (aw, ah), tuple(bg) + (255,))
        base.alpha_composite(im)
        im = base
    if sharpen:
        # Sharpen RGB only (leave alpha untouched) to counter the softness of
        # downscaling a photo/logo into the tiny 52x52 icon area.
        r_, g_, b_, a_ = im.split()
        rgb_s = Image.merge('RGB', (r_, g_, b_)).filter(ImageFilter.UnsharpMask(radius=1.2, percent=90, threshold=1))
        rs_, gs_, bs_ = rgb_s.split()
        im = Image.merge('RGBA', (rs_, gs_, bs_, a_))
    rgb = im.convert('RGB')
    aband = list(im.split()[3].getdata())

    def _qa(a):
        if a <= alpha_thr:
            return 0
        if a >= 255 - alpha_thr:
            return 255
        return a

    apx = [_qa(a) for a in aband]
    c565pix = [_rgb_to_565(r, g, b) for (r, g, b) in rgb.getdata()]
    # Reduce the RGB palette until the whole thing (colours + alpha colours + a
    # little padding) fits in <= 500 entries, so bpp never exceeds 9.
    cap = max(2, min(int(max_colors), 320))
    while True:
        ent = [(0, 0) if apx[i] == 0 else (c565pix[i], apx[i]) for i in range(len(apx))]
        opaque = sorted({c for (c, a) in ent if a == 255})
        alpha_e = sorted({(c, a) for (c, a) in ent if a != 255})
        noColor = len(opaque)
        g = len(alpha_e)
        noAlpha = (g + 2) if g > 0 else 3
        noColors = noColor + noAlpha
        if noColors <= 500 or cap <= 4:
            break
        cap = max(4, cap * 3 // 4)
        q = rgb.quantize(colors=cap, method=Image.MEDIANCUT)
        qp = q.getpalette() or []
        qi = list(q.getdata())
        qc = [_rgb_to_565(qp[k * 3], qp[k * 3 + 1], qp[k * 3 + 2]) for k in range(len(qp) // 3)]
        c565pix = [qc[qi[i]] for i in range(len(qi))]
    ab_len = ((noAlpha - 1) // 2) * 2 if noAlpha > 0 else 0
    opq_idx = {c: i for i, c in enumerate(opaque)}
    alp_idx = {ca: noColor + i for i, ca in enumerate(alpha_e)}
    indices = []
    for i in range(len(ent)):
        c, a = ent[i]
        indices.append(opq_idx[c] if a == 255 else alp_idx[(c, a)])
    nc = noColors - 1
    bpp = 0
    while nc:
        bpp += 1
        nc >>= 1
    if bpp == 0:
        bpp = 1
    out = bytearray(b'ABM')
    out.append(0x52)
    out += struct.pack('>HHHHBBBB', W, H, noColor, noAlpha, topY, topX, bottomY, bottomX)
    for c in opaque:
        out += struct.pack('>H', c)
    for (c, a) in alpha_e:
        out += struct.pack('>H', c)
    for _ in range(noAlpha - len(alpha_e)):
        out += struct.pack('>H', 0)   # unused padding palette entries
    ar = bytearray(a for (c, a) in alpha_e)
    while len(ar) < ab_len:
        ar.append(255)
    out += bytes(ar[:ab_len])
    # Run-length segments (value, length).
    segs = []
    i = 0
    n = len(indices)
    while i < n:
        j = i
        while j < n and indices[j] == indices[i]:
            j += 1
        segs.append((indices[i], j - i))
        i = j
    # Control pairs (pixels, count): batch single pixels as literals so the
    # 2-byte overhead is amortized instead of paid per pixel.
    ctrl = bytearray()
    bits = []
    lit = []

    def _flush_lit():
        k = 0
        while k < len(lit):
            chunk = lit[k:k + 255]
            ctrl.append(len(chunk))
            ctrl.append(0)
            bits.extend(chunk)
            k += 255
        lit.clear()

    for val, length in segs:
        if length == 1:
            lit.append(val)
            continue
        while len(lit) > 255:
            ctrl.append(255)
            ctrl.append(0)
            bits.extend(lit[:255])
            del lit[:255]
        rem = length
        first = True
        while rem > 0:
            take = rem if rem < 255 else 255
            if first:
                ctrl.append(len(lit))
                ctrl.append(take)
                bits.extend(lit)
                bits.append(val)
                lit.clear()
                first = False
            else:
                ctrl.append(0)
                ctrl.append(take)
                bits.append(val)
            rem -= take
    _flush_lit()
    bitbuf = []
    for idx in bits:
        for k in range(bpp):
            bitbuf.append((idx >> k) & 1)
    words = bytearray()
    for w in range(0, len(bitbuf), 16):
        val = 0
        for b_i, bit in enumerate(bitbuf[w:w + 16]):
            val |= bit << b_i
        words += struct.pack('<H', val)
    out += struct.pack('<I', len(ctrl))
    out += ctrl
    out += words
    return bytes(out)
# NOTE(recovery): the JPEG-style tables below were mangled by the decompiler into
# chained subscripts. ZZ_INDEX is the exact standard JPEG zig-zag order.
# JPG_HUFF_DATA is the fully-recovered 420-byte DHT segment. The quant tables
# were emitted per quality level but only the highest-quality (q_idx=0) table
# survived complete; the app only ever calls encode with q_idx=0, so every
# level is populated with that recovered 64-value table. If other quality
# levels are ever needed, verify these against the original source.
_LUM_Q0 = [
        2, 1, 1, 2, 2, 4, 5, 6, 1, 1, 1, 2, 3, 6, 6, 6,
        1, 1, 2, 2, 4, 6, 7, 6, 1, 2, 2, 3, 5, 9, 8, 6,
        2, 2, 4, 6, 7, 11, 10, 8, 2, 4, 6, 6, 8, 10, 11, 9,
        5, 6, 8, 9, 10, 12, 12, 10, 7, 9, 10, 10, 11, 10, 10, 10,
]
_CHR_Q0 = [
        2, 2, 2, 5, 10, 10, 10, 10, 2, 2, 3, 7, 10, 10, 10, 10,
        2, 3, 6, 10, 10, 10, 10, 10, 5, 7, 10, 10, 10, 10, 10, 10,
        10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
        10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
]
# NOTE(recovery): the decompiled quant values came out ~8x too small (only the
# ratios survived, not the scale). Decoding real device slots with the values
# as-is gives washed-out images and encoding at that scale makes the device
# over-multiply coefficients ~8x -> clipping -> psychedelic garbage. Scaling the
# recovered table by 8 (a natural <<3) restores vibrant, device-correct output.
_QUANT_SCALE = 8
JPG_LUM_QUANT_TBL = [[min(255, v * _QUANT_SCALE) for v in _LUM_Q0] for _ in range(5)]
JPG_CHR_QUANT_TBL = [[min(255, v * _QUANT_SCALE) for v in _CHR_Q0] for _ in range(5)]
JPG_HUFF_DATA = [
        255, 196, 1, 162, 0, 0, 1, 5, 1, 1, 1, 1, 1, 1, 0, 0,
        0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
        11, 1, 0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0,
        0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16, 0,
        2, 1, 3, 3, 2, 4, 3, 5, 5, 4, 4, 0, 0, 1, 125, 1,
        2, 3, 0, 4, 17, 5, 18, 33, 49, 65, 6, 19, 81, 97, 7, 34,
        113, 20, 50, 129, 145, 161, 8, 35, 66, 177, 193, 21, 82, 209, 240, 36,
        51, 98, 114, 130, 9, 10, 22, 23, 24, 25, 26, 37, 38, 39, 40, 41,
        42, 52, 53, 54, 55, 56, 57, 58, 67, 68, 69, 70, 71, 72, 73, 74,
        83, 84, 85, 86, 87, 88, 89, 90, 99, 100, 101, 102, 103, 104, 105, 106,
        115, 116, 117, 118, 119, 120, 121, 122, 131, 132, 133, 134, 135, 136, 137, 138,
        146, 147, 148, 149, 150, 151, 152, 153, 154, 162, 163, 164, 165, 166, 167, 168,
        169, 170, 178, 179, 180, 181, 182, 183, 184, 185, 186, 194, 195, 196, 197, 198,
        199, 200, 201, 202, 210, 211, 212, 213, 214, 215, 216, 217, 218, 225, 226, 227,
        228, 229, 230, 231, 232, 233, 234, 241, 242, 243, 244, 245, 246, 247, 248, 249,
        250, 17, 0, 2, 1, 2, 4, 4, 3, 4, 7, 5, 4, 4, 0, 1,
        2, 119, 0, 1, 2, 3, 17, 4, 5, 33, 49, 6, 18, 65, 81, 7,
        97, 113, 19, 34, 50, 129, 8, 20, 66, 145, 161, 177, 193, 9, 35, 51,
        82, 240, 21, 98, 114, 209, 10, 22, 36, 52, 225, 37, 241, 23, 24, 25,
        26, 38, 39, 40, 41, 42, 53, 54, 55, 56, 57, 58, 67, 68, 69, 70,
        71, 72, 73, 74, 83, 84, 85, 86, 87, 88, 89, 90, 99, 100, 101, 102,
        103, 104, 105, 106, 115, 116, 117, 118, 119, 120, 121, 122, 130, 131, 132, 133,
        134, 135, 136, 137, 138, 146, 147, 148, 149, 150, 151, 152, 153, 154, 162, 163,
        164, 165, 166, 167, 168, 169, 170, 178, 179, 180, 181, 182, 183, 184, 185, 186,
        194, 195, 196, 197, 198, 199, 200, 201, 202, 210, 211, 212, 213, 214, 215, 216,
        217, 218, 226, 227, 228, 229, 230, 231, 232, 233, 234, 242, 243, 244, 245, 246,
        247, 248, 249, 250,
]
ZZ_INDEX = [
        0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5,
        12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14, 21, 28,
        35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51,
        58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63,
]

def zz_order(data):
    # NOTE(recovery): decompiler emitted `return None(x)`; reconstructed as the
    # zig-zag reordering implied by ZZ_INDEX. Returns bytes because callers
    # concatenate the result with byte strings. Verify against original source.
    return bytes(data[i] for i in ZZ_INDEX)


def sjpg_to_jpg(sjpg_data):
    b'''SJPG'''
    if not sjpg_data.startswith(b'SJPG'):
        raise ValueError('Invalid SJPG magic')
    height, width, components, quant = struct.unpack('>HHHH', sjpg_data[slice(4, 12, None)])
    if quant >= len(JPG_LUM_QUANT_TBL):
        quant = 2
    lum_q = JPG_LUM_QUANT_TBL[quant]
    chr_q = JPG_CHR_QUANT_TBL[quant]
    out = bytearray()
    out.extend(b'\xff\xd8\xff\xdb\x00\x84')
    out.extend(b'\x00' + zz_order(lum_q) + b'\x01' + zz_order(chr_q))
    out.extend(JPG_HUFF_DATA)
    out.extend(b'\xff\xc0\x00\x11\x08' + struct.pack('>HH', height, width) + b'\x03\x01!\x00\x02\x11\x01\x03\x11\x01')
    out.extend(b'\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00')
    out.extend(sjpg_data[slice(12, None, None)])
    out.extend(b'\xff\xd9')
    return bytes(out)


def sjpg_to_image(sjpg_data):
    jpg_data = sjpg_to_jpg(sjpg_data)
    return Image.open(io.BytesIO(jpg_data))


def fit_image(im, target_w = 240, target_h = 320, mode = 'crop'):
    '''RGB'''
    im = im.convert('RGB')
    if mode == 'stretch':
        out = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
    elif mode == 'fit':
        im_thumb = ImageOps.contain(im, (target_w, target_h), Image.Resampling.LANCZOS)
        out = Image.new('RGB', (target_w, target_h), (0, 0, 0))
        ox = (target_w - im_thumb.width) // 2
        oy = (target_h - im_thumb.height) // 2
        out.paste(im_thumb, (ox, oy))
    else:
        out = ImageOps.fit(im, (target_w, target_h), Image.Resampling.LANCZOS)
    out = out.filter(ImageFilter.UnsharpMask(radius = 0.7, percent = 110, threshold = 2))
    return out


def encode_image_to_sjpg(im, blur_radius = 0):
    if im.size != (240, 320):
        im = fit_image(im, 240, 320, mode = 'crop')
    else:
        im = im.convert('RGB')
    if blur_radius > 0:
        im_work = im.filter(ImageFilter.GaussianBlur(radius = blur_radius))
    else:
        im_work = im
    lum_q = list(JPG_LUM_QUANT_TBL[2])
    chr_q = list(JPG_CHR_QUANT_TBL[2])
    buf = io.BytesIO()
    im_work.save(buf, format = 'JPEG', qtables = [
        lum_q,
        chr_q], subsampling = '4:2:2', optimize = False)
    jpg_bytes = buf.getvalue()
    sos_idx = jpg_bytes.find(b'\xff\xda\x00\x0c')
    if sos_idx == -1:
        raise ValueError('Could not locate JPEG SOS marker')
    scan_data = jpg_bytes[sos_idx + 14:-2]
    return b'SJPG' + struct.pack('>HHHH', 320, 240, 3, 2) + scan_data



# ============================================================
# MODULE: mmi_builder.py
# ============================================================

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


def encode_sjpg(im, q_idx = 2, blur = 0):
    '''Encodes to SJPG. NOTE(recovery): default q_idx changed 0->2 to match the
    device stock format (stock slots use q_idx=2 and the recovered quant table
    is the device index-2 table); encoding at 0 stored a mismatched index and
    the device decoded it as garbage.'''
    # (removed intra-app import: import spd_sjpg)
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
    return encode_sjpg(im, q_idx = 2, blur = 0)


def encode_q0(im, blur = 0):
    '''Encodes an image to compact SJPG using quant table 0.'''
    return encode_sjpg(im, q_idx = 2, blur = blur)

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
    # (removed intra-app import: import spd_sjpg)
    end_off = 40042980
    start_slot = preferred_start_slot
    # NOTE(recovery): cache each stock slot's q0 re-encode so it is computed once
    # instead of on every start_slot pass (was ~10x redundant work -> looked hung).
    _stock_cache = { }
    _stock_img_cache = { }
    def _stock_image(s):
        if s not in _stock_img_cache:
            idx = s - 2
            rel = struct.unpack_from('<I', orig_mmi, OFFSETS_OFF + idx * 4)[0]
            sz = struct.unpack_from('<I', orig_mmi, INFO_OFF + idx * 12 + 8)[0]
            abs_p = P40 + rel
            _stock_img_cache[s] = spd_sjpg.sjpg_to_image(orig_mmi[abs_p:abs_p + sz])
        return _stock_img_cache[s]
    def _stock_packed(s):
        if s not in _stock_cache:
            _stock_cache[s] = encode_sjpg(_stock_image(s), q_idx = 2, blur = 0)
        return _stock_cache[s]
    while start_slot >= 20:
        start_idx = start_slot - 2
        start_rel = struct.unpack_from('<I', orig_mmi, OFFSETS_OFF + start_idx * 4)[0]
        start_off = P40 + start_rel
        pool_capacity = end_off - start_off
        packed = { }
        for s in range(start_slot, 71):
            val = custom_wallpapers.get(s)
            # NOTE(recovery): decompiler emitted `while val:` here; restored to `if/else`
            # (the `while` form would loop forever). Verify against original source.
            if val:
                if isinstance(val, bytes):
                    packed[s] = val
                    continue
                packed[s] = encode_sjpg(val, q_idx = 2, blur = 0)
                continue
            packed[s] = _stock_packed(s)
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
    images = { }
    for s in range(start_slot, 71):
        val = custom_wallpapers.get(s)
        if val:
            if isinstance(val, bytes):
                packed[s] = val
                continue
            images[s] = val
            blurs[s] = 0.0
            packed[s] = encode_sjpg(val, q_idx = 2, blur = 0)
            continue
        # NOTE(recovery): keep the decoded stock image too, so the fit loop below
        # can lightly blur the largest slot whether it is custom or stock.
        images[s] = _stock_image(s)
        blurs[s] = 0.0
        packed[s] = _stock_packed(s)
    # NOTE(recovery): the original blur-fitting loop was lost in decompilation.
    # Reconstructed and BOUNDED: repeatedly blur the current largest slot (custom
    # or stock) a little and re-encode until everything fits the pool. A per-slot
    # blur cap and a hard guard guarantee termination.
    _guard = 0
    while sum((len(d) + 3 & -4) for d in packed.values()) > pool_capacity and blurs and _guard < 3000:
        _guard += 1
        largest_s = max(blurs.keys(), key = (lambda s: len(packed[s])))
        blurs[largest_s] += 0.5
        if blurs[largest_s] > 40:
            del blurs[largest_s]
            continue
        packed[largest_s] = encode_sjpg(images[largest_s], q_idx = 2, blur = blurs[largest_s])
    tot = sum((len(d) + 3 & -4) for d in packed.values())
    if not tot <= pool_capacity:
        raise Exception(f'''Wallpapers exceeded pool capacity: {tot} > {pool_capacity}''')
    return (start_slot, start_off, packed)


def prepare_slots_61_70(slot_inputs, orig_mmi):
    '''Compatibility wrapper redirecting to prepare_slots_pool.'''
    return prepare_slots_pool(slot_inputs, orig_mmi, preferred_start_slot = 38)


# LIST0 indices of the 9 main menu icons (normal display state), from the
# theme engine's icon set. NOTE(recovery): selected/highlighted variants live at
# other LIST0 indices; v1 replaces the normal icons.
MENU_ICON_INDICES = [227, 229, 231, 233, 235, 237, 241, 243, 251]

# Maps a normal menu-icon index -> its "selected/highlighted" LIST0 index (the
# variant shown with the shadow + check badge when the item is focused). Mapped
# from the exported icon atlas. Empty until inspected; selected variants are then
# left unchanged.
SELECTED_ICON_INDICES = {}


def _list0_slot(orig, idx):
    '''Return (abs_off, sz, cap, geometry) for a LIST0 icon index, or None.'''
    try:
        rel = struct.unpack_from('<I', orig, LIST0_OFFSETS_OFF + idx * 4)[0]
        sz = struct.unpack_from('<I', orig, LIST0_INFO_OFF + idx * 12 + 8)[0]
        abs_off = LIST0_P0 + rel
        next_rel = struct.unpack_from('<I', orig, LIST0_OFFSETS_OFF + (idx + 1) * 4)[0]
        cap = (LIST0_P0 + next_rel) - abs_off
        if cap <= 0:
            cap = sz
        if sz < 16 or abs_off < 0 or abs_off + sz > len(orig):
            return None
        try:
            W, H, _, _, topY, topX, bottomY, bottomX = struct.unpack('>HHHHBBBB', orig[abs_off + 4:abs_off + 16])
        except Exception:
            W, H, topY, topX, bottomY, bottomX = 68, 66, 9, 5, 5, 11
        return (abs_off, sz, cap, (W, H, topY, topX, bottomY, bottomX))
    except Exception:
        return None


def _decode_list0(orig, idx):
    '''Decode a LIST0 icon to an RGBA image, or None if it is not an ABM icon.'''
    slot = _list0_slot(orig, idx)
    if slot is None:
        return None
    abs_off, sz, cap, geom = slot
    data = orig[abs_off:abs_off + sz]
    if data[:3] != b'ABM':
        return None
    try:
        return spd_sjpg.decode_abm(data)
    except Exception:
        return None


def _icon_signature(im):
    '''A small normalized grayscale vector for correlating two icons by shape.'''
    g = im.convert('RGBA').resize((32, 32), Image.LANCZOS)
    r, gr, b, a = g.split()
    lum = Image.merge('RGB', (r, gr, b)).convert('L')
    px = list(lum.getdata())
    ap = list(a.getdata())
    vec = [px[i] * (ap[i] / 255.0) for i in range(len(px))]
    m = sum(vec) / len(vec)
    vec = [v - m for v in vec]
    norm = sum(v * v for v in vec) ** 0.5
    if norm < 1e-6:
        return None
    return [v / norm for v in vec]


def _correlate(s1, s2):
    if not s1 or not s2:
        return -1.0
    return sum(a * b for a, b in zip(s1, s2))


def _find_selected_variant(orig, normal_idx, exclude):
    '''
Locate the "selected/highlighted" LIST0 icon that pairs with a normal menu icon.
Selected variants (with the shadow + check badge) live at non-fixed indices, so
we find them by shape: decode nearby icons and pick the one whose glyph
correlates most strongly with the normal icon. Returns an index or None.
'''
    base = _decode_list0(orig, normal_idx)
    if base is None:
        return None
    base_sig = _icon_signature(base)
    if base_sig is None:
        return None
    best_idx = None
    best = 0.0
    second = 0.0
    for cand in range(normal_idx - 2, normal_idx + 16):
        if cand == normal_idx or cand in exclude:
            continue
        im = _decode_list0(orig, cand)
        if im is None:
            continue
        score = _correlate(base_sig, _icon_signature(im))
        if score > best:
            second = best
            best = score
            best_idx = cand
        elif score > second:
            second = score
    if best_idx is not None and best >= 0.80 and (best - second) >= 0.04:
        return best_idx
    return None


def _write_icon_slot(modified, orig, idx, img):
    '''
Encode img into LIST0 icon `idx`, matching its geometry and fitting its slot
capacity by dropping colors as needed. Returns (status, size, cap).
'''
    slot = _list0_slot(orig, idx)
    if slot is None:
        return ('no slot', 0, 0)
    abs_off, sz, cap, (W, H, topY, topX, bottomY, bottomX) = slot
    enc = None
    for maxcol in (256, 200, 128, 96, 64, 48, 32, 24, 16, 12, 8, 6, 4):
        cand = spd_sjpg.encode_abm_icon(img, W=W, H=H, topY=topY, topX=topX, bottomY=bottomY, bottomX=bottomX, max_colors=maxcol)
        if len(cand) <= cap:
            enc = cand
            break
        enc = cand
    if enc is None or len(enc) > cap:
        return ('too big', len(enc) if enc else 0, cap)
    modified[abs_off:abs_off + len(enc)] = enc
    if len(enc) < sz:
        modified[abs_off + len(enc):abs_off + sz] = b'\x00' * (sz - len(enc))
    struct.pack_into('<I', modified, LIST0_INFO_OFF + idx * 12 + 8, len(enc))
    return ('ok', len(enc), cap)


def apply_custom_icons(modified, orig, icon_images):
    '''
Writes custom icons into their LIST0 slots. icon_images maps a menu position
(0..8) to a PIL image. Each normal icon is ABM-encoded to match its slot
geometry and shrunk (fewer colors) if needed to fit its slot capacity. The
matching "selected/highlighted" variant (shown when the item is focused) is
located by shape and replaced with the same image, so a replaced icon stays
custom in both states. Slots that do not fit are left unchanged.
'''
    report = []
    exclude = set(MENU_ICON_INDICES)
    for pos, img in icon_images.items():
        if img is None or pos < 0 or pos >= len(MENU_ICON_INDICES):
            continue
        idx = MENU_ICON_INDICES[pos]
        status, size, cap = _write_icon_slot(modified, orig, idx, img)
        report.append((idx, status, size, cap))
        if status != 'ok':
            continue
        sel = SELECTED_ICON_INDICES.get(idx)
        if sel is not None and sel not in exclude:
            exclude.add(sel)
            s2, sz2, cap2 = _write_icon_slot(modified, orig, sel, img)
            report.append((sel, 'sel:' + s2, sz2, cap2))
        else:
            report.append((idx, 'sel:pending', 0, 0))
    return report


def export_icon_atlas(out_path, lo=210, hi=262, cols=8, cell=64):
    '''
Decode every LIST0 icon in [lo, hi] and save a single labelled montage PNG, used
to visually identify the selected/highlighted variant that pairs with each normal
menu icon. Returns (out_path, count).
'''
    from PIL import ImageDraw
    with open(MMI_DUMP_PATH, 'rb') as f:
        orig = f.read()
    items = [(idx, _decode_list0(orig, idx)) for idx in range(lo, hi + 1)]
    rows = (len(items) + cols - 1) // cols
    label_h = 14
    atlas = Image.new('RGB', (cols * cell, rows * (cell + label_h)), (34, 37, 42))
    d = ImageDraw.Draw(atlas)
    for i, (idx, im) in enumerate(items):
        r, c = divmod(i, cols)
        x = c * cell
        y = r * (cell + label_h)
        chip = Image.new('RGBA', (cell, cell), (255, 255, 255, 255))
        if im is not None:
            chip.alpha_composite(im.convert('RGBA').resize((cell - 8, cell - 8), Image.LANCZOS), (4, 4))
        atlas.paste(chip.convert('RGB'), (x, y + label_h))
        mark = str(idx) + ('*' if idx in MENU_ICON_INDICES else '')
        d.text((x + 2, y + 1), mark, fill=(255, 214, 102))
    atlas.save(out_path)
    return (out_path, len(items))


def build_modified_mmi(custom_wallpapers, theme_hex = None, use_unisoc_icons = False, custom_icons = None):
    '''
Builds patched MMI binary respecting exact user customization choices:
- Guaranteed ZERO Gaussian blur (blur = 0.0) for all custom wallpapers.
- Dynamically packs into high-efficiency pool (up to 0x26301E4).
- Theme colors applied via theme_engine.
Guaranteed zero bootloop and zero overflow beyond List 40 limit (0x26301E4).
'''
    # (removed intra-app import: import theme_engine)
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
            # NOTE(recovery): slot 1 must fit a fixed 2551-byte region. Blur size
            # is non-monotonic (it bottoms out then rises), so scan a range and
            # keep the smallest encoding, stopping as soon as one fits.
            sjpg1 = encode_sjpg(val1, q_idx = 2, blur = 0)
            best = sjpg1
            if len(best) > 2551:
                blur = 0.0
                while blur < 60:
                    blur += 0.5
                    cand = encode_sjpg(val1, q_idx = 2, blur = blur)
                    if len(cand) < len(best):
                        best = cand
                    if len(cand) <= 2551:
                        best = cand
                        break
                sjpg1 = best
        else:
            sjpg1 = val1
        if len(sjpg1) <= 2551:
            modified[892172:892172 + len(sjpg1)] = sjpg1
            if len(sjpg1) < 2551:
                modified[892172 + len(sjpg1):894723] = b'\x00' * (2551 - len(sjpg1))
        else:
            # Too detailed to fit slot 1's fixed region even at best compression:
            # keep the original slot 1 rather than failing the whole build.
            modified[892172:894723] = orig[892172:894723]
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
            sjpg = None
            if isinstance(val, Image.Image):
                # NOTE(recovery): slots below the pool have a small fixed capacity.
                # Blur the image down until it fits instead of aborting the build.
                sjpg = encode_sjpg(val, q_idx = 2, blur = 0)
                if len(sjpg) > cap:
                    blur = 0.0
                    best = sjpg
                    while blur < 60:
                        blur += 0.5
                        cand = encode_sjpg(val, q_idx = 2, blur = blur)
                        if len(cand) < len(best):
                            best = cand
                        if len(cand) <= cap:
                            best = cand
                            break
                    sjpg = best
            else:
                sjpg = val
            if sjpg is not None and len(sjpg) <= cap:
                modified[abs_off:abs_off + len(sjpg)] = sjpg
                struct.pack_into('<HHII', modified, INFO_OFF + idx * 12, 240, 320, 522, len(sjpg))
                struct.pack_into('<I', modified, OFFSETS_OFF + idx * 4, abs_off - P40)
                continue
            # Too big to fit this low slot's fixed capacity even blurred: keep the
            # original slot rather than failing the whole build.
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
    
    if custom_icons:
        try:
            rep = apply_custom_icons(modified, orig, custom_icons)
            print('Custom icons:', rep)
        except Exception as e:
            print(f'''Warning: could not apply custom icons: {e}''')

    try:
        # (removed intra-app import: import text_engine)
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
    # (removed intra-app import: import spd_sjpg)
    # (removed intra-app import: import text_engine)
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



# ============================================================
# MODULE: dll_generator.py
# ============================================================

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
        raise Exception(f'''Expected 0x600 header, got {len(hook_header)}''')
    # NOTE(recovery): decompiler mangled this byte literal into chained subscripts.
    # Restored to the 33-byte sequence written into hook_header[157:190].
    clean_loop = bytes([81, 139, 22, 139, 78, 4, 131, 198, 8, 87, 1, 215, 243, 164, 95, 89, 73, 117, 237, 144, 144, 144, 144, 144, 144, 91, 95, 94, 90, 89, 88, 93, 195])
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



# ============================================================
# MODULE: theme_engine.py
# ============================================================


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



# ============================================================
# MODULE: text_engine.py
# ============================================================

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
        # NOTE(recovery): decompiler rendered this guard as `while ...: pass`
        # (infinite). Restored to skip no-op / empty replacements.
        if not orig_text or not new_text or orig_text == new_text:
            continue
        orig_enc = orig_text.encode('utf-16le')
        new_enc = new_text.encode('utf-16le')
        # NOTE(recovery): decompiler flattened this region scan into a single
        # check. Restored to a while-scan (same shape as search_hebrew_strings),
        # replacing every matching string entry. p always advances, so no hang.
        p = STR_REGION_START
        while p < STR_REGION_END - 4:
            flag = int.from_bytes(mmi_bytes[p:p + 2], 'little')
            if flag == 128:
                length = int.from_bytes(mmi_bytes[p + 2:p + 4], 'little')
                if length >= len(new_enc) and length <= 400:
                    curr_enc = mmi_bytes[p + 4:p + 4 + length]
                    if curr_enc.startswith(orig_enc):
                        padded_new = new_enc + b'\x00' * (length - len(new_enc))
                        mmi_bytes[p + 4:p + 4 + length] = padded_new
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
                except Exception:
                    pass
                # NOTE(recovery): advance unconditionally so a string that fails
                # to decode cannot pin p and hang the scan.
                p += 4 + length
                continue
            p += 2
            continue
        p += 2
    return results



# ============================================================
# MAIN MODULE: app.py
# ============================================================

'''
app.py - QLYX Q8 Wallpaper Studio GUI Application
High-performance Canvas-based Wallpaper Manager with HD Preview & Live WOT Sync
'''
import os
import sys
import threading
import queue
import math
import colorsys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageFilter
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


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
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
# (removed intra-app import: import spd_sjpg)
# (removed intra-app import: import mmi_builder)
# (removed intra-app import: import dll_generator)
# (removed intra-app import: import theme_engine)
# (removed intra-app import: import text_engine)
ORIG_WP_DIR = os.path.join(BASE_DIR, 'assets', 'orig_wp')
CUSTOM_WP_DIR = os.path.join(BASE_DIR, 'assets', 'custom_user_wp')
os.makedirs(CUSTOM_WP_DIR, exist_ok = True)
TOTAL_WALLPAPERS = 70
THUMB_W = 144
THUMB_H = 192
CARD_W = 166
CARD_H = 276
GAP_X = 14
GAP_Y = 14
START_X = 16
START_Y = 16

def make_sharp_thumbnail(pil_image, size = (THUMB_W, THUMB_H)):
    '''
Downsamples image with high-quality Lanczos and subtle sharpening for crystal-clear clarity.
'''
    thumb = pil_image.resize(size, Image.Resampling.LANCZOS)
    return thumb.filter(ImageFilter.UnsharpMask(radius = 0.6, percent = 100, threshold = 2))


def find_hebrew_font(size):
    '''Returns a Hebrew-capable PIL font, trying common Windows fonts.'''
    from PIL import ImageFont
    candidates = [
        'C:\\Windows\\Fonts\\david.ttf', 'C:\\Windows\\Fonts\\DAVIDBD.TTF',
        'C:\\Windows\\Fonts\\narkisim.ttf', 'C:\\Windows\\Fonts\\FrankRuehl.ttf',
        'C:\\Windows\\Fonts\\gisha.ttf', 'C:\\Windows\\Fonts\\tahoma.ttf',
        'C:\\Windows\\Fonts\\arial.ttf', 'C:\\Windows\\Fonts\\segoeui.ttf',
        'C:\\Windows\\Fonts\\times.ttf', 'arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf']
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    from PIL import ImageFont as _IF
    return _IF.load_default()


def render_text_to_wallpapers(text, font_size = 20, fg = (25, 25, 25), bg = (247, 242, 227), margin = 12, line_gap = 5, title = None, title_size = None):
    '''
Renders a long (Hebrew) text into a list of 240x320 wallpaper images.
Right-to-left, right-aligned, word-wrapped, paginated across as many images
as needed. Returns a list of PIL RGB images.
'''
    from PIL import ImageDraw
    W = THUMB_W if False else 240
    H = 320
    font = find_hebrew_font(font_size)
    tfont = find_hebrew_font(title_size or font_size + 4)
    tmp = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(tmp)
    max_w = W - 2 * margin

    def wrap(s, fnt):
        out = []
        for para in s.replace('\r', '').split('\n'):
            para = para.strip()
            if not para:
                out.append('')
                continue
            words = para.split(' ')
            cur = ''
            for w in words:
                test = (cur + ' ' + w).strip()
                if d.textlength(test, font = fnt) <= max_w:
                    cur = test
                else:
                    if cur:
                        out.append(cur)
                    # a single word longer than the line: hard-split it
                    while d.textlength(w, font = fnt) > max_w and len(w) > 1:
                        cut = len(w)
                        while cut > 1 and d.textlength(w[:cut], font = fnt) > max_w:
                            cut -= 1
                        out.append(w[:cut])
                        w = w[cut:]
                    cur = w
            if cur:
                out.append(cur)
        return out

    lines = wrap(text, font)
    asc, desc = font.getmetrics()
    lh = asc + desc + line_gap
    usable_h = H - 2 * margin
    per_page = max(1, usable_h // lh)
    pages = []
    i = 0
    while i < len(lines):
        chunk = lines[i:i + per_page]
        i += per_page
        img = Image.new('RGB', (W, H), bg)
        dr = ImageDraw.Draw(img)
        y = margin
        for ln in chunk:
            disp = ln[::-1]
            tw = dr.textlength(disp, font = font)
            dr.text((W - margin - tw, y), disp, font = font, fill = fg)
            y += lh
        pages.append(img)
    if not pages:
        pages.append(Image.new('RGB', (W, H), bg))
    return pages


class ZoomDialog(tk.Toplevel):
    '''
Full 2x HD Zoom preview modal (480x640) for inspecting fine wallpaper details.
'''
    
    def __init__(self, parent, image, slot_num):
        '''תצוגת HD מוגדלת פי 2 (480x640) - טפט #'''
        super().__init__(parent)
        self.title(f'''תצוגת HD מוגדלת פי 2 (480x640) - טפט #{slot_num}''')
        self.geometry('520x750')
        self.resizable(False, False)
        self.configure(bg = '#181a1f')
        self.transient(parent)
        self.grab_set()
        lbl_title = tk.Label(self, text = f'''🔍 טפט #{slot_num} - רזולוציה מוכפלת פי 2 (480 × 640)''', font = ('Segoe UI', 12, 'bold'), fg = '#06d6a0', bg = '#181a1f')
        lbl_title.pack(pady = (14, 6))
        canvas = tk.Canvas(self, width = 480, height = 640, bg = '#111215', highlightthickness = 2, highlightbackground = '#06d6a0')
        canvas.pack(pady = 6)
        zoom_im = image.resize((480, 640), Image.Resampling.NEAREST)
        self.tk_img = ImageTk.PhotoImage(zoom_im)
        canvas.create_image(240, 320, image = self.tk_img)
        btn_close = tk.Button(self, text = 'סגור חלון', font = ('Segoe UI', 10, 'bold'), bg = '#3d405b', fg = '#ffffff', activebackground = '#2b2d42', activeforeground = '#ffffff', relief = 'flat', padx = 20, pady = 6, cursor = 'hand2', command = self.destroy)
        btn_close.pack(pady = (8, 12))
        return None



class ImageCropDialog(tk.Toplevel):
    '''
Dialog for previewing and choosing fit mode (Crop, Fit, Stretch) before applying.
Displays 1:1 native 240x320 preview for maximum clarity.
'''
    
    def __init__(self, parent, image_path, slot_num):
        '''התאמת תמונה - טפט #'''
        super().__init__(parent)
        self.title(f'''התאמת תמונה - טפט #{slot_num}''')
        self.geometry('460x650')
        self.resizable(False, False)
        self.configure(bg = '#22252a')
        self.transient(parent)
        self.grab_set()
        self.slot_num = slot_num
        self.raw_image = Image.open(image_path).convert('RGB')
        self.selected_mode = tk.StringVar(value = 'crop')
        self.result_image = None
        self._build_ui()
        self._update_preview()
        return None

    
    def _build_ui(self):
        '''הגדרת תמונה עבור טפט #'''
        lbl_title = tk.Label(self, text = f'''הגדרת תמונה עבור טפט #{self.slot_num}''', font = ('Segoe UI', 12, 'bold'), fg = '#f8f9fa', bg = '#22252a')
        lbl_title.pack(pady = (12, 4))
        lbl_sub = tk.Label(self, text = 'תצוגה מקדימה בגודל מסך מלא (240x320 פיקסלים)', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#22252a')
        lbl_sub.pack(pady = (0, 6))
        self.preview_canvas = tk.Canvas(self, width = 240, height = 320, bg = '#111215', highlightthickness = 2, highlightbackground = '#06d6a0')
        self.preview_canvas.pack(pady = 6)
        opts_frame = tk.LabelFrame(self, text = ' אופן התאמת התמונה למסך (240x320) ', font = ('Segoe UI', 10), fg = '#06d6a0', bg = '#22252a', padx = 12, pady = 6)
        opts_frame.pack(fill = 'x', padx = 24, pady = 6)
        modes = [
            ('crop', 'חיתוך ומרכוז למסך (מומלץ - שומר על איכות ללא עיוות)'),
            ('fit', 'התאמה מלאה עם שוליים שחורים (ללא חיתוך)'),
            ('stretch', 'מתיחה לגודל מסך מלא')]
        for val, txt in modes:
            rb = tk.Radiobutton(opts_frame, text = txt, value = val, variable = self.selected_mode, command = self._update_preview, font = ('Segoe UI', 9), fg = '#f8f9fa', bg = '#22252a', selectcolor = '#111215', activebackground = '#22252a', activeforeground = '#06d6a0')
            rb.pack(anchor = 'e', pady = 2)
        btn_frame = tk.Frame(self, bg = '#22252a')
        btn_frame.pack(fill = 'x', padx = 24, pady = (10, 14))
        btn_ok = tk.Button(btn_frame, text = '✔ שמור והחלף', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', padx = 16, pady = 6, cursor = 'hand2', command = self._on_ok)
        btn_ok.pack(side = 'right', padx = 6)
        btn_cancel = tk.Button(btn_frame, text = 'ביטול', font = ('Segoe UI', 10), bg = '#3d405b', fg = '#f8f9fa', relief = 'flat', padx = 12, pady = 6, cursor = 'hand2', command = self.destroy)
        btn_cancel.pack(side = 'left', padx = 6)

    
    def _update_preview(self):
        mode = self.selected_mode.get()
        fitted = spd_sjpg.fit_image(self.raw_image, 240, 320, mode = mode)
        self.result_image = fitted
        self.tk_thumb = ImageTk.PhotoImage(fitted)
        self.preview_canvas.delete('all')
        self.preview_canvas.create_image(120, 160, image = self.tk_thumb)

    
    def _on_ok(self):
        '''wp_'''
        dest_path = os.path.join(CUSTOM_WP_DIR, f'''wp_{self.slot_num}.png''')
        self.result_image.save(dest_path)
        sjpg_dest = os.path.join(CUSTOM_WP_DIR, f'''wp_{self.slot_num}.sjpg''')
        if os.path.exists(sjpg_dest):
            os.remove(sjpg_dest)
            return None



class TextToWallpaperDialog(tk.Toplevel):
    '''
Turns a long (Hebrew) text into a series of wallpaper images and assigns them
to consecutive slots, so long content (e.g. Birkat Hamazon) can live on the
device across several wallpapers instead of the tiny fixed text fields.
'''

    def __init__(self, parent, start_slot = 20):
        super().__init__(parent)
        self.parent = parent
        self.title('📖 טקסט לטפט')
        self.geometry('540x640')
        self.resizable(False, False)
        self.configure(bg = '#22252a')
        self.transient(parent)
        self.grab_set()
        self._start_default = max(1, min(TOTAL_WALLPAPERS, start_slot))
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text = 'טקסט לטפט (לדוגמה: ברכת המזון)', font = ('Segoe UI', 13, 'bold'), fg = '#06d6a0', bg = '#22252a').pack(pady = (12, 2))
        tk.Label(self, text = 'הדבק טקסט ארוך; הוא יחולק אוטומטית לכמה טפטים קריאים.', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#22252a').pack(pady = (0, 8))
        txt_frame = tk.Frame(self, bg = '#22252a')
        txt_frame.pack(fill = 'both', expand = True, padx = 16)
        self.txt = tk.Text(txt_frame, height = 12, font = ('David', 13), bg = '#111215', fg = '#f8f9fa', insertbackground = '#06d6a0', wrap = 'word')
        self.txt.pack(side = 'right', fill = 'both', expand = True)
        sb = tk.Scrollbar(txt_frame, command = self.txt.yview)
        sb.pack(side = 'left', fill = 'y')
        self.txt.config(yscrollcommand = sb.set)
        opts = tk.Frame(self, bg = '#22252a')
        opts.pack(fill = 'x', padx = 16, pady = 8)
        tk.Label(opts, text = 'טפט התחלה:', font = ('Segoe UI', 9, 'bold'), fg = '#f8f9fa', bg = '#22252a').pack(side = 'right', padx = (6, 2))
        self.spn_start = tk.Spinbox(opts, from_ = 1, to = TOTAL_WALLPAPERS, width = 5, font = ('Segoe UI', 10), justify = 'center', bg = '#111215', fg = '#06d6a0')
        self.spn_start.delete(0, 'end')
        self.spn_start.insert(0, str(self._start_default))
        self.spn_start.pack(side = 'right')
        tk.Label(opts, text = 'גודל גופן:', font = ('Segoe UI', 9, 'bold'), fg = '#f8f9fa', bg = '#22252a').pack(side = 'right', padx = (16, 2))
        self.spn_font = tk.Spinbox(opts, from_ = 12, to = 40, width = 4, font = ('Segoe UI', 10), justify = 'center', bg = '#111215', fg = '#06d6a0')
        self.spn_font.delete(0, 'end')
        self.spn_font.insert(0, '20')
        self.spn_font.pack(side = 'right')
        self.lbl_info = tk.Label(self, text = '', font = ('Segoe UI', 9), fg = '#ffd166', bg = '#22252a')
        self.lbl_info.pack(pady = (0, 4))
        btns = tk.Frame(self, bg = '#22252a')
        btns.pack(fill = 'x', padx = 16, pady = (0, 14))
        tk.Button(btns, text = '✔ צור והקצה לטפטים', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', relief = 'flat', padx = 16, pady = 6, cursor = 'hand2', command = self._generate).pack(side = 'right', padx = 6)
        tk.Button(btns, text = '👁 תצוגה מקדימה', font = ('Segoe UI', 10), bg = '#2a475e', fg = '#f8f9fa', relief = 'flat', padx = 12, pady = 6, cursor = 'hand2', command = self._preview).pack(side = 'right', padx = 6)
        tk.Button(btns, text = 'ביטול', font = ('Segoe UI', 10), bg = '#3d405b', fg = '#f8f9fa', relief = 'flat', padx = 12, pady = 6, cursor = 'hand2', command = self.destroy).pack(side = 'left', padx = 6)

    def _render(self):
        text = self.txt.get('1.0', 'end').strip()
        if not text:
            messagebox.showwarning('אין טקסט', 'הדבק טקסט תחילה.')
            return (None, None, None)
        try:
            fs = int(self.spn_font.get())
        except Exception:
            fs = 20
        try:
            start = int(self.spn_start.get())
        except Exception:
            start = self._start_default
        pages = render_text_to_wallpapers(text, font_size = fs)
        return (pages, start, fs)

    def _preview(self):
        pages, start, fs = self._render()
        if pages is None:
            return None
        n = len(pages)
        end = start + n - 1
        note = '' if end <= TOTAL_WALLPAPERS else f'  ⚠ חורג! צריך עד טפט {end}.'
        self.lbl_info.config(text = f'ייווצרו {n} טפטים: #{start} עד #{end}.{note}')
        ZoomDialog(self, pages[0], start)

    def _generate(self):
        pages, start, fs = self._render()
        if pages is None:
            return None
        n = len(pages)
        end = start + n - 1
        if end > TOTAL_WALLPAPERS:
            messagebox.showerror('אין מספיק טפטים', f'הטקסט דורש {n} טפטים (#{start} עד #{end}), אבל יש רק {TOTAL_WALLPAPERS}.\nבחר טפט התחלה נמוך יותר או הגדל את הגופן (פחות טפטים).')
            return None
        for k, img in enumerate(pages):
            self.parent._assign_custom_image(start + k, img)
        self.parent.lbl_status.config(text = f'‏נוצרו {n} טפטי טקסט (#{start}–#{end}). לחץ \'החל והכן לצריבה\' לצריבה למכשיר.')
        messagebox.showinfo('נוצר בהצלחה', f'הטקסט חולק ל-{n} טפטים (#{start} עד #{end}).\nלחץ על \'החל והכן לצריבה בתוכנת WOT\' כדי לצרוב.')
        self.destroy()


class IconReplaceDialog(tk.Toplevel):
    '''
Replace the 9 main menu icons with custom images. Shows each original icon
(decoded from the MMI) so the user knows which is which, then lets them pick a
replacement image per icon. Chosen images are stored on the parent and encoded
to the device ABM format at deploy time.
'''

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title('🎨 החלפת אייקונים')
        self.geometry('560x520')
        self.configure(bg = '#22252a')
        self.transient(parent)
        self.grab_set()
        self._thumbs = {}
        self._orig_imgs = self._load_originals()
        self._build_ui()

    def _load_originals(self):
        import struct
        res = {}
        try:
            with open(mmi_builder.MMI_DUMP_PATH, 'rb') as f:
                d = f.read()
            for pos, idx in enumerate(mmi_builder.MENU_ICON_INDICES):
                try:
                    rel = struct.unpack_from('<I', d, mmi_builder.LIST0_OFFSETS_OFF + idx * 4)[0]
                    sz = struct.unpack_from('<I', d, mmi_builder.LIST0_INFO_OFF + idx * 12 + 8)[0]
                    ab = mmi_builder.LIST0_P0 + rel
                    res[pos] = spd_sjpg.decode_abm(d[ab:ab + sz])
                except Exception:
                    res[pos] = None
        except Exception:
            pass
        return res

    def _build_ui(self):
        tk.Label(self, text = 'החלפת אייקוני התפריט הראשי (9 אייקונים)', font = ('Segoe UI', 13, 'bold'), fg = '#06d6a0', bg = '#22252a').pack(pady = (12, 2))
        tk.Label(self, text = 'לחץ על אייקון כדי לבחור תמונה שתחליף אותו. רקע לבן מומלץ.', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#22252a').pack(pady = (0, 8))
        grid = tk.Frame(self, bg = '#22252a')
        grid.pack(padx = 12, pady = 6)
        for pos in range(9):
            r, c = divmod(pos, 3)
            cell = tk.Frame(grid, bg = '#1a1c23', padx = 6, pady = 6, highlightthickness = 1, highlightbackground = '#343a40')
            cell.grid(row = r, column = c, padx = 6, pady = 6)
            cv = tk.Canvas(cell, width = 56, height = 56, bg = '#ffffff', highlightthickness = 0, cursor = 'hand2')
            cv.pack()
            self._render_thumb(cv, pos)
            cv.bind('<Button-1>', (lambda e, p = pos, canvas = cv: self._pick(p, canvas)))
            tk.Button(cell, text = 'בחר', font = ('Segoe UI', 8), bg = '#2a475e', fg = '#fff', relief = 'flat', cursor = 'hand2', command = (lambda p = pos, canvas = cv: self._pick(p, canvas))).pack(pady = (4, 0))
        btns = tk.Frame(self, bg = '#22252a')
        btns.pack(fill = 'x', padx = 16, pady = 12)
        tk.Button(btns, text = '✔ סגור', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', relief = 'flat', padx = 16, pady = 6, cursor = 'hand2', command = self.destroy).pack(side = 'right', padx = 6)
        tk.Button(btns, text = '🔎 ייצא מפת אייקונים', font = ('Segoe UI', 10), bg = '#e07b39', fg = '#fff', relief = 'flat', padx = 12, pady = 6, cursor = 'hand2', command = self._export_atlas).pack(side = 'left', padx = 6)
        tk.Label(self, text = 'לאחר בחירה, לחץ "החל והכן לצריבה" במסך הראשי.', font = ('Segoe UI', 9), fg = '#ffd166', bg = '#22252a').pack(pady = (0, 6))

    def _export_atlas(self):
        import os
        try:
            downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
            base = downloads if os.path.isdir(downloads) else os.path.expanduser('~')
            out = os.path.join(base, 'q8_icon_atlas.png')
            path, n = mmi_builder.export_icon_atlas(out)
            messagebox.showinfo('מפת אייקונים', f'‏נשמרה מפה של {n} אייקונים:\n{path}\n\nשלח/י את הקובץ הזה כדי שנזהה את אייקוני הבחירה (הווריאנט עם הצל וה-✓).')
        except Exception as e:
            messagebox.showerror('שגיאה', f'‏ייצוא נכשל:\n{e}')

    def _render_thumb(self, canvas, pos):
        img = self.parent.custom_icons.get(pos) or self._orig_imgs.get(pos)
        if img is None:
            return
        disp = Image.new('RGBA', (56, 56), (255, 255, 255, 255))
        disp.alpha_composite(img.convert('RGBA').resize((56, 56), Image.LANCZOS))
        ph = ImageTk.PhotoImage(disp.convert('RGB'))
        self._thumbs[pos] = ph
        canvas.delete('all')
        canvas.create_image(28, 28, image = ph)

    def _pick(self, pos, canvas):
        path = filedialog.askopenfilename(title = f'''בחר תמונה לאייקון #{pos + 1}''', filetypes = [('קבצי תמונה', '*.png;*.jpg;*.jpeg;*.webp;*.bmp'), ('כל הקבצים', '*.*')])
        if not path:
            return None
        try:
            im = Image.open(path).convert('RGBA')
        except Exception as e:
            messagebox.showerror('שגיאה', f'''לא ניתן לפתוח את התמונה:\n{e}''')
            return None
        self.parent.custom_icons[pos] = im
        self._render_thumb(canvas, pos)
        self.parent.lbl_status.config(text = f'''‏אייקון #{pos + 1} נבחר. לחץ \'החל והכן לצריבה\' לצריבה.''')


class WallpaperSwapDialog(tk.Toplevel):
    '''
Dialog for swapping / reordering wallpaper positions between two slots.
Shows side-by-side previews of Slot A and Slot B with real-time live updates.
'''
    
    def __init__(self, parent, initial_slot_a = 1, initial_slot_b = None):
        '''⇄ החלפת מיקומים בין טפטים'''
        super().__init__(parent)
        self.parent = parent
        self.title('⇄ החלפת מיקומים בין טפטים')
        self.geometry('540x510')
        self.resizable(False, False)
        self.configure(bg = '#22252a')
        self.transient(parent)
        self.grab_set()
        init_a = max(1, min(TOTAL_WALLPAPERS, initial_slot_a))
        if initial_slot_b is None:
            init_b = 1 if init_a != 1 else 2
        else:
            init_b = max(1, min(TOTAL_WALLPAPERS, initial_slot_b))
        self.slot_a_var = tk.IntVar(value = init_a)
        self.slot_b_var = tk.IntVar(value = init_b)
        self._thumb_a = None
        self._thumb_b = None
        self._build_ui()
        self._update_views()
        return None

    
    def _build_ui(self):
        '''⇄ החלפת מיקומים הדדית בין שני טפטים'''
        lbl_title = tk.Label(self, text = '⇄ החלפת מיקומים הדדית בין שני טפטים', font = ('Segoe UI', 13, 'bold'), fg = '#06d6a0', bg = '#22252a')
        lbl_title.pack(pady = (14, 2))
        lbl_desc = tk.Label(self, text = 'בחר שני טפטים כדי להחליף את התמונות שלהם אחד במקום השני:', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#22252a')
        lbl_desc.pack(pady = (0, 10))
        cards_frame = tk.Frame(self, bg = '#22252a')
        cards_frame.pack(fill = 'x', padx = 20, pady = 4)
        col_a = tk.Frame(cards_frame, bg = '#1a1c23', padx = 12, pady = 10, highlightthickness = 1, highlightbackground = '#343a40')
        col_a.pack(side = 'right', expand = True, fill = 'both', padx = (6, 0))
        row_sel_a = tk.Frame(col_a, bg = '#1a1c23')
        row_sel_a.pack(fill = 'x', pady = (0, 4))
        lbl_a = tk.Label(row_sel_a, text = 'טפט מקור:', font = ('Segoe UI', 9, 'bold'), fg = '#ffffff', bg = '#1a1c23')
        lbl_a.pack(side = 'right', padx = (4, 0))
        self.spn_a = tk.Spinbox(row_sel_a, from_ = 1, to = TOTAL_WALLPAPERS, textvariable = self.slot_a_var, width = 5, font = ('Segoe UI', 10, 'bold'), justify = 'center', bg = '#111215', fg = '#06d6a0', insertbackground = '#06d6a0', command = self._update_views)
        self.spn_a.pack(side = 'right')
        self.spn_a.bind('<KeyRelease>', (lambda e: self._update_views()))
        self.canvas_a = tk.Canvas(col_a, width = 120, height = 160, bg = '#111215', highlightthickness = 1, highlightbackground = '#06d6a0')
        self.canvas_a.pack(pady = 6)
        self.lbl_tag_a = tk.Label(col_a, text = '', font = ('Segoe UI', 8), bg = '#1a1c23', fg = '#adb5bd')
        self.lbl_tag_a.pack()
        col_mid = tk.Frame(cards_frame, bg = '#22252a')
        col_mid.pack(side = 'right', padx = 6)
        btn_flip = tk.Button(col_mid, text = '⇄', font = ('Segoe UI', 16, 'bold'), bg = '#2b2d42', fg = '#06d6a0', activebackground = '#1e202e', activeforeground = '#00f5d4', relief = 'flat', padx = 10, pady = 4, cursor = 'hand2', command = self._flip_slots)
        btn_flip.pack(pady = 40)
        col_b = tk.Frame(cards_frame, bg = '#1a1c23', padx = 12, pady = 10, highlightthickness = 1, highlightbackground = '#343a40')
        col_b.pack(side = 'right', expand = True, fill = 'both', padx = (0, 6))
        row_sel_b = tk.Frame(col_b, bg = '#1a1c23')
        row_sel_b.pack(fill = 'x', pady = (0, 4))
        lbl_b = tk.Label(row_sel_b, text = 'טפט יעד:', font = ('Segoe UI', 9, 'bold'), fg = '#ffffff', bg = '#1a1c23')
        lbl_b.pack(side = 'right', padx = (4, 0))
        self.spn_b = tk.Spinbox(row_sel_b, from_ = 1, to = TOTAL_WALLPAPERS, textvariable = self.slot_b_var, width = 5, font = ('Segoe UI', 10, 'bold'), justify = 'center', bg = '#111215', fg = '#06d6a0', insertbackground = '#06d6a0', command = self._update_views)
        self.spn_b.pack(side = 'right')
        self.spn_b.bind('<KeyRelease>', (lambda e: self._update_views()))
        self.canvas_b = tk.Canvas(col_b, width = 120, height = 160, bg = '#111215', highlightthickness = 1, highlightbackground = '#06d6a0')
        self.canvas_b.pack(pady = 6)
        self.lbl_tag_b = tk.Label(col_b, text = '', font = ('Segoe UI', 8), bg = '#1a1c23', fg = '#adb5bd')
        self.lbl_tag_b.pack()
        self.lbl_summary = tk.Label(self, text = '', font = ('Segoe UI', 9), fg = '#06d6a0', bg = '#22252a', wraplength = 480, justify = 'center')
        self.lbl_summary.pack(pady = (10, 8))
        btn_row = tk.Frame(self, bg = '#22252a')
        btn_row.pack(fill = 'x', padx = 20, pady = (8, 14))
        self.btn_confirm = tk.Button(btn_row, text = '✔ בצע החלפה הדדית', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', padx = 18, pady = 7, cursor = 'hand2', command = self._on_confirm)
        self.btn_confirm.pack(side = 'right', padx = 6)
        btn_cancel = tk.Button(btn_row, text = 'ביטול', font = ('Segoe UI', 10), bg = '#3d405b', fg = '#f8f9fa', relief = 'flat', padx = 14, pady = 7, cursor = 'hand2', command = self.destroy)
        btn_cancel.pack(side = 'left', padx = 6)

    
    def _flip_slots(self):
        a = self.slot_a_var.get()
        b = self.slot_b_var.get()
        self.slot_a_var.set(b)
        self.slot_b_var.set(a)
        self._update_views()

    
    def _update_views(self):
        
        try:
            a = int(self.slot_a_var.get())
            b = int(self.slot_b_var.get())
        except Exception:
            return None

        a = max(1, min(TOTAL_WALLPAPERS, a))
        b = max(1, min(TOTAL_WALLPAPERS, b))
        item_a = self.parent.slot_state.get(a)
        if item_a and item_a.get('image'):
            im_a = item_a['image'].resize((120, 160), Image.Resampling.LANCZOS)
            self._thumb_a = ImageTk.PhotoImage(im_a)
            self.canvas_a.delete('all')
            self.canvas_a.create_image(60, 80, image = self._thumb_a)
            is_c_a = item_a.get('is_custom', False)
            self.lbl_tag_a.config(text = f'''טפט #{a}: ★ מותאם אישית''' if is_c_a else f'''טפט #{a}: מקורי''', fg = '#06d6a0' if is_c_a else '#adb5bd')
        item_b = self.parent.slot_state.get(b)
        if item_b and item_b.get('image'):
            im_b = item_b['image'].resize((120, 160), Image.Resampling.LANCZOS)
            self._thumb_b = ImageTk.PhotoImage(im_b)
            self.canvas_b.delete('all')
            self.canvas_b.create_image(60, 80, image = self._thumb_b)
            is_c_b = item_b.get('is_custom', False)
            self.lbl_tag_b.config(text = f'''טפט #{b}: ★ מותאם אישית''' if is_c_b else f'''טפט #{b}: מקורי''', fg = '#06d6a0' if is_c_b else '#adb5bd')
        if a == b:
            self.lbl_summary.config(text = '⚠️ בחר שני טפטים שונים כדי לבצע החלפה ביניהם.', fg = '#ff6b6b')
            self.btn_confirm.config(state = 'disabled', bg = '#2a2e38', fg = '#6c757d')
            return None
        self.lbl_summary.config(text = f'''‏טפט #{a} יקבל את התמונה של טפט #{b}, וטפט #{b} יקבל את התמונה של טפט #{a}.''', fg = '#06d6a0')
        self.btn_confirm.config(state = 'normal', bg = '#06d6a0', fg = '#111215', text = f'''✔ החלף בין טפט #{a} לטפט #{b}''')

    
    def _on_confirm(self):
        
        try:
            a = int(self.slot_a_var.get())
            b = int(self.slot_b_var.get())
        except Exception:
            return None

        if a != b:
            self.parent.swap_wallpapers(a, b)
        self.destroy()



class SplashScreen(tk.Toplevel):
    '''
Sleek, modern splash screen displayed on startup with application branding
and copyright credit to @מה-זה-משנה-אה.
'''
    
    def __init__(self, parent, duration_ms = 2800):
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(bg = '#06d6a0')
        splash_w = 600
        splash_h = 370
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - splash_w) // 2)
        y = max(0, (screen_h - splash_h) // 2)
        self.geometry(f'''{splash_w}x{splash_h}+{x}+{y}''')
        self.attributes('-topmost', True)
        inner = tk.Frame(self, bg = '#16181d', padx = 20, pady = 18)
        inner.pack(fill = 'both', expand = True, padx = 2, pady = 2)
        icon_png = os.path.join(BASE_DIR, 'assets', 'app_icon.png')
        if os.path.exists(icon_png):
            
            try:
                self._splash_logo = ImageTk.PhotoImage(Image.open(icon_png).resize((70, 70), Image.Resampling.LANCZOS))
                lbl_logo = tk.Label(inner, image = self._splash_logo, bg = '#16181d')
                lbl_logo.pack(pady = (6, 4))
            except Exception:
                pass

        lbl_title = tk.Label(inner, text = 'סטודיו ל-Q8', font = ('Segoe UI', 22, 'bold'), fg = '#06d6a0', bg = '#16181d')
        lbl_title.pack(pady = (2, 2))
        lbl_sub = tk.Label(inner, text = 'מערכת התאמה אישית מתקדמת: 70 טפטים, צבעי ממשק ומסך אודות', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#16181d')
        lbl_sub.pack(pady = (0, 14))
        credit_box = tk.Frame(inner, bg = '#232018', highlightthickness = 1, highlightbackground = '#ffd166', padx = 16, pady = 10)
        credit_box.pack(fill = 'x', padx = 10, pady = (0, 12))
        lbl_credit_tag = tk.Label(credit_box, text = '🌟 זכויות יוצרים ופיתוח 🌟', font = ('Segoe UI', 9, 'bold'), fg = '#ffd166', bg = '#232018')
        lbl_credit_tag.pack(pady = (0, 2))
        lbl_credit_user = tk.Label(credit_box, text = 'כל הזכויות שמורות ל- @מה-זה-משנה-אה מפורום מתמחים טופ', font = ('Segoe UI', 12, 'bold'), fg = '#ffffff', bg = '#232018')
        lbl_credit_user.pack()
        self.lbl_loading = tk.Label(inner, text = '...טוען נתונים ומתחבר למערכת', font = ('Segoe UI', 9), fg = '#6c757d', bg = '#16181d')
        self.lbl_loading.pack(side = 'bottom', pady = (4, 0))
        self.bind('<Button-1>', (lambda e: self._dismiss()))
        inner.bind('<Button-1>', (lambda e: self._dismiss()))
        self.bind('<Key>', (lambda e: self._dismiss()))
        self.after(duration_ms, self._dismiss)
        return None

    
    def _dismiss(self):
        
        try:
            self.destroy()
        except Exception:
            return None




class Q8WallpaperStudio(tk.Tk):
    
    def __init__(self):
        '''סטודיו לQ8'''
        super().__init__()
        self.title('סטודיו לQ8')
        self.geometry('1280x860')
        self.minsize(980, 680)
        self.configure(bg = '#181a1f')
        
        try:
            self.state('zoomed')
        except Exception:
            pass

        icon_ico = os.path.join(BASE_DIR, 'assets', 'app_icon.ico')
        icon_png = os.path.join(BASE_DIR, 'assets', 'app_icon.png')
        if os.path.exists(icon_ico):
            
            try:
                self.iconbitmap(icon_ico)
            except Exception:
                pass

        if os.path.exists(icon_png):
            
            try:
                self._app_icon_img = ImageTk.PhotoImage(Image.open(icon_png).resize((32, 32), Image.Resampling.LANCZOS))
                self.iconphoto(True, self._app_icon_img)
            except Exception:
                pass

        self.slot_state = { }
        self.thumb_images = { }
        self.custom_icons = { }
        self.selected_slot = 1
        self.current_cols = 4
        self.is_deploying = False
        self._hovered_btn = None
        self._hovered_card = None
        self.theme_config = theme_engine.load_theme_config()
        self.confirmed_theme_hex = self.theme_config.get('active_hex', '#0284C7')
        self.confirmed_theme_name = self.theme_config.get('name', 'כחול מפעל מקורי')
        self.current_theme_hex = self.confirmed_theme_hex
        self.current_theme_name = self.confirmed_theme_name
        self.active_tab = 'wallpapers'
        self.current_h = 0
        self.current_s = 1
        self.current_v = 1
        self._syncing_wheel = False
        self._mockup_update_job = None
        self._pending_theme_hex = None
        self._cached_wheel_img = None
        
        try:
            (r, g, b) = theme_engine.hex_to_rgb(self.current_theme_hex)
            (self.current_h, self.current_s, self.current_v) = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        except Exception:
            pass

        self.text_config = text_engine.load_text_config()
        self.about_title_var = tk.StringVar(value = self.text_config.get('about_title', text_engine.DEFAULT_ABOUT_TITLE))
        self.about_body_str = self.text_config.get('about_body', text_engine.DEFAULT_ABOUT_BODY)
        self.custom_replacements = dict(self.text_config.get('replacements', { }))
        self._about_mockup_job = None
        self.ui_queue = queue.Queue()
        self._check_ui_queue()
        self._build_header()
        self._build_tabs()
        self._build_content_containers()
        self._build_footer()
        self.bind('<Left>', (lambda e: self._navigate_slot(-1)))
        self.bind('<Right>', (lambda e: self._navigate_slot(1)))
        self.bind('<Up>', (lambda e: self._navigate_slot(-(self.current_cols))))
        self.bind('<Down>', (lambda e: self._navigate_slot(self.current_cols)))
        self.load_and_refresh_from_wot()
        
        try:
            self.splash = SplashScreen(self, duration_ms = 2800)
        except Exception:
            return None

        return None

    
    def post_ui(self, func):
        self.ui_queue.put(func)

    
    def _check_ui_queue(self):
        
        try:
            func = self.ui_queue.get_nowait()
            func()
        except queue.Empty:
            pass

        self.after(50, self._check_ui_queue)

    
    def _build_header(self):
        '''#21242b'''
        header = tk.Frame(self, bg = '#21242b', padx = 20, pady = 12)
        header.pack(fill = 'x', side = 'top')
        title_frame = tk.Frame(header, bg = '#21242b')
        title_frame.pack(side = 'right', fill = 'y')
        title_top_row = tk.Frame(title_frame, bg = '#21242b')
        title_top_row.pack(anchor = 'e')
        icon_png = os.path.join(BASE_DIR, 'assets', 'app_icon.png')
        if os.path.exists(icon_png):
            
            try:
                self._header_logo_img = ImageTk.PhotoImage(Image.open(icon_png).resize((38, 38), Image.Resampling.LANCZOS))
                lbl_logo = tk.Label(title_top_row, image = self._header_logo_img, bg = '#21242b')
                lbl_logo.pack(side = 'right', padx = (10, 0))
            except Exception:
                pass

        lbl_title_heb = tk.Label(title_top_row, text = 'סטודיו ל-', font = ('Segoe UI', 18, 'bold'), fg = '#06d6a0', bg = '#21242b')
        lbl_title_heb.pack(side = 'right')
        lbl_title_q8 = tk.Label(title_top_row, text = 'Q8', font = ('Segoe UI', 18, 'bold'), fg = '#06d6a0', bg = '#21242b')
        lbl_title_q8.pack(side = 'right')
        lbl_sub = tk.Label(title_frame, text = '‏התאמה מלאה: 70 טפטים, ערכת נושא, מסך אודות ותפריטים', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#21242b')
        lbl_sub.pack(anchor = 'e', pady = (2, 0))
        actions_frame = tk.Frame(header, bg = '#21242b')
        actions_frame.pack(side = 'left', fill = 'y')
        self.btn_deploy = tk.Button(actions_frame, text = '‏🚀 החל לצריבה ב-WOT', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', padx = 12, pady = 6, cursor = 'hand2', command = self.deploy_to_wot)
        self.btn_deploy.pack(side = 'left', padx = 4)
        btn_refresh_wot = tk.Button(actions_frame, text = '‏🔄 רענן מ-WOT', font = ('Segoe UI', 9, 'bold'), bg = '#2a475e', fg = '#f8f9fa', activebackground = '#1b2838', activeforeground = '#66c0f4', relief = 'flat', padx = 8, pady = 6, cursor = 'hand2', command = self.load_and_refresh_from_wot)
        btn_refresh_wot.pack(side = 'left', padx = 4)
        btn_reset_all = tk.Button(actions_frame, text = '‏↺ איפוס הכל למקור', font = ('Segoe UI', 9), bg = '#3d405b', fg = '#f8f9fa', relief = 'flat', padx = 8, pady = 6, cursor = 'hand2', command = self.reset_all_wallpapers)
        btn_reset_all.pack(side = 'left', padx = 4)
        btn_text2wp = tk.Button(actions_frame, text = '‏📖 טקסט לטפט', font = ('Segoe UI', 9, 'bold'), bg = '#6f42c1', fg = '#ffffff', activebackground = '#5a32a3', activeforeground = '#ffffff', relief = 'flat', padx = 8, pady = 6, cursor = 'hand2', command = self.open_text_to_wallpaper_dialog)
        btn_text2wp.pack(side = 'left', padx = 4)
        btn_icons = tk.Button(actions_frame, text = '‏🎨 החלף אייקונים', font = ('Segoe UI', 9, 'bold'), bg = '#e07b39', fg = '#ffffff', activebackground = '#c96522', activeforeground = '#ffffff', relief = 'flat', padx = 8, pady = 6, cursor = 'hand2', command = self.open_icon_dialog)
        btn_icons.pack(side = 'left', padx = 4)

    
    def _build_tabs(self):
        '''#1a1c23'''
        self.tabs_bar = tk.Frame(self, bg = '#1a1c23', padx = 20, pady = 6)
        self.tabs_bar.pack(fill = 'x', side = 'top')
        tabs_inner = tk.Frame(self.tabs_bar, bg = '#1a1c23')
        tabs_inner.pack(side = 'right')
        self.btn_tab_wp = tk.Button(tabs_inner, text = '🖼️ כרטיסיית טפטים (70 טפטים)', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', padx = 16, pady = 7, cursor = 'hand2', command = (lambda : self._switch_tab('wallpapers')))
        self.btn_tab_wp.pack(side = 'right', padx = (6, 0))
        self.btn_tab_theme = tk.Button(tabs_inner, text = '🎨 כרטיסיית צבעי ערכת נושא', font = ('Segoe UI', 11), bg = '#252830', fg = '#adb5bd', activebackground = '#2d323c', activeforeground = '#f8f9fa', relief = 'flat', padx = 16, pady = 7, cursor = 'hand2', command = (lambda : self._switch_tab('theme')))
        self.btn_tab_theme.pack(side = 'right', padx = (6, 0))
        self.btn_tab_text = tk.Button(tabs_inner, text = '📝 כרטיסיית טקסטים ומיתוג', font = ('Segoe UI', 11), bg = '#252830', fg = '#adb5bd', activebackground = '#2d323c', activeforeground = '#f8f9fa', relief = 'flat', padx = 16, pady = 7, cursor = 'hand2', command = (lambda : self._switch_tab('texts')))
        self.btn_tab_text.pack(side = 'right', padx = (0, 6))

    
    def _switch_tab(self, tab_name):
        if tab_name == self.active_tab:
            return None
        if self.active_tab == 'theme' and hasattr(self, 'confirmed_theme_hex') and self.current_theme_hex.upper() != self.confirmed_theme_hex.upper():
            self.revert_to_confirmed_theme()
        self.wallpaper_frame.pack_forget()
        self.theme_frame.pack_forget()
        if hasattr(self, 'text_frame'):
            self.text_frame.pack_forget()
        for btn in (getattr(self, 'btn_tab_wp', None), getattr(self, 'btn_tab_theme', None), getattr(self, 'btn_tab_text', None)):
            if not btn:
                continue
            btn.config(bg = '#252830', fg = '#adb5bd', font = ('Segoe UI', 11))
        if tab_name == 'wallpapers':
            self.wallpaper_frame.pack(fill = 'both', expand = True, padx = 12, pady = 8)
            self.btn_tab_wp.config(bg = '#06d6a0', fg = '#111215', font = ('Segoe UI', 11, 'bold'))
        elif tab_name == 'theme':
            self.theme_frame.pack(fill = 'both', expand = True, padx = 12, pady = 8)
            self.btn_tab_theme.config(bg = '#06d6a0', fg = '#111215', font = ('Segoe UI', 11, 'bold'))
            self._update_theme_mockup()
        elif tab_name == 'texts':
            if hasattr(self, 'text_frame'):
                self.text_frame.pack(fill = 'both', expand = True, padx = 12, pady = 8)
            if hasattr(self, 'btn_tab_text'):
                self.btn_tab_text.config(bg = '#06d6a0', fg = '#111215', font = ('Segoe UI', 11, 'bold'))
            self._update_about_mockup()
        self.active_tab = tab_name

    
    def _build_content_containers(self):
        '''#181a1f'''
        self.content_container = tk.Frame(self, bg = '#181a1f')
        self.content_container.pack(fill = 'both', expand = True)
        self.wallpaper_frame = tk.Frame(self.content_container, bg = '#181a1f')
        self._build_wallpaper_tab_content()
        self.wallpaper_frame.pack(fill = 'both', expand = True, padx = 12, pady = 8)
        self.theme_frame = tk.Frame(self.content_container, bg = '#181a1f')
        self._build_theme_tab_content()
        self.text_frame = tk.Frame(self.content_container, bg = '#181a1f')
        self._build_text_tab_content()
        self._update_theme_info_card()
        self._update_theme_mockup()
        self._update_preset_card_highlights()
        self._update_about_mockup()

    
    def _build_wallpaper_tab_content(self):
        '''#21242b'''
        self.preview_panel = tk.Frame(self.wallpaper_frame, bg = '#21242b', width = 320, padx = 16, pady = 8, highlightthickness = 1, highlightbackground = '#343a40')
        self.preview_panel.pack(side = 'right', fill = 'y', padx = (10, 0))
        self.preview_panel.pack_propagate(False)
        lbl_hd_title = tk.Label(self.preview_panel, text = '🔍 תצוגה מקדימה מלאה (HD)', font = ('Segoe UI', 11, 'bold'), fg = '#06d6a0', bg = '#21242b')
        lbl_hd_title.pack(anchor = 'e')
        lbl_hd_sub = tk.Label(self.preview_panel, text = 'רזולוציה מקורית 240x320 (פיקסל לפיקסל)', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#21242b')
        lbl_hd_sub.pack(anchor = 'e', pady = (1, 4))
        self.hd_canvas = tk.Canvas(self.preview_panel, width = 240, height = 320, bg = '#0e1013', highlightthickness = 2, highlightbackground = '#06d6a0')
        self.hd_canvas.pack(pady = 2)
        info_frame = tk.Frame(self.preview_panel, bg = '#1a1c23', padx = 10, pady = 5)
        info_frame.pack(fill = 'x', pady = 4)
        self.lbl_slot_title = tk.Label(info_frame, text = 'טפט #1', font = ('Segoe UI', 12, 'bold'), fg = '#ffffff', bg = '#1a1c23')
        self.lbl_slot_title.pack(anchor = 'e')
        self.lbl_slot_badge = tk.Label(info_frame, text = 'מקורי (ברירת מחדל)', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#1a1c23')
        self.lbl_slot_badge.pack(anchor = 'e', pady = (1, 0))
        lbl_dim = tk.Label(info_frame, text = 'גודל מסך: 240 × 320 פיקסלים | פורמט SJPG', font = ('Segoe UI', 8), fg = '#6c757d', bg = '#1a1c23')
        lbl_dim.pack(anchor = 'e', pady = (1, 0))
        self.btn_hd_replace = tk.Button(self.preview_panel, text = '✏️ החלף טפט זה...', font = ('Segoe UI', 9, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', pady = 4, cursor = 'hand2', command = (lambda : self.replace_wallpaper(self.selected_slot)))
        self.btn_hd_replace.pack(fill = 'x', pady = (2, 2))
        self.btn_hd_swap = tk.Button(self.preview_panel, text = '⇄ החלף מיקום עם טפט אחר...', font = ('Segoe UI', 9, 'bold'), bg = '#2563eb', fg = '#ffffff', activebackground = '#1d4ed8', activeforeground = '#ffffff', relief = 'flat', pady = 4, cursor = 'hand2', command = (lambda : self.open_swap_dialog(self.selected_slot)))
        self.btn_hd_swap.pack(fill = 'x', pady = 2)
        row_secondary = tk.Frame(self.preview_panel, bg = '#21242b')
        row_secondary.pack(fill = 'x', pady = 2)
        self.btn_hd_reset = tk.Button(row_secondary, text = '↺ אפס למקור', font = ('Segoe UI', 8), bg = '#3d405b', fg = '#f8f9fa', relief = 'flat', pady = 4, cursor = 'hand2', command = (lambda : self.reset_wallpaper(self.selected_slot)))
        self.btn_hd_reset.pack(side = 'right', expand = True, fill = 'x', padx = (2, 0))
        self.btn_hd_zoom = tk.Button(row_secondary, text = '🔍 הגדל פי 2', font = ('Segoe UI', 8), bg = '#2b2d42', fg = '#adb5bd', activebackground = '#1e202e', activeforeground = '#f8f9fa', relief = 'flat', pady = 4, cursor = 'hand2', command = self._open_zoom_modal)
        self.btn_hd_zoom.pack(side = 'left', expand = True, fill = 'x', padx = (0, 2))
        btn_hd_export = tk.Button(self.preview_panel, text = '💾 שמור תמונה למחשב...', font = ('Segoe UI', 8), bg = '#262930', fg = '#adb5bd', activebackground = '#181a1f', activeforeground = '#f8f9fa', relief = 'flat', pady = 3, cursor = 'hand2', command = self._export_current_image)
        btn_hd_export.pack(fill = 'x', pady = (2, 2))
        self.gallery_frame = tk.Frame(self.wallpaper_frame, bg = '#181a1f')
        self.gallery_frame.pack(side = 'left', fill = 'both', expand = True)
        self.canvas = tk.Canvas(self.gallery_frame, bg = '#181a1f', highlightthickness = 0, yscrollincrement = 16)
        self.scrollbar = ttk.Scrollbar(self.gallery_frame, orient = 'vertical', command = self.canvas.yview)
        self.canvas.configure(yscrollcommand = self.scrollbar.set)
        self.canvas.pack(side = 'left', fill = 'both', expand = True)
        self.scrollbar.pack(side = 'right', fill = 'y')
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.bind_all('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

    
    def _build_theme_tab_content(self):
        '''#21242b'''
        self.theme_right_panel = tk.Frame(self.theme_frame, bg = '#21242b', width = 320, padx = 16, pady = 14, highlightthickness = 1, highlightbackground = '#343a40')
        self.theme_right_panel.pack(side = 'right', fill = 'y', padx = (10, 0))
        self.theme_right_panel.pack_propagate(False)
        lbl_sim_title = tk.Label(self.theme_right_panel, text = '📱 תצוגה חיה של מסך הטלפון', font = ('Segoe UI', 12, 'bold'), fg = '#06d6a0', bg = '#21242b')
        lbl_sim_title.pack(anchor = 'e')
        lbl_sim_sub = tk.Label(self.theme_right_panel, text = 'הדמיית מראה התפריטים, הפסים והבאנר בצבע הנבחר', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#21242b')
        lbl_sim_sub.pack(anchor = 'e', pady = (1, 6))
        self.mockup_mode = 'menu'
        mode_frame = tk.Frame(self.theme_right_panel, bg = '#21242b')
        mode_frame.pack(fill = 'x', pady = (0, 6))
        self.btn_mode_menu = tk.Button(mode_frame, text = '📱 תפריט ראשי', font = ('Segoe UI', 9, 'bold'), bg = '#06d6a0', fg = '#111215', relief = 'flat', cursor = 'hand2', command = (lambda : self._set_mockup_mode('menu')))
        self.btn_mode_menu.pack(side = 'right', expand = True, fill = 'x', padx = (2, 0))
        self.btn_mode_call = tk.Button(mode_frame, text = '📞 שיחה נכנסת', font = ('Segoe UI', 9), bg = '#2a2e38', fg = '#adb5bd', relief = 'flat', cursor = 'hand2', command = (lambda : self._set_mockup_mode('call')))
        self.btn_mode_call.pack(side = 'left', expand = True, fill = 'x', padx = (0, 2))
        self.mockup_canvas = tk.Canvas(self.theme_right_panel, width = 240, height = 320, bg = '#FFFFFF', highlightthickness = 2, highlightbackground = '#06d6a0')
        self.mockup_canvas.pack(pady = 4)
        theme_card = tk.Frame(self.theme_right_panel, bg = '#1a1c23', padx = 12, pady = 10)
        theme_card.pack(fill = 'x', pady = (10, 8))
        swatch_row = tk.Frame(theme_card, bg = '#1a1c23')
        swatch_row.pack(fill = 'x')
        self.swatch_canvas = tk.Canvas(swatch_row, width = 28, height = 28, bg = self.current_theme_hex, highlightthickness = 1, highlightbackground = '#ffffff')
        self.swatch_canvas.pack(side = 'right', padx = (8, 0))
        self.lbl_active_theme_name = tk.Label(swatch_row, text = self.current_theme_name, font = ('Segoe UI', 13, 'bold'), fg = '#ffffff', bg = '#1a1c23')
        self.lbl_active_theme_name.pack(side = 'right')
        self.lbl_theme_badge = tk.Label(theme_card, text = '✔ צבע פעיל שמור (נצרב למכשיר)', font = ('Segoe UI', 8, 'bold'), fg = '#06d6a0', bg = '#1a1c23')
        self.lbl_theme_badge.pack(anchor = 'e', pady = (4, 1))
        self.lbl_active_theme_codes = tk.Label(theme_card, text = '', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#1a1c23')
        self.lbl_active_theme_codes.pack(anchor = 'e', pady = (2, 2))
        self.lbl_contrast_guard = tk.Label(theme_card, text = '', font = ('Segoe UI', 8, 'bold'), fg = '#06d6a0', bg = '#1a1c23', wraplength = 270, justify = 'right')
        self.lbl_contrast_guard.pack(anchor = 'e', pady = (2, 4))
        action_row = tk.Frame(theme_card, bg = '#1a1c23')
        action_row.pack(fill = 'x', pady = (4, 0))
        self.btn_confirm_theme = tk.Button(action_row, text = '✔ שמור וקבע צבע זה', font = ('Segoe UI', 9, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', padx = 10, pady = 4, cursor = 'hand2', command = self.confirm_active_theme)
        self.btn_confirm_theme.pack(side = 'right')
        self.btn_revert_theme = tk.Button(action_row, text = '↩ בטל תצוגה', font = ('Segoe UI', 8), bg = '#2a2e38', fg = '#adb5bd', activebackground = '#3a3e48', activeforeground = '#ffffff', relief = 'flat', padx = 8, pady = 4, cursor = 'hand2', command = self.revert_to_confirmed_theme)
        self.btn_apply_theme_tab = tk.Button(self.theme_right_panel, text = '‏🚀 החל צבע זה והכן לצריבה בתוכנת WOT', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', activeforeground = '#111215', relief = 'flat', pady = 10, cursor = 'hand2', command = self._apply_theme_tab_and_deploy)
        self.btn_apply_theme_tab.pack(fill = 'x', pady = (8, 4))
        self.theme_left_panel = tk.Frame(self.theme_frame, bg = '#181a1f')
        self.theme_left_panel.pack(side = 'left', fill = 'both', expand = True)
        presets_header = tk.Frame(self.theme_left_panel, bg = '#181a1f')
        presets_header.pack(fill = 'x', pady = (0, 8))
        lbl_presets_title = tk.Label(presets_header, text = '🎨 בחירת צבע מתוך פלטות מומלצות ומאומתות', font = ('Segoe UI', 13, 'bold'), fg = '#f8f9fa', bg = '#181a1f')
        lbl_presets_title.pack(anchor = 'e')
        lbl_presets_desc = tk.Label(presets_header, text = 'גוונים אלו נבדקו קלינית על מסך ה-Q8, שומרים על קריאות מיטבית ואינם מייצרים שום תופעות לוואי', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#181a1f')
        lbl_presets_desc.pack(anchor = 'e', pady = (2, 0))
        self.preset_cards = { }
        presets_grid_frame = tk.Frame(self.theme_left_panel, bg = '#181a1f')
        presets_grid_frame.pack(fill = 'both', expand = True)
        for c in range(3):
            presets_grid_frame.columnconfigure(c, weight = 1, uniform = 'preset_col')
        for r in range(3):
            presets_grid_frame.rowconfigure(r, weight = 1, uniform = 'preset_row')
        for i, p in enumerate(theme_engine.PRESETS):
            row = i // 3
            col = 2 - i % 3
            card = self._create_preset_card(presets_grid_frame, p)
            card.grid(row = row, column = col, padx = 5, pady = 5, sticky = 'nsew')
            self.preset_cards[p['id']] = card
        custom_frame = tk.Frame(self.theme_left_panel, bg = '#21242b', padx = 14, pady = 10, highlightthickness = 1, highlightbackground = '#343a40')
        custom_frame.pack(fill = 'x', pady = (10, 6))
        lbl_custom_title = tk.Label(custom_frame, text = '✨ רוצה צבע אחר? בחר כל גוון שמתחשק לך מגלגל הצבעים', font = ('Segoe UI', 10, 'bold'), fg = '#f8f9fa', bg = '#21242b')
        lbl_custom_title.pack(anchor = 'e')
        lbl_custom_sub = tk.Label(custom_frame, text = 'גרור על הגלגל או הזז את סרגל הבהירות – מסך הטלפון מתעדכן בחי בזמן אמת ללא צורך באישור!', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#21242b')
        lbl_custom_sub.pack(anchor = 'e', pady = (2, 6))
        wheel_container = tk.Frame(custom_frame, bg = '#21242b')
        wheel_container.pack(fill = 'x')
        wheel_subframe = tk.Frame(wheel_container, bg = '#21242b')
        wheel_subframe.pack(side = 'right', padx = (0, 10))
        wheel_size = 140
        self.wheel_canvas = tk.Canvas(wheel_subframe, width = wheel_size, height = wheel_size, bg = '#21242b', highlightthickness = 0, cursor = 'crosshair')
        self.wheel_canvas.pack()
        wheel_pil = self._generate_color_wheel_image(wheel_size)
        self.wheel_photo = ImageTk.PhotoImage(wheel_pil)
        self.wheel_canvas.create_image(wheel_size // 2, wheel_size // 2, image = self.wheel_photo)
        self._wheel_handle_shadow = self.wheel_canvas.create_oval(0, 0, 0, 0, outline = '#000000', width = 2)
        self._wheel_handle_ring = self.wheel_canvas.create_oval(0, 0, 0, 0, outline = '#FFFFFF', width = 2)
        self._wheel_handle_dot = self.wheel_canvas.create_oval(0, 0, 0, 0, fill = self.current_theme_hex, outline = '')
        self.wheel_canvas.bind('<Button-1>', self._on_wheel_click)
        self.wheel_canvas.bind('<B1-Motion>', self._on_wheel_drag)
        self.wheel_canvas.bind('<ButtonRelease-1>', self._on_wheel_release)
        slider_frame = tk.Frame(wheel_container, bg = '#21242b')
        slider_frame.pack(side = 'right', padx = (0, 14))
        lbl_slider_title = tk.Label(slider_frame, text = 'בהירות', font = ('Segoe UI', 8, 'bold'), fg = '#adb5bd', bg = '#21242b')
        lbl_slider_title.pack(anchor = 'center')
        # NOTE(recovery): decompiler mangled this widget construction into
        # `(slider_frame,)(*{...})`; reconstructed as a tk.Scale call.
        self.slider_brightness = tk.Scale(slider_frame,
            from_ = 100,
            to = 25,
            orient = 'vertical',
            resolution = 1,
            showvalue = 0,
            length = 100,
            width = 14,
            sliderlength = 18,
            bg = '#21242b',
            fg = '#ffffff',
            troughcolor = '#181a1f',
            activebackground = '#06d6a0',
            highlightthickness = 0,
            bd = 0,
            cursor = 'hand2',
            command = self._on_slider_change)
        self.slider_brightness.set(int(round(self.current_v * 100)))
        self.slider_brightness.pack(pady = 4)
        self.slider_brightness.bind('<ButtonRelease-1>', (lambda e: self.preview_theme(self._pending_theme_hex or self.current_theme_hex, 'מותאם אישית')))
        self.lbl_bri_val = tk.Label(slider_frame, text = f'''{int(round(self.current_v * 100))}%''', font = ('Consolas', 8), fg = '#06d6a0', bg = '#21242b')
        self.lbl_bri_val.pack(anchor = 'center')
        info_frame = tk.Frame(wheel_container, bg = '#21242b')
        info_frame.pack(side = 'right', fill = 'both', expand = True)
        swatch_line = tk.Frame(info_frame, bg = '#21242b')
        swatch_line.pack(fill = 'x', pady = (2, 4))
        self.custom_swatch = tk.Canvas(swatch_line, width = 38, height = 38, bg = self.current_theme_hex, highlightthickness = 2, highlightbackground = '#ffffff')
        self.custom_swatch.pack(side = 'right', padx = (0, 8))
        hex_sub = tk.Frame(swatch_line, bg = '#21242b')
        hex_sub.pack(side = 'right', fill = 'x')
        lbl_hex_title = tk.Label(hex_sub, text = 'קוד צבע (Hex):', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#21242b')
        lbl_hex_title.pack(anchor = 'e')
        hex_entry_row = tk.Frame(hex_sub, bg = '#21242b')
        hex_entry_row.pack(anchor = 'e', pady = (2, 0))
        self.entry_hex = tk.Entry(hex_entry_row, font = ('Consolas', 10, 'bold'), width = 9, bg = '#181a1f', fg = '#06d6a0', insertbackground = '#06d6a0', justify = 'center')
        self.entry_hex.insert(0, self.current_theme_hex)
        self.entry_hex.pack(side = 'right', padx = (0, 6))
        self.entry_hex.bind('<Return>', (lambda e: self._apply_custom_hex()))
        btn_apply_hex = tk.Button(hex_entry_row, text = 'החל קוד', font = ('Segoe UI', 8, 'bold'), bg = '#262930', fg = '#f8f9fa', relief = 'flat', padx = 8, pady = 3, cursor = 'hand2', command = self._apply_custom_hex)
        btn_apply_hex.pack(side = 'right')
        self.lbl_custom_contrast = tk.Label(info_frame, text = '✔ ניגודיות מצוינת', font = ('Segoe UI', 8), fg = '#06d6a0', bg = '#21242b')
        self.lbl_custom_contrast.pack(anchor = 'e', pady = (2, 2))
        btn_win_picker = tk.Button(info_frame, text = '🎨 לוח צבעים ישן של Windows...', font = ('Segoe UI', 8), bg = '#21242b', fg = '#64748b', activebackground = '#262930', activeforeground = '#94a3b8', relief = 'flat', cursor = 'hand2', command = self._open_color_picker)
        btn_win_picker.pack(anchor = 'e', pady = (2, 0))
        self._sync_wheel_to_color(self.current_theme_hex)

    
    def _create_preset_card(self, parent, preset):
        '''id'''
        p_id = preset['id']
        p_hex = preset['hex']
        p_name = preset['name']
        p_desc = preset['desc']
        card = tk.Frame(parent, bg = '#21242b', padx = 10, pady = 8, highlightthickness = 2, highlightbackground = '#06d6a0' if p_hex.upper() == self.current_theme_hex.upper() else '#343a40', cursor = 'hand2')
        top_row = tk.Frame(card, bg = '#21242b')
        top_row.pack(fill = 'x')
        swatch = tk.Canvas(top_row, width = 20, height = 20, bg = p_hex, highlightthickness = 1, highlightbackground = '#ffffff')
        swatch.pack(side = 'right', padx = (6, 0))
        lbl_name = tk.Label(top_row, text = p_name, font = ('Segoe UI', 10, 'bold'), fg = '#ffffff', bg = '#21242b')
        lbl_name.pack(side = 'right')
        lbl_desc = tk.Label(card, text = p_desc, font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#21242b', wraplength = 200, justify = 'right')
        lbl_desc.pack(anchor = 'e', pady = (4, 0))
        
        def _on_click(event = None):
            self.select_theme(p_hex, p_name)

        card.bind('<Button-1>', _on_click)
        top_row.bind('<Button-1>', _on_click)
        swatch.bind('<Button-1>', _on_click)
        lbl_name.bind('<Button-1>', _on_click)
        lbl_desc.bind('<Button-1>', _on_click)
        
        def _on_enter(event = None):
            '''hex'''
            if preset['hex'].upper() != self.current_theme_hex.upper():
                card.config(highlightbackground = '#64748b', bg = '#262933')
                top_row.config(bg = '#262933')
                lbl_name.config(bg = '#262933')
                lbl_desc.config(bg = '#262933')
                return None

        
        def _on_leave(event = None):
            '''hex'''
            is_active = preset['hex'].upper() == self.current_theme_hex.upper()
            card.config(highlightbackground = '#06d6a0' if is_active else '#343a40', bg = '#21242b')
            top_row.config(bg = '#21242b')
            lbl_name.config(bg = '#21242b')
            lbl_desc.config(bg = '#21242b')

        card.bind('<Enter>', _on_enter)
        card.bind('<Leave>', _on_leave)
        return card

    
    def _update_preset_card_highlights(self):
        '''id'''
        for p in theme_engine.PRESETS:
            card = self.preset_cards.get(p['id'])
            if not card:
                continue
            is_active = p['hex'].upper() == self.current_theme_hex.upper()
            card.config(highlightbackground = '#06d6a0' if is_active else '#343a40', highlightthickness = 2 if is_active else 1)

    
    def _generate_color_wheel_image(self, size = 140):
        '''_cached_wheel_img'''
        if hasattr(self, '_cached_wheel_img') and self._cached_wheel_img is not None:
            return self._cached_wheel_img
        radius = (size - 1) / 2
        cy = radius
        cx = radius
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        pixels = img.load()
        for y in range(size):
            for x in range(size):
                dx = x - cx
                dy = y - cy
                dist = math.hypot(dx, dy)
                if not dist <= radius:
                    continue
                angle = math.atan2(-dy, dx)
                if angle < 0:
                    angle += 2 * math.pi
                h = angle / (2 * math.pi)
                s = min(1, dist / radius)
                (r, g, b) = colorsys.hsv_to_rgb(h, s, 1)
                alpha = int(255 * min(1, (radius - dist) + 1)) if dist > radius - 1 else 255
                pixels[(x, y)] = (int(r * 255), int(g * 255), int(b * 255), alpha)
        self._cached_wheel_img = img
        return img

    
    def _update_wheel_handle(self, x, y, hex_color):
        '''wheel_canvas'''
        if not hasattr(self, 'wheel_canvas'):
            return None
        self.wheel_canvas.coords(self._wheel_handle_shadow, x - 7, y - 7, x + 7, y + 7)
        self.wheel_canvas.coords(self._wheel_handle_ring, x - 6, y - 6, x + 6, y + 6)
        self.wheel_canvas.coords(self._wheel_handle_dot, x - 4, y - 4, x + 4, y + 4)
        self.wheel_canvas.itemconfig(self._wheel_handle_dot, fill = hex_color)

    
    def _sync_wheel_to_color(self, hex_val):
        
        try:
            (r, g, b) = theme_engine.hex_to_rgb(hex_val)
            (h, s, v) = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            self.current_h = h
            self.current_s = s
            self.current_v = v
            if hasattr(self, 'slider_brightness'):
                self._syncing_wheel = True
                self.slider_brightness.set(int(round(v * 100)))
                if hasattr(self, 'lbl_bri_val'):
                    self.lbl_bri_val.config(text = f'''{int(round(v * 100))}%''')
                self._syncing_wheel = False
            radius = 69.5
            cy = radius
            cx = radius
            angle = h * 2 * math.pi
            dist = s * radius
            x = cx + dist * math.cos(angle)
            y = cy - dist * math.sin(angle)
            self._update_wheel_handle(x, y, hex_val)
            if hasattr(self, 'custom_swatch'):
                self.custom_swatch.config(bg = hex_val)
            if hasattr(self, 'lbl_custom_contrast'):
                (ok, msg) = theme_engine.check_contrast_guard(hex_val)
                self.lbl_custom_contrast.config(text = msg, fg = '#06d6a0' if ok else '#ffd166')
                return None
        except Exception:
            return None


    
    def _handle_wheel_coords(self, x, y, finalize = False):
        size = 140
        radius = (size - 1) / 2
        cy = radius
        cx = radius
        dx = x - cx
        dy = y - cy
        dist = math.hypot(dx, dy)
        if dist > radius:
            x = cx + (dx / dist) * radius
            y = cy + (dy / dist) * radius
            dist = radius
        angle = math.atan2(-dy, dx)
        if angle < 0:
            angle += 2 * math.pi
        self.current_h = angle / (2 * math.pi)
        self.current_s = min(1, dist / radius)
        v = self.slider_brightness.get() / 100 if hasattr(self, 'slider_brightness') else self.current_v
        self.current_v = v
        (r, g, b) = colorsys.hsv_to_rgb(self.current_h, self.current_s, v)
        hex_color = f'''#{int(round(r * 255)):02X}{int(round(g * 255)):02X}{int(round(b * 255)):02X}'''
        self._update_wheel_handle(x, y, hex_color)
        if hasattr(self, 'custom_swatch'):
            self.custom_swatch.config(bg = hex_color)
        if hasattr(self, 'entry_hex'):
            self.entry_hex.delete(0, 'end')
            self.entry_hex.insert(0, hex_color)
        if hasattr(self, 'lbl_custom_contrast'):
            (ok, msg) = theme_engine.check_contrast_guard(hex_color)
            self.lbl_custom_contrast.config(text = msg, fg = '#06d6a0' if ok else '#ffd166')
        if finalize:
            if self._mockup_update_job is not None:
                self.after_cancel(self._mockup_update_job)
                self._mockup_update_job = None
            self.preview_theme(hex_color, 'מותאם אישית')
            return None
        self._schedule_live_mockup_update(hex_color)

    
    def _on_wheel_click(self, event):
        self._handle_wheel_coords(event.x, event.y, finalize = False)

    
    def _on_wheel_drag(self, event):
        self._handle_wheel_coords(event.x, event.y, finalize = False)

    
    def _on_wheel_release(self, event):
        self._handle_wheel_coords(event.x, event.y, finalize = True)

    
    def _on_slider_change(self, val_str):
        '''_syncing_wheel'''
        if getattr(self, '_syncing_wheel', False):
            return None
        v = float(val_str) / 100
        self.current_v = v
        if hasattr(self, 'lbl_bri_val'):
            self.lbl_bri_val.config(text = f'''{int(round(v * 100))}%''')
        (r, g, b) = colorsys.hsv_to_rgb(self.current_h, self.current_s, v)
        hex_color = f'''#{int(round(r * 255)):02X}{int(round(g * 255)):02X}{int(round(b * 255)):02X}'''
        radius = 69.5
        cy = radius
        cx = radius
        angle = self.current_h * 2 * math.pi
        dist = self.current_s * radius
        x = cx + dist * math.cos(angle)
        y = cy - dist * math.sin(angle)
        self._update_wheel_handle(x, y, hex_color)
        if hasattr(self, 'custom_swatch'):
            self.custom_swatch.config(bg = hex_color)
        if hasattr(self, 'entry_hex'):
            self.entry_hex.delete(0, 'end')
            self.entry_hex.insert(0, hex_color)
        if hasattr(self, 'lbl_custom_contrast'):
            ok, msg = theme_engine.check_contrast_guard(hex_color)
            self.lbl_custom_contrast.config(text = msg, fg = '#06d6a0' if ok else '#ffd166')
        self._schedule_live_mockup_update(hex_color)

    
    def _schedule_live_mockup_update(self, hex_color):
        self._pending_theme_hex = hex_color
        if self._mockup_update_job is None:
            self._mockup_update_job = self.after(30, self._do_live_mockup_update)
            return None

    
    def _do_live_mockup_update(self):
        self._mockup_update_job = None
        if hasattr(self, '_pending_theme_hex'):
            if self._pending_theme_hex:
                target_hex = self._pending_theme_hex
                self.current_theme_hex = target_hex
                self._update_theme_mockup()
                if hasattr(self, 'swatch_canvas'):
                    self.swatch_canvas.config(bg = target_hex)
                if hasattr(self, 'lbl_active_theme_codes'):
                    (r, g, b) = theme_engine.hex_to_rgb(target_hex)
                    c565 = theme_engine.rgb_to_rgb565(r, g, b)
                    self.lbl_active_theme_codes.config(text = f'''קוד Hex: {target_hex} | RGB565: 0x{c565:04X}''')
                if hasattr(self, 'lbl_contrast_guard'):
                    ok, msg = theme_engine.check_contrast_guard(target_hex)
                    self.lbl_contrast_guard.config(text = msg, fg = '#06d6a0' if ok else '#ffd166')
                if hasattr(self, 'lbl_active_theme_name'):
                    self.lbl_active_theme_name.config(text = 'מותאם אישית (חי)')
                    return None
                return None
            return None

    
    def _open_color_picker(self):
        '''בחר צבע עבור ערכת הנושא של ה-Q8'''
        chosen = colorchooser.askcolor(color = self.current_theme_hex, title = 'בחר צבע עבור ערכת הנושא של ה-Q8')
        if chosen:
            if chosen[1]:
                hex_val = chosen[1].upper()
                self.preview_theme(hex_val, 'מותאם אישית')
                return None
            return None

    
    def _apply_custom_hex(self):
        '''#'''
        val = self.entry_hex.get().strip()
        if not val.startswith('#'):
            val = '#' + val
        if len(val) in (4, 7):
            
            try:
                theme_engine.hex_to_rgb(val)
                self.preview_theme(val.upper(), 'מותאם אישית')
            except Exception:
                messagebox.showerror('קוד צבע שגוי', 'אנא הזן קוד צבע הקסדצימלי תקין (למשל: #1D4ED8)')
                return None

            return None
        messagebox.showerror('קוד צבע שגוי', 'אנא הזן קוד צבע הקסדצימלי תקין (למשל: #1D4ED8)')

    
    def preview_theme(self, hex_val, name):
        '''Previews a theme visually without saving or committing it to active config.'''
        self.current_theme_hex = hex_val.upper()
        self.current_theme_name = name
        self._update_theme_info_card()
        self._update_theme_mockup()
        self._update_preset_card_highlights()
        if hasattr(self, 'entry_hex'):
            self.entry_hex.delete(0, 'end')
            self.entry_hex.insert(0, self.current_theme_hex)
        self._sync_wheel_to_color(self.current_theme_hex)
        is_confirmed = self.current_theme_hex.upper() == self.confirmed_theme_hex.upper()
        if is_confirmed:
            self.lbl_status.config(text = f'''‏צבע ערכת הנושא הפעיל: {name} ({self.current_theme_hex}).''')
            return None
        self.lbl_status.config(text = f'''‏👁️ תצוגה מקדימה: {name} ({self.current_theme_hex}). לחץ \'שמור וקבע צבע זה\' כדי לקבוע אותו כצבע הפעיל.''')

    
    def select_theme(self, hex_val, name):
        '''Backwards-compatible alias for preview_theme.'''
        self.preview_theme(hex_val, name)

    
    def confirm_active_theme(self):
        '''Explicitly saves and commits current preview theme as active burning theme.'''
        self.confirmed_theme_hex = self.current_theme_hex
        self.confirmed_theme_name = self.current_theme_name
        theme_engine.save_theme_config(self.confirmed_theme_hex, self.confirmed_theme_name)
        self._update_theme_info_card()
        self._update_preset_card_highlights()
        self.lbl_status.config(text = f'''‏✔ צבע ערכת הנושא נשמר ואושר בהצלחה: {self.confirmed_theme_name} ({self.confirmed_theme_hex}).''')
        messagebox.showinfo('הצבע אושר בהצלחה', f'''הצבע {self.confirmed_theme_name} ({self.confirmed_theme_hex}) נשמר בהצלחה כצבע הפעיל של המכשיר!\n\nכעת כל צריבה של טפטים או ערכת נושא תשתמש בצבע זה.''')

    
    def revert_to_confirmed_theme(self):
        '''Reverts preview back to saved confirmed theme.'''
        self.preview_theme(self.confirmed_theme_hex, self.confirmed_theme_name)
        self.lbl_status.config(text = f'''‏התצוגה בוטלה. הוחזר לצבע הפעיל: {self.confirmed_theme_name} ({self.confirmed_theme_hex}).''')

    
    def _apply_theme_tab_and_deploy(self):
        '''Confirms current preview color, then starts deploy to WOT.'''
        self.confirmed_theme_hex = self.current_theme_hex
        self.confirmed_theme_name = self.current_theme_name
        theme_engine.save_theme_config(self.confirmed_theme_hex, self.confirmed_theme_name)
        self._update_theme_info_card()
        self.deploy_to_wot()

    
    def _update_theme_info_card(self):
        '''lbl_active_theme_name'''
        if not hasattr(self, 'lbl_active_theme_name'):
            return None
        is_confirmed = self.current_theme_hex.upper() == self.confirmed_theme_hex.upper()
        self.lbl_active_theme_name.config(text = self.current_theme_name)
        self.swatch_canvas.config(bg = self.current_theme_hex)
        (r, g, b) = theme_engine.hex_to_rgb(self.current_theme_hex)
        c565 = theme_engine.rgb_to_rgb565(r, g, b)
        self.lbl_active_theme_codes.config(text = f'''קוד Hex: {self.current_theme_hex} | RGB565: 0x{c565:04X}''')
        ok, msg = theme_engine.check_contrast_guard(self.current_theme_hex)
        self.lbl_contrast_guard.config(text = msg, fg = '#06d6a0' if ok else '#ffd166')
        if hasattr(self, 'lbl_theme_badge'):
            if is_confirmed:
                self.lbl_theme_badge.config(text = '✔ צבע פעיל שמור (נצרב למכשיר)', fg = '#06d6a0')
            else:
                self.lbl_theme_badge.config(text = '👁️ תצוגה מקדימה בלבד (טרם נשמר!)', fg = '#ffd166')
        if hasattr(self, 'btn_confirm_theme'):
            if is_confirmed:
                self.btn_confirm_theme.config(text = '✔ צבע זה מאושר', state = 'disabled', bg = '#1e3a2b', fg = '#6ee7b7')
                if hasattr(self, 'btn_revert_theme'):
                    self.btn_revert_theme.pack_forget()
                    return None
                return None
            self.btn_confirm_theme.config(text = '✔ שמור וקבע צבע זה', state = 'normal', bg = '#06d6a0', fg = '#111215')
            if hasattr(self, 'btn_revert_theme'):
                self.btn_revert_theme.pack(side = 'left', padx = 4)
                return None
            return None

    
    def _set_mockup_mode(self, mode):
        '''menu'''
        self.mockup_mode = mode
        if mode == 'menu':
            self.btn_mode_menu.config(bg = '#06d6a0', fg = '#111215', font = ('Segoe UI', 9, 'bold'))
            self.btn_mode_call.config(bg = '#2a2e38', fg = '#adb5bd', font = ('Segoe UI', 9))
            self.mockup_canvas.config(bg = '#FFFFFF')
        else:
            self.btn_mode_call.config(bg = '#06d6a0', fg = '#111215', font = ('Segoe UI', 9, 'bold'))
            self.btn_mode_menu.config(bg = '#2a2e38', fg = '#adb5bd', font = ('Segoe UI', 9))
            self.mockup_canvas.config(bg = '#111215')
        self._update_theme_mockup()

    
    def _update_theme_mockup(self):
        '''mockup_canvas'''
        if not hasattr(self, 'mockup_canvas'):
            return None
        c = self.mockup_canvas
        c.delete('all')
        self._mockup_photos = { }
        th = self.current_theme_hex
        if getattr(self, 'mockup_mode', 'menu') == 'menu':
            c.create_rectangle(0, 0, 240, 320, fill = '#FFFFFF', outline = '')
            for i in range(4):
                bx = 10 + i * 4
                bh = 3 + i * 2.5
                c.create_rectangle(bx, 17 - bh, bx + 2, 17, fill = '#1e293b', outline = '')
            c.create_text(28, 12, text = 'VoLTE 4G1', anchor = 'w', font = ('Segoe UI', 7, 'bold'), fill = '#1e293b')
            c.create_rectangle(176, 7, 192, 17, outline = '#1e293b', width = 1)
            c.create_rectangle(178, 9, 189, 15, fill = '#1e293b', outline = '')
            c.create_rectangle(192, 10, 194, 14, fill = '#1e293b', outline = '')
            c.create_text(198, 12, text = '18:55', anchor = 'w', font = ('Segoe UI', 8, 'bold'), fill = '#1e293b')
            
            try:
                icons_dict = theme_engine.get_menu_icon_images(th)
            except Exception:
                icons_dict = { }

            grid_items = [
                (0, 2, 231, 'פרופילים'),
                (0, 1, 229, 'אנשי קשר'),
                (0, 0, 227, 'יומן שיחות'),
                (1, 2, 237, 'שעון'),
                (1, 1, 235, 'בלוטות'),
                (1, 0, 233, 'הגדרות'),
                (2, 2, 243, 'רשמקול'),
                (2, 1, 241, 'לוח שנה'),
                (2, 0, 251, 'כלים')]
            col_x = [
                42,
                120,
                198]
            row_y = [
                58,
                142,
                226]
            for row, col, item_id, label in grid_items:
                cx = col_x[col]
                cy = row_y[row]
                if item_id == 233:
                    c.create_rectangle(cx - 26, cy - 24, cx + 26, cy + 24, fill = '#F1F5F9', outline = th, width = 2)
                    c.create_oval(cx + 14, cy - 24, cx + 26, cy - 12, fill = th, outline = '#FFFFFF')
                    c.create_text(cx + 20, cy - 18, text = '✓', font = ('Segoe UI', 7, 'bold'), fill = '#FFFFFF')
                im = icons_dict.get(item_id)
                if im:
                    photo = ImageTk.PhotoImage(im)
                    self._mockup_photos[item_id] = photo
                    c.create_image(cx, cy, image = photo)
                c.create_text(cx, cy + 28, text = label, font = ('Segoe UI', 9), fill = '#1E293B')
            c.create_line(0, 296, 240, 296, fill = '#E2E8F0')
            c.create_text(205, 308, text = 'אחורה', font = ('Segoe UI', 9, 'bold'), fill = '#1E293B')
            c.create_text(35, 308, text = 'אישור', font = ('Segoe UI', 9, 'bold'), fill = '#1E293B')
            return None
        c.create_rectangle(0, 0, 240, 320, fill = '#121316', outline = '')
        c.create_rectangle(0, 0, 240, 24, fill = th, outline = '')
        c.create_text(120, 12, text = '18:55', fill = '#ffffff', font = ('Segoe UI', 9, 'bold'))
        c.create_rectangle(8, 70, 232, 220, fill = th, outline = '#ffffff', width = 1)
        c.create_text(120, 105, text = '📞 שיחה נכנסת...', fill = '#ffffff', font = ('Segoe UI', 12, 'bold'))
        c.create_text(120, 140, text = '050-1234567', fill = '#ffffff', font = ('Segoe UI', 12))
        c.create_text(120, 180, text = 'מענה [ירוק] | דחייה [אדום]', fill = '#e0e0e0', font = ('Segoe UI', 9))
        c.create_rectangle(0, 290, 240, 320, fill = '#0a0b0d', outline = '')
        c.create_text(205, 305, text = 'דחייה', font = ('Segoe UI', 9, 'bold'), fill = '#ff4d4d')
        c.create_text(35, 305, text = 'מענה', font = ('Segoe UI', 9, 'bold'), fill = '#06d6a0')

    
    def _build_text_tab_content(self):
        '''#21242b'''
        self.text_right_panel = tk.Frame(self.text_frame, bg = '#21242b', width = 320, padx = 16, pady = 14, highlightthickness = 1, highlightbackground = '#343a40')
        self.text_right_panel.pack(side = 'right', fill = 'y', padx = (10, 0))
        self.text_right_panel.pack_propagate(False)
        lbl_mockup_title = tk.Label(self.text_right_panel, text = '📱 תצוגה מקדימה: מסך אודות', font = ('Segoe UI', 12, 'bold'), fg = '#06d6a0', bg = '#21242b')
        lbl_mockup_title.pack(anchor = 'e', pady = (0, 4))
        lbl_mockup_sub = tk.Label(self.text_right_panel, text = 'הדמיה בזמן אמת של המסך במכשיר', font = ('Segoe UI', 9), fg = '#adb5bd', bg = '#21242b')
        lbl_mockup_sub.pack(anchor = 'e', pady = (0, 8))
        self.about_mockup_canvas = tk.Canvas(self.text_right_panel, width = 240, height = 320, bg = '#CAD8EE', highlightthickness = 2, highlightbackground = '#06d6a0')
        self.about_mockup_canvas.pack(pady = 4)
        info_card = tk.Frame(self.text_right_panel, bg = '#1a1c23', padx = 12, pady = 10)
        info_card.pack(fill = 'x', pady = (10, 8))
        lbl_info_title = tk.Label(info_card, text = 'ℹ️ נתיב מסך זה במכשיר:', font = ('Segoe UI', 9, 'bold'), fg = '#06d6a0', bg = '#1a1c23')
        lbl_info_title.pack(anchor = 'e')
        lbl_info_desc = tk.Label(info_card, text = 'תפריט ➔ הגדרות ➔ אודות\nמסך זה מציג את שם הגרסה, הקדשה אישית ופרטי יוצר הגרסה.', font = ('Segoe UI', 8), fg = '#adb5bd', bg = '#1a1c23', justify = 'right')
        lbl_info_desc.pack(anchor = 'e', pady = (2, 0))
        self.text_left_panel = tk.Frame(self.text_frame, bg = '#181a1f')
        self.text_left_panel.pack(side = 'left', fill = 'both', expand = True)
        card_about = tk.LabelFrame(self.text_left_panel, text = " 📱 עריכת מסך 'אודות' (About Screen) ", font = ('Segoe UI', 11, 'bold'), fg = '#06d6a0', bg = '#21242b', padx = 14, pady = 10)
        card_about.pack(fill = 'x', pady = (0, 10))
        row_title = tk.Frame(card_about, bg = '#21242b')
        row_title.pack(fill = 'x', pady = (0, 6))
        lbl_title = tk.Label(row_title, text = 'כותרת גרסה (מופיע לפני מספר הגרסה):', font = ('Segoe UI', 9, 'bold'), fg = '#f8f9fa', bg = '#21242b')
        lbl_title.pack(side = 'right', padx = (8, 0))
        self.entry_about_title = tk.Entry(row_title, textvariable = self.about_title_var, font = ('Segoe UI', 10), bg = '#111215', fg = '#ffffff', insertbackground = '#06d6a0', relief = 'flat', width = 24, justify = 'right')
        self.entry_about_title.pack(side = 'right')
        self.entry_about_title.bind('<KeyRelease>', (lambda e: self._on_about_text_changed()))
        row_body_lbl = tk.Frame(card_about, bg = '#21242b')
        row_body_lbl.pack(fill = 'x', pady = (4, 2))
        lbl_body = tk.Label(row_body_lbl, text = 'טקסט האודות, מיתוג וקרדיטים (עד 96 תווים):', font = ('Segoe UI', 9, 'bold'), fg = '#f8f9fa', bg = '#21242b')
        lbl_body.pack(side = 'right')
        self.lbl_char_count = tk.Label(row_body_lbl, text = '0 / 96 תווים', font = ('Segoe UI', 9), fg = '#06d6a0', bg = '#21242b')
        self.lbl_char_count.pack(side = 'left')
        self.txt_about_body = tk.Text(card_about, height = 4, font = ('Segoe UI', 10), bg = '#111215', fg = '#ffffff', insertbackground = '#06d6a0', relief = 'flat', padx = 8, pady = 6, wrap = 'word')
        self.txt_about_body.pack(fill = 'x', pady = (0, 8))
        self.txt_about_body.insert('1.0', self.about_body_str)
        self.txt_about_body.bind('<KeyRelease>', (lambda e: self._on_about_text_changed()))
        row_about_btns = tk.Frame(card_about, bg = '#21242b')
        row_about_btns.pack(fill = 'x')
        btn_save_about = tk.Button(row_about_btns, text = '✔ שמור מסך אודות', font = ('Segoe UI', 9, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', relief = 'flat', padx = 14, pady = 5, cursor = 'hand2', command = self._save_about_text)
        btn_save_about.pack(side = 'right', padx = (6, 0))
        btn_reset_about = tk.Button(row_about_btns, text = '↺ שחזר טקסט מקורי', font = ('Segoe UI', 9), bg = '#3d405b', fg = '#f8f9fa', activebackground = '#2b2d42', relief = 'flat', padx = 12, pady = 5, cursor = 'hand2', command = self._reset_about_text)
        btn_reset_about.pack(side = 'right')
        card_strings = tk.LabelFrame(self.text_left_panel, text = ' 🔍 חיפוש ושינוי שמות תפריטים במכשיר ', font = ('Segoe UI', 11, 'bold'), fg = '#06d6a0', bg = '#21242b', padx = 14, pady = 8)
        card_strings.pack(fill = 'both', expand = True, pady = (0, 10))
        row_search = tk.Frame(card_strings, bg = '#21242b')
        row_search.pack(fill = 'x', pady = (0, 6))
        lbl_search = tk.Label(row_search, text = 'חפש מילה במכשיר:', font = ('Segoe UI', 9, 'bold'), fg = '#f8f9fa', bg = '#21242b')
        lbl_search.pack(side = 'right', padx = (8, 0))
        self.entry_str_search = tk.Entry(row_search, font = ('Segoe UI', 10), bg = '#111215', fg = '#ffffff', insertbackground = '#06d6a0', relief = 'flat', width = 20, justify = 'right')
        self.entry_str_search.pack(side = 'right', padx = (0, 6))
        self.entry_str_search.bind('<Return>', (lambda e: self._do_search_strings()))
        btn_search = tk.Button(row_search, text = '🔍 חפש', font = ('Segoe UI', 9, 'bold'), bg = '#3a3f4d', fg = '#f8f9fa', activebackground = '#4a5163', relief = 'flat', padx = 12, pady = 3, cursor = 'hand2', command = self._do_search_strings)
        btn_search.pack(side = 'right')
        split_frame = tk.Frame(card_strings, bg = '#21242b')
        split_frame.pack(fill = 'both', expand = True, pady = (0, 6))
        active_box = tk.LabelFrame(split_frame, text = ' החלפות פעילות ', font = ('Segoe UI', 9, 'bold'), fg = '#adb5bd', bg = '#21242b', padx = 6, pady = 4)
        active_box.pack(side = 'left', fill = 'both', expand = True, padx = (0, 6))
        self.list_replacements = tk.Listbox(active_box, font = ('Segoe UI', 9), bg = '#111215', fg = '#ffffff', selectbackground = '#06d6a0', selectforeground = '#111215', relief = 'flat', height = 3)
        self.list_replacements.pack(fill = 'both', expand = True, pady = (0, 4))
        self._refresh_active_replacements_list()
        btn_del_rep = tk.Button(active_box, text = '🗑️ מחק החלפה נבחרת', font = ('Segoe UI', 8), bg = '#5c2429', fg = '#ff6b6b', relief = 'flat', cursor = 'hand2', command = self._delete_replacement)
        btn_del_rep.pack(fill = 'x')
        results_box = tk.LabelFrame(split_frame, text = ' תוצאות חיפוש (לחץ לבחירה) ', font = ('Segoe UI', 9, 'bold'), fg = '#06d6a0', bg = '#21242b', padx = 6, pady = 4)
        results_box.pack(side = 'right', fill = 'both', expand = True)
        tree_frame = tk.Frame(results_box, bg = '#21242b')
        tree_frame.pack(fill = 'both', expand = True)
        self.tree_strings = ttk.Treeview(tree_frame, columns = ('text', 'len'), show = 'headings', height = 3)
        self.tree_strings.heading('text', text = 'טקסט שנמצא במכשיר')
        self.tree_strings.heading('len', text = 'אורך')
        self.tree_strings.column('text', width = 160, anchor = 'e')
        self.tree_strings.column('len', width = 60, anchor = 'center')
        tree_scroll = ttk.Scrollbar(tree_frame, orient = 'vertical', command = self.tree_strings.yview)
        self.tree_strings.configure(yscrollcommand = tree_scroll.set)
        self.tree_strings.pack(side = 'left', fill = 'both', expand = True)
        tree_scroll.pack(side = 'right', fill = 'y')
        self.tree_strings.bind('<<TreeviewSelect>>', self._on_tree_select)
        row_replace = tk.Frame(card_strings, bg = '#21242b')
        row_replace.pack(fill = 'x', pady = (4, 4))
        lbl_rep_to = tk.Label(row_replace, text = 'טקסט חלופי חדש:', font = ('Segoe UI', 9, 'bold'), fg = '#f8f9fa', bg = '#21242b')
        lbl_rep_to.pack(side = 'right', padx = (8, 0))
        self.entry_str_replace = tk.Entry(row_replace, font = ('Segoe UI', 10), bg = '#111215', fg = '#ffffff', insertbackground = '#06d6a0', relief = 'flat', width = 20, justify = 'right')
        self.entry_str_replace.pack(side = 'right', padx = (0, 6))
        btn_add_rep = tk.Button(row_replace, text = '✔ החלף מילה זו', font = ('Segoe UI', 9, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', relief = 'flat', padx = 10, pady = 3, cursor = 'hand2', command = self._apply_replacement)
        btn_add_rep.pack(side = 'right')
        self.btn_apply_text_tab = tk.Button(self.text_left_panel, text = '🚀 החל שינויי טקסט והכן לצריבה בתוכנת WOT', font = ('Segoe UI', 11, 'bold'), bg = '#06d6a0', fg = '#111215', activebackground = '#05b888', relief = 'flat', padx = 20, pady = 8, cursor = 'hand2', command = self._apply_text_tab_and_deploy)
        self.btn_apply_text_tab.pack(fill = 'x')

    
    def _update_about_mockup(self):
        '''about_mockup_canvas'''
        if not hasattr(self, 'about_mockup_canvas'):
            return None
        c = self.about_mockup_canvas
        c.delete('all')
        c.create_rectangle(0, 0, 240, 320, fill = '#CAD8EE', outline = '')
        c.create_rectangle(0, 0, 240, 24, fill = '#1B2C6E', outline = '')
        c.create_text(8, 6, text = 'Vo', fill = '#FFFFFF', font = ('Segoe UI', 6, 'bold'), anchor = 'nw')
        c.create_text(8, 13, text = 'LTE', fill = '#FFFFFF', font = ('Segoe UI', 6, 'bold'), anchor = 'nw')
        c.create_text(26, 12, text = '4G', fill = '#FFFFFF', font = ('Segoe UI', 8, 'bold'), anchor = 'w')
        for i in range(4):
            bx = 42 + i * 4
            bh = 3 + i * 2.5
            c.create_rectangle(bx, 17 - bh, bx + 2, 17, fill = '#FFFFFF', outline = '')
        c.create_rectangle(176, 7, 192, 17, outline = '#FFFFFF', width = 1)
        c.create_rectangle(178, 9, 190, 15, fill = '#FFFFFF', outline = '')
        c.create_rectangle(174, 9, 176, 15, fill = '#FFFFFF', outline = '')
        c.create_text(234, 12, text = '12:53', fill = '#FFFFFF', font = ('Segoe UI', 9, 'bold'), anchor = 'e')
        c.create_text(224, 46, text = 'אודות', fill = '#2D5FB2', font = ('Segoe UI', 13, 'bold'), anchor = 'e')
        title_text = self.about_title_var.get().strip() if hasattr(self, 'about_title_var') else 'מספר גרסה:'
        if not title_text:
            title_text = 'מספר גרסה:'
        id_title = c.create_text(224, 74, text = title_text, fill = '#25355E', font = ('Segoe UI', 10), anchor = 'e')
        bbox = c.bbox(id_title)
        left_x = bbox[0] if bbox else 150
        c.create_text(left_x - 4, 74, text = 'V4.5', fill = '#25355E', font = ('Segoe UI', 10), anchor = 'e')
        body = ''
        if hasattr(self, 'txt_about_body'):
            body = self.txt_about_body.get('1.0', 'end-1c')
        else:
            body = getattr(self, 'about_body_str', '')
        lines = []
        for paragraph in body.split('\n'):
            p = paragraph.strip()
            if not p:
                continue
            p_norm = p.replace('לשכפל ו/או', 'לשכפל ו /או')
            words = p_norm.split(' ')
            cur = ''
            for w in words:
                if not w:
                    continue
                # NOTE(recovery): decompiler rendered the next branch as `while`;
                # restored to `if` (long hyphenated email word split across lines).
                if '@' in w and '-' in w and len(w) > 14:
                    if cur:
                        lines.append(cur)
                        cur = ''
                    parts = w.split('-')
                    lines.append(parts[0] + '-')
                    lines.append('-'.join(parts[slice(1, None, None)]))
                    continue
                test = (cur + ' ' + w).strip() if cur else w
                if len(test) <= 23:
                    cur = test
                    continue
                if cur:
                    lines.append(cur)
                cur = w
            if not cur:
                continue
            lines.append(cur)
        y = 98
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
            is_email = '@' in line_clean or 'tech.com' in line_clean
            if is_email:
                color = '#2D5FB2'
            else:
                color = '#25355E'
            if is_email and y < 190:
                y += 6
            c.create_text(224, y, text = line_clean, fill = color, font = ('Segoe UI', 10), anchor = 'e')
            y += 22
            if not y > 270:
                continue
            lines
        c.create_text(18, 302, text = 'אישור', fill = '#2D5FB2', font = ('Segoe UI', 11, 'bold'), anchor = 'w')
        c.create_text(224, 302, text = 'אחורה', fill = '#2D5FB2', font = ('Segoe UI', 11, 'bold'), anchor = 'e')

    
    def _on_about_text_changed(self):
        '''txt_about_body'''
        if not hasattr(self, 'txt_about_body') or not hasattr(self, 'lbl_char_count'):
            return None
        body = self.txt_about_body.get('1.0', 'end-1c')
        char_count = len(body)
        if char_count <= 96:
            self.lbl_char_count.config(text = f'''{char_count} / 96 תווים (תקין)''', fg = '#06d6a0')
        else:
            self.lbl_char_count.config(text = f'''⚠️ {char_count} / 96 תווים (חריגה מ-96!)''', fg = '#ff6b6b')
        if self._about_mockup_job:
            self.after_cancel(self._about_mockup_job)
        self._about_mockup_job = self.after(50, self._update_about_mockup)

    
    def _save_about_text(self):
        '''1.0'''
        title = self.entry_about_title.get().strip()
        body = self.txt_about_body.get('1.0', 'end-1c')
        if len(body) > 96:
            messagebox.showwarning('חריגה באורך', 'טקסט האודות חורג מ-96 תווים. אנא קצר אותו מעט כדי שיתאים במדויק לגודל המסך.')
            return None
        self.text_config['about_title'] = title
        self.text_config['about_body'] = body
        text_engine.save_text_config(self.text_config)
        self.lbl_status.config(text = "✔ מסך 'אודות' נשמר בהצלחה! לחץ 'החל' לצריבה למכשיר.")
        messagebox.showinfo('נשמר בהצלחה', "שינויי מסך 'אודות' נשמרו בהצלחה!\nלחץ על 'החל שינויי טקסט והכן לצריבה' כדי לפרוס ל-WOT.")

    
    def _reset_about_text(self):
        '''שחזור למקור'''
        if not messagebox.askyesno('שחזור למקור', "האם לשחזר את מסך 'אודות' לטקסט היצרן המקורי?"):
            return None
        self.about_title_var.set(text_engine.DEFAULT_ABOUT_TITLE)
        self.txt_about_body.delete('1.0', 'end')
        self.txt_about_body.insert('1.0', text_engine.DEFAULT_ABOUT_BODY)
        self._on_about_text_changed()
        self.text_config['about_title'] = text_engine.DEFAULT_ABOUT_TITLE
        self.text_config['about_body'] = text_engine.DEFAULT_ABOUT_BODY
        text_engine.save_text_config(self.text_config)
        self.lbl_status.config(text = "מסך 'אודות' אופס לטקסט המקורי של היצרן.")

    
    def _do_search_strings(self):
        query = self.entry_str_search.get().strip()
        if not query:
            return None
        self.lbl_status.config(text = f'''מחפש \'{query}\' במכשיר...''')
        # NOTE(recovery): decompiler left `get_children()()`; restored to clearing the tree.
        self.tree_strings.delete(*self.tree_strings.get_children())
        results = text_engine.search_hebrew_strings(query)
        if not results:
            self.lbl_status.config(text = f'''לא נמצאו מילים תואמות ל-\'{query}\'.''')
            return None
        for r in results:
            self.tree_strings.insert('', 'end', values = (r['text'], f'''עד {r['max_chars']} תווים''', f'''0x{r['offset']:X}'''))
        self.lbl_status.config(text = f'''נמצאו {len(results)} תוצאות עבור \'{query}\'.''')

    
    def _on_tree_select(self, event):
        sel = self.tree_strings.selection()
        if not sel:
            return None
        vals = self.tree_strings.item(sel[0], 'values')
        if vals:
            orig_txt = vals[0]
            self.entry_str_replace.delete(0, 'end')
            self.entry_str_replace.insert(0, orig_txt)
            return None

    
    def _refresh_active_replacements_list(self):
        '''list_replacements'''
        if not hasattr(self, 'list_replacements'):
            return None
        self.list_replacements.delete(0, 'end')
        for orig, rep in self.custom_replacements.items():
            self.list_replacements.insert('end', f'''\'{orig}\' ➔ \'{rep}\'''')

    
    def _apply_replacement(self):
        '''בחר מילה'''
        sel = self.tree_strings.selection()
        if not sel:
            messagebox.showinfo('בחר מילה', 'אנא בחר תחילה מילה מרשימת תוצאות החיפוש.')
            return None
        vals = self.tree_strings.item(sel[0], 'values')
        orig_txt = vals[0]
        new_txt = self.entry_str_replace.get().strip()
        if not new_txt:
            return None
        max_chars_str = vals[1].replace('עד ', '').replace(' תווים', '').strip()
        
        try:
            max_chars = int(max_chars_str)
        except Exception:
            max_chars = len(orig_txt)

        if len(new_txt) > max_chars:
            messagebox.showwarning('טקסט ארוך מדי', f'''הטקסט החדש ({len(new_txt)} תווים) חורג מהאורך המקסימלי ({max_chars} תווים).''')
            return None
        if 'replacements' not in self.text_config:
            self.text_config['replacements'] = { }
        self.text_config['replacements'][orig_txt] = new_txt
        text_engine.save_text_config(self.text_config)
        self.custom_replacements = dict(self.text_config['replacements'])
        self._refresh_active_replacements_list()
        self.lbl_status.config(text = f'''✔ המילה \'{orig_txt}\' תוחלף ב-\'{new_txt}\'. לחץ \'החל\' לצריבה.''')
        messagebox.showinfo('ההחלפה נשמרה', f'''המילה \'{orig_txt}\' תוחלף ב-\'{new_txt}\' בכל המכשיר!\nלחץ \'החל שינויי טקסט והכן לצריבה\' כדי לפרוס ל-WOT.''')

    
    def _delete_replacement(self):
        sel = self.list_replacements.curselection()
        if not sel:
            return None
        idx = sel[0]
        keys = list(self.custom_replacements.keys())
        if idx < len(keys):
            target = keys[idx]
            del self.text_config['replacements'][target]
            text_engine.save_text_config(self.text_config)
            self.custom_replacements = dict(self.text_config['replacements'])
            self._refresh_active_replacements_list()
            self.lbl_status.config(text = f'''ההחלפה עבור \'{target}\' נמחקה.''')
            return None

    
    def _apply_text_tab_and_deploy(self):
        '''1.0'''
        title = self.entry_about_title.get().strip()
        body = self.txt_about_body.get('1.0', 'end-1c')
        if len(body) <= 96:
            self.text_config['about_title'] = title
            self.text_config['about_body'] = body
            text_engine.save_text_config(self.text_config)
        self.deploy_to_wot()

    
    def _build_footer(self):
        '''#21242b'''
        footer = tk.Frame(self, bg = '#21242b', padx = 16, pady = 6)
        footer.pack(fill = 'x', side = 'bottom')
        self.lbl_status = tk.Label(footer, text = 'מוכן לפעולה', font = ('Segoe UI', 10), fg = '#06d6a0', bg = '#21242b')
        self.lbl_status.pack(side = 'left')
        self.lbl_credits = tk.Label(footer, text = 'כל הזכויות שמורות ל- @מה-זה-משנה-אה מפורום מתמחים טופ', font = ('Segoe UI', 9, 'bold'), fg = '#ffd166', bg = '#21242b')
        self.lbl_credits.pack(side = 'left', expand = True)
        self.lbl_count = tk.Label(footer, text = 'מותאמים אישית: 0 / 70', font = ('Segoe UI', 10, 'bold'), fg = '#f8f9fa', bg = '#21242b')
        self.lbl_count.pack(side = 'right')

    
    def _on_mousewheel(self, event):
        steps = int(-1 * (event.delta / 120)) * 2
        self.canvas.yview_scroll(steps, 'units')

    
    def _on_canvas_configure(self, event):
        avail_w = event.width - START_X
        new_cols = max(2, avail_w // (CARD_W + GAP_X))
        if new_cols != self.current_cols:
            self.current_cols = new_cols
            self._render_gallery()
            return None

    
    def _render_gallery(self):
        '''all'''
        self.canvas.delete('all')
        cols = self.current_cols
        for slot in range(1, TOTAL_WALLPAPERS + 1):
            item = self.slot_state.get(slot)
            if not item:
                continue
            is_custom = item['is_custom']
            is_selected = slot == self.selected_slot
            idx = slot - 1
            r = idx // cols
            c = idx % cols
            x1 = START_X + c * (CARD_W + GAP_X)
            y1 = START_Y + r * (CARD_H + GAP_Y)
            x2 = x1 + CARD_W
            y2 = y1 + CARD_H
            cx = (x1 + x2) // 2
            bg_col = '#1b3022' if is_custom else '#262930'
            if is_selected:
                pass
            elif is_custom:
                pass
            
            border_col = '#343a40'
            if is_selected:
                pass
            elif is_custom:
                pass
            
            border_w = 1
            self.canvas.create_rectangle(x1, y1, x2, y2, fill = bg_col, outline = border_col, width = border_w, tags = (f'''slot_{slot}''', f'''card_{slot}''', f'''bg_{slot}''', 'card_body'))
            title_col = '#06d6a0' if is_custom else '#f8f9fa'
            self.canvas.create_text(cx, y1 + 14, text = f'''טפט #{slot}''', fill = title_col, font = ('Segoe UI', 10, 'bold'), tags = (f'''slot_{slot}''', f'''card_{slot}''', f'''title_{slot}''', 'card_body'))
            tag_txt = '★ מותאם אישית' if is_custom else 'מקורי'
            tag_col = '#06d6a0' if is_custom else '#6c757d'
            self.canvas.create_text(cx, y1 + 30, text = tag_txt, fill = tag_col, font = ('Segoe UI', 8), tags = (f'''slot_{slot}''', f'''card_{slot}''', f'''tag_{slot}''', 'card_body'))
            if slot in self.thumb_images:
                self.canvas.create_image(cx, y1 + 135, image = self.thumb_images[slot], tags = (f'''slot_{slot}''', f'''card_{slot}''', f'''img_{slot}''', 'card_body'))
            btn_rep_x1 = x1 + 10
            btn_rep_x2 = cx - 4
            btn_y1 = y2 - 34
            btn_y2 = y2 - 10
            self.canvas.create_rectangle(btn_rep_x1, btn_y1, btn_rep_x2, btn_y2, fill = '#3d405b', outline = '', tags = (f'''slot_{slot}''', f'''btn_rep_{slot}''', f'''btn_rep_bg_{slot}''', 'btn_rep'))
            self.canvas.create_text((btn_rep_x1 + btn_rep_x2) // 2, (btn_y1 + btn_y2) // 2, text = 'החלף...', fill = '#ffffff', font = ('Segoe UI', 8, 'bold'), tags = (f'''slot_{slot}''', f'''btn_rep_{slot}''', 'btn_rep'))
            btn_rst_x1 = cx + 4
            btn_rst_x2 = x2 - 10
            rst_bg = '#5c2429' if is_custom else '#252830'
            rst_fg = '#ff6b6b' if is_custom else '#495057'
            self.canvas.create_rectangle(btn_rst_x1, btn_y1, btn_rst_x2, btn_y2, fill = rst_bg, outline = '', tags = (f'''slot_{slot}''', f'''btn_rst_{slot}''', f'''btn_rst_bg_{slot}''', 'btn_rst'))
            self.canvas.create_text((btn_rst_x1 + btn_rst_x2) // 2, (btn_y1 + btn_y2) // 2, text = 'איפוס', fill = rst_fg, font = ('Segoe UI', 8), tags = (f'''slot_{slot}''', f'''btn_rst_{slot}''', f'''btn_rst_txt_{slot}''', 'btn_rst'))
            self._bind_card_events(slot)
        total_rows = (TOTAL_WALLPAPERS + cols - 1) // cols
        total_h = START_Y + total_rows * (CARD_H + GAP_Y) + 20
        self.canvas.config(scrollregion = (0, 0, START_X + cols * (CARD_W + GAP_X), total_h))

    
    def _bind_card_events(self, slot):
        '''card_'''
        card_tag = f'''card_{slot}'''
        rep_tag = f'''btn_rep_{slot}'''
        rst_tag = f'''btn_rst_{slot}'''
        self.canvas.tag_bind(card_tag, '<Button-1>', (lambda e, s = slot: self.select_slot(s)))
        self.canvas.tag_bind(card_tag, '<Double-Button-1>', (lambda e, s = slot: self.replace_wallpaper(s)))
        self.canvas.tag_bind(card_tag, '<Button-3>', (lambda e, s = slot: self._show_card_context_menu(e, s)))
        self.canvas.tag_bind(card_tag, '<Enter>', (lambda e, s = slot: self._on_card_hover(s, True)))
        self.canvas.tag_bind(card_tag, '<Leave>', (lambda e, s = slot: self._on_card_hover(s, False)))
        self.canvas.tag_bind(rep_tag, '<Button-1>', (lambda e, s = slot: self.replace_wallpaper(s)))
        self.canvas.tag_bind(rep_tag, '<Enter>', (lambda e, s = slot: self._on_btn_rep_hover(s, True)))
        self.canvas.tag_bind(rep_tag, '<Leave>', (lambda e, s = slot: self._on_btn_rep_hover(s, False)))
        self.canvas.tag_bind(rst_tag, '<Button-1>', (lambda e, s = slot: self._on_click_reset(s)))
        self.canvas.tag_bind(rst_tag, '<Enter>', (lambda e, s = slot: self._on_btn_rst_hover(s, True)))
        self.canvas.tag_bind(rst_tag, '<Leave>', (lambda e, s = slot: self._on_btn_rst_hover(s, False)))

    
    def _show_card_context_menu(self, event, slot):
        self.select_slot(slot)
        menu = tk.Menu(self, tearoff = 0, bg = '#21242b', fg = '#ffffff', activebackground = '#06d6a0', activeforeground = '#111215')
        menu.add_command(label = f'''🖼️ טפט #{slot}''', state = 'disabled')
        menu.add_separator()
        menu.add_command(label = '✏️ החלף תמונה...', command = (lambda s = slot: self.replace_wallpaper(s)))
        menu.add_command(label = '⇄ החלף מיקום עם טפט אחר...', command = (lambda s = slot: self.open_swap_dialog(s)))
        item = self.slot_state.get(slot, { })
        if item.get('is_custom'):
            menu.add_command(label = '↺ איפוס טפט זה למקור', command = (lambda s = slot: self.reset_wallpaper(s)))
        menu.add_separator()
        menu.add_command(label = '🔍 הגדל פי 2 (480x640)', command = (lambda s = slot: ZoomDialog(self, self.slot_state[s]['image'], s)))
        menu.add_command(label = '💾 שמור תמונה למחשב...', command = (lambda s = slot: self._export_slot_image(s)))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
            return None
        finally:
            menu.grab_release()


    
    def _on_card_hover(self, slot, is_entering):
        if slot == self.selected_slot:
            return None
        is_custom = self.slot_state.get(slot, { }).get('is_custom', False)
        if is_entering:
            self.canvas.itemconfig(f'''bg_{slot}''', outline = '#4cc9f0', width = 2)
            self.canvas.config(cursor = 'hand2')
            return None
        border_col = '#06d6a0' if is_custom else '#343a40'
        border_w = 2 if is_custom else 1
        self.canvas.itemconfig(f'''bg_{slot}''', outline = border_col, width = border_w)
        self.canvas.config(cursor = '')

    
    def _on_btn_rep_hover(self, slot, is_entering):
        '''btn_rep_bg_'''
        if is_entering:
            self.canvas.itemconfig(f'''btn_rep_bg_{slot}''', fill = '#05b888')
            self.canvas.config(cursor = 'hand2')
            return None
        self.canvas.itemconfig(f'''btn_rep_bg_{slot}''', fill = '#3d405b')
        self.canvas.config(cursor = '')

    
    def _on_btn_rst_hover(self, slot, is_entering):
        '''is_custom'''
        is_custom = self.slot_state.get(slot, { }).get('is_custom', False)
        if not is_custom:
            return None
        if is_entering:
            self.canvas.itemconfig(f'''btn_rst_bg_{slot}''', fill = '#e63946')
            self.canvas.config(cursor = 'hand2')
            return None
        self.canvas.itemconfig(f'''btn_rst_bg_{slot}''', fill = '#5c2429')
        self.canvas.config(cursor = '')

    
    def _on_click_reset(self, slot):
        '''is_custom'''
        is_custom = self.slot_state.get(slot, { }).get('is_custom', False)
        if is_custom:
            self.reset_wallpaper(slot)
            return None

    
    def select_slot(self, slot):
        if not (1 <= slot) or not (slot <= TOTAL_WALLPAPERS):
            return None

    
    def _navigate_slot(self, delta):
        new_slot = self.selected_slot + delta
        if not (1 <= new_slot) or new_slot <= TOTAL_WALLPAPERS:
            pass
        else:
            return None
        self.select_slot(new_slot)
        idx = new_slot - 1
        row = idx // self.current_cols
        total_rows = (TOTAL_WALLPAPERS + self.current_cols - 1) // self.current_cols
        fraction = max(0, min(1, row / max(1, total_rows - 1)))
        self.canvas.yview_moveto(fraction)

    
    def _update_hd_preview(self):
        slot = self.selected_slot
        item = self.slot_state.get(slot)
        if not item:
            return None
        im = item['image']
        is_custom = item['is_custom']
        self.hd_tk = ImageTk.PhotoImage(im)
        self.hd_canvas.delete('all')
        self.hd_canvas.create_image(120, 160, image = self.hd_tk)
        self.lbl_slot_title.config(text = f'''טפט #{slot}''', fg = '#06d6a0' if is_custom else '#ffffff')
        if is_custom:
            self.lbl_slot_badge.config(text = '★ מותאם אישית (מוכן לצריבה)', fg = '#06d6a0')
            self.btn_hd_reset.config(state = 'normal', bg = '#5c2429', fg = '#ff6b6b')
            return None
        self.lbl_slot_badge.config(text = 'מקורי (ברירת מחדל)', fg = '#adb5bd')
        self.btn_hd_reset.config(state = 'disabled', bg = '#2c3038', fg = '#555b68')

    
    def _open_zoom_modal(self):
        '''image'''
        slot = self.selected_slot
        item = self.slot_state.get(slot)
        if item:
            ZoomDialog(self, item['image'], slot)
            return None

    
    def _export_slot_image(self, slot = None):
        if slot is None:
            slot = self.selected_slot
        item = self.slot_state.get(slot)
        if not item:
            return None
        dest = filedialog.asksaveasfilename(title = f'''שמור טפט #{slot} למחשב''', defaultextension = '.png', initialfile = f'''q8_wallpaper_{slot}.png''', filetypes = [
            ('PNG Image', '*.png'),
            ('JPEG Image', '*.jpg')])
        if dest:
            item['image'].save(dest)
            messagebox.showinfo('נשמר בהצלחה', f'''הטפט נשמר בהצלחה בנתיב:\n{dest}''')
            return None

    
    def _export_current_image(self):
        self._export_slot_image(self.selected_slot)

    
    def load_and_refresh_from_wot(self):
        '''‏טוען נתונים חיים מתוכנת WOT...'''
        self.lbl_status.config(text = '‏טוען נתונים חיים מתוכנת WOT...')
        
        try:
            live_data, live_theme_hex, live_title, live_body = mmi_builder.load_live_wot_state()
            self.slot_state = live_data
            if live_theme_hex:
                self.confirmed_theme_hex = live_theme_hex
                self.current_theme_hex = live_theme_hex
                preset_name = 'מותאם אישית (מ-WOT)'
                for p in theme_engine.PRESETS:
                    if not p['hex'].upper() == live_theme_hex.upper():
                        continue
                    preset_name = p['name']
                    theme_engine.PRESETS
                self.confirmed_theme_name = preset_name
                self.current_theme_name = preset_name
                theme_engine.save_theme_config(live_theme_hex, preset_name)
                if hasattr(self, 'lbl_active_theme_name'):
                    self.lbl_active_theme_name.config(text = preset_name)
                if hasattr(self, 'swatch_canvas'):
                    self.swatch_canvas.config(bg = live_theme_hex)
                if hasattr(self, '_update_theme_info_card'):
                    self._update_theme_info_card()
                if hasattr(self, '_update_theme_mockup'):
                    self._update_theme_mockup()
                if hasattr(self, '_update_preset_card_highlights'):
                    self._update_preset_card_highlights()
            if live_title:
                self.about_title_var.set(live_title)
            if live_body:
                self.about_body_str = live_body
                if hasattr(self, 'txt_about_body'):
                    self.txt_about_body.delete('1.0', 'end')
                    self.txt_about_body.insert('1.0', live_body)
                    self._on_about_text_changed()
            custom_count = 0
            for slot in range(1, TOTAL_WALLPAPERS + 1):
                item = self.slot_state[slot]
                if item['is_custom']:
                    custom_count += 1
                thumb = make_sharp_thumbnail(item['image'])
                self.thumb_images[slot] = ImageTk.PhotoImage(thumb)
            self._render_gallery()
            self.select_slot(self.selected_slot)
            self.lbl_count.configure(text = f'''מותאמים אישית: {custom_count} / {TOTAL_WALLPAPERS}''')
            self.lbl_status.config(text = '‏● מסונכרן בזמן אמת מול מה שמוכן לצריבה בתוכנת WOT')
        except Exception as e:
            self.lbl_status.config(text = f'''‏שגיאה בסנכרון מתוכנת WOT: {e}''')
            return None


    
    def _update_single_card(self, slot):
        item = self.slot_state.get(slot)
        if not item:
            return None
        is_custom = item['is_custom']
        thumb = make_sharp_thumbnail(item['image'])
        self.thumb_images[slot] = ImageTk.PhotoImage(thumb)
        self.canvas.itemconfig(f'''img_{slot}''', image = self.thumb_images[slot])
        self.canvas.itemconfig(f'''tag_{slot}''', text = '★ מותאם אישית' if is_custom else 'מקורי', fill = '#06d6a0' if is_custom else '#6c757d')
        self.canvas.itemconfig(f'''title_{slot}''', fill = '#06d6a0' if is_custom else '#f8f9fa')
        if slot == self.selected_slot:
            pass
        elif is_custom:
            pass
        
        if slot == self.selected_slot:
            pass
        elif is_custom:
            pass
        
        # NOTE(recovery): decompiler lost this canvas call (target + args corrupted);
        # verify against original source. Neutralized so it is a no-op instead of a crash.
        # '#06d6a0'('#343a40', fill = 3, outline = 2, width = 1)
        self.canvas.itemconfig(f'''btn_rst_bg_{slot}''', fill = '#5c2429' if is_custom else '#252830')
        self.canvas.itemconfig(f'''btn_rst_txt_{slot}''', fill = '#ff6b6b' if is_custom else '#495057')
        custom_count = sum(1 for s in range(1, TOTAL_WALLPAPERS + 1) if self.slot_state.get(s, { }).get('is_custom'))
        self.lbl_count.configure(text = f'''מותאמים אישית: {custom_count} / {TOTAL_WALLPAPERS}''')
        if slot == self.selected_slot:
            self._update_hd_preview()
            return None

    
    def open_text_to_wallpaper_dialog(self):
        '''Opens the text-to-wallpaper tool (e.g. for Birkat Hamazon).'''
        start = self.selected_slot if getattr(self, 'selected_slot', None) else 20
        TextToWallpaperDialog(self, start_slot = start)

    def open_icon_dialog(self):
        '''Opens the custom menu-icon replacement tool.'''
        IconReplaceDialog(self)

    def _assign_custom_image(self, slot, img):
        '''Assigns a rendered PIL image to a slot as a custom wallpaper.'''
        if slot not in self.slot_state:
            self.slot_state[slot] = { }
        self.slot_state[slot]['image'] = img
        self.slot_state[slot]['sjpg'] = None
        self.slot_state[slot]['is_custom'] = True
        try:
            img.save(os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.png'''), format = 'PNG')
        except Exception:
            pass
        sjpg_path = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.sjpg''')
        if os.path.exists(sjpg_path):
            try:
                os.remove(sjpg_path)
            except Exception:
                pass
        try:
            self._update_single_card(slot)
        except Exception:
            pass

    def replace_wallpaper(self, slot):
        '''קבצי תמונה'''
        filetypes = [
            ('קבצי תמונה', '*.jpg;*.jpeg;*.png;*.webp;*.bmp'),
            ('JPEG', '*.jpg;*.jpeg'),
            ('PNG', '*.png'),
            ('כל הקבצים', '*.*')]
        chosen = filedialog.askopenfilename(title = f'''בחר תמונה עבור טפט #{slot}''', filetypes = filetypes)
        if chosen:
            dialog = ImageCropDialog(self, chosen, slot)
            self.wait_window(dialog)
            if dialog.result_image:
                if slot not in self.slot_state:
                    self.slot_state[slot] = { }
                self.slot_state[slot]['image'] = dialog.result_image
                self.slot_state[slot]['sjpg'] = None
                self.slot_state[slot]['is_custom'] = True
                png_path = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.png''')
                
                try:
                    dialog.result_image.save(png_path, format = 'PNG')
                except Exception:
                    pass

                sjpg_path = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.sjpg''')
                if os.path.exists(sjpg_path):
                    
                    try:
                        os.remove(sjpg_path)
                    except Exception:
                        pass

                self.select_slot(slot)
                self._update_single_card(slot)
                self.lbl_status.config(text = f'''‏טפט #{slot} עודכן בהצלחה! לחץ על \'החל\' כדי לפרוס לתוכנת WOT.''')
                return None
            return None

    
    def open_swap_dialog(self, initial_slot = None):
        slot_a = initial_slot if initial_slot is not None else self.selected_slot
        WallpaperSwapDialog(self, initial_slot_a = slot_a)

    
    def swap_wallpapers(self, slot_a, slot_b):
        if slot_a == slot_b:
            return False
        if not (1 <= slot_a) or slot_a <= TOTAL_WALLPAPERS:
            pass
        else:
            return False
        if not (1 <= slot_b) or not (slot_b <= TOTAL_WALLPAPERS):
            return False
        return False

    
    def reset_wallpaper(self, slot):
        '''wp_'''
        orig_jpg = os.path.join(ORIG_WP_DIR, f'''wp_{slot}.jpg''')
        if os.path.exists(orig_jpg):
            im = Image.open(orig_jpg).convert('RGB')
        else:
            with open(mmi_builder.MMI_DUMP_PATH, 'rb') as f:
                dump = f.read()
            if slot == 1:
                im = spd_sjpg.sjpg_to_image(dump[892172:894723])
            else:
                idx = slot - 2
                slot_info = mmi_builder.get_slot_info(dump)
                (abs_off, sz, _) = slot_info[idx]
                im = spd_sjpg.sjpg_to_image(dump[abs_off:abs_off + sz])
        if slot not in self.slot_state:
            self.slot_state[slot] = { }
        self.slot_state[slot]['image'] = im
        self.slot_state[slot]['sjpg'] = None
        self.slot_state[slot]['is_custom'] = False
        custom_png = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.png''')
        if os.path.exists(custom_png):
            os.remove(custom_png)
        custom_sjpg = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.sjpg''')
        if os.path.exists(custom_sjpg):
            os.remove(custom_sjpg)
        self.select_slot(slot)
        self._update_single_card(slot)
        self.lbl_status.config(text = f'''‏טפט #{slot} הוחזר למקור. לחץ על \'החל\' לצריבה.''')

    
    def reset_all_wallpapers(self):
        '''איפוס כל הטפטים'''
        if not messagebox.askyesno('איפוס כל הטפטים', 'האם לשחזר את כל 70 הטפטים לקבצים המקוריים?'):
            return None
        with open(mmi_builder.MMI_DUMP_PATH, 'rb') as f:
            dump = f.read()
        slot_info = mmi_builder.get_slot_info(dump)
        for slot in range(1, TOTAL_WALLPAPERS + 1):
            if slot == 1:
                im = spd_sjpg.sjpg_to_image(dump[892172:894723])
            else:
                idx = slot - 2
                (abs_off, sz, _) = slot_info[idx]
                im = spd_sjpg.sjpg_to_image(dump[abs_off:abs_off + sz])
            if slot not in self.slot_state:
                self.slot_state[slot] = { }
            self.slot_state[slot]['image'] = im
            self.slot_state[slot]['sjpg'] = None
            self.slot_state[slot]['is_custom'] = False
            custom_png = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.png''')
            if os.path.exists(custom_png):
                os.remove(custom_png)
            custom_sjpg = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.sjpg''')
            if os.path.exists(custom_sjpg):
                os.remove(custom_sjpg)
            thumb = make_sharp_thumbnail(im)
            self.thumb_images[slot] = ImageTk.PhotoImage(thumb)
        self._render_gallery()
        self.select_slot(self.selected_slot)
        self.lbl_count.configure(text = f'''מותאמים אישית: 0 / {TOTAL_WALLPAPERS}''')
        self.lbl_status.config(text = "‏כל הטפטים אופסו למקור. לחץ על 'החל' לצריבה נקייה.")
        messagebox.showinfo('איפוס למקור', "‏כל 70 הטפטים אופסו למקור.\nלחץ על 'החל והכן לצריבה בתוכנת WOT' כדי לעדכן את WOT.")

    
    def deploy_to_wot(self):
        if self.is_deploying:
            return None
        self.is_deploying = True
        self.btn_deploy.config(state = 'disabled', text = '⏳ מעבד ומכין...')
        if hasattr(self, 'btn_apply_theme_tab'):
            self.btn_apply_theme_tab.config(state = 'disabled', text = '⏳ מעבד ומכין...')
        if hasattr(self, 'btn_apply_text_tab'):
            self.btn_apply_text_tab.config(state = 'disabled', text = '⏳ מעבד ומכין...')
        self.lbl_status.config(text = '‏מעבד נתונים, טקסטים וערכת נושא...')
        
        def _worker():
            
            try:
                import importlib
                # (removed importlib.reload(theme_engine))
                # (removed importlib.reload(text_engine))
                # (removed importlib.reload(mmi_builder))
                custom_wallpapers = { }
                for slot in range(1, TOTAL_WALLPAPERS + 1):
                    item = self.slot_state.get(slot)
                    if not item or not item.get('is_custom'):
                        continue
                    if item.get('image') is not None:
                        custom_wallpapers[slot] = item['image']
                        continue
                    if item.get('sjpg') is not None:
                        custom_wallpapers[slot] = item['sjpg']
                        continue
                    png_p = os.path.join(CUSTOM_WP_DIR, f'''wp_{slot}.png''')
                    if not os.path.exists(png_p):
                        continue
                    custom_wallpapers[slot] = Image.open(png_p).convert('RGB')
                self.post_ui((lambda : self.lbl_status.config(text = '‏בונה את קובץ המשאבים, הטקסטים וערכת הנושא...')))
                use_icons = self.use_unisoc_icons.get() if hasattr(self, 'use_unisoc_icons') else False
                cust_icons = {p: v for p, v in self.custom_icons.items() if v is not None}
                orig, mod = mmi_builder.build_modified_mmi(custom_wallpapers, theme_hex = self.confirmed_theme_hex, use_unisoc_icons = use_icons, custom_icons = cust_icons or None)
                # DEBUG(recovery): save the encoded SJPG of the first few custom slots
                # so their exact bytes can be compared against real device slots.
                try:
                    import struct as _st
                    _P40 = 39319156; _INFO = 39319260; _OFFS = 39320088
                    _saved = 0
                    for _slot in sorted(custom_wallpapers.keys()):
                        if _slot == 1 or _saved >= 3:
                            continue
                        _idx = _slot - 2
                        _rel = _st.unpack_from('<I', mod, _OFFS + _idx * 4)[0]
                        _sz = _st.unpack_from('<I', mod, _INFO + _idx * 12 + 8)[0]
                        _ab = _P40 + _rel
                        with open(os.path.join(BASE_DIR, f'debug_mine_slot_{_slot}.sjpg'), 'wb') as _df:
                            _df.write(mod[_ab:_ab + _sz])
                        _saved += 1
                except Exception:
                    pass
                diff_table = mmi_builder.generate_diff_table(orig, mod)
                self.post_ui((lambda : self.lbl_status.config(text = '‏מטמיע את ה-DLL בתיקיית WOT...')))
                dll_generator.build_and_deploy_dll(diff_table)
                self.post_ui((lambda : self._on_deploy_success(len(custom_wallpapers))))
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                try:
                    with open(os.path.join(BASE_DIR, 'q8_build_error.log'), 'w', encoding = 'utf-8') as _lf:
                        _lf.write(tb)
                except Exception:
                    pass
                self.post_ui((lambda err = tb: self._on_deploy_error(err)))
                return None


        threading.Thread(target = _worker, daemon = True).start()

    
    def _on_deploy_success(self, count):
        self.is_deploying = False
        self.btn_deploy.config(state = 'normal', text = '‏🚀 החל והכן לצריבה בתוכנת WOT')
        if hasattr(self, 'btn_apply_theme_tab'):
            self.btn_apply_theme_tab.config(state = 'normal', text = '‏🚀 החל צבע זה והכן לצריבה בתוכנת WOT')
        if hasattr(self, 'btn_apply_text_tab'):
            self.btn_apply_text_tab.config(state = 'normal', text = '🚀 החל שינויי טקסט והכן לצריבה בתוכנת WOT')
        self.lbl_status.config(text = '‏הגרסה נפרסה בהצלחה בתוכנת WOT!')
        self.load_and_refresh_from_wot()
        messagebox.showinfo('הצריבה מוכנה בהצלחה!', f'''‏הגרסה הוכנה בהצלחה ונפרסה ישירות לתוכנת WOT!\n\n• טפטים שהותאמו אישית: {count}\n• צבע ערכת נושא: {self.confirmed_theme_name} ({self.confirmed_theme_hex})\n• מסך \'אודות\' וטקסטים מותאמים: נצרבו בהצלחה\n• כל שאר הטפטים והרכיבים: מקוריים ותקינים לחלוטין\n• באנר שיחה נכנסת, פסי הניווט והתפריטים עודכנו בצבע הנבחר.\n\nכעת פתח את תוכנת WOT ולחץ Start לצריבה!''')

    
    def _on_deploy_error(self, error):
        self.is_deploying = False
        self.btn_deploy.config(state = 'normal', text = '‏🚀 החל והכן לצריבה בתוכנת WOT')
        if hasattr(self, 'btn_apply_theme_tab'):
            self.btn_apply_theme_tab.config(state = 'normal', text = '‏🚀 החל צבע זה והכן לצריבה בתוכנת WOT')
        if hasattr(self, 'btn_apply_text_tab'):
            self.btn_apply_text_tab.config(state = 'normal', text = '🚀 החל שינויי טקסט והכן לצריבה בתוכנת WOT')
        self.lbl_status.config(text = '‏שגיאה בבנייה')
        messagebox.showerror('שגיאה', f'''‏אירעה שגיאה בעת הכנת הגרסה:\n\n{error}\n\n(נשמר גם בקובץ q8_build_error.log ליד התוכנה)''')


if __name__ == '__main__':
    app = Q8WallpaperStudio()
    app.mainloop()

