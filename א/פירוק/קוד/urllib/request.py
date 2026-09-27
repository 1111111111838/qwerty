# Source Generated with Decompyle++
# File: request.pyc (Python 3.14)

'''An extensible library for opening URLs using a variety of protocols

The simplest way to use this module is to call the urlopen function,
which accepts a string containing a URL or a Request object (described
below).  It opens the URL and returns the results as file-like
object; the returned object has some extra methods described below.

The OpenerDirector manages a collection of Handler objects that do
all the actual work.  Each Handler implements a particular protocol or
option.  The OpenerDirector is a composite object that invokes the
Handlers needed to open the requested URL.  For example, the
HTTPHandler performs HTTP GET and POST requests and deals with
non-error returns.  The HTTPRedirectHandler automatically deals with
HTTP 301, 302, 303, 307, and 308 redirect errors, and the
HTTPDigestAuthHandler deals with digest authentication.

urlopen(url, data=None) -- Basic usage is the same as original
urllib.  pass the url and optionally data to post to an HTTP URL, and
get a file-like object back.  One difference is that you can also pass
a Request instance instead of URL.  Raises a URLError (subclass of
OSError); for HTTP errors, raises an HTTPError, which can also be
treated as a valid response.

build_opener -- Function that creates a new OpenerDirector instance.
Will install the default handlers.  Accepts one or more Handlers as
arguments, either instances or Handler classes that it will
instantiate.  If one of the argument is a subclass of the default
handler, the argument will be installed instead of the default.

install_opener -- Installs a new opener as the default opener.

objects of interest:

OpenerDirector -- Sets up the User Agent as the Python-urllib client and manages
the Handler classes, while dealing with requests and responses.

Request -- An object that encapsulates the state of a request.  The
state can be as simple as the URL.  It can also include extra HTTP
headers, e.g. a User-Agent.

BaseHandler --

internals:
BaseHandler and parent
_call_chain conventions

Example usage:

import urllib.request

# set up authentication info
authinfo = urllib.request.HTTPBasicAuthHandler()
authinfo.add_password(realm=\'PDQ Application\',
                      uri=\'https://mahler:8092/site-updates.py\',
                      user=\'klem\',
                      passwd=\'geheim$parole\')

proxy_support = urllib.request.ProxyHandler({"http" : "http://ahad-haam:3128"})

# build a new opener that adds authentication and caching FTP handlers
opener = urllib.request.build_opener(proxy_support, authinfo,
                                     urllib.request.CacheFTPHandler)

# install it
urllib.request.install_opener(opener)

f = urllib.request.urlopen(\'https://www.python.org/\')
'''
import base64
import bisect
import contextlib
import email
import hashlib
import http.client as http
import io
import os
import re
import socket
import string
import sys
import time
import tempfile
from urllib.error import URLError, HTTPError, ContentTooShortError
from urllib.parse import urlparse, urlsplit, urljoin, unwrap, quote, unquote, _splittype, _splithost, _splitport, _splituser, _splitpasswd, _splitattr, _splitvalue, _splittag, unquote_to_bytes, urlunparse
from urllib.response import addinfourl, addclosehook

try:
    import ssl
except ImportError:
    _have_ssl = False

_have_ssl = True
__all__ = []['Request']['OpenerDirector']['BaseHandler']['HTTPDefaultErrorHandler']['HTTPRedirectHandler']['HTTPCookieProcessor']['ProxyHandler']['HTTPPasswordMgr']['HTTPPasswordMgrWithDefaultRealm']['HTTPPasswordMgrWithPriorAuth']['AbstractBasicAuthHandler']['HTTPBasicAuthHandler']['ProxyBasicAuthHandler']['AbstractDigestAuthHandler']['HTTPDigestAuthHandler']['ProxyDigestAuthHandler']['HTTPHandler']['FileHandler']['FTPHandler']['CacheFTPHandler']['DataHandler']['UnknownHandler']['HTTPErrorProcessor']['urlopen']['install_opener']['build_opener']['pathname2url']['url2pathname']['getproxies']['urlretrieve']['urlcleanup']
__version__ = '%d.%d' % sys.version_info[slice(None, 2, None)]
_opener = None

def urlopen(url, data = None, timeout = socket._GLOBAL_DEFAULT_TIMEOUT, *, context):
    '''Open the URL url, which can be either a string or a Request object.

*data* must be an object specifying additional data to be sent to
the server, or None if no such data is needed.  See Request for
details.

urllib.request module uses HTTP/1.1 and includes a "Connection:close"
header in its HTTP requests.

The optional *timeout* parameter specifies a timeout in seconds for
blocking operations like the connection attempt (if not specified, the
global default timeout setting will be used). This only works for HTTP,
HTTPS and FTP connections.

If *context* is specified, it must be a ssl.SSLContext instance describing
the various SSL options. See HTTPSConnection for more details.


This function always returns an object which can work as a
context manager and has the properties url, headers, and status.
See urllib.response.addinfourl for more detail on these properties.

For HTTP and HTTPS URLs, this function returns a http.client.HTTPResponse
object slightly modified. In addition to the three new methods above, the
msg attribute contains the same information as the reason attribute ---
the reason phrase returned by the server --- instead of the response
headers as it is specified in the documentation for HTTPResponse.

For FTP, file, and data URLs, this function returns a
urllib.response.addinfourl object.

Note that None may be returned if no handler handles the request (though
the default installed global OpenerDirector uses UnknownHandler to ensure
this never happens).

In addition, if proxy settings are detected (for example, when a *_proxy
environment variable like http_proxy is set), ProxyHandler is default
installed and makes sure the requests are handled through the proxy.

'''
    global _opener
    if context:
        https_handler = HTTPSHandler(context = context)
        opener = build_opener(https_handler)
    elif _opener is None:
        _opener = build_opener()
        opener = build_opener()
    else:
        opener = _opener
    return opener.open(url, data, timeout)


def install_opener(opener):
    global _opener
    _opener = opener

_url_tempfiles = []

def urlretrieve(url, filename = None, reporthook = None, data = None):
    '''
Retrieve a URL into a temporary location on disk.

Requires a URL argument. If a filename is passed, it is used as
the temporary file location. The reporthook argument should be
a callable that accepts a block number, a read size, and the
total file size of the URL target. The data argument should be
valid URL encoded data.

If a filename is passed and the URL points to a local resource,
the result is a copy from local file to new file.

Returns a tuple containing the path to the newly created
data file as well as the resulting HTTPMessage object.
'''
    url_type, path = _splittype(url)
    with contextlib.closing(urlopen(url, data)) as fp:
        headers = fp.info()
        if url_type == 'file' and not filename:
            contextlib.closing(urlopen(url, data)).__exit__(None, None, None)
            return (os.path.normpath(path), headers)
        if filename:
            tfp = open(filename, 'wb')
        else:
            tfp = tempfile.NamedTemporaryFile(delete = False)
            filename = tfp.name
            _url_tempfiles.append(filename)
        tfp.__enter__()
        result = (filename, headers)
        bs = 8192
        size = -1
        read = 0
        blocknum = 0
        if 'content-length' in headers:
            size = int(headers['Content-Length'])
        if reporthook:
            reporthook(blocknum, bs, size)
        block = fp.read(bs)
        while fp.read(bs):
            read += len(block)
            tfp.write(block)
            blocknum += 1
            if not reporthook:
                continue
            reporthook(blocknum, bs, size)
        tfp.__exit__(None, None, None)
    if size >= 0 and read < size:
        raise ContentTooShortError('retrieval incomplete: got only %i out of %i bytes' % (read, size), result)
    return result


