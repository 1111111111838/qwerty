# Source Generated with Decompyle++
# File: ipaddress.pyc (Python 3.14)

'''A fast, lightweight IPv4/IPv6 manipulation library in Python.

This library is used to create/poke/manipulate IPv4 and IPv6 addresses
and networks.

'''
__version__ = '1.0'
import functools
IPV4LENGTH = 32
IPV6LENGTH = 128

class AddressValueError(ValueError):
    '''A Value Error related to the address.'''
    pass


class NetmaskValueError(ValueError):
    '''A Value Error related to the netmask.'''
    pass


def ip_address(address):
    """Take an IP string/int and return an object of the correct type.

Args:
    address: A string or integer, the IP address.  Either IPv4 or
      IPv6 addresses may be supplied; integers less than 2**32 will
      be considered to be IPv4 by default.

Returns:
    An IPv4Address or IPv6Address object.

Raises:
    ValueError: if the *address* passed isn't either a v4 or a v6
      address

"""
    
    try:
        return IPv4Address(address)
    except (AddressValueError, NetmaskValueError):
        pass

    
    try:
        return IPv6Address(address)
    except (AddressValueError, NetmaskValueError):
        pass

    raise ValueError(f'''{address!r} does not appear to be an IPv4 or IPv6 address''')


def ip_network(address, strict = True):
    """Take an IP string/int and return an object of the correct type.

Args:
    address: A string or integer, the IP network.  Either IPv4 or
      IPv6 networks may be supplied; integers less than 2**32 will
      be considered to be IPv4 by default.

Returns:
    An IPv4Network or IPv6Network object.

Raises:
    ValueError: if the string passed isn't either a v4 or a v6
      address. Or if the network has host bits set.

"""
    
    try:
        return IPv4Network(address, strict)
    except (AddressValueError, NetmaskValueError):
        pass

    
    try:
        return IPv6Network(address, strict)
    except (AddressValueError, NetmaskValueError):
        pass

    raise ValueError(f'''{address!r} does not appear to be an IPv4 or IPv6 network''')


def ip_interface(address):
    """Take an IP string/int and return an object of the correct type.

Args:
    address: A string or integer, the IP address.  Either IPv4 or
      IPv6 addresses may be supplied; integers less than 2**32 will
      be considered to be IPv4 by default.

Returns:
    An IPv4Interface or IPv6Interface object.

Raises:
    ValueError: if the string passed isn't either a v4 or a v6
      address.

Notes:
    The IPv?Interface classes describe an Address on a particular
    Network, so they're basically a combination of both the Address
    and Network classes.

"""
    
    try:
        return IPv4Interface(address)
    except (AddressValueError, NetmaskValueError):
        pass

    
    try:
        return IPv6Interface(address)
    except (AddressValueError, NetmaskValueError):
        pass

    raise ValueError(f'''{address!r} does not appear to be an IPv4 or IPv6 interface''')


def v4_int_to_packed(address):
    '''Represent an address as 4 packed bytes in network (big-endian) order.

Args:
    address: An integer representation of an IPv4 IP address.

Returns:
    The integer address packed as 4 bytes in network (big-endian) order.

Raises:
    ValueError: If the integer is negative or too large to be an
      IPv4 IP address.

'''
    
    try:
        return address.to_bytes(4)
    except OverflowError:
        raise ValueError('Address negative or too large for IPv4')



def v6_int_to_packed(address):
    '''Represent an address as 16 packed bytes in network (big-endian) order.

Args:
    address: An integer representation of an IPv6 IP address.

Returns:
    The integer address packed as 16 bytes in network (big-endian) order.

'''
    
    try:
        return address.to_bytes(16)
    except OverflowError:
        raise ValueError('Address negative or too large for IPv6')



def _split_optional_netmask(address):
    '''Helper to split the netmask and raise AddressValueError if needed'''
    addr = str(address).split('/')
    if len(addr) > 2:
        raise AddressValueError(f'''Only one \'/\' permitted in {address!r}''')
    return addr


def _find_address_range(addresses):
    '''Find a sequence of sorted deduplicated IPv#Address.

Args:
    addresses: a list of IPv#Address objects.

Yields:
    A tuple containing the first and last IP addresses in the sequence.

'''
    it = iter(addresses)
    first = next(it)
    last = next(it)
    for ip in it:
        if ip._ip != last._ip + 1:
            yield (first, last)
            it
            first = ip
        last = ip
    yield (first, last)


def _count_righthand_zero_bits(number, bits):
    '''Count the number of zero bits on the right hand side.

Args:
    number: an integer.
    bits: maximum number of bits to count.

Returns:
    The number of zero bits on the right hand side of the number.

'''
    if number == 0:
        return bits
    return min(bits, (~number & number - 1).bit_length())


