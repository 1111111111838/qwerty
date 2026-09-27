# Source Generated with Decompyle++
# File: PdfParser.pyc (Python 3.14)

from __future__ import annotations
import calendar
import codecs
import collections
import mmap
import os
import re
import time
import zlib
from typing import Any, NamedTuple
from . import ImageFile
TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import IO
    _DictBase = collections.UserDict[(str | bytes, Any)]
else:
    _DictBase = collections.UserDict

def encode_text(s):
    '''utf_16_be'''
    return codecs.BOM_UTF16_BE + s.encode('utf_16_be')

PDFDocEncoding = {
    22: '\x17',
    24: '˘',
    25: 'ˇ',
    26: 'ˆ',
    27: '˙',
    28: '˝',
    29: '˛',
    30: '˚',
    31: '˜',
    128: '•',
    129: '†',
    130: '‡',
    131: '…',
    132: '—',
    133: '–',
    134: 'ƒ',
    135: '⁄',
    136: '‹',
    137: '›',
    138: '−',
    139: '‰',
    140: '„',
    141: '“',
    142: '”',
    143: '‘',
    144: '’',
    145: '‚',
    146: '™',
    147: 'ﬁ',
    148: 'ﬂ',
    149: 'Ł',
    150: 'Œ',
    151: 'Š',
    152: 'Ÿ',
    160: '€',
    158: 'ž',
    157: 'š',
    156: 'œ',
    155: 'ł',
    154: 'ı',
    153: 'Ž' }

def decode_text(b):
    if b[:len(codecs.BOM_UTF16_BE)] == codecs.BOM_UTF16_BE:
        return b[len(codecs.BOM_UTF16_BE):].decode('utf_16_be')
    return (lambda .0: for byte in .0:
PDFDocEncoding.get(byte, chr(byte)).0)(b())


class PdfFormatError(RuntimeError):
    '''An error that probably indicates a syntactic or semantic error in the
PDF file structure'''
    pass


def check_format_condition(condition, error_message):
    if not condition:
        raise PdfFormatError(error_message)


class IndirectReferenceTuple(NamedTuple):
    generation: 'int' = 'IndirectReferenceTuple'


class IndirectReference(IndirectReferenceTuple):
    
    def __str__(self):
        ''' '''
        return f'''{self.object_id} {self.generation} R'''

    
    def __bytes__(self):
        '''us-ascii'''
        return self.__str__().encode('us-ascii')

    
    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        if not isinstance(other, IndirectReference):
            raise AssertionError
        return other.object_id == self.object_id and other.generation == self.generation

    
    def __ne__(self, other):
        return not (self == other)

    
    def __hash__(self):
        return hash((self.object_id, self.generation))



class IndirectObjectDef(IndirectReference):
    
    def __str__(self):
        ''' '''
        return f'''{self.object_id} {self.generation} obj'''