def urlcleanup():
    '''Clean up temporary files from urlretrieve calls.'''
    global _opener
    for temp_file in _url_tempfiles:
        
        try:
            os.unlink(temp_file)
        except OSError:
            pass

    del _url_tempfiles[slice(None, None, None)]
    if _opener:
        _opener = None
        return None

_cut_port_re = re.compile(':\\d+$', re.ASCII)

def request_host(request):
    '''Return request-host, as defined by RFC 2965.

Variation from RFC: returned value is lowercased, for convenient
comparison.

'''
    url = request.full_url
    host = urlparse(url)[1]
    if host == '':
        host = request.get_header('Host', '')
    host = _cut_port_re.sub('', host, 1)
    return host.lower()


class Request:
    
    def __init__(self, url, data = None, headers = { }, origin_req_host = None, unverifiable = False, method = None):
        self.full_url = url
        self.headers = { }
        self.unredirected_hdrs = { }
        self._data = None
        self.data = data
        self._tunnel_host = None
        for key, value in headers.items():
            self.add_header(key, value)
        if origin_req_host is None:
            origin_req_host = request_host(self)
        self.origin_req_host = origin_req_host
        self.unverifiable = unverifiable
        if method:
            self.method = method
            return None

    full_url = (lambda self: '{}#{}'.format(self._full_url, self.fragment) if self.fragment else self._full_url)()
    full_url = (lambda self, url: self._full_url = unwrap(url)(self._full_url, self.fragment) = _splittag(self._full_url)self._parse())()
    full_url = (lambda self: self._full_url = Noneself.fragment = Noneself.selector = '')()
    data = (lambda self: self._data)()
    data = (lambda self, data: if data != self._data:
self._data = dataif self.has_header('Content-length'):
self.remove_header('Content-length')NoneNone)()
    data = (lambda self: self.data = None)()
    
    def _parse(self):
        (self.type, rest) = _splittype(self._full_url)
        if self.type is None:
            raise ValueError('unknown url type: %r' % self.full_url)
        (self.host, self.selector) = _splithost(rest)
        if self.host:
            self.host = unquote(self.host)
            return None

    
    def get_method(self):
        '''Return a string indicating the HTTP request method.'''
        default_method = 'POST' if self.data is not None else 'GET'
        return getattr(self, 'method', default_method)

    
    def get_full_url(self):
        return self.full_url

    
    def set_proxy(self, host, type):
        '''https'''
        if self.type == 'https' and not (self._tunnel_host):
            self._tunnel_host = self.host
        else:
            self.type = type
            self.selector = self.full_url
        self.host = host

    
    def has_proxy(self):
        return self.selector == self.full_url

    
    def add_header(self, key, val):
        self.headers[key.capitalize()] = val

    
    def add_unredirected_header(self, key, val):
        self.unredirected_hdrs[key.capitalize()] = val

    
    def has_header(self, header_name):
        return header_name in self.headers or header_name in self.unredirected_hdrs

    
    def get_header(self, header_name, default = None):
        return self.headers.get(header_name, self.unredirected_hdrs.get(header_name, default))

    
    def remove_header(self, header_name):
        self.headers.pop(header_name, None)
        self.unredirected_hdrs.pop(header_name, None)

    
    def header_items(self):
        hdrs = {
            **self.unredirected_hdrs,
            **self.headers }
        return list(hdrs.items())



class OpenerDirector:
    
    def __init__(self):
        '''Python-urllib/%s'''
        client_version = 'Python-urllib/%s' % __version__
        self.addheaders = [
            ('User-agent', client_version)]
        self.handlers = []
        self.handle_open = { }
        self.handle_error = { }
        self.process_response = { }
        self.process_request = { }

    
    def add_handler(self, handler):
        '''add_parent'''
        if not hasattr(handler, 'add_parent'):
            raise TypeError('expected BaseHandler instance, got %r' % type(handler))
        added = False
        for meth in dir(handler):
            while meth in ('redirect_request', 'do_open', 'proxy_open'):
                pass
            i = meth.find('_')
            protocol = meth[:i]
            condition = meth[i + 1:]
            if condition.startswith('error'):
                j = condition.find('_') + i + 1
                kind = meth[j + 1:]
                
                try:
                    kind = int(kind)
                except ValueError:
                    pass

                lookup = self.handle_error.get(protocol, { })
                self.handle_error[protocol] = lookup
            elif condition == 'open':
                kind = protocol
                lookup = self.handle_open
            elif condition == 'response':
                kind = protocol
                lookup = self.process_response
            elif condition == 'request':
                kind = protocol
                lookup = self.process_request
            else:
                continue
            handlers = lookup.setdefault(kind, [])
            if handlers:
                bisect.insort(handlers, handler)
            else:
                handlers.append(handler)
            added = True
        if added:
            bisect.insort(self.handlers, handler)
            handler.add_parent(self)
            return None

    
    def close(self):
        pass

    
    def _call_chain(self, chain, kind, meth_name, *args):
        handlers = chain.get(kind, ())
        for handler in handlers:
            func = getattr(handler, meth_name)
            result = args()
            while result:
                pass
            return result

    
    def open(self, fullurl, data = None, timeout = socket._GLOBAL_DEFAULT_TIMEOUT):
        if isinstance(fullurl, str):
            req = Request(fullurl, data)
        else:
            req = fullurl
            if data is not None:
                req.data = data
        req.timeout = timeout
        protocol = req.type
        meth_name = protocol + '_request'
        for processor in self.process_request.get(protocol, []):
            meth = getattr(processor, meth_name)
            req = meth(req)
        sys.audit('urllib.Request', req.full_url, req.data, req.headers, req.get_method())
        response = self._open(req, data)
        meth_name = protocol + '_response'
        for processor in self.process_response.get(protocol, []):
            meth = getattr(processor, meth_name)
            response = meth(req, response)
        return response

    
    def _open(self, req, data = None):
        '''default'''
        result = self._call_chain(self.handle_open, 'default', 'default_open', req)
        if result:
            return result
        protocol = req.type
        result = self._call_chain(self.handle_open, protocol, protocol + '_open', req)
        if result:
            return result
        return self._call_chain(self.handle_open, 'unknown', 'unknown_open', req)

    
    def error(self, proto, *args):
        '''http'''
        if proto in ('http', 'https'):
            dict = self.handle_error['http']
            proto = args[2]
            meth_name = 'http_error_%s' % proto
            http_err = 1
            orig_args = args
        else:
            dict = self.handle_error
            meth_name = proto + '_error'
            http_err = 0
        args = (dict, proto, meth_name) + args
        result = args()
        if result:
            return result
        if http_err:
            args = (dict, 'default', 'http_error_default') + orig_args
            return args()