def summarize_address_range(first, last):
    """Summarize a network range given the first and last IP addresses.

Example:
    >>> list(summarize_address_range(IPv4Address('192.0.2.0'),
    ...                              IPv4Address('192.0.2.130')))
    ...                                #doctest: +NORMALIZE_WHITESPACE
    [IPv4Network('192.0.2.0/25'), IPv4Network('192.0.2.128/31'),
     IPv4Network('192.0.2.130/32')]

Args:
    first: the first IPv4Address or IPv6Address in the range.
    last: the last IPv4Address or IPv6Address in the range.

Returns:
    An iterator of the summarized IPv(4|6) network objects.

Raise:
    TypeError:
        If the first and last objects are not IP addresses.
        If the first and last objects are not the same version.
    ValueError:
        If the last object is not greater than the first.
        If the version of the first address is not 4 or 6.

"""
    if not isinstance(first, _BaseAddress) or not isinstance(last, _BaseAddress):
        raise TypeError('first and last must be IP addresses, not networks')
    if first.version != last.version:
        raise TypeError(f'''{first!s} and {last!s} are not of the same version''')
    if first > last:
        raise ValueError('last IP address must be greater than first')
    if first.version == 4:
        ip = IPv4Network
    elif first.version == 6:
        ip = IPv6Network
    else:
        raise ValueError('unknown IP version')
    ip_bits = first.max_prefixlen
    first_int = first._ip
    last_int = last._ip
    while first_int <= last_int:
        nbits = min(_count_righthand_zero_bits(first_int, ip_bits), ((last_int - first_int) + 1).bit_length() - 1)
        net = ip((first_int, ip_bits - nbits))
        yield net
        first_int += 1 << nbits
        if not first_int - 1 == ip._ALL_ONES:
            continue
        return None


def _collapse_addresses_internal(addresses):
    """Loops through the addresses, collapsing concurrent netblocks.

Example:

    ip1 = IPv4Network('192.0.2.0/26')
    ip2 = IPv4Network('192.0.2.64/26')
    ip3 = IPv4Network('192.0.2.128/26')
    ip4 = IPv4Network('192.0.2.192/26')

    _collapse_addresses_internal([ip1, ip2, ip3, ip4]) ->
      [IPv4Network('192.0.2.0/24')]

    This shouldn't be called directly; it is called via
      collapse_addresses([]).

Args:
    addresses: A list of IPv4Network's or IPv6Network's

Returns:
    A list of IPv4Network's or IPv6Network's depending on what we were
    passed.

"""
    to_merge = list(addresses)
    subnets = { }
    while to_merge:
        net = to_merge.pop()
        supernet = net.supernet()
        existing = subnets.get(supernet)
        if existing is None:
            subnets[supernet] = net
            continue
        if not existing != net:
            continue
        del subnets[supernet]
        to_merge.append(supernet)
    last = None
    for net in sorted(subnets.values()):
        while last and last.broadcast_address >= net.broadcast_address:
            pass
        yield net
        sorted(subnets.values())
        last = net


def collapse_addresses(addresses):
    """Collapse a list of IP objects.

Example:
    collapse_addresses([IPv4Network('192.0.2.0/25'),
                        IPv4Network('192.0.2.128/25')]) ->
                       [IPv4Network('192.0.2.0/24')]

Args:
    addresses: An iterable of IPv4Network or IPv6Network objects.

Returns:
    An iterator of the collapsed IPv(4|6)Network objects.

Raises:
    TypeError: If passed a list of mixed version objects.

"""
    addrs = []
    ips = []
    nets = []
    for ip in addresses:
        while isinstance(ip, _BaseAddress):
            if ips and ips[-1].version != ip.version:
                raise TypeError(f'''{ip!s} and {ips[-1]!s} are not of the same version''')
            ips.append(ip)
        if ip._prefixlen == ip.max_prefixlen:
            if ips and ips[-1].version != ip.version:
                raise TypeError(f'''{ip!s} and {ips[-1]!s} are not of the same version''')
            
            try:
                ips.append(ip.ip)
            except AttributeError:
                ips.append(ip.network_address)

            continue
        if nets and nets[-1].version != ip.version:
            raise TypeError(f'''{ip!s} and {nets[-1]!s} are not of the same version''')
        nets.append(ip)
    ips = sorted(set(ips))
    if ips:
        for first, last in _find_address_range(ips):
            addrs.extend(summarize_address_range(first, last))
    return _collapse_addresses_internal(addrs + nets)


def get_mixed_type_key(obj):
    """Return a key suitable for sorting between networks and addresses.

Address and Network objects are not sortable by default; they're
fundamentally different so the expression

    IPv4Address('192.0.2.0') <= IPv4Network('192.0.2.0/24')

doesn't make any sense.  There are some times however, where you may wish
to have ipaddress sort these for you anyway. If you need to do this, you
can use this function as the key= argument to sorted().

Args:
  obj: either a Network or Address object.
Returns:
  appropriate key.

"""
    if isinstance(obj, _BaseNetwork):
        return obj._get_networks_key()
    if isinstance(obj, _BaseAddress):
        return obj._get_address_key()
    return NotImplemented