class XrefTable:
    
    def __init__(self):
        self.existing_entries = { }
        self.new_entries = { }
        self.deleted_entries = {
            0: 65536 }
        self.reading_finished = False

    
    def __setitem__(self, key, value):
        if self.reading_finished:
            self.new_entries[key] = value
        else:
            self.existing_entries[key] = value
        if key in self.deleted_entries:
            del self.deleted_entries[key]
            return None

    
    def __getitem__(self, key):
        
        try:
            return self.new_entries[key]
        except KeyError:
            return self.existing_entries[key]


    
    def __delitem__(self, key):
        if key in self.new_entries:
            generation = self.new_entries[key][1] + 1
            del self.new_entries[key]
            self.deleted_entries[key] = generation
            return None
        if key in self.existing_entries:
            generation = self.existing_entries[key][1] + 1
            self.deleted_entries[key] = generation
            return None
        if key in self.deleted_entries:
            generation = self.deleted_entries[key]
            return None
        msg = f'''object ID {key} cannot be deleted because it doesn\'t exist'''
        raise IndexError(msg)

    
    def __contains__(self, key):
        return key in self.existing_entries or key in self.new_entries

    
    def __len__(self):
        return len(set(self.existing_entries.keys()) | set(self.new_entries.keys()) | set(self.deleted_entries.keys()))

    
    def keys(self):
        return set(self.existing_entries.keys()) - set(self.deleted_entries.keys()) | set(self.new_entries.keys())

    
    def write(self, f):
        b'''xref
'''
        keys = sorted(set(self.new_entries.keys()) | set(self.deleted_entries.keys()))
        deleted_keys = sorted(set(self.deleted_entries.keys()))
        startxref = f.tell()
        f.write(b'xref\n')
        while keys:
            prev = None
            for index, key in enumerate(keys):
                if prev is not None:
                    while prev + 1 == key:
                        prev = key
                contiguous_keys = keys[:index]
                keys = keys[index:]
                enumerate(keys)
            contiguous_keys = keys
            keys = []
            f.write(b'%d %d\n' % (contiguous_keys[0], len(contiguous_keys)))
            for object_id in contiguous_keys:
                while object_id in self.new_entries:
                    f.write(b'%010d %05d n \n' % self.new_entries[object_id])
                this_deleted_object_id = deleted_keys.pop(0)
                check_format_condition(object_id == this_deleted_object_id, f'''expected the next deleted object ID to be {object_id}, instead found {this_deleted_object_id}''')
                
                try:
                    next_in_linked_list = deleted_keys[0]
                except IndexError:
                    next_in_linked_list = 0

                f.write(b'%010d %05d f \n' % (next_in_linked_list, self.deleted_entries[object_id]))
        return startxref



class PdfName:
    name: 'bytes' = 'PdfName'
    
    def __init__(self, name):
        '''us-ascii'''
        if isinstance(name, PdfName):
            self.name = name.name
            return None
        if isinstance(name, bytes):
            self.name = name
            return None
        self.name = name.encode('us-ascii')

    
    def name_as_str(self):
        '''us-ascii'''
        return self.name.decode('us-ascii')

    
    def __eq__(self, other):
        return isinstance(other, PdfName) and other.name == self.name or other == self.name

    
    def __hash__(self):
        return hash(self.name)

    
    def __repr__(self):
        '''('''
        return f'''{self.__class__.__name__}({repr(self.name)})'''

    from_pdf_stream = (lambda cls, data: cls(PdfParser.interpret_name(data)))()
    allowed_chars = classmethod - c
    
    def __bytes__(self):
        b'''/'''
        result = bytearray(b'/')
        for b in self.name:
            while b in self.allowed_chars:
                result.append(b)
            result.extend(b'#%02X' % b)
        return bytes(result)



def PdfArray():
    '''PdfArray'''
    
    def __bytes__(self):
        b'''[ '''
        return b' '.join + (lambda .0: for x in .0:
pdf_repr(x).0)(self()) + b' ]'


PdfArray = __build_class__(PdfArray, 'PdfArray', list[Any])

class PdfDict(_DictBase):
    
    def __setattr__(self, key, value):
        '''data'''
        if key == 'data':
            collections.UserDict.__setattr__(self, key, value)
            return None
        self[key.encode('us-ascii')] = value

    
    def __getattr__(self, key):
        '''us-ascii'''
        
        try:
            value = self[key.encode('us-ascii')]
        except KeyError as e:
            raise AttributeError(key) from e

        if isinstance(value, bytes):
            value = decode_text(value)
        if key.endswith('Date'):
            if value.startswith('D:'):
                value = value[slice(2, None, None)]
            relationship = 'Z'
            if len(value) > 17:
                relationship = value[14]
                offset = int(value[slice(15, 17, None)]) * 60
                if len(value) > 20:
                    offset += int(value[slice(18, 20, None)])
            format = '%Y%m%d%H%M%S'[:len(value) - 2]
            value = time.strptime(value[:len(format) + 2], format)
            if relationship in ('+', '-'):
                offset *= 60
                if relationship == '+':
                    offset *= -1
                value = time.gmtime(calendar.timegm(value) + offset)
        return value

    
    def __bytes__(self):
        b'''<<'''
        out = bytearray(b'<<')
        for key, value in self.items():
            while value:
                pass
            value = pdf_repr(value)
            out.extend(b'\n')
            out.extend(bytes(PdfName(key)))
            out.extend(b' ')
            out.extend(value)
        out.extend(b'\n>>')
        return bytes(out)