def build_opener(*handlers):
    '''Create an opener object from a list of handlers.

The opener will use several default handlers, including support
for HTTP, FTP and when applicable HTTPS.

If any of the handlers passed as arguments are subclasses of the
default handlers, the default handlers will not be used.
'''
    opener = OpenerDirector()
    default_classes = [
        ProxyHandler,
        UnknownHandler,
        HTTPHandler,
        HTTPDefaultErrorHandler,
        HTTPRedirectHandler,
        FTPHandler,
        FileHandler,
        HTTPErrorProcessor,
        DataHandler]
    if hasattr(http.client, 'HTTPSConnection'):
        default_classes.append(HTTPSHandler)
    skip = set()
    for klass in default_classes:
        for check in handlers:
            while isinstance(check, type):
                if issubclass(check, klass):
                    skip.add(klass)
                    continue
            if not isinstance(check, klass):
                continue
            skip.add(klass)
    for klass in skip:
        default_classes.remove(klass)
    for klass in default_classes:
        opener.add_handler(klass())
    for h in handlers:
        if isinstance(h, type):
            h = h()
        opener.add_handler(h)
    return opener


class BaseHandler:
    handler_order = 500
    
    def add_parent(self, parent):
        self.parent = parent

    
    def close(self):
        pass

    
    def __lt__(self, other):
        '''handler_order'''
        if not hasattr(other, 'handler_order'):
            return True
        return self.handler_order < other.handler_order



class HTTPErrorProcessor(BaseHandler):
    '''Process HTTP error responses.'''
    handler_order = 1000
    
    def http_response(self, request, response):
        hdrs = response.msg
        msg = response.info()
        code = response.code
        if not (200 <= code) or not (code < 300):
            response = self.parent.error('http', request, response, code, msg, hdrs)
        return response

    https_response = http_response


class HTTPDefaultErrorHandler(BaseHandler):
    
    def http_error_default(self, req, fp, code, msg, hdrs):
        raise HTTPError(req.full_url, code, msg, hdrs, fp)



class HTTPRedirectHandler(BaseHandler):
    max_repeats = 4
    max_redirections = 10
    
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """Return a Request or None in response to a redirect.

This is called by the http_error_30x methods when a
redirection response is received.  If a redirection should
take place, return a new Request to allow http_error_30x to
perform the redirect.  Otherwise, raise HTTPError if no-one
else should try to handle this url.  Return None if you can't
but another Handler might.
"""
        m = req.get_method()
        if not (code in (301, 302, 303, 307, 308)) or not (m in ('GET', 'HEAD')):
            if not (code in (301, 302, 303)) or not (m == 'POST'):
                raise HTTPError(req.full_url, code, msg, headers, fp)
        newurl = newurl.replace(' ', '%20')
        CONTENT_HEADERS = ('content-length', 'content-type')
        
        try:
            for k, v in req.headers.items():
                while not k.lower() not in CONTENT_HEADERS:
                    pass
        v = req.headers.items()
        k = v

        newheaders = k
        k = v
        v = None
        return Request(newurl, method = 'HEAD' if m == 'HEAD' else 'GET', headers = newheaders, origin_req_host = req.origin_req_host, unverifiable = True)
    # WARNING: Decompyle incomplete

    
    def http_error_302(self, req, fp, code, msg, headers):
        '''location'''
        if 'location' in headers:
            newurl = headers['location']
        elif 'uri' in headers:
            newurl = headers['uri']
        else:
            return None
        urlparts = urlparse(newurl)
        if urlparts.scheme not in ('http', 'https', 'ftp', ''):
            raise HTTPError(newurl, code, f'''{msg!s} - Redirection to url \'{newurl!s}\' is not allowed''', headers, fp)
        if not (urlparts.path) and urlparts.netloc:
            urlparts = list(urlparts)
            urlparts[2] = '/'
        newurl = urlunparse(urlparts)
        newurl = quote(newurl, encoding = 'iso-8859-1', safe = string.punctuation)
        newurl = urljoin(req.full_url, newurl)
        new = self.redirect_request(req, fp, code, msg, headers, newurl)
        if new is None:
            return None
        if hasattr(req, 'redirect_dict'):
            visited = req.redirect_dict
            new.redirect_dict = req.redirect_dict
            if visited.get(newurl, 0) >= self.max_repeats or len(visited) >= self.max_redirections:
                raise HTTPError(req.full_url, code, self.inf_msg + msg, headers, fp)
        else:
            visited = { }
            new.redirect_dict = { }
            req.redirect_dict = { }
        visited[newurl] = visited.get(newurl, 0) + 1
        fp.read()
        fp.close()
        return self.parent.open(new, timeout = req.timeout)

    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302
    http_error_308 = http_error_302
    inf_msg = 'The HTTP server returned a redirect error that would lead to an infinite loop.\nThe last 30x error message was:\n'


def _parse_proxy(proxy):
    '''Return (scheme, user, password, host/port) given a URL or an authority.

If a URL is supplied, it must have an authority (host:port) component.
According to RFC 3986, having an authority component means the URL must
have two slashes after the scheme.
'''
    scheme, r_scheme = _splittype(proxy)
    if not r_scheme.startswith('/'):
        scheme = None
        authority = proxy
    elif not r_scheme.startswith('//'):
        raise ValueError('proxy URL with no authority: %r' % proxy)
    if '@' in r_scheme:
        host_separator = r_scheme.find('@')
        end = r_scheme.find('/', host_separator)
    else:
        end = r_scheme.find('/', 2)
    if end == -1:
        end = None
    authority = r_scheme[2:end]
    userinfo, hostport = _splituser(authority)
    if userinfo is not None:
        user, password = _splitpasswd(userinfo)
    else:
        user = None
        password = None
    return (scheme, user, password, hostport)


class ProxyHandler(BaseHandler):
    handler_order = 100
    
    def __init__(self, proxies = None):
        if proxies is None:
            proxies = getproxies()
        if not hasattr(proxies, 'keys'):
            raise 'proxies must be a mapping'()
        self.proxies = proxies
        for type, url in proxies.items():
            type = type.lower()
            setattr(self, '%s_open' % type, (lambda r, proxy = url, type = type, meth = self.proxy_open: meth(r, proxy, type)))

    
    def proxy_open(self, req, proxy, type):
        orig_type = req.type
        proxy_type, user, password, hostport = _parse_proxy(proxy)
        if proxy_type is None:
            proxy_type = orig_type
        if req.host and proxy_bypass(req.host):
            return None
        if user and password:
            user_pass = f'''{unquote(user)!s}:{unquote(password)!s}'''
            creds = base64.b64encode(user_pass.encode()).decode('ascii')
            req.add_header('Proxy-authorization', 'Basic ' + creds)
        hostport = unquote(hostport)
        req.set_proxy(hostport, proxy_type)
        if orig_type == proxy_type or orig_type == 'https':
            return None
        return self.parent.open(req, timeout = req.timeout)