class _IPAddressBase:
    '''The mother class.'''
    __slots__ = ()
    exploded = (lambda self: self._explode_shorthand_ip_string())()
    compressed = (lambda self: str(self))()
    reverse_pointer = (lambda self: self._reverse_pointer())()
    
    def _check_int_address(self, address):
        if address < 0:
            msg = '%d (< 0) is not permitted as an IPv%d address'
            raise AddressValueError(msg % (address, self.version))
        if address > self._ALL_ONES:
            msg = '%d (>= 2**%d) is not permitted as an IPv%d address'
            raise AddressValueError(msg % (address, self.max_prefixlen, self.version))

    
    def _check_packed_address(self, address, expected_len):
        '''%r (len %d != %d) is not permitted as an IPv%d address'''
        address_len = len(address)
        if address_len != expected_len:
            msg = '%r (len %d != %d) is not permitted as an IPv%d address'
            raise AddressValueError(msg % (address, address_len, expected_len, self.version))

    _ip_int_from_prefix = (lambda cls, prefixlen: cls._ALL_ONES ^ cls._ALL_ONES >> prefixlen)()
    _prefix_from_ip_int = (lambda cls, ip_int: trailing_zeroes = _count_righthand_zero_bits(ip_int, cls.max_prefixlen)prefixlen = cls.max_prefixlen - trailing_zeroesleading_ones = ip_int >> trailing_zeroesall_ones = (1 << prefixlen) - 1if leading_ones != all_ones:
byteslen = cls.max_prefixlen // 8details = ip_int.to_bytes(byteslen, 'big')msg = 'Netmask pattern %r mixes zeroes & ones'raise ValueError(msg % details)prefixlen)()
    _report_invalid_netmask = (lambda cls, netmask_str: msg = '%r is not a valid netmask' % netmask_strraise NetmaskValueError(msg) from None)()
    _prefix_from_prefix_string = (lambda cls, prefixlen_str: if not prefixlen_str.isascii() or not prefixlen_str.isdigit():
cls._report_invalid_netmask(prefixlen_str)try:
prefixlen = int(prefixlen_str)except ValueError:
cls._report_invalid_netmask(prefixlen_str)if not (0 <= prefixlen) or not (prefixlen <= cls.max_prefixlen):
cls._report_invalid_netmask(prefixlen_str)prefixlen)()
    _prefix_from_ip_string = (lambda cls, ip_str: try:
ip_int = cls._ip_int_from_string(ip_str)except AddressValueError:
cls._report_invalid_netmask(ip_str)try:
cls._prefix_from_ip_int(ip_int)except ValueError:
passexcept:
passip_int ^= cls._ALL_ONEStry:
cls._prefix_from_ip_int(ip_int)except ValueError:
cls._report_invalid_netmask(ip_str)None)()
    _split_addr_prefix = (lambda cls, address: if isinstance(address, (bytes, int)):
(address, cls.max_prefixlen)if not isinstance(address, tuple):
address = _split_optional_netmask(address)if len(address) > 1:
address(address[0], cls.max_prefixlen))()
    
    def __reduce__(self):
        return (self.__class__, (str(self),))


_address_fmt_re = None
_BaseAddress = <NODE:12>()
_BaseNetwork = <NODE:12>()

class _BaseConstants:
    _private_networks = []

_BaseNetwork._constants = _BaseConstants

class _BaseV4:
    '''Base IPv4 object.

The following methods are used by IPv4 objects in both single IP
addresses and networks.

'''
    __slots__ = ()
    version = 4
    _ALL_ONES = 2 ** IPV4LENGTH - 1
    max_prefixlen = IPV4LENGTH
    _netmask_cache = { }
    
    def _explode_shorthand_ip_string(self):
        return str(self)

    _make_netmask = (lambda cls, arg: if arg not in cls._netmask_cache:
if isinstance(arg, int):
prefixlen = argif not (0 <= prefixlen) or not (prefixlen <= cls.max_prefixlen):
cls._report_invalid_netmask(prefixlen)else:
try:
prefixlen = cls._prefix_from_prefix_string(arg)except NetmaskValueError:
prefixlen = cls._prefix_from_ip_string(arg)netmask = IPv4Address(cls._ip_int_from_prefix(prefixlen))cls._netmask_cache[arg] = (netmask, prefixlen)cls._netmask_cache[arg])()
    _ip_int_from_string = (lambda cls, ip_str: if not ip_str:
raise AddressValueError('Address cannot be empty')octets = ip_str.split('.')if len(octets) != 4:
raise AddressValueError('Expected 4 octets in %r' % ip_str)try:
int.from_bytes(map(cls._parse_octet, octets), 'big')except ValueError as exc:
raise AddressValueError(f'''{exc!s} in {ip_str!r}''') from None)()
    _parse_octet = (lambda cls, octet_str: if not octet_str:
raise ValueError('Empty octet not permitted')if not octet_str.isascii() or not octet_str.isdigit():
msg = 'Only decimal digits permitted in %r'raise ValueError(msg % octet_str)if len(octet_str) > 3:
msg = 'At most 3 characters permitted in %r'raise ValueError(msg % octet_str)if octet_str != '0' and octet_str[0] == '0':
msg = 'Leading zeros are not permitted in %r'raise ValueError(msg % octet_str)octet_int = int(octet_str, 10)if octet_int > 255:
raise ValueError('Octet %d (> 255) not permitted' % octet_int)octet_int)()
    _string_from_ip_int = (lambda cls, ip_int: '.'.join(map(str, ip_int.to_bytes(4, 'big'))))()
    
    def _reverse_pointer(self):
        '''Return the reverse DNS pointer name for the IPv4 address.

This implements the method described in RFC1035 3.5.

'''
        reverse_octets = str(self).split('.')[::-1]
        return '.'.join(reverse_octets) + '.in-addr.arpa'



class IPv4Address(_BaseAddress, _BaseV4):
    '''Represent and manipulate single IPv4 Addresses.'''
    __slots__ = ('_ip', '__weakref__')
    
    def __init__(self, address):
        """
Args:
    address: A string or integer representing the IP

      Additionally, an integer can be passed, so
      IPv4Address('192.0.2.1') == IPv4Address(3221225985).
      or, more generally
      IPv4Address(int(IPv4Address('192.0.2.1'))) ==
        IPv4Address('192.0.2.1')

Raises:
    AddressValueError: If ipaddress isn't a valid IPv4 address.

"""
        if isinstance(address, int):
            self._check_int_address(address)
            self._ip = address
            return None
        if isinstance(address, bytes):
            self._check_packed_address(address, 4)
            self._ip = int.from_bytes(address)
            return None
        addr_str = str(address)
        if '/' in addr_str:
            raise AddressValueError(f'''Unexpected \'/\' in {address!r}''')
        self._ip = self._ip_int_from_string(addr_str)

    packed = (lambda self: v4_int_to_packed(self._ip))()
    is_reserved = (lambda self: self in self._constants._reserved_network)()
    is_private = (lambda self: if any is any:
anyfor None in self._constants._private_networks():
while not None:
passif all is all:
allfor None in self._constants._private_networks_exceptions():
while None:
passFalseTrueall and (lambda .0: for net in .0:
self not in net.0)(self._constants._private_networks_exceptions())
)()()
    is_global = (lambda self: self not in self._constants._public_network and not (self.is_private))()()
    is_multicast = (lambda self: self in self._constants._multicast_network)()
    is_unspecified = (lambda self: self == self._constants._unspecified_address)()
    is_loopback = (lambda self: self in self._constants._loopback_network)()
    is_link_local = (lambda self: self in self._constants._linklocal_network)()
    ipv6_mapped = (lambda self: IPv6Address(f'''::ffff:{self}'''))()


class IPv4Interface(IPv4Address):
    
    def __init__(self, address):
        addr, mask = self._split_addr_prefix(address)
        IPv4Address.__init__(self, addr)
        self.network = IPv4Network((addr, mask), strict = False)
        self.netmask = self.network.netmask
        self._prefixlen = self.network._prefixlen

    hostmask = (lambda self: self.network.hostmask)()
    
    def __str__(self):
        '''%s/%d'''
        return '%s/%d' % (self._string_from_ip_int(self._ip), self._prefixlen)

    
    def __eq__(self, other):
        address_equal = IPv4Address.__eq__(self, other)
        if address_equal is NotImplemented or not address_equal:
            return address_equal
        
        try:
            return self.network == other.network
        except AttributeError:
            return False


    
    def __lt__(self, other):
        address_less = IPv4Address.__lt__(self, other)
        if address_less is NotImplemented:
            return NotImplemented
        
        try:
            return self.network == other.network and address_less
        except AttributeError:
            return False


    
    def __hash__(self):
        return hash((self._ip, self._prefixlen, int(self.network.network_address)))

    __reduce__ = _IPAddressBase.__reduce__
    ip = (lambda self: IPv4Address(self._ip))()
    with_prefixlen = (lambda self: f'''{self._string_from_ip_int(self._ip)!s}/{self._prefixlen!s}''')()
    with_netmask = (lambda self: f'''{self._string_from_ip_int(self._ip)!s}/{self.netmask!s}''')()
    with_hostmask = (lambda self: f'''{self._string_from_ip_int(self._ip)!s}/{self.hostmask!s}''')()


class IPv4Network(_BaseNetwork, _BaseV4):
    """This class represents and manipulates 32-bit IPv4 network + addresses..

Attributes: [examples for IPv4Network('192.0.2.0/27')]
    .network_address: IPv4Address('192.0.2.0')
    .hostmask: IPv4Address('0.0.0.31')
    .broadcast_address: IPv4Address('192.0.2.32')
    .netmask: IPv4Address('255.255.255.224')
    .prefixlen: 27

"""
    _address_class = IPv4Address
    
    def __init__(self, address, strict = True):
        """Instantiate a new IPv4 network object.

Args:
    address: A string or integer representing the IP [& network].
      '192.0.2.0/24'
      '192.0.2.0/255.255.255.0'
      '192.0.2.0/0.0.0.255'
      are all functionally the same in IPv4. Similarly,
      '192.0.2.1'
      '192.0.2.1/255.255.255.255'
      '192.0.2.1/32'
      are also functionally equivalent. That is to say, failing to
      provide a subnetmask will create an object with a mask of /32.

      If the mask (portion after the / in the argument) is given in
      dotted quad form, it is treated as a netmask if it starts with a
      non-zero field (e.g. /255.0.0.0 == /8) and as a hostmask if it
      starts with a zero field (e.g. 0.255.255.255 == /8), with the
      single exception of an all-zero mask which is treated as a
      netmask == /0. If no mask is given, a default of /32 is used.

      Additionally, an integer can be passed, so
      IPv4Network('192.0.2.1') == IPv4Network(3221225985)
      or, more generally
      IPv4Interface(int(IPv4Interface('192.0.2.1'))) ==
        IPv4Interface('192.0.2.1')

Raises:
    AddressValueError: If ipaddress isn't a valid IPv4 address.
    NetmaskValueError: If the netmask isn't valid for
      an IPv4 address.
    ValueError: If strict is True and a network address is not
      supplied.
"""
        (addr, mask) = self._split_addr_prefix(address)
        self.network_address = IPv4Address(addr)
        (self.netmask, self._prefixlen) = self._make_netmask(mask)
        packed = int(self.network_address)
        if packed & int(self.netmask) != packed:
            if strict:
                raise ValueError('%s has host bits set' % self)
            self.network_address = IPv4Address(packed & int(self.netmask))
        if self._prefixlen == self.max_prefixlen - 1:
            self.hosts = self.__iter__
            return None
        if self._prefixlen == self.max_prefixlen:
            
            self.hosts = lambda : iter((IPv4Address(addr),))
            return None

    is_global = (lambda self: not (self.network_address in IPv4Network('100.64.0.0/10') and self.broadcast_address in IPv4Network('100.64.0.0/10')) and not (self.is_private))()()


class _IPv4Constants:
    _linklocal_network = IPv4Network('169.254.0.0/16')
    _loopback_network = IPv4Network('127.0.0.0/8')
    _multicast_network = IPv4Network('224.0.0.0/4')
    _public_network = IPv4Network('100.64.0.0/10')
    _private_networks = [
        IPv4Network('0.0.0.0/8'),
        IPv4Network('10.0.0.0/8'),
        IPv4Network('127.0.0.0/8'),
        IPv4Network('169.254.0.0/16'),
        IPv4Network('172.16.0.0/12'),
        IPv4Network('192.0.0.0/24'),
        IPv4Network('192.0.0.170/31'),
        IPv4Network('192.0.2.0/24'),
        IPv4Network('192.168.0.0/16'),
        IPv4Network('198.18.0.0/15'),
        IPv4Network('198.51.100.0/24'),
        IPv4Network('203.0.113.0/24'),
        IPv4Network('240.0.0.0/4'),
        IPv4Network('255.255.255.255/32')]
    _private_networks_exceptions = [
        IPv4Network('192.0.0.9/32'),
        IPv4Network('192.0.0.10/32')]
    _reserved_network = IPv4Network('240.0.0.0/4')
    _unspecified_address = IPv4Address('0.0.0.0')

IPv4Address._constants = _IPv4Constants
IPv4Network._constants = _IPv4Constants

class _BaseV6:
    '''Base IPv6 object.

The following methods are used by IPv6 objects in both single IP
addresses and networks.

'''
    __slots__ = ()
    version = 6
    _ALL_ONES = 2 ** IPV6LENGTH - 1
    _HEXTET_COUNT = 8
    _HEX_DIGITS = frozenset('0123456789ABCDEFabcdef')
    max_prefixlen = IPV6LENGTH
    _netmask_cache = { }
    _make_netmask = (lambda cls, arg: if arg not in cls._netmask_cache:
if isinstance(arg, int):
prefixlen = argif not (0 <= prefixlen) or not (prefixlen <= cls.max_prefixlen):
cls._report_invalid_netmask(prefixlen)else:
prefixlen = cls._prefix_from_prefix_string(arg)netmask = IPv6Address(cls._ip_int_from_prefix(prefixlen))cls._netmask_cache[arg] = (netmask, prefixlen)cls._netmask_cache[arg])()
    _ip_int_from_string = (lambda cls, ip_str: if not ip_str:
raise AddressValueError('Address cannot be empty')if len(ip_str) > 45:
shorten = ip_strif len(shorten) > 100:
shorten = f'''{ip_str[slice(None, 45, None)]}({len(ip_str) - 90} chars elided){ip_str[-45:]}'''raise AddressValueError(f'''At most 45 characters expected in {shorten!r}''')_max_parts = cls._HEXTET_COUNT + 1parts = ip_str.split(':', maxsplit = _max_parts)_min_parts = 3if len(parts) < _min_parts:
msg = 'At least %d parts expected in %r' % (_min_parts, ip_str)raise AddressValueError(msg)if '.' in parts[-1]:
try:
ipv4_int = IPv4Address(parts.pop())._ipexcept AddressValueError as exc:
raise AddressValueError(f'''{exc!s} in {ip_str!r}''') from Noneparts.append('%x' % (ipv4_int >> 16 & 65535))parts.append('%x' % (ipv4_int & 65535))if len(parts) > _max_parts:
msg = 'At most %d colons permitted in %r' % (_max_parts - 1, ip_str)raise AddressValueError(msg)skip_index = Nonefor i in range(1, len(parts) - 1):
while parts[i]:
passif skip_index is not None:
msg = "At most one '::' permitted in %r" % ip_strraise AddressValueError(msg)skip_index = iif skip_index is not None:
parts_hi = skip_indexparts_lo = len(parts) - skip_index - 1if not parts[0]:
parts_hi -= 1if parts_hi:
msg = "Leading ':' only permitted as part of '::' in %r"raise AddressValueError(msg % ip_str)if not parts[-1]:
parts_lo -= 1if parts_lo:
msg = "Trailing ':' only permitted as part of '::' in %r"raise AddressValueError(msg % ip_str)parts_skipped = cls._HEXTET_COUNT - (parts_hi + parts_lo)if parts_skipped < 1:
msg = "Expected at most %d other parts with '::' in %r"raise AddressValueError(msg % (cls._HEXTET_COUNT - 1, ip_str))elif len(parts) != cls._HEXTET_COUNT:
msg = "Exactly %d parts expected without '::' in %r"raise AddressValueError(msg % (cls._HEXTET_COUNT, ip_str))if not parts[0]:
msg = "Leading ':' only permitted as part of '::' in %r"raise AddressValueError(msg % ip_str)if not parts[-1]:
msg = "Trailing ':' only permitted as part of '::' in %r"raise AddressValueError(msg % ip_str)parts_hi = len(parts)parts_lo = 0parts_skipped = 0try:
ip_int = 0for i in range(parts_hi):
ip_int <<= 16ip_int |= cls._parse_hextet(parts[i])ip_int <<= 16 * parts_skippedfor i in range(-parts_lo, 0):
ip_int <<= 16ip_int |= cls._parse_hextet(parts[i])ip_intexcept ValueError as exc:
raise AddressValueError(f'''{exc!s} in {ip_str!r}''') from None)()
    _parse_hextet = (lambda cls, hextet_str: if not cls._HEX_DIGITS.issuperset(hextet_str):
raise ValueError('Only hex digits permitted in %r' % hextet_str)if len(hextet_str) > 4:
msg = 'At most 4 characters permitted in %r'raise ValueError(msg % hextet_str)int(hextet_str, 16))()
    _compress_hextets = (lambda cls, hextets: best_doublecolon_start = -1best_doublecolon_len = 0doublecolon_start = -1doublecolon_len = 0for index, hextet in enumerate(hextets):
while hextet == '0':
doublecolon_len += 1if doublecolon_start == -1:
doublecolon_start = indexif doublecolon_len > best_doublecolon_len:
best_doublecolon_len = doublecolon_lenbest_doublecolon_start = doublecolon_startcontinuedoublecolon_len = 0doublecolon_start = -1if best_doublecolon_len > 1:
best_doublecolon_end = best_doublecolon_start + best_doublecolon_lenif best_doublecolon_end == len(hextets):
hextets += [
'']hextets[best_doublecolon_start:best_doublecolon_end] = [
'']if best_doublecolon_start == 0:
hextets = [
''] + hextetshextets)()
    _string_from_ip_int = (lambda cls, ip_int = None: if ip_int is None:
ip_int = int(cls._ip)if ip_int > cls._ALL_ONES:
raise ValueError('IPv6 address is too large')hex_str = '%032x' % ip_inttry:
for x in range(0, 32, 4):
passx = range(0, 32, 4)hextets = []x = xhextets = cls._compress_hextets(hextets)':'.join(hextets)# WARNING: Decompyle incomplete
)()
    
    def _explode_shorthand_ip_string(self):
        '''Expand a shortened IPv6 address.

Returns:
    A string, the expanded IPv6 address.

'''
        if isinstance(self, IPv6Network):
            ip_str = str(self.network_address)
        elif isinstance(self, IPv6Interface):
            ip_str = str(self.ip)
        else:
            ip_str = str(self)
        ip_int = self._ip_int_from_string(ip_str)
        hex_str = '%032x' % ip_int
        
        try:
            for x in range(0, 32, 4):
                pass
        x = range(0, 32, 4)

        parts = []
        x = x
        if isinstance(self, (_BaseNetwork, IPv6Interface)):
            return '%s/%d' % (':'.join(parts), self._prefixlen)
        return ':'.join(parts)
    # WARNING: Decompyle incomplete

    
    def _reverse_pointer(self):
        '''Return the reverse DNS pointer name for the IPv6 address.

This implements the method described in RFC3596 2.5.

'''
        reverse_chars = self.exploded[::-1].replace(':', '')
        return '.'.join(reverse_chars) + '.ip6.arpa'

    _split_scope_id = (lambda ip_str: (addr, sep, scope_id) = ip_str.partition('%')if not sep:
scope_id = None(addr, scope_id)if not scope_id or '%' in scope_id:
raise AddressValueError('Invalid IPv6 address: "%r"' % ip_str)(addr, scope_id))()


class IPv6Address(_BaseAddress, _BaseV6):
    '''Represent and manipulate single IPv6 Addresses.'''
    __slots__ = ('_ip', '_scope_id', '__weakref__')
    
    def __init__(self, address):
        """Instantiate a new IPv6 address object.

Args:
    address: A string or integer representing the IP

      Additionally, an integer can be passed, so
      IPv6Address('2001:db8::') ==
        IPv6Address(42540766411282592856903984951653826560)
      or, more generally
      IPv6Address(int(IPv6Address('2001:db8::'))) ==
        IPv6Address('2001:db8::')

Raises:
    AddressValueError: If address isn't a valid IPv6 address.

"""
        if isinstance(address, int):
            self._check_int_address(address)
            self._ip = address
            self._scope_id = None
            return None
        if isinstance(address, bytes):
            self._check_packed_address(address, 16)
            self._ip = int.from_bytes(address, 'big')
            self._scope_id = None
            return None
        addr_str = str(address)
        if '/' in addr_str:
            raise AddressValueError(f'''Unexpected \'/\' in {address!r}''')
        addr_str = ()
        self._ip_int_from_string(addr_str) = self._split_scope_id(addr_str)
        return None
    # WARNING: Decompyle incomplete

    
    def _explode_shorthand_ip_string(self):
        ipv4_mapped = self.ipv4_mapped
        if ipv4_mapped is None:
            # unsupported opcode LOAD_SUPER_ATTR
            return self()
        prefix_len = 30
        # unsupported opcode LOAD_SUPER_ATTR
        raw_exploded_str = self()
        return f'''{raw_exploded_str[:prefix_len]}{ipv4_mapped!s}'''
    # WARNING: Decompyle incomplete

    
    def _reverse_pointer(self):
        ipv4_mapped = self.ipv4_mapped
        if ipv4_mapped is None:
            # unsupported opcode LOAD_SUPER_ATTR
            return self()
        prefix_len = 30
        # unsupported opcode LOAD_SUPER_ATTR
        raw_exploded_str = self()[:prefix_len]
        ipv4_int = ipv4_mapped._ip
        reverse_chars = f'''{raw_exploded_str}{ipv4_int:008x}'''[::-1].replace(':', '')
        return '.'.join(reverse_chars) + '.ip6.arpa'
    # WARNING: Decompyle incomplete

    
    def _ipv4_mapped_ipv6_to_str(self):
        """Return convenient text representation of IPv4-mapped IPv6 address

See RFC 4291 2.5.5.2, 2.2 p.3 for details.

Returns:
    A string, 'x:x:x:x:x:x:d.d.d.d', where the 'x's are the hexadecimal values of
    the six high-order 16-bit pieces of the address, and the 'd's are
    the decimal values of the four low-order 8-bit pieces of the
    address (standard IPv4 representation) as defined in RFC 4291 2.2 p.3.

"""
        ipv4_mapped = self.ipv4_mapped
        if ipv4_mapped is None:
            raise AddressValueError('Can not apply to non-IPv4-mapped IPv6 address %s' % str(self))
        high_order_bits = self._ip >> 32
        return f'''{self._string_from_ip_int(high_order_bits)!s}:{str(ipv4_mapped)!s}'''

    
    def __str__(self):
        ipv4_mapped = self.ipv4_mapped
        if ipv4_mapped is None:
            # unsupported opcode LOAD_SUPER_ATTR
            ip_str = self()
        else:
            ip_str = self._ipv4_mapped_ipv6_to_str()
        if self._scope_id:
            return ip_str + '%' + self._scope_id
        return ip_str
    # WARNING: Decompyle incomplete

    
    def __hash__(self):
        return hash((self._ip, self._scope_id))

    
    def __eq__(self, other):
        # unsupported opcode LOAD_SUPER_ATTR
        address_equal = self(other)
        if address_equal is NotImplemented:
            return NotImplemented
        if not address_equal:
            return False
        return self._scope_id == getattr(other, '_scope_id', None)
    # WARNING: Decompyle incomplete

    
    def __reduce__(self):
        return (self.__class__, (str(self),))

    scope_id = (lambda self: self._scope_id)()
    packed = (lambda self: v6_int_to_packed(self._ip))()
    is_multicast = (lambda self: ipv4_mapped = self.ipv4_mappedif ipv4_mapped is not None:
ipv4_mapped.is_multicastself in self._constants._multicast_network)()
    is_reserved = (lambda self: ipv4_mapped = self.ipv4_mappedif ipv4_mapped is not None:
ipv4_mapped.is_reservedif any is any:
anyfor None in self._constants._reserved_networks():
while not None:
passTrueFalse(lambda .0: for x in .0:
self in x.0)(self._constants._reserved_networks())
)()
    is_link_local = (lambda self: ipv4_mapped = self.ipv4_mappedif ipv4_mapped is not None:
ipv4_mapped.is_link_localself in self._constants._linklocal_network)()
    is_site_local = (lambda self: self in self._constants._sitelocal_network)()
    is_private = (lambda self: ipv4_mapped = self.ipv4_mappedif ipv4_mapped is not None:
ipv4_mapped.is_privateif any is any:
anyfor None in self._constants._private_networks():
while not None:
passif all is all:
allfor None in self._constants._private_networks_exceptions():
while None:
passFalseTrueall and (lambda .0: for net in .0:
self not in net.0)(self._constants._private_networks_exceptions())
)()()
    is_global = (lambda self: ipv4_mapped = self.ipv4_mappedif ipv4_mapped is not None:
ipv4_mapped.is_globalnot (self.is_private))()
    is_unspecified = (lambda self: ipv4_mapped = self.ipv4_mappedif ipv4_mapped is not None:
ipv4_mapped.is_unspecifiedself._ip == 0)()
    is_loopback = (lambda self: ipv4_mapped = self.ipv4_mappedif ipv4_mapped is not None:
ipv4_mapped.is_loopbackself._ip == 1)()
    ipv4_mapped = (lambda self: None if self._ip >> 32 != 65535 else IPv4Address(self._ip & 0xFFFFFFFF))()
    teredo = (lambda self: None if self._ip >> 96 != 536936448 else (IPv4Address(self._ip >> 64 & 0xFFFFFFFF), IPv4Address(~(self._ip) & 0xFFFFFFFF)))()
    sixtofour = (lambda self: None if self._ip >> 112 != 8194 else IPv4Address(self._ip >> 80 & 0xFFFFFFFF))()


class IPv6Interface(IPv6Address):
    
    def __init__(self, address):
        addr, mask = self._split_addr_prefix(address)
        IPv6Address.__init__(self, addr)
        self.network = IPv6Network((addr, mask), strict = False)
        self.netmask = self.network.netmask
        self._prefixlen = self.network._prefixlen

    hostmask = (lambda self: self.network.hostmask)()
    
    def __str__(self):
        '''%s/%d'''
        # unsupported opcode LOAD_SUPER_ATTR
        return __class__ % (self(), self._prefixlen)
    # WARNING: Decompyle incomplete

    
    def __eq__(self, other):
        address_equal = IPv6Address.__eq__(self, other)
        if address_equal is NotImplemented or not address_equal:
            return address_equal
        
        try:
            return self.network == other.network
        except AttributeError:
            return False


    
    def __lt__(self, other):
        address_less = IPv6Address.__lt__(self, other)
        if address_less is NotImplemented:
            return address_less
        
        try:
            return self.network == other.network and address_less
        except AttributeError:
            return False


    
    def __hash__(self):
        return hash((self._ip, self._prefixlen, int(self.network.network_address)))

    __reduce__ = _IPAddressBase.__reduce__
    ip = (lambda self: IPv6Address(self._ip))()
    with_prefixlen = (lambda self: f'''{self._string_from_ip_int(self._ip)!s}/{self._prefixlen!s}''')()
    with_netmask = (lambda self: f'''{self._string_from_ip_int(self._ip)!s}/{self.netmask!s}''')()
    with_hostmask = (lambda self: f'''{self._string_from_ip_int(self._ip)!s}/{self.hostmask!s}''')()
    is_unspecified = (lambda self: self._ip == 0 and self.network.is_unspecified)()
    is_loopback = (lambda self: # unsupported opcode LOAD_SUPER_ATTRself and self.network.is_loopback# WARNING: Decompyle incomplete
)()


class IPv6Network(_BaseNetwork, _BaseV6):
    """This class represents and manipulates 128-bit IPv6 networks.

Attributes: [examples for IPv6('2001:db8::1000/124')]
    .network_address: IPv6Address('2001:db8::1000')
    .hostmask: IPv6Address('::f')
    .broadcast_address: IPv6Address('2001:db8::100f')
    .netmask: IPv6Address('ffff:ffff:ffff:ffff:ffff:ffff:ffff:fff0')
    .prefixlen: 124

"""
    _address_class = IPv6Address
    
    def __init__(self, address, strict = True):
        """Instantiate a new IPv6 Network object.

Args:
    address: A string or integer representing the IPv6 network or the
      IP and prefix/netmask.
      '2001:db8::/128'
      '2001:db8:0000:0000:0000:0000:0000:0000/128'
      '2001:db8::'
      are all functionally the same in IPv6.  That is to say,
      failing to provide a subnetmask will create an object with
      a mask of /128.

      Additionally, an integer can be passed, so
      IPv6Network('2001:db8::') ==
        IPv6Network(42540766411282592856903984951653826560)
      or, more generally
      IPv6Network(int(IPv6Network('2001:db8::'))) ==
        IPv6Network('2001:db8::')

    strict: A boolean. If true, ensure that we have been passed
      A true network address, eg, 2001:db8::1000/124 and not an
      IP address on a network, eg, 2001:db8::1/124.

Raises:
    AddressValueError: If address isn't a valid IPv6 address.
    NetmaskValueError: If the netmask isn't valid for
      an IPv6 address.
    ValueError: If strict was True and a network address was not
      supplied.
"""
        (addr, mask) = self._split_addr_prefix(address)
        self.network_address = IPv6Address(addr)
        (self.netmask, self._prefixlen) = self._make_netmask(mask)
        packed = int(self.network_address)
        if packed & int(self.netmask) != packed:
            if strict:
                raise ValueError('%s has host bits set' % self)
            self.network_address = IPv6Address(packed & int(self.netmask))
        if self._prefixlen == self.max_prefixlen - 1:
            self.hosts = self.__iter__
            return None
        if self._prefixlen == self.max_prefixlen:
            
            self.hosts = lambda : iter((IPv6Address(addr),))
            return None

    
    def hosts(self):
        """Generate Iterator over usable hosts in a network.

This is like __iter__ except it doesn't return the
Subnet-Router anycast address.

"""
        network = int(self.network_address)
        broadcast = int(self.broadcast_address)
        for x in range(network + 1, broadcast + 1):
            yield self._address_class(x)
            range(network + 1, broadcast + 1)

    is_site_local = (lambda self: self.network_address.is_site_local and self.broadcast_address.is_site_local)()


class _IPv6Constants:
    _linklocal_network = IPv6Network('fe80::/10')
    _multicast_network = IPv6Network('ff00::/8')
    _private_networks = [
        IPv6Network('::1/128'),
        IPv6Network('::/128'),
        IPv6Network('::ffff:0:0/96'),
        IPv6Network('64:ff9b:1::/48'),
        IPv6Network('100::/64'),
        IPv6Network('2001::/23'),
        IPv6Network('2001:db8::/32'),
        IPv6Network('2002::/16'),
        IPv6Network('3fff::/20'),
        IPv6Network('fc00::/7'),
        IPv6Network('fe80::/10')]
    _private_networks_exceptions = [
        IPv6Network('2001:1::1/128'),
        IPv6Network('2001:1::2/128'),
        IPv6Network('2001:3::/32'),
        IPv6Network('2001:4:112::/48'),
        IPv6Network('2001:20::/28'),
        IPv6Network('2001:30::/28')]
    _reserved_networks = [
        IPv6Network('::/8'),
        IPv6Network('100::/8'),
        IPv6Network('200::/7'),
        IPv6Network('400::/6'),
        IPv6Network('800::/5'),
        IPv6Network('1000::/4'),
        IPv6Network('4000::/3'),
        IPv6Network('6000::/3'),
        IPv6Network('8000::/3'),
        IPv6Network('A000::/3'),
        IPv6Network('C000::/3'),
        IPv6Network('E000::/4'),
        IPv6Network('F000::/5'),
        IPv6Network('F800::/6'),
        IPv6Network('FE00::/9')]
    _sitelocal_network = IPv6Network('fec0::/10')

IPv6Address._constants = _IPv6Constants
IPv6Network._constants = _IPv6Constants