class PdfBinary:
    
    def __init__(self, data):
        self.data = data

    
    def __bytes__(self):
        b'''<%s>'''
        return b''.join % (lambda .0: for b in .0:
b'%02X' % b.0)(self.data())



class PdfStream:
    
    def __init__(self, dictionary, buf):
        self.dictionary = dictionary
        self.buf = buf

    
    def decode(self, max_length = ImageFile.SAFEBLOCK):
        b'''Filter'''
        
        try:
            filter = self.dictionary[b'Filter']
        except KeyError:
            return self.buf

        if filter == b'FlateDecode':
            dobj = zlib.decompressobj()
            plaintext = dobj.decompress(self.buf, max_length)
            if dobj.unconsumed_tail:
                msg = 'Decompressed data too large'
                raise ValueError(msg)
            return plaintext
        msg = f'''stream filter {repr(filter)} unknown/unsupported'''
        raise NotImplementedError(msg)



def pdf_repr(x):
    if x is True:
        return b'true'
    if x is False:
        return b'false'
    if x is None:
        return b'null'
    if isinstance(x, (PdfName, PdfDict, PdfArray, PdfBinary)):
        return bytes(x)
    if isinstance(x, (int, float)):
        return str(x).encode('us-ascii')
    if isinstance(x, time.struct_time):
        return b'(D:' + time.strftime('%Y%m%d%H%M%SZ', x).encode('us-ascii') + b')'
    if isinstance(x, dict):
        return bytes(PdfDict(x))
    if isinstance(x, list):
        return bytes(PdfArray(x))
    if isinstance(x, str):
        return pdf_repr(encode_text(x))
    if isinstance(x, bytes):
        x = x.replace(b'\\', b'\\\\')
        x = x.replace(b'(', b'\\(')
        x = x.replace(b')', b'\\)')
        return b'(' + x + b')'
    return bytes(x)