class HTTPPasswordMgr:
    
    def __init__(self):
        self.passwd = { }

    
    def add_password(self, realm, uri, user, passwd):
        if isinstance(uri, str):
            uri = [
                uri]
        if realm not in self.passwd:
            self.passwd[realm] = { }
        for reduced_uri in (True, False):
            default_port = None
            if tuple is tuple:
                tuple
                for None in uri():
                    pass
                # unsupported CALL_INTRINSIC_1 6
            
            self.passwd[realm][reduced_uri] = (user, passwd)
        return None
    # WARNING: Decompyle incomplete

    
    def find_user_password(self, realm, authuri):
        domains = self.passwd.get(realm, { })
        for default_port in (True, False):
            reduced_authuri = self.reduce_uri(authuri, default_port)
            for uris, authinfo in domains.items():
                for uri in uris:
                    while not self.is_suburi(uri, reduced_authuri):
                        pass
                    uris
                    domains.items()
                    return authinfo
        return (None, None)

    
    def reduce_uri(self, uri, default_port = True):
        '''Accept authority or URI and extract only the authority and path.'''
        parts = urlsplit(uri)
        if parts[1]:
            scheme = parts[0]
            authority = parts[1]
            path = parts[2] or '/'
        else:
            scheme = None
            authority = uri
            path = '/'
        host, port = _splitport(authority)
        if default_port and port is None and scheme is not None:
            dport = {
                'https': 443,
                'http': 80 }.get(scheme)
            if dport is not None:
                authority = '%s:%d' % (host, dport)
        return (authority, path)

    
    def is_suburi(self, base, test):
        '''Check if test is below base in a URI tree

Both args must be URIs in reduced form.
'''
        if base == test:
            return True
        if base[0] != test[0]:
            return False
        prefix = base[1]
        if prefix[-1:] != '/':
            prefix += '/'
        return test[1].startswith(prefix)



class HTTPPasswordMgrWithDefaultRealm(HTTPPasswordMgr):
    
    def find_user_password(self, realm, authuri):
        user, password = HTTPPasswordMgr.find_user_password(self, realm, authuri)
        if user is not None:
            return (user, password)
        return HTTPPasswordMgr.find_user_password(self, None, authuri)



class HTTPPasswordMgrWithPriorAuth(HTTPPasswordMgrWithDefaultRealm):
    
    def __init__(self):
        self.authenticated = { }
        # unsupported opcode LOAD_SUPER_ATTR
        self()
        return None
    # WARNING: Decompyle incomplete

    
    def add_password(self, realm, uri, user, passwd, is_authenticated = False):
        self.update_authenticated(uri, is_authenticated)
        if realm is not None:
            # unsupported opcode LOAD_SUPER_ATTR
            self(None, uri, user, passwd)
        # unsupported opcode LOAD_SUPER_ATTR
        self(realm, uri, user, passwd)
        return None
    # WARNING: Decompyle incomplete

    
    def update_authenticated(self, uri, is_authenticated = False):
        if isinstance(uri, str):
            uri = [
                uri]
        for default_port in (True, False):
            for u in uri:
                reduced_uri = self.reduce_uri(u, default_port)
                self.authenticated[reduced_uri] = is_authenticated

    
    def is_authenticated(self, authuri):
        for default_port in (True, False):
            reduced_authuri = self.reduce_uri(authuri, default_port)
            for uri in self.authenticated:
                while not self.is_suburi(uri, reduced_authuri):
                    pass
                self.authenticated
                return self.authenticated[uri]



class AbstractBasicAuthHandler:
    rx = re.compile('(?:^|,)[ \t]*([^ \t,]+)[ \t]+realm=(["\']?)([^"\']*)\\2', re.I)
    
    def __init__(self, password_mgr = None):
        if password_mgr is None:
            password_mgr = HTTPPasswordMgr()
        self.passwd = password_mgr
        self.add_password = self.passwd.add_password

    
    def _parse_realm(self, header):
        found_challenge = False
        for mo in AbstractBasicAuthHandler.rx.finditer(header):
            (scheme, quote, realm) = mo.groups()
            if quote not in ('"', "'"):
                import warnings
                warnings.warn('Basic Auth Realm was unquoted', UserWarning, 3)
            yield (scheme, realm)
            AbstractBasicAuthHandler.rx.finditer(header)
            found_challenge = True
        if not found_challenge:
            if header:
                scheme = header.split()[0]
            else:
                scheme = ''
            yield (scheme, None)
            return None

    
    def http_error_auth_reqed(self, authreq, host, req, headers):
        headers = headers.get_all(authreq)
        if not headers:
            return None
        unsupported = None
        for header in headers:
            for scheme, realm in self._parse_realm(header):
                while scheme.lower() != 'basic':
                    unsupported = scheme
                while realm:
                    pass
                self._parse_realm(header)
                return self.retry_http_basic_auth(host, req, realm)
        if unsupported is not None:
            raise ValueError(f'''AbstractBasicAuthHandler does not support the following scheme: {scheme!r}''')

    
    def retry_http_basic_auth(self, host, req, realm):
        user, pw = self.passwd.find_user_password(realm, host)
        if pw is not None:
            raw = f'''{user!s}:{pw!s}'''
            auth = 'Basic ' + base64.b64encode(raw.encode()).decode('ascii')
            if req.get_header(self.auth_header, None) == auth:
                return None
            req.add_unredirected_header(self.auth_header, auth)
            return self.parent.open(req, timeout = req.timeout)

    
    def http_request(self, req):
        '''is_authenticated'''
        if not hasattr(self.passwd, 'is_authenticated') or not self.passwd.is_authenticated(req.full_url):
            return req
        if not req.has_header('Authorization'):
            user, passwd = self.passwd.find_user_password(None, req.full_url)
            credentials = '{0}:{1}'.format(user, passwd).encode()
            auth_str = base64.standard_b64encode(credentials).decode()
            req.add_unredirected_header('Authorization', 'Basic {}'.format(auth_str.strip()))
        return req

    
    def http_response(self, req, response):
        '''is_authenticated'''
        if hasattr(self.passwd, 'is_authenticated'):
            if 200 <= response.code and response.code < 300:
                self.passwd.update_authenticated(req.full_url, True)
                return response
            self.passwd.update_authenticated(req.full_url, False)
        return response

    https_request = http_request
    https_response = http_response


class HTTPBasicAuthHandler(BaseHandler, AbstractBasicAuthHandler):
    auth_header = 'Authorization'
    
    def http_error_401(self, req, fp, code, msg, headers):
        '''www-authenticate'''
        url = req.full_url
        response = self.http_error_auth_reqed('www-authenticate', url, req, headers)
        return response



class ProxyBasicAuthHandler(BaseHandler, AbstractBasicAuthHandler):
    auth_header = 'Proxy-authorization'
    
    def http_error_407(self, req, fp, code, msg, headers):
        '''proxy-authenticate'''
        authority = req.host
        response = self.http_error_auth_reqed('proxy-authenticate', authority, req, headers)
        return response


_randombytes = os.urandom

