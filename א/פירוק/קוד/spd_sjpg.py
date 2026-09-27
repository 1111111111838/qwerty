# Source Generated with Decompyle++
# File: spd_sjpg.pyc (Python 3.14)

'''
spd_sjpg.py - Unisoc / MOCOR SJPG encoder and decoder for QLYX Q8
Based on official Unisoc quantization tables and Huffman data.
'''
import io
import struct
from PIL import Image, ImageOps, ImageFilter
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
JPG_LUM_QUANT_TBL = [list(_LUM_Q0) for _ in range(5)]
JPG_CHR_QUANT_TBL = [list(_CHR_Q0) for _ in range(5)]
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

