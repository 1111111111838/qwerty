# Source Generated with Decompyle++
# File: spd_sjpg.pyc (Python 3.14)

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


def encode_abm_icon(img, W=68, H=66, topY=9, topX=5, bottomY=5, bottomX=11, bg=(255, 255, 255)):
    '''
Encode a PIL image to a device-format ABM icon (opaque, composited over bg so
the menu background shows through cleanly). Matches the stock icon geometry.
'''
    aw = W - bottomX - topX
    ah = H - bottomY - topY
    im = img.convert('RGBA').resize((aw, ah), Image.LANCZOS)
    base = Image.new('RGBA', (aw, ah), tuple(bg) + (255,))
    base.alpha_composite(im)
    rgb = base.convert('RGB')
    pix = list(rgb.getdata())
    c565 = [_rgb_to_565(r, g, b) for (r, g, b) in pix]
    uniq = sorted(set(c565))
    if len(uniq) > 512:
        q = rgb.quantize(colors=256, method=Image.MEDIANCUT)
        qp = q.getpalette()
        qi = list(q.getdata())
        qcol = [_rgb_to_565(qp[i * 3], qp[i * 3 + 1], qp[i * 3 + 2]) for i in range(256)]
        uniq = sorted(set(qcol))
        idxmap = {c: i for i, c in enumerate(uniq)}
        indices = [idxmap[qcol[qi[k]]] for k in range(len(qi))]
    else:
        idxmap = {c: i for i, c in enumerate(uniq)}
        indices = [idxmap[c] for c in c565]
    noColor = len(uniq)
    noAlpha = 0
    noColors = noColor
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
    for c in uniq:
        out += struct.pack('>H', c)
    # Build run-length segments (value, length).
    segs = []
    i = 0
    n = len(indices)
    while i < n:
        j = i
        while j < n and indices[j] == indices[i]:
            j += 1
        segs.append((indices[i], j - i))
        i = j
    # Emit control pairs (pixels, count). A pair reads `pixels` individual
    # palette indices, then (if count > 0) one more index repeated `count`
    # times. Runs of length 1 are batched as literals so the 2-byte control
    # overhead is amortized across up to 255 pixels instead of paid per pixel
    # (the old scheme cost 2 ctrl bytes for every single pixel in noisy areas,
    # which blew detailed icons past their slot capacity).
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
        # a real run: first drain any literal overflow beyond one pair's 255
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