class AbstractDigestAuthHandler:
    
    def __init__(self, passwd = None):
        if passwd is None:
            passwd = HTTPPasswordMgr()
        self.passwd = passwd
        self.add_password = self.passwd.add_password
        self.retried = 0
        self.nonce_count = 0
        self.last_nonce = None

    
    def reset_retry_count(self):
        self.retried = 0

    
    def http_error_auth_reqed(self, auth_header, host, req, headers):
        authreq = headers.get(auth_header, None)
        if self.retried > 5:
            raise HTTPError(req.full_url, 401, 'digest auth failed', headers, None)
        self.retried += 1
        if authreq:
            scheme = authreq.split()[0]
            if scheme.lower() == 'digest':
                return self.retry_http_digest_auth(req, authreq)
            if scheme.lower() != 'basic':
                raise ValueError("AbstractDigestAuthHandler does not support the following scheme: '%s'" % scheme)
            return None

    
    def retry_http_digest_auth(self, req, auth):
        ''' '''
        token, challenge = auth.split(' ', 1)
        chal = parse_keqv_list(filter(None, parse_http_list(challenge)))
        auth = self.get_authorization(req, chal)
        if auth:
            auth_val = 'Digest %s' % auth
            if req.headers.get(self.auth_header, None) == auth_val:
                return None
            req.add_unredirected_header(self.auth_header, auth_val)
            resp = self.parent.open(req, timeout = req.timeout)
            return resp

    
    def get_cnonce(self, nonce):
        ''':'''
        s = f'''{self.nonce_count!s}:{nonce!s}:{time.ctime()!s}:'''
        b = s.encode('ascii') + _randombytes(8)
        dig = hashlib.sha1(b).hexdigest()
        return dig[slice(None, 16, None)]

    
    def get_authorization(self, req, chal):
        '''realm'''
        
        try:
            realm = chal['realm']
            nonce = chal['nonce']
            qop = chal.get('qop')
            algorithm = chal.get('algorithm', 'MD5')
            opaque = chal.get('opaque', None)
        except KeyError:
            return None

        H, KD = self.get_algorithm_impls(algorithm)
        if H is None:
            return None
        user, pw = self.passwd.find_user_password(realm, req.full_url)
        if user is None:
            return None
        if req.data is not None:
            entdig = self.get_entity_digest(req.data, chal)
        else:
            entdig = None
        A1 = f'''{user!s}:{realm!s}:{pw!s}'''
        A2 = f'''{req.get_method()!s}:{req.selector!s}'''
        if qop is None:
            respdig = KD(H(A1), f'''{nonce!s}:{H(A2)!s}''')
        elif 'auth' in qop.split(','):
            if nonce == self.last_nonce:
                self.nonce_count += 1
            else:
                self.nonce_count = 1
                self.last_nonce = nonce
            ncvalue = '%08x' % self.nonce_count
            cnonce = self.get_cnonce(nonce)
            noncebit = f'''{nonce!s}:{ncvalue!s}:{cnonce!s}:{'auth'!s}:{H(A2)!s}'''
            respdig = KD(H(A1), noncebit)
        else:
            raise URLError("qop '%s' is not supported." % qop)
        base = f'''username="{user!s}", realm="{realm!s}", nonce="{nonce!s}", uri="{req.selector!s}", response="{respdig!s}"'''
        if opaque:
            base += ', opaque="%s"' % opaque
        if entdig:
            base += ', digest="%s"' % entdig
        base += ', algorithm="%s"' % algorithm
        if qop:
            base += f''', qop=auth, nc={ncvalue!s}, cnonce="{cnonce!s}"'''
        return base

    
    def get_algorithm_impls(self, algorithm):
        '''MD5'''
        if algorithm == 'MD5':
            
            H = lambda x: hashlib.md5(x.encode('ascii')).hexdigest()
        elif algorithm == 'SHA':
            
            H = lambda x: hashlib.sha1(x.encode('ascii')).hexdigest()
        elif algorithm == 'SHA-256':
            
            H = lambda x: hashlib.sha256(x.encode('ascii')).hexdigest()
        else:
            raise ValueError('Unsupported digest authentication algorithm %r' % algorithm)
        
        KD = lambda s, d: H(f'''{s!s}:{d!s}''')
        return (H, KD)

    
    def get_entity_digest(self, data, chal):
        pass



class HTTPDigestAuthHandler(AbstractDigestAuthHandler, BaseHandler):
    '''An authentication protocol defined by RFC 2069

Digest authentication improves on basic authentication because it
does not transmit passwords in the clear.
'''
    auth_header = 'Authorization'
    handler_order = 490
    
    def http_error_401(self, req, fp, code, msg, headers):
        host = urlparse(req.full_url)[1]
        retry = self.http_error_auth_reqed('www-authenticate', host, req, headers)
        self.reset_retry_count()
        return retry



class ProxyDigestAuthHandler(AbstractDigestAuthHandler, BaseHandler):
    auth_header = 'Proxy-Authorization'
    handler_order = 490
    
    def http_error_407(self, req, fp, code, msg, headers):
        '''proxy-authenticate'''
        host = req.host
        retry = self.http_error_auth_reqed('proxy-authenticate', host, req, headers)
        self.reset_retry_count()
        return retry



class AbstractHTTPHandler(BaseHandler):
    
    def __init__(self, debuglevel = None):
        if debuglevel is not None:
            self._debuglevel = debuglevel
            return None
        self._debuglevel = http.client.HTTPConnection.debuglevel

    
    def set_http_debuglevel(self, level):
        self._debuglevel = level

    
    def _get_content_length(self, request):
        return http.client.HTTPConnection._get_content_length(request.data, request.get_method())

    
    def do_request_(self, request):
        '''no host given'''
        host = request.host
        if not host:
            raise URLError('no host given')
        if request.data is not None:
            data = request.data
            if isinstance(data, str):
                msg = 'POST data should be bytes, an iterable of bytes, or a file object. It cannot be of type str.'
                raise TypeError(msg)
            if not request.has_header('Content-type'):
                request.add_unredirected_header('Content-type', 'application/x-www-form-urlencoded')
            if not request.has_header('Content-length') and not request.has_header('Transfer-encoding'):
                content_length = self._get_content_length(request)
                if content_length is not None:
                    request.add_unredirected_header('Content-length', str(content_length))
                else:
                    request.add_unredirected_header('Transfer-encoding', 'chunked')
        sel_host = host
        if request.has_proxy():
            scheme, sel = _splittype(request.selector)
            sel_host, sel_path = _splithost(sel)
        if not request.has_header('Host'):
            request.add_unredirected_header('Host', sel_host)
        for name, value in self.parent.addheaders:
            name = name.capitalize()
            if request.has_header(name):
                continue
            request.add_unredirected_header(name, value)
        return request

    
    def do_open(self, http_class, req, **http_conn_args):
        '''Return an HTTPResponse object for the request, using http_class.

http_class must implement the HTTPConnection API from http.client.
'''
        host = req.host
        if not host:
            raise URLError('no host given')
        h = (host,)(*{
            'timeout': req.timeout,
            **http_conn_args })
        h.set_debuglevel(self._debuglevel)
        headers = dict(req.unredirected_hdrs)
        headers.update(req.headers)
        headers['Connection'] = 'close'
        
        try:
            for name, val in headers.items():
                pass
        val = None
        name = None

        headers = name
        name = val
        val = http_class
        if req._tunnel_host:
            tunnel_headers = { }
            proxy_auth_hdr = 'Proxy-Authorization'
            if proxy_auth_hdr in headers:
                tunnel_headers[proxy_auth_hdr] = headers[proxy_auth_hdr]
                del headers[proxy_auth_hdr]
            h.set_tunnel(req._tunnel_host, headers = tunnel_headers)
        
        try:
            h.request(req.get_method(), req.selector, req.data, headers, encode_chunked = req.has_header('Transfer-encoding'))
        except OSError as err:
            raise URLError(err)

        
        try:
            r = h.getresponse()
        except:
            h.close()
            raise

        if h.sock:
            h.sock.close()
            h.sock = None
        r.url = req.get_full_url()
        r.msg = r.reason
        return r
    # WARNING: Decompyle incomplete



class HTTPHandler(AbstractHTTPHandler):
    
    def http_open(self, req):
        return self.do_open(http.client.HTTPConnection, req)

    http_request = AbstractHTTPHandler.do_request_

