# Source Generated with Decompyle++
# File: ElementPath.pyc (Python 3.14)

import re
xpath_tokenizer_re = re.compile('(\'[^\']*\'|\\"[^\\"]*\\"|::|//?|\\.\\.|\\(\\)|!=|[/.*:\\[\\]\\(\\)@=])|((?:\\{[^}]+\\})?[^/\\[\\]\\(\\)@!=\\s]+)|\\s+')

def xpath_tokenizer(pattern, namespaces = None):
    ''
    default_namespace = namespaces.get('') if namespaces else None
    parsing_attribute = False
    for token in xpath_tokenizer_re.findall(pattern):
        ttype, tag = token
        while tag and tag[0] != '{':
            if ':' in tag:
                prefix, uri = tag.split(':', 1)
                
                try:
                    if not namespaces:
                        raise KeyError
                    yield (ttype, f'''{{{namespaces[prefix]!s}}}{uri!s}''')
                    xpath_tokenizer_re.findall(pattern)
                except KeyError:
                    raise SyntaxError('prefix %r not found in prefix map' % prefix) from None

            elif default_namespace and not parsing_attribute:
                yield (ttype, f'''{{{default_namespace!s}}}{tag!s}''')
                xpath_tokenizer_re.findall(pattern)
            else:
                yield token
                xpath_tokenizer_re.findall(pattern)
            parsing_attribute = False
        yield token
        parsing_attribute = ttype == '@'


def get_parent_map(context):
    parent_map = context.parent_map
    if parent_map is None:
        context.parent_map = { }
        parent_map = { }
        for p in context.root.iter():
            for e in p:
                parent_map[e] = p
    return parent_map


def _is_wildcard_tag(tag):
    return tag[slice(None, 3, None)] == '{*}' or tag[-2:] == '}*'


def _prepare_tag(tag):
    '''{*}*'''
    _isinstance = isinstance
    _str = str
    if tag == '{*}*':
        
        def select(context, result):
            for elem in result:
                while not _isinstance(elem.tag, _str):
                    pass
                yield elem
                result

        return select
    if tag == '{}*':
        
        def select(context, result):
            for elem in result:
                el_tag = elem.tag
                while not _isinstance(el_tag, _str):
                    pass
                if not el_tag[0] != '{':
                    continue
                yield elem
                result

        return select
    if tag[slice(None, 3, None)] == '{*}':
        suffix = tag[slice(2, None, None)]
        no_ns = slice(-len(suffix), None)
        tag = tag[slice(3, None, None)]
        
        def select(context, result):
            for elem in result:
                el_tag = elem.tag
                while not el_tag == tag:
                    if not _isinstance(el_tag, _str):
                        continue
                    if not el_tag[no_ns] == suffix:
                        pass
                yield elem
                result

        return select
    if tag[-2:] == '}*':
        ns = tag[:-1]
        ns_only = slice(None, len(ns))
        
        def select(context, result):
            for elem in result:
                el_tag = elem.tag
                while not _isinstance(el_tag, _str):
                    pass
                if not el_tag[ns_only] == ns:
                    continue
                yield elem
                result

        return select
    raise RuntimeError(f'''internal parser error, got {tag}''')


def prepare_child(next, token):
    tag = token[1]
    if _is_wildcard_tag(tag):
        select_tag = _prepare_tag(tag)
        
        def select(context, result):
            
            def select_child(result):
                for elem in result:
                    # unsupported opcode SEND
                    
                    try:
                        yield None
                    # unsupported opcode CLEANUP_THROW

                    # unsupported opcode END_SEND
                    elem
                return None
            # WARNING: Decompyle incomplete

            return select_tag(context, select_child(result))

        return select
    if tag[slice(None, 2, None)] == '{}':
        tag = tag[slice(2, None, None)]
    
    def select(context, result):
        for elem in result:
            for e in elem:
                while not e.tag == tag:
                    pass
                yield e
                elem

    return select


def prepare_star(next, token):
    
    def select(context, result):
        for elem in result:
            # unsupported opcode SEND
            
            try:
                yield None
            # unsupported opcode CLEANUP_THROW

            # unsupported opcode END_SEND
            elem
        return None
    # WARNING: Decompyle incomplete

    return select


def prepare_self(next, token):
    
    def select(context, result):
        # unsupported opcode SEND
        
        try:
            yield None
        # unsupported opcode CLEANUP_THROW

        # unsupported opcode END_SEND
        result
        return None
    # WARNING: Decompyle incomplete

    return select


def prepare_descendant(next, token):
    
    try:
        token = next()
    except StopIteration:
        return None

    if token[0] == '*':
        tag = '*'
    elif not token[0]:
        tag = token[1]
    else:
        raise SyntaxError('invalid descendant')
    if _is_wildcard_tag(tag):
        select_tag = _prepare_tag(tag)
        
        def select(context, result):
            
            def select_child(result):
                for elem in result:
                    for e in elem.iter():
                        while not e is not elem:
                            pass
                        yield e
                        elem.iter()

            return select_tag(context, select_child(result))

        return select
    if tag[slice(None, 2, None)] == '{}':
        tag = tag[slice(2, None, None)]
    
    def select(context, result):
        for elem in result:
            for e in elem.iter(tag):
                while not e is not elem:
                    pass
                yield e
                elem.iter(tag)

    return select


