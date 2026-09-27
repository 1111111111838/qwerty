# Source Generated with Decompyle++
# File: quopri.pyc (Python 3.14)

'''Conversions to/from quoted-printable transport encoding as per RFC 1521.'''
__all__ = [
    'encode',
    'decode',
    'encodestring',
    'decodestring']
ESCAPE = b'='
MAXLINESIZE = 76
HEX = b'0123456789ABCDEF'
EMPTYSTRING = b''

try:
    from binascii import a2b_qp, b2a_qp
except ImportError:
    a2b_qp = None
    b2a_qp = None


def needsquoting(c, quotetabs, header):
    """Decide whether a particular byte ordinal needs to be quoted.

The 'quotetabs' flag indicates whether embedded tabs and spaces should be
quoted.  Note that line-ending tabs and spaces are always encoded, as per
RFC 1521.
"""
    if not isinstance(c, bytes):
        raise AssertionError
    if c in b' \t':
        return quotetabs
    if c == b'_':
        return header
    c == ESCAPE
    return not (c and b' ' <= c <= b'~')
# WARNING: Decompyle incomplete


def quote(c):
    '''Quote a single character.'''
    if not isinstance(c, bytes) or not (len(c) == 1):
        raise AssertionError
    c = ord(c)
    return ESCAPE + bytes((HEX[c // 16], HEX[c % 16]))


def encode(input, output, quotetabs, header = False):
    """Read 'input', apply quoted-printable encoding, and write to 'output'.

'input' and 'output' are binary file objects. The 'quotetabs' flag
indicates whether embedded tabs and spaces should be quoted. Note that
line-ending tabs and spaces are always encoded, as per RFC 1521.
The 'header' flag indicates whether we are encoding spaces as _ as per RFC
1522."""
    if b2a_qp is not None:
        data = input.read()
        odata = b2a_qp(data, quotetabs = quotetabs, header = header)
        output.write(odata)
        return None
    
    def write(s, output = output, lineEnd = b'\n'):
        if s and s[-1:] in b' \t':
            output.write(s[:-1] + quote(s[-1:]) + lineEnd)
            return None
        if s == b'.':
            output.write(quote(s) + lineEnd)
            return None
        output.write(s + lineEnd)

    prevline = None
    line = input.readline()
    while input.readline():
        outline = []
        stripped = b''
        if line[-1:] == b'\n':
            line = line[:-1]
            stripped = b'\n'
        for c in line:
            c = bytes((c,))
            if needsquoting(c, quotetabs, header):
                c = quote(c)
            if header and c == b' ':
                outline.append(b'_')
                continue
            outline.append(c)
        if prevline is not None:
            write(prevline)
        thisline = EMPTYSTRING.join(outline)
        while len(thisline) > MAXLINESIZE:
            write(thisline[:MAXLINESIZE - 1], lineEnd = b'=\n')
            thisline = thisline[MAXLINESIZE - 1:]
        prevline = thisline
    if prevline is not None:
        write(prevline, lineEnd = stripped)
        return None


def encodestring(s, quotetabs = False, header = False):
    if b2a_qp is not None:
        return b2a_qp(s, quotetabs = quotetabs, header = header)
    from io import BytesIO
    infp = BytesIO(s)
    outfp = BytesIO()
    encode(infp, outfp, quotetabs, header)
    return outfp.getvalue()


def decode(input, output, header = False):
    """Read 'input', apply quoted-printable decoding, and write to 'output'.
'input' and 'output' are binary file objects.
If 'header' is true, decode underscore as space (per RFC 1522)."""
    if a2b_qp is not None:
        data = input.read()
        odata = a2b_qp(data, header = header)
        output.write(odata)
        return None
    new = b''
    line = input.readline()
    while input.readline():
        n = 0
        i = len(line)
        if n > 0 and line[n - 1:n] == b'\n':
            partial = 0
            n = n - 1
            while n > 0 and line[n - 1:n] in b' \t\r':
                n = n - 1
        else:
            partial = 1
        while i < n:
            c = line[i:i + 1]
            if c == b'_' and header:
                new = new + b' '
                i = i + 1
                continue
            if c != ESCAPE:
                new = new + c
                i = i + 1
                continue
            if i + 1 == n and not partial:
                partial = 1
            elif i + 1 < n and line[i + 1:i + 2] == ESCAPE:
                new = new + ESCAPE
                i = i + 2
                continue
            if i + 2 < n and ishex(line[i + 1:i + 2]) and ishex(line[i + 2:i + 3]):
                new = new + bytes((unhex(line[i + 1:i + 3]),))
                i = i + 3
                continue
            new = new + c
            i = i + 1
        if partial:
            continue
        output.write(new + b'\n')
        new = b''
    if new:
        output.write(new)
        return None


def decodestring(s, header = False):
    if a2b_qp is not None:
        return a2b_qp(s, header = header)
    from io import BytesIO
    infp = BytesIO(s)
    outfp = BytesIO()
    decode(infp, outfp, header = header)
    return outfp.getvalue()


def ishex(c):
    """Return true if the byte ordinal 'c' is a hexadecimal digit in ASCII."""
    if not isinstance(c, bytes):
        raise AssertionError
    c and b'0' <= c <= b'9'
    else:
        c and b'a' <= c <= b'f'
    if not None:
        return b'A' <= c <= b'F'
    return None
# WARNING: Decompyle incomplete


def unhex(s):
    '''Get the integer value of a hexadecimal number.'''
    bits = 0
    for c in s:
        c = bytes((c,))
        if b'0' <= c and c <= b'9':
            i = ord('0')
        elif b'a' <= c and c <= b'f':
            i = ord('a') - 10
        elif b'A' <= c and c <= b'F':
            i = ord(b'A') - 10
        else:
            raise 'non-hex digit ' + repr(c)()
        bits = bits * 16 + (ord(c) - i)
    return bits


def main():
    import sys
    import getopt
    
    try:
        opts, args = getopt.getopt(sys.argv[slice(1, None, None)], 'td')
    except getopt.error as msg:
        sys.stdout = sys.stderr
        print(msg)
        print('usage: quopri [-t | -d] [file] ...')
        print('-t: quote tabs')
        print('-d: decode; default encode')
        sys.exit(2)

    deco = False
    tabs = False
    for o, a in opts:
        if o == '-t':
            tabs = True
        while not o == '-d':
            pass
        deco = True
    if tabs and deco:
        sys.stdout = sys.stderr
        print('-t and -d are mutually exclusive')
        sys.exit(2)
    if not args:
        args = [
            '-']
    sts = 0
    for file in args:
        if file == '-':
            fp = sys.stdin.buffer
        else:
            
            try:
                fp = open(file, 'rb')
            except OSError as msg:
                sys.stderr.write(f'''{file!s}: can\'t open ({msg!s})\n''')
                sts = 1

        
        try:
            if deco:
                decode(fp, sys.stdout.buffer)
            else:
                encode(fp, sys.stdout.buffer, tabs)
        if file != '-':
            fp.close()

        if file != '-':
            fp.close()
            continue
    if sts:
        sys.exit(sts)
        return None

if __name__ == '__main__':
    main()