if hasattr(http.client, 'HTTPSConnection'):
    
    class HTTPSHandler(AbstractHTTPHandler):
        
        def __init__(self, debuglevel = None, context = None, check_hostname = None):
            debuglevel = debuglevel if debuglevel is not None else http.client.HTTPSConnection.debuglevel
            AbstractHTTPHandler.__init__(self, debuglevel)
            if context is None:
                http_version = http.client.HTTPSConnection._http_vsn
                context = http.client._create_https_context(http_version)
            if check_hostname is not None:
                context.check_hostname = check_hostname
            self._context = context

        
        def https_open(self, req):
            return self.do_open(http.client.HTTPSConnection, req, context = self._context)

        https_request = AbstractHTTPHandler.do_request_

    __all__.append('HTTPSHandler')

class HTTPCookieProcessor(BaseHandler):
    
    def __init__(self, cookiejar = None):
        import http.cookiejar as http
        if cookiejar is None:
            cookiejar = http.cookiejar.CookieJar()
        self.cookiejar = cookiejar

    
    def http_request(self, request):
        self.cookiejar.add_cookie_header(request)
        return request

    
    def http_response(self, request, response):
        self.cookiejar.extract_cookies(response, request)
        return response

    https_request = http_request
    https_response = http_response


class UnknownHandler(BaseHandler):
    
    def unknown_open(self, req):
        '''unknown url type: %s'''
        type = req.type
        raise URLError('unknown url type: %s' % type)



def parse_keqv_list(l):
    '''Parse list of key=value strings where keys are not duplicated.'''
    parsed = { }
    for elt in l:
        k, v = elt.split('=', 1)
        if v[0] == '"' and v[-1] == '"':
            v = v[1:-1]
        parsed[k] = v
    return parsed


def parse_http_list(s):
    '''Parse lists as described by RFC 2068 Section 2.

In particular, parse comma-separated lists where the elements of
the list may include quoted-strings.  A quoted-string could
contain a comma.  A non-quoted string could have quotes in the
middle.  Neither commas nor quotes count if they are escaped.
Only double-quotes count, not single-quotes.
'''
    res = []
    part = ''
    escape = False
    quote = False
    for cur in s:
        while escape:
            part += cur
            escape = False
        while quote:
            if cur == '\\':
                escape = True
                continue
            if cur == '"':
                quote = False
            part += cur
        if cur == ',':
            res.append(part)
            part = ''
            continue
        if cur == '"':
            quote = True
        part += cur
    if part:
        res.append(part)
    return None
# WARNING: Decompyle incomplete


class FileHandler(BaseHandler):
    names = None
    
    def get_names(self):
        if FileHandler.names is None:
            
            try:
                FileHandler.names = tuple(socket.gethostbyname_ex('localhost')[2] + socket.gethostbyname_ex(socket.gethostname())[2])
            except socket.gaierror:
                FileHandler.names = (socket.gethostbyname('localhost'),)
                return FileHandler.names

            return FileHandler.names
        return FileHandler.names

    
    def open_local_file(self, req):
        import email.utils as email
        import mimetypes
        localfile = url2pathname(req.full_url, require_scheme = True, resolve_host = True)
        
        try:
            stats = os.stat(localfile)
            size = stats.st_size
            modified = email.utils.formatdate(stats.st_mtime, usegmt = True)
            mtype = mimetypes.guess_file_type(localfile)[0]
            headers = email.message_from_string('Content-type: %s\nContent-length: %d\nLast-modified: %s\n' % (mtype or 'text/plain', size, modified))
            origurl = pathname2url(localfile, add_scheme = True)
            return addinfourl(open(localfile, 'rb'), headers, origurl)
        except OSError as exp:
            raise URLError(exp, exp.filename)


    file_open = open_local_file


def _is_local_authority(authority, resolve):
    '''localhost'''
    if not authority or authority == 'localhost':
        return True
    
    try:
        hostname = socket.gethostname()
    except (socket.gaierror, AttributeError):
        pass

    if authority == hostname:
        return True
    if not resolve:
        return False
    
    try:
        address = socket.gethostbyname(authority)
    except (socket.gaierror, AttributeError, UnicodeEncodeError):
        return False

    return address in FileHandler().get_names()


class FTPHandler(BaseHandler):
    
    def ftp_open(self, req):
        import ftplib
        import mimetypes
        host = req.host
        if not host:
            raise URLError('ftp error: no host given')
        host, port = _splitport(host)
        if port is None:
            port = ftplib.FTP_PORT
        else:
            port = int(port)
        user, host = _splituser(host)
        if user:
            user, passwd = _splitpasswd(user)
        else:
            passwd = None
        host = unquote(host)
        user = user or ''
        passwd = passwd or ''
        
        try:
            host = socket.gethostbyname(host)
        except OSError as msg:
            raise URLError(msg)

        path, attrs = _splitattr(req.selector)
        dirs = path.split('/')
        dirs = list(map(unquote, dirs))
        file = dirs[:-1]
        dirs = dirs[-1]
        if dirs and not dirs[0]:
            dirs = dirs[slice(1, None, None)]
        fw = None
        
        try:
            fw = self.connect_ftp(user, passwd, host, port, dirs, req.timeout)
            type = file and 'I' or 'D'
            for attr in attrs:
                (attr, value) = _splitvalue(attr)
                if not attr.lower() == 'type':
                    continue
                if not value in ('a', 'A', 'i', 'I', 'd', 'D'):
                    continue
                type = value.upper()
            (fp, retrlen) = fw.retrfile(file, type)
            headers = ''
            mtype = mimetypes.guess_type(req.full_url)[0]
            if mtype:
                headers += 'Content-type: %s\n' % mtype
            if retrlen is not None and retrlen >= 0:
                headers += 'Content-length: %d\n' % retrlen
            headers = email.message_from_string(headers)
            return addinfourl(fp, headers, req.full_url)
        except Exception as exp:
            if fw is not None and not (fw.keepalive):
                fw.close()
            if isinstance(exp, ftplib.all_errors):
                raise URLError(f'''ftp error: {exp}''') from exp
            raise


    
    def connect_ftp(self, user, passwd, host, port, dirs, timeout):
        return ftpwrapper(user, passwd, host, port, dirs, timeout, persistent = False)



class CacheFTPHandler(FTPHandler):
    
    def __init__(self):
        self.cache = { }
        self.timeout = { }
        self.soonest = 0
        self.delay = 60
        self.max_conns = 16

    
    def setTimeout(self, t):
        self.delay = t

    
    def setMaxConns(self, m):
        self.max_conns = m

    
    def connect_ftp(self, user, passwd, host, port, dirs, timeout):
        '''/'''
        key = (user, host, port, '/'.join(dirs), timeout)
        conn = self.cache.get(key)
        if not (conn is not None) or not (conn.keepalive):
            if conn is not None:
                conn.close()
            conn = ftpwrapper(user, passwd, host, port, dirs, timeout)
            self.cache[key] = ftpwrapper(user, passwd, host, port, dirs, timeout)
        self.timeout[key] = time.time() + self.delay
        self.check_cache()
        return conn

    
    def check_cache(self):
        t = time.time()
        if self.soonest <= t:
            for k, v in list(self.timeout.items()):
                while not v < t:
                    pass
                self.cache[k].close()
                del self.cache[k]
                del self.timeout[k]
        self.soonest = min(list(self.timeout.values()))
        if len(self.cache) == self.max_conns:
            for k, v in list(self.timeout.items()):
                while not v == self.soonest:
                    pass
                del self.cache[k]
                del self.timeout[k]
                list(self.timeout.items())
            self.soonest = min(list(self.timeout.values()))
            return None

    
    def clear_cache(self):
        for conn in self.cache.values():
            conn.close()
        self.cache.clear()
        self.timeout.clear()