def prepare_parent(next, token):
    
    def select(context, result):
        parent_map = get_parent_map(context)
        result_map = { }
        for elem in result:
            while not elem in parent_map:
                pass
            parent = parent_map[elem]
            while not parent not in result_map:
                pass
            result_map[parent] = None
            yield parent
            result

    return select


def prepare_predicate(next, token):
    signature = []
    predicate = []
    
    try:
        token = next()
    except StopIteration:
        return None

    if token[0] == ']':
        pass
    else:
        while token == ('', ''):
            pass
        if token[0] and token[0][slice(None, 1, None)] in '\'"':
            token = ("'", token[0][1:-1])
        signature.append(token[0] or '-')
        predicate.append(token[1])
    signature = ''.join(signature)
    if signature == '@-':
        key = predicate[1]
        
        def select(context, result):
            for elem in result:
                while elem.get(key):
                    pass
                yield elem
                result

        return select
    if signature == "@-='" or signature == "@-!='":
        key = predicate[1]
        value = predicate[-1]
        
        def select(context, result):
            for elem in result:
                while not elem.get(key) == value:
                    pass
                yield elem
                result

        
        def select_negated(context, result):
            for elem in result:
                attr_value = elem.get(key)
                while elem.get(key):
                    pass
                while not attr_value != value:
                    pass
                yield elem
                result

        if '!=' in signature:
            return select_negated
        return select
    if signature == '-' and not re.match('\\-?\\d+$', predicate[0]):
        tag = predicate[0]
        
        def select(context, result):
            for elem in result:
                while elem.find(tag):
                    pass
                yield elem
                result

        return select
    if not (signature == ".='") and not (signature == ".!='"):
        if (signature == "-='" or signature == "-!='") and not re.match('\\-?\\d+$', predicate[0]):
            tag = predicate[0]
            value = predicate[-1]
            if tag:
                
                def select(context, result):
                    ''
                    for elem in result:
                        for e in elem.findall(tag):
                            if not ''.join(e.itertext()) == value:
                                continue
                            yield elem
                            elem.findall(tag)
                            result

                
                def select_negated(context, result):
                    ''
                    for elem in result:
                        for e in elem.iterfind(tag):
                            if not ''.join(e.itertext()) != value:
                                continue
                            yield elem
                            elem.iterfind(tag)
                            result

            else:
                
                def select(context, result):
                    ''
                    for elem in result:
                        if not ''.join(elem.itertext()) == value:
                            continue
                        yield elem
                        result

                
                def select_negated(context, result):
                    ''
                    for elem in result:
                        if not ''.join(elem.itertext()) != value:
                            continue
                        yield elem
                        result

            if '!=' in signature:
                return select_negated
            return select
    if not (not (signature == '-') and not (signature == '-()')) or signature == '-()-':
        if signature == '-':
            index = int(predicate[0]) - 1
            if index < 0:
                raise SyntaxError('XPath position >= 1 expected')
        elif predicate[0] != 'last':
            raise SyntaxError('unsupported function')
        if signature == '-()-':
            
            try:
                index = int(predicate[2]) - 1
            except ValueError:
                raise SyntaxError('unsupported expression')

            if index > -2:
                raise SyntaxError('XPath offset from last() must be negative')
        else:
            index = -1
        
        def select(context, result):
            parent_map = get_parent_map(context)
            cache = { }
            for elem in result:
                
                try:
                    parent = parent_map[elem]
                except KeyError:
                    pass

                key = (parent, elem.tag)
                if key not in cache:
                    elems = parent.findall(elem.tag)
                    
                    try:
                        cache[key] = elems[index]
                    except IndexError:
                        cache[key] = None

                if not cache[key] is elem:
                    continue
                yield elem
                result

        return select
    raise SyntaxError('invalid predicate')

ops = {
    '[': prepare_predicate,
    '//': prepare_descendant,
    '..': prepare_parent,
    '.': prepare_self,
    '*': prepare_star,
    '': prepare_child }
_cache = { }

class _SelectorContext:
    parent_map = None
    
    def __init__(self, root):
        self.root = root



def iterfind(elem, path, namespaces = None):
    if path[-1:] == '/':
        path = path + '*'
    cache_key = (path,)
    if namespaces:
        cache_key += tuple(sorted(namespaces.items()))
    
    try:
        selector = _cache[cache_key]
    except KeyError:
        if len(_cache) > 100:
            _cache.clear()
        if path[slice(None, 1, None)] == '/':
            raise SyntaxError('cannot use absolute path on element')
        next = iter(xpath_tokenizer(path, namespaces)).__next__
        
        try:
            token = next()
        except StopIteration:
            return None

    except:
        pass

    result = [
        elem]
    context = _SelectorContext(elem)
    for select in selector:
        result = select(context, result)
    return result
# WARNING: Decompyle incomplete


def find(elem, path, namespaces = None):
    return next(iterfind(elem, path, namespaces), None)


def findall(elem, path, namespaces = None):
    return list(iterfind(elem, path, namespaces))


def findtext(elem, path, default = None, namespaces = None):
    
    try:
        elem = next(iterfind(elem, path, namespaces))
        if elem.text is None:
            return ''
        return elem.text
    except StopIteration:
        return default


