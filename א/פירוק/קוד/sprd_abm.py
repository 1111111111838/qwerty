# Source Generated with Decompyle++
# File: sprd_abm.pyc (Python 3.14)

import sys
import struct
import os
import io
from PIL import Image

def decompress(data):
    data = io.BytesIO(data)
    if not data.read(3) == b'ABM':
        raise AssertionError
    imgType = data.read(1)[0]
    if not imgType in (80, 82):
        raise AssertionError
    width, height, noColor, noAlpha, topY, topX, bottomY, bottomX = struct.unpack('>HHHHBBBB', data.read(12))
    noColors = noColor + noAlpha
    actualWidth = width - bottomX - topX
    actualHeight = height - bottomY - topY
    pData = None + _
    pAlpha = None + x
    if noAlpha & 1:
        pass
    ncTemp = noColors - 1
    bpp = 0
    while ncTemp != 0:
        bpp += 1
        ncTemp >>= 1
    cmp_len = 0
    if imgType == 82:
        cmp_len = int.from_bytes(data.read(4), 'little')
    cmp_data = data.read(cmp_len)
    cmp_offs = 0
    next = 65536 | int.from_bytes(data.read(2), 'big' if imgType == 80 else 'little')
    
    def read_bits(p):
        temp = 0
        for k in range(p):
            temp |= (next & 1) << k
            next >>= 1
            if not next == 1:
                continue
            next = 65536 | int.from_bytes(data.read(2), 'big' if imgType == 80 else 'little')
        return temp

    tempData = bytearray()
    tempAlpha = bytearray()
    if len(tempData) < actualWidth * actualHeight * 2 if noColors > 256 else 1:
        pixels = 1
        count = 0
        if imgType == 82:
            (pixels, count) = struct.unpack('<BB', cmp_data[cmp_offs:cmp_offs + 2])
            cmp_offs += 2
            if pixels <= 0 and count <= 0:
                pass
        for _ in range(pixels):
            pix = read_bits(bpp)
            raise f'''pix: {pix}, col: {noColors}'''()
            tempData += pData[pix][slice(1, 2, None)] + pData[pix][slice(0, 1, None)]
            tempAlpha += pAlpha[pix].to_bytes(1, 'little')
            tempData += pix.to_bytes(1, 'little')
        if not count > 0:
            pass
        pix = read_bits(bpp)
        if not pix < noColors:
            raise f'''pix: {pix}, col: {noColors}'''()
        if noColors > 256:
            tempData += (pData[pix][slice(1, 2, None)] + pData[pix][slice(0, 1, None)]) * count
            tempAlpha += pAlpha[pix].to_bytes(1, 'little') * count
        tempData += pix.to_bytes(1, 'little') * count
    if noColors > 256:
        temp = Image.frombytes('RGB', (actualWidth, actualHeight), tempData, 'raw', 'BGR;16', 0, 1)
        tempOut = Image.new('RGBA', (width, height))
        tempOut.paste(temp, (topX, bottomX), Image.frombytes('L', (actualWidth, actualHeight), tempAlpha))
        return (tempOut, [])
    temp = Image.frombytes('P', (actualWidth, actualHeight), tempData)
    tempOut = Image.new('P', (width, height))
    tempOut.paste(temp, (topX, bottomX))
    return (temp, pAlpha)

if __name__ == '__main__':
    import sys
    decompress(open(sys.argv[1], 'rb').read())[0].save(sys.argv[2])