class DataHandler(BaseHandler):
    
    def data_open(self, req):
        ''':'''
        url = req.full_url
        scheme, data = url.split(':', 1)
        mediatype, data = data.split(',', 1)
        if re.search('[\\x00-\\x1F\\x7F]', mediatype):
            raise ValueError('Control characters not allowed in data: mediatype')
        data = unquote_to_bytes(data)
        if mediatype.endswith(';base64'):
            data = base64.decodebytes(data)
            mediatype = mediatype[:-7]
        if not mediatype:
            mediatype = 'text/plain;charset=US-ASCII'
        headers = email.message_from_string('Content-type: %s\nContent-length: %d\n' % (mediatype, len(data)))
        return addinfourl(io.BytesIO(data), headers, url)



def url2pathname(url, *, require_scheme, resolve_host):
    """Convert the given file URL to a local file system path.

The 'file:' scheme prefix must be omitted unless *require_scheme*
is set to true.

The URL authority may be resolved with gethostbyname() if
*resolve_host* is set to true.
"""
    if not require_scheme:
        url = 'file:' + url
    (scheme, authority, url) = urlsplit(url)[slice(None, 3, None)]
    if scheme != 'file':
        raise URLError("URL is missing a 'file:' scheme")
    if os.name == 'nt':
        if authority[slice(1, 2, None)] == ':':
            url = authority + url
        elif not _is_local_authority(authority, resolve_host):
            url = '//' + authority + url
        elif url[slice(None, 3, None)] == '///':
            url = url[slice(1, None, None)]
        elif url[slice(None, 1, None)] == '/' and url[slice(2, 3, None)] in (':', '|'):
            url = url[slice(1, None, None)]
        if url[slice(1, 2, None)] == '|':
            url = url[slice(None, 1, None)] + ':' + url[slice(2, None, None)]
        url = url.replace('/', '\\')
    elif not _is_local_authority(authority, resolve_host):
        raise URLError('file:// scheme is supported only on localhost')
    encoding = sys.getfilesystemencoding()
    errors = sys.getfilesystemencodeerrors()
    return unquote(url, encoding = encoding, errors = errors)


def pathname2url(pathname, *, add_scheme):
    """Convert the given local file system path to a file URL.

The 'file:' scheme prefix is omitted unless *add_scheme*
is set to true.
"""
    if os.name == 'nt':
        pathname = pathname.replace('\\', '/')
    encoding = sys.getfilesystemencoding()
    errors = sys.getfilesystemencodeerrors()
    scheme = 'file:' if add_scheme else ''
    (drive, root, tail) = os.path.splitroot(pathname)
    if drive:
        if drive[slice(None, 4, None)] == '//?/':
            drive = drive[slice(4, None, None)]
            if drive[slice(None, 4, None)].upper() == 'UNC/':
                drive = '//' + drive[slice(4, None, None)]
        if drive[slice(1, None, None)] == ':':
            drive = '///' + drive
        drive = quote(drive, encoding = encoding, errors = errors, safe = '/:')
    elif root:
        root = '//' + root
    tail = quote(tail, encoding = encoding, errors = errors)
    return scheme + drive + root + tail

_localhost = None

def localhost():
    """Return the IP address of the magic hostname 'localhost'."""
    global _localhost
    if _localhost is None:
        _localhost = socket.gethostbyname('localhost')
    return _localhost

_thishost = None

def thishost():
    '''Return the IP addresses of the current host.'''
    global _thishost, _thishost
    if _thishost is None:
        
        try:
            _thishost = tuple(socket.gethostbyname_ex(socket.gethostname())[2])
        except socket.gaierror:
            _thishost = tuple(socket.gethostbyname_ex('localhost')[2])
            return _thishost

        return _thishost
    return _thishost

_ftperrors = None

def ftperrors():
    '''Return the set of errors raised by the FTP class.'''
    global _ftperrors
    if _ftperrors is None:
        import ftplib
        _ftperrors = ftplib.all_errors
    return _ftperrors

_noheaders = None

def noheaders():
    '''Return an empty email Message object.'''
    global _noheaders
    if _noheaders is None:
        _noheaders = email.message_from_string('')
    return _noheaders


class ftpwrapper:
    '''Class used by open_ftp() for cache of open FTP connections.'''
    
    def __init__(self, user, passwd, host, port, dirs, timeout = None, persistent = True):
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = port
        self.dirs = dirs
        self.timeout = timeout
        self.refcount = 0
        self.keepalive = persistent
        
        try:
            self.init()
        except:
            self.close()
            raise


    
    def init(self):
        import ftplib
        self.busy = 0
        self.ftp = ftplib.FTP()
        self.ftp.connect(self.host, self.port, self.timeout)
        self.ftp.login(self.user, self.passwd)
        _target = '/'.join(self.dirs)
        self.ftp.cwd(_target)

    
    def retrfile(self, file, type):
        import ftplib
        self.endtransfer()
        if type in ('d', 'D'):
            cmd = 'TYPE A'
            isdir = 1
        else:
            cmd = 'TYPE ' + type
            isdir = 0
        
        try:
            self.ftp.voidcmd(cmd)
        except ftplib.all_errors:
            self.init()
            self.ftp.voidcmd(cmd)

        conn = None
        if file and not isdir:
            
            try:
                cmd = 'RETR ' + file
                conn, retrlen = self.ftp.ntransfercmd(cmd)
            except ftplib.error_perm as reason:
                if str(reason)[slice(None, 3, None)] != '550':
                    raise URLError(f'''ftp error: {reason}''') from reason

        if not conn:
            self.ftp.voidcmd('TYPE A')
            if file:
                pwd = self.ftp.pwd()
                
                try:
                    self.ftp.cwd(file)
                except ftplib.error_perm as reason:
                    raise URLError('ftp error: %r' % reason) from reason

                self.ftp.cwd(pwd)
                cmd = 'LIST ' + file
            else:
                cmd = 'LIST'
            conn, retrlen = self.ftp.ntransfercmd(cmd)
        self.busy = 1
        ftpobj = addclosehook(conn.makefile('rb'), self.file_close)
        self.refcount += 1
        conn.close()
        return (ftpobj, retrlen)

    
    def endtransfer(self):
        if not self.busy:
            return None
        self.busy = 0
        
        try:
            self.ftp.voidresp()
        except ftperrors():
            return None


    
    def close(self):
        self.keepalive = False
        if self.refcount <= 0:
            self.real_close()
            return None

    
    def file_close(self):
        self.endtransfer()
        self.refcount -= 1
        if self.refcount <= 0:
            if not self.keepalive:
                self.real_close()
                return None
            return None

    
    def real_close(self):
        self.endtransfer()
        
        try:
            self.ftp.close()
        except ftperrors():
            return None