class PdfParser:
    '''Based on
https://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
Supports PDF up to 1.4
'''
    
    def __init__(self, filename = None, f = None, buf = None, start_offset = 0, mode = 'rb'):
        '''specify buf or f or filename, but not both buf and f'''
        if buf and f:
            msg = 'specify buf or f or filename, but not both buf and f'
            raise RuntimeError(msg)
        self.filename = filename
        self.buf = buf
        self.f = f
        self.start_offset = start_offset
        self.should_close_buf = False
        self.should_close_file = False
        if filename is not None and f is None:
            self.f = open(filename, mode)
            f = open(filename, mode)
            self.should_close_file = True
        if f is not None:
            self.buf = self.get_buf_from_file(f)
            self.should_close_buf = True
            if not filename and hasattr(f, 'name'):
                self.filename = f.name
        self.cached_objects = { }
        self
        self
        self
        self
        if self.buf:
            
            try:
                self.read_pdf_info()
            except PdfFormatError:
                self.close()
                raise

        else:
            self.file_size_total = 0
            self.file_size_this = 0
            self.root = PdfDict()
            self.root_ref = None
            self.info = PdfDict()
            self.info_ref = None
            self.page_tree_root = PdfDict()
            self.pages = []
            self.orig_pages = []
            self.pages_ref = None
            self.last_xref_section_offset = None
            self.trailer_dict = { }
            self.xref_table = XrefTable()
        self.xref_table.reading_finished = True
        if f:
            self.seek_end()
            return None

    
    def __enter__(self):
        return self

    
    def __exit__(self, *args):
        self.close()

    
    def start_writing(self):
        self.close_buf()
        self.seek_end()

    
    def close_buf(self):
        if isinstance(self.buf, memoryview):
            self.buf.release()
        elif isinstance(self.buf, mmap.mmap):
            self.buf.close()
        self.buf = None

    
    def close(self):
        if self.should_close_buf:
            self.close_buf()
        if self.f is not None:
            if self.should_close_file:
                self.f.close()
                self.f = None
                return None
            return None

    
    def seek_end(self):
        if self.f is None:
            raise AssertionError
        self.f.seek(0, os.SEEK_END)

    
    def write_header(self):
        if self.f is None:
            raise AssertionError
        self.f.write(b'%PDF-1.4\n')

    
    def write_comment(self, s):
        if self.f is None:
            raise AssertionError
        self.f.write(f'''% {s}\n'''.encode())

    
    def write_catalog(self):
        if self.f is None:
            raise AssertionError
        self.del_root()
        self.root_ref = self.next_object_id(self.f.tell())
        self.pages_ref = self.next_object_id(0)
        self.rewrite_pages()
        self.write_obj(self.root_ref, Type = PdfName(b'Catalog'), Pages = self.pages_ref)
        self.write_obj(self.pages_ref, Type = PdfName(b'Pages'), Count = len(self.pages), Kids = self.pages)
        return self.root_ref

    
    def rewrite_pages(self):
        b'''Parent'''
        pages_tree_nodes_to_delete = []
        for i, page_ref in enumerate(self.orig_pages):
            page_info = self.cached_objects[page_ref]
            del self.xref_table[page_ref.object_id]
            pages_tree_nodes_to_delete.append(page_info[PdfName(b'Parent')])
            if page_ref not in self.pages:
                continue
            stringified_page_info = { }
            for key, value in page_info.items():
                stringified_page_info[key.name_as_str()] = value
            stringified_page_info['Parent'] = self.pages_ref
            new_page_ref = (None,)(*{
                **stringified_page_info })
            for j, cur_page_ref in enumerate(self.pages):
                while not cur_page_ref == page_ref:
                    pass
                self.pages[j] = new_page_ref
        for pages_tree_node_ref in pages_tree_nodes_to_delete:
            while not pages_tree_node_ref:
                pass
            pages_tree_node = self.cached_objects[pages_tree_node_ref]
            if pages_tree_node_ref.object_id in self.xref_table:
                del self.xref_table[pages_tree_node_ref.object_id]
            pages_tree_node_ref = pages_tree_node.get(b'Parent', None)
        self.orig_pages = []

    
    def write_xref_and_trailer(self, new_root_ref = None):
        if self.f is None:
            raise AssertionError
        if new_root_ref:
            self.del_root()
            self.root_ref = new_root_ref
        if self.info:
            self.info_ref = self.write_obj(None, self.info)
        start_xref = self.xref_table.write(self.f)
        num_entries = len(self.xref_table)
        trailer_dict = {
            b'Size': num_entries,
            b'Root': self.root_ref }
        if self.last_xref_section_offset is not None:
            trailer_dict[b'Prev'] = self.last_xref_section_offset
        if self.info:
            trailer_dict[b'Info'] = self.info_ref
        self.last_xref_section_offset = start_xref
        self.f.write(b'trailer\n' + bytes(PdfDict(trailer_dict)) + b'\nstartxref\n%d\n%%%%EOF' % start_xref)

    
    def write_page(self, ref, *objs, **dict_obj):
        '''Type'''
        obj_ref = self.pages[ref] if isinstance(ref, int) else ref
        if 'Type' not in dict_obj:
            dict_obj['Type'] = PdfName(b'Page')
        if 'Parent' not in dict_obj:
            dict_obj['Parent'] = self.pages_ref
        # unsupported CALL_INTRINSIC_1 6
        return self.write_obj(*{
            **dict_obj })
    # WARNING: Decompyle incomplete

    
    def write_obj(self, ref, *objs, **dict_obj):
        if self.f is None:
            raise AssertionError
        f = self.f
        if ref is None:
            ref = self.next_object_id(f.tell())
        else:
            self.xref_table[ref.object_id] = (f.tell(), ref.generation)
        bytes(IndirectObjectDef(ref()))
        stream = dict_obj.pop('stream', None)
        if stream is not None:
            dict_obj['Length'] = len(stream)
        if dict_obj:
            f.write(pdf_repr(dict_obj))
        for obj in objs:
            f.write(pdf_repr(obj))
        if stream is not None:
            f.write(b'stream\n')
            f.write(stream)
            f.write(b'\nendstream\n')
        f.write(b'endobj\n')
        return ref

    
    def del_root(self):
        if self.root_ref is None:
            return None
        del self.xref_table[self.root_ref.object_id]
        del self.xref_table[self.root[b'Pages'].object_id]

    get_buf_from_file = (lambda f: if hasattr(f, 'getbuffer'):
f.getbuffer()if hasattr(f, 'getvalue'):
f.getvalue()try:
mmap.mmap(f.fileno(), 0, access = mmap.ACCESS_READ)except ValueError:
b'')()
    
    def read_pdf_info(self):
        if self.buf is None:
            raise AssertionError
        self.file_size_total = len(self.buf)
        self.file_size_this = self.file_size_total - self.start_offset
        self.read_trailer()
        check_format_condition(self.trailer_dict.get(b'Root') is not None, 'Root is missing')
        self.root_ref = self.trailer_dict[b'Root']
        if self.root_ref is None:
            raise AssertionError
        self.info_ref = self.trailer_dict.get(b'Info', None)
        self.root = PdfDict(self.read_indirect(self.root_ref))
        if self.info_ref is None:
            self.info = PdfDict()
        else:
            self.info = PdfDict(self.read_indirect(self.info_ref))
        check_format_condition(b'Type' in self.root, '/Type missing in Root')
        check_format_condition(self.root[b'Type'] == b'Catalog', '/Type in Root is not /Catalog')
        check_format_condition(self.root.get(b'Pages') is not None, '/Pages missing in Root')
        check_format_condition(isinstance(self.root[b'Pages'], IndirectReference), '/Pages in Root is not an indirect reference')
        self.pages_ref = self.root[b'Pages']
        if self.pages_ref is None:
            raise AssertionError
        self.page_tree_root = self.read_indirect(self.pages_ref)
        self.pages = self.linearize_page_tree(self.page_tree_root)
        self.orig_pages = self.pages[slice(None, None, None)]

    
    def next_object_id(self, offset = None):
        
        try:
            reference = IndirectReference(max(self.xref_table.keys()) + 1, 0)
        except ValueError:
            reference = IndirectReference(1, 0)

        if offset is not None:
            self.xref_table[reference.object_id] = (offset, 0)
        return reference

    delimiter = b'[][()<>{}/%]'
    delimiter_or_ws = b'[][()<>{}/%\\000\\011\\012\\014\\015\\040]'
    whitespace = b'[\\000\\011\\012\\014\\015\\040]'
    whitespace_or_hex = b'[\\000\\011\\012\\014\\015\\0400-9a-fA-F]'
    whitespace_optional = whitespace + b'*'
    whitespace_mandatory = whitespace + b'+'
    whitespace_optional_no_nl = b'[\\000\\011\\014\\040]*'
    newline_only = b'[\\r\\n]+'
    newline = whitespace_optional_no_nl + newline_only + whitespace_optional_no_nl
    re_trailer_end = re.compile(whitespace_mandatory + b'trailer' + whitespace_optional + b'<<(.*>>)' + newline + b'startxref' + newline + b'([0-9]+)' + newline + b'%%EOF' + whitespace_optional + b'$', re.DOTALL)
    re_trailer_prev = re.compile(whitespace_optional + b'trailer' + whitespace_optional + b'<<(.*?>>)' + newline + b'startxref' + newline + b'([0-9]+)' + newline + b'%%EOF' + whitespace_optional, re.DOTALL)
    
    def read_trailer(self):
        if self.buf is None:
            raise AssertionError
        search_start_offset = len(self.buf) - 16384
        if search_start_offset < self.start_offset:
            search_start_offset = self.start_offset
        m = self.re_trailer_end.search(self.buf, search_start_offset)
        check_format_condition(m is not None, 'trailer end not found')
        last_match = m
        while m:
            last_match = m
            m = self.re_trailer_end.search(self.buf, m.start() + 16)
        if not m:
            m = last_match
        if m is None:
            raise AssertionError
        trailer_data = m.group(1)
        self.last_xref_section_offset = int(m.group(2))
        self.trailer_dict = self.interpret_trailer(trailer_data)
        self.xref_table = XrefTable()
        self.read_xref_table(xref_section_offset = self.last_xref_section_offset)
        if b'Prev' in self.trailer_dict:
            self.read_prev_trailer(self.trailer_dict[b'Prev'])
            return None

    
    def read_prev_trailer(self, xref_section_offset, processed_offsets = None):
        if self.buf is None:
            raise AssertionError
        trailer_offset = self.read_xref_table(xref_section_offset = xref_section_offset)
        m = self.re_trailer_prev.search(self.buf[trailer_offset:trailer_offset + 16384])
        check_format_condition(m is not None, 'previous trailer not found')
        if m is None:
            raise AssertionError
        trailer_data = m.group(1)
        check_format_condition(int(m.group(2)) == xref_section_offset, "xref section offset in previous trailer doesn't match what was expected")
        trailer_dict = self.interpret_trailer(trailer_data)
        if b'Prev' in trailer_dict:
            if processed_offsets is None:
                processed_offsets = []
            processed_offsets.append(xref_section_offset)
            check_format_condition(trailer_dict[b'Prev'] not in processed_offsets, 'trailer loop found')
            self.read_prev_trailer(trailer_dict[b'Prev'], processed_offsets)
            return None

    re_whitespace_optional = re.compile(whitespace_optional)
    re_name = re.compile(whitespace_optional + b"/([!-$&'*-.0-;=?-Z\\\\^-z|~]+)(?=" + delimiter_or_ws + b')')
    re_dict_start = re.compile(whitespace_optional + b'<<')
    re_dict_end = re.compile(whitespace_optional + b'>>' + whitespace_optional)
    interpret_trailer = (lambda cls, trailer_data: trailer = { }offset = 0m = cls.re_name.match(trailer_data, offset)if not m:
m = cls.re_dict_end.match(trailer_data, offset)check_format_condition(m is not None and m.end() == len(trailer_data), 'name not found in trailer, remaining data: ' + repr(trailer_data[offset:]))else:
key = cls.interpret_name(m.group(1))if not isinstance(key, bytes):
raise AssertionErrorvalue, value_offset = cls.get_value(trailer_data, m.end())trailer[key] = valueif value_offset is None:
passelse:
offset = value_offsetcheck_format_condition(b'Size' in trailer and isinstance(trailer[b'Size'], int), '/Size not in trailer or not an integer')check_format_condition(b'Root' in trailer and isinstance(trailer[b'Root'], IndirectReference), '/Root not in trailer or not an indirect reference')trailer)()
    re_hashes_in_name = re.compile(b'([^#]*)(#([0-9a-fA-F]{2}))?')
    interpret_name = (lambda cls, raw, as_text = False: name = b''for m in cls.re_hashes_in_name.finditer(raw):
while m.group(3):
name += m.group(1) + bytearray.fromhex(m.group(3).decode('us-ascii'))name += m.group(1)if as_text:
name.decode('utf-8')bytes(name))()
    re_null = re.compile(whitespace_optional + b'null(?=' + delimiter_or_ws + b')')
    re_true = re.compile(whitespace_optional + b'true(?=' + delimiter_or_ws + b')')
    re_false = re.compile(whitespace_optional + b'false(?=' + delimiter_or_ws + b')')
    re_int = re.compile(whitespace_optional + b'([-+]?[0-9]+)(?=' + delimiter_or_ws + b')')
    re_real = re.compile(whitespace_optional + b'([-+]?([0-9]+\\.[0-9]*|[0-9]*\\.[0-9]+))(?=' + delimiter_or_ws + b')')
    re_array_start = re.compile(whitespace_optional + b'\\[')
    re_array_end = re.compile(whitespace_optional + b']')
    re_string_hex = re.compile(whitespace_optional + b'<(' + whitespace_or_hex + b'*)>')
    re_string_lit = re.compile(whitespace_optional + b'\\(')
    re_indirect_reference = re.compile(whitespace_optional + b'([-+]?[0-9]+)' + whitespace_mandatory + b'([-+]?[0-9]+)' + whitespace_mandatory + b'R(?=' + delimiter_or_ws + b')')
    re_indirect_def_start = re.compile(whitespace_optional + b'([-+]?[0-9]+)' + whitespace_mandatory + b'([-+]?[0-9]+)' + whitespace_mandatory + b'obj(?=' + delimiter_or_ws + b')')
    re_indirect_def_end = re.compile(whitespace_optional + b'endobj(?=' + delimiter_or_ws + b')')
    re_comment = re.compile(b'(' + whitespace_optional + b'%[^\\r\\n]*' + newline + b')*')
    re_stream_start = re.compile(whitespace_optional + b'stream\\r?\\n')
    re_stream_end = re.compile(whitespace_optional + b'endstream(?=' + delimiter_or_ws + b')')
    get_value = (lambda cls, data, offset, expect_indirect = None, max_nesting = -1: if max_nesting == 0:
(None, None)m = cls.re_comment.match(data, offset)if m:
offset = m.end()m = cls.re_indirect_def_start.match(data, offset)if m:
check_format_condition(int(m.group(1)) > 0, 'indirect object definition: object ID must be greater than 0')check_format_condition(int(m.group(2)) >= 0, 'indirect object definition: generation must be non-negative')check_format_condition(expect_indirect is None or expect_indirect == IndirectReference(int(m.group(1)), int(m.group(2))), 'indirect object definition different than expected')object, object_offset = cls.get_value(data, m.end(), max_nesting = max_nesting - 1)if object_offset is None:
(object, None)m = cls.re_indirect_def_end.match(data, object_offset)check_format_condition(m is not None, 'indirect object definition end not found')if m is None:
raise AssertionError(object, m.end())check_format_condition(not expect_indirect, 'indirect object definition not found')m = cls.re_indirect_reference.match(data, offset)if m:
check_format_condition(int(m.group(1)) > 0, 'indirect object reference: object ID must be greater than 0')check_format_condition(int(m.group(2)) >= 0, 'indirect object reference: generation must be non-negative')(IndirectReference(int(m.group(1)), int(m.group(2))), m.end())m = cls.re_dict_start.match(data, offset)if m:
offset = m.end()result = { }m = cls.re_dict_end.match(data, offset)current_offset = offsetwhile not m:
if current_offset is None:
raise AssertionErrorkey, current_offset = cls.get_value(data, current_offset, max_nesting = max_nesting - 1)if current_offset is None:
(result, None)value, current_offset = cls.get_value(data, current_offset, max_nesting = max_nesting - 1)result[key] = valueif current_offset is None:
(result, None)m = cls.re_dict_end.match(data, current_offset)current_offset = m.end()m = cls.re_stream_start.match(data, current_offset)if m:
stream_len = result.get(b'Length')if not (stream_len is not None) or not isinstance(stream_len, int):
msg = f'''bad or missing Length in stream dict ({stream_len})'''raise PdfFormatError(msg)stream_data = bytes(data[m.end():m.end() + stream_len])m = cls.re_stream_end.match(data, m.end() + stream_len)check_format_condition(m is not None, 'stream end not found')if m is None:
raise AssertionErrorcurrent_offset = m.end()(PdfStream(PdfDict(result), stream_data), current_offset)(PdfDict(result), current_offset)m = cls.re_array_start.match(data, offset)if m:
offset = m.end()results = []m = cls.re_array_end.match(data, offset)current_offset = offsetwhile not m:
if current_offset is None:
raise AssertionErrorvalue, current_offset = cls.get_value(data, current_offset, max_nesting = max_nesting - 1)results.append(value)if current_offset is None:
(results, None)m = cls.re_array_end.match(data, current_offset)(results, m.end())m = cls.re_null.match(data, offset)if m:
(None, m.end())m = cls.re_true.match(data, offset)if m:
(True, m.end())m = cls.re_false.match(data, offset)if m:
(False, m.end())m = cls.re_name.match(data, offset)if m:
(PdfName(cls.interpret_name(m.group(1))), m.end())m = cls.re_int.match(data, offset)if m:
(int(m.group(1)), m.end())m = cls.re_real.match(data, offset)if m:
(float(m.group(1)), m.end())m = cls.re_string_hex.match(data, offset)if m:
hex_string = (lambda .0: for b in .0:
while not b in b'0123456789abcdefABCDEF':
passb.0)(m.group(1)())
            if len(hex_string) % 2 == 1:
                hex_string.append(ord(b'0'))
            return (bytearray.fromhex(hex_string.decode('us-ascii')), m.end())
        m = cls.re_string_lit.match(data, offset)
        if m:
            return cls.get_literal_string(data, m.end())
        msg = f'''unrecognized object: {repr(data[offset:offset + 32])}'''
        raise PdfFormatError(msg)
)()
    re_lit_str_token = re.compile(b'(\\\\[nrtbf()\\\\])|(\\\\[0-9]{1,3})|(\\\\(\\r\\n|\\r|\\n))|(\\r\\n|\\r|\\n)|(\\()|(\\))')
    escaped_chars = {
        b'n': b'\n',
        b'r': b'\r',
        b't': b'\t',
        b'b': b'\x08',
        b'f': b'\x0c',
        b'(': b'(',
        b')': b')',
        b'\\': b'\\',
        ord(b'n'): b'\n',
        ord(b'r'): b'\r',
        ord(b't'): b'\t',
        ord(b'b'): b'\x08',
        ord(b'f'): b'\x0c',
        ord(b'('): b'(',
        ord(b')'): b')',
        ord(b'\\'): b'\\' }
    get_literal_string = (lambda cls, data, offset: nesting_depth = 0result = bytearray()for m in cls.re_lit_str_token.finditer(data, offset):
result.extend(data[offset:m.start()])if m.group(1):
result.extend(cls.escaped_chars[m.group(1)[1]])elif m.group(2):
result.append(int(m.group(2)[slice(1, None, None)], 8))elif m.group(3):
passelif m.group(5):
result.extend(b'\n')elif m.group(6):
result.extend(b'(')nesting_depth += 1elif m.group(7):
if nesting_depth == 0:
(bytes(result), m.end())result.extend(b')')nesting_depth -= 1offset = m.end()msg = 'unfinished literal string'raise PdfFormatError(msg))()
    re_xref_section_start = re.compile(whitespace_optional + b'xref' + newline)
    re_xref_subsection_start = re.compile(whitespace_optional + b'([0-9]+)' + whitespace_mandatory + b'([0-9]+)' + whitespace_optional + newline_only)
    re_xref_entry = re.compile(b'([0-9]{10}) ([0-9]{5}) ([fn])( \\r| \\n|\\r\\n)')
    
    def read_xref_table(self, xref_section_offset):
        if self.buf is None:
            raise AssertionError
        subsection_found = False
        m = self.re_xref_section_start.match(self.buf, xref_section_offset + self.start_offset)
        check_format_condition(m is not None, 'xref section start not found')
        if m is None:
            raise AssertionError
        offset = m.end()
        m = self.re_xref_subsection_start.match(self.buf, offset)
        if not m:
            check_format_condition(subsection_found, 'xref subsection start not found')
            return offset
        subsection_found = True
        offset = m.end()
        first_object = int(m.group(1))
        num_objects = int(m.group(2))
        for i in range(first_object, first_object + num_objects):
            m = self.re_xref_entry.match(self.buf, offset)
            check_format_condition(m is not None, 'xref entry not found')
            if m is None:
                raise AssertionError
            offset = m.end()
            is_free = m.group(3) == b'f'
            if is_free:
                continue
            generation = int(m.group(2))
            new_entry = (int(m.group(1)), generation)
            if not i not in self.xref_table:
                continue
            self.xref_table[i] = new_entry

    
    def read_indirect(self, ref, max_nesting = -1):
        offset, generation = self.xref_table[ref[0]]
        check_format_condition(generation == ref[1], f'''expected to find generation {ref[1]} for object ID {ref[0]} in xref table, instead found generation {generation} at offset {offset}''')
        if self.buf is None:
            raise AssertionError
        value = offset + self.start_offset(None, IndirectReference, expect_indirect = ref(), max_nesting = max_nesting)[0]
        self.cached_objects[ref] = value
        return value

    
    def linearize_page_tree(self, node = None):
        page_node = node if node is not None else self.page_tree_root
        check_format_condition(page_node[b'Type'] == b'Pages', '/Type of page tree node is not /Pages')
        pages = []
        for kid in page_node[b'Kids']:
            kid_object = self.read_indirect(kid)
            while kid_object[b'Type'] == b'Page':
                pages.append(kid)
            pages.extend(self.linearize_page_tree(node = kid_object))
        return pages