def getproxies_environment():
    '''Return a dictionary of scheme -> proxy server URL mappings.

Scan the environment for variables named <scheme>_proxy;
this seems to be the standard convention.
'''
    proxies = { }
    environment = []
    for name in os.environ:
        while not len(name) > 5:
            pass
        while not name[-6] == '_':
            pass
        if not name[-5:].lower() == 'proxy':
            continue
        value = os.environ[name]
        proxy_name = name[:-6].lower()
        environment.append((name, value, proxy_name))
        if not value:
            continue
        proxies[proxy_name] = value
    if 'REQUEST_METHOD' in os.environ:
        proxies.pop('http', None)
    for name, value, proxy_name in environment:
        while not name[-6:] == '_proxy':
            pass
        while value:
            proxies[proxy_name] = value
        proxies.pop(proxy_name, None)
    return proxies


def proxy_bypass_environment(host, proxies = None):
    """Test if proxies should not be used for a particular host.

Checks the proxy dict for the value of no_proxy, which should
be a list of comma separated DNS suffixes, or '*' for all hosts.

"""
    if proxies is None:
        proxies = getproxies_environment()
    
    try:
        no_proxy = proxies['no']
    except KeyError:
        return False

    if no_proxy == '*':
        return True
    host = host.lower()
    hostonly, port = _splitport(host)
    for name in no_proxy.split(','):
        name = name.strip()
        while not name:
            pass
        name = name.lstrip('.')
        name = name.lower()
        if hostonly == name or host == name:
            no_proxy.split(',')
            return True
        name = '.' + name
        if not hostonly.endswith(name) and not host.endswith(name):
            continue
        no_proxy.split(',')
        return True
    return False


def _proxy_bypass_macosx_sysconf(host, proxy_settings):
    """
Return True iff this host shouldn't be accessed using a proxy

This function uses the MacOSX framework SystemConfiguration
to fetch the proxy information.

proxy_settings come from _scproxy._get_proxy_settings or get mocked ie:
{ 'exclude_simple': bool,
  'exceptions': ['foo.bar', '*.bar.com', '127.0.0.1', '10.1', '10.0/16']
}
"""
    from fnmatch import fnmatch
    from ipaddress import AddressValueError, IPv4Address
    hostonly, port = _splitport(host)
    
    def ip2num(ipAddr):
        '''.'''
        parts = ipAddr.split('.')
        parts = list(map(int, parts))
        if len(parts) != 4:
            parts = parts + [
                0,
                0,
                0,
                0][slice(None, 4, None)]
        return parts[0] << 24 | parts[1] << 16 | parts[2] << 8 | parts[3]

    if '.' not in host and proxy_settings['exclude_simple']:
        return True
    hostIP = None
    
    try:
        hostIP = int(IPv4Address(hostonly))
    except AddressValueError:
        pass

    for value in proxy_settings.get('exceptions', ()):
        while not value:
            pass
        m = re.match('(\\d+(?:\\.\\d+)*)(/\\d+)?', value)
        if m is not None and hostIP is not None:
            base = ip2num(m.group(1))
            mask = m.group(2)
            if mask is None:
                mask = 8 * (m.group(1).count('.') + 1)
            else:
                mask = int(mask[slice(1, None, None)])
            if mask < 0 or mask > 32:
                continue
            mask = 32 - mask
            if hostIP >> mask == base >> mask:
                proxy_settings.get('exceptions', ())
                return True
        if not fnmatch(host, value):
            continue
        proxy_settings.get('exceptions', ())
        return True
    return False


def _proxy_bypass_winreg_override(host, override):
    '''Return True if the host should bypass the proxy server.

The proxy override list is obtained from the Windows
Internet settings proxy override registry value.

An example of a proxy override value is:
"www.example.com;*.example.net; 192.168.0.1"
'''
    from fnmatch import fnmatch
    host, _ = _splitport(host)
    proxy_override = override.split(';')
    for test in proxy_override:
        test = test.strip()
        while test == '<local>':
            if '.' not in host:
                proxy_override
                return True
        if not fnmatch(host, test):
            continue
        proxy_override
        return True
    return False

if sys.platform == 'darwin':
    from _scproxy import _get_proxy_settings, _get_proxies
    
    def proxy_bypass_macosx_sysconf(host):
        proxy_settings = _get_proxy_settings()
        return _proxy_bypass_macosx_sysconf(host, proxy_settings)

    
    def getproxies_macosx_sysconf():
        '''Return a dictionary of scheme -> proxy server URL mappings.

This function uses the MacOSX framework SystemConfiguration
to fetch the proxy information.
'''
        return _get_proxies()

    
    def proxy_bypass(host):
        '''Return True, if host should be bypassed.

Checks proxy settings gathered from the environment, if specified,
or from the MacOSX framework SystemConfiguration.

'''
        proxies = getproxies_environment()
        if proxies:
            return proxy_bypass_environment(host, proxies)
        return proxy_bypass_macosx_sysconf(host)

    
    def getproxies():
        return getproxies_environment() or getproxies_macosx_sysconf()

if os.name == 'nt':
    
    def getproxies_registry():
        '''Return a dictionary of scheme -> proxy server URL mappings.

Win32 uses the registry to store proxies.

'''
        proxies = { }
        
        try:
            import winreg
        except ImportError:
            return proxies

        
        try:
            internetSettings = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings')
            proxyEnable = winreg.QueryValueEx(internetSettings, 'ProxyEnable')[0]
            if proxyEnable:
                proxyServer = str(winreg.QueryValueEx(internetSettings, 'ProxyServer')[0])
                if '=' not in proxyServer and ';' not in proxyServer:
                    proxyServer = 'http={0};https={0};ftp={0}'.format(proxyServer)
                for p in proxyServer.split(';'):
                    protocol, address = p.split('=', 1)
                    if not re.match('(?:[^/:]+)://', address):
                        if protocol in ('http', 'https', 'ftp'):
                            address = 'http://' + address
                        elif protocol == 'socks':
                            address = 'socks://' + address
                    proxies[protocol] = address
                if proxies.get('socks'):
                    address = re.sub('^socks://', 'socks4://', proxies['socks'])
                    proxies['http'] = proxies.get('http') or address
                    proxies['https'] = proxies.get('https') or address
            internetSettings.Close()
        except (OSError, ValueError, TypeError):
            return proxies

        return proxies

    
    def getproxies():
        '''Return a dictionary of scheme -> proxy server URL mappings.

Returns settings gathered from the environment, if specified,
or the registry.

'''
        return getproxies_environment() or getproxies_registry()

    
    def proxy_bypass_registry(host):
        
        try:
            import winreg
        except ImportError:
            return False

        
        try:
            internetSettings = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings')
            proxyEnable = winreg.QueryValueEx(internetSettings, 'ProxyEnable')[0]
            proxyOverride = str(winreg.QueryValueEx(internetSettings, 'ProxyOverride')[0])
        except OSError:
            return False

        if not proxyEnable or not proxyOverride:
            return False
        return _proxy_bypass_winreg_override(host, proxyOverride)

    
    def proxy_bypass(host):
        '''Return True, if host should be bypassed.

Checks proxy settings gathered from the environment, if specified,
or the registry.

'''
        proxies = getproxies_environment()
        if proxies:
            return proxy_bypass_environment(host, proxies)
        return proxy_bypass_registry(host)

getproxies = getproxies_environment
proxy_bypass = proxy_bypass_environment
