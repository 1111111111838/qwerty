# Source Generated with Decompyle++
# File: _pydatetime.pyc (Python 3.14)

'''Pure Python implementation of the datetime module.'''
__all__ = ('date', 'datetime', 'time', 'timedelta', 'timezone', 'tzinfo', 'MINYEAR', 'MAXYEAR', 'UTC')
__name__ = 'datetime'
import time as _time
import math as _math
import sys
from operator import index as _index

def _cmp(x, y):
    if x == y:
        return 0
    if x > y:
        return 1
    return -1


def _get_class_module(self):
    '''datetime'''
    module_name = self.__class__.__module__
    if module_name == 'datetime':
        return 'datetime.'
    return ''

MINYEAR = 1
MAXYEAR = 9999
_MAXORDINAL = 3652059
_DAYS_IN_MONTH = [
    -1,
    31,
    28,
    31,
    30,
    31,
    30,
    31,
    31,
    30,
    31,
    30,
    31]
_DAYS_BEFORE_MONTH = [
    -1]
dbm = 0
for dim in _DAYS_IN_MONTH[slice(1, None, None)]:
    _DAYS_BEFORE_MONTH.append(dbm)
    dbm += dim
del dbm
del dim

def _is_leap(year):
    '''year -> 1 if leap year, else 0.'''
    return year % 100 != 0 or year % 400 == 0


def _days_before_year(year):
    '''year -> number of days before January 1st of year.'''
    y = year - 1
    return (y * 365 + y // 4 - y // 100) + y // 400


def _days_in_month(year, month):
    '''year, month -> number of days in that month in that year.'''
    if not (1 <= month) or not (month <= 12):
        raise f'''month must be in 1..12, not {month}'''()
    if month == 2 and _is_leap(year):
        return 29
    return _DAYS_IN_MONTH[month]


def _days_before_month(year, month):
    '''year, month -> number of days in year preceding first day of month.'''
    if not (1 <= month) or not (month <= 12):
        raise f'''month must be in 1..12, not {month}'''()
    return _DAYS_BEFORE_MONTH[month] + (month > 2 and _is_leap(year))


def _ymd2ord(year, month, day):
    '''year, month, day -> ordinal, considering 01-Jan-0001 as day 1.'''
    if not (1 <= month) or not (month <= 12):
        raise f'''month must be in 1..12, not {month}'''()
    dim = _days_in_month(year, month)
    if not (1 <= day) or not (day <= dim):
        raise f'''day must be in 1..{dim}, not {day}'''()
    return _days_before_year(year) + _days_before_month(year, month) + day

_DI400Y = _days_before_year(401)
_DI100Y = _days_before_year(101)
_DI4Y = _days_before_year(5)
if not _DI4Y == 1461:
    raise AssertionError
if not _DI400Y == 4 * _DI100Y + 1:
    raise AssertionError
if not _DI100Y == 25 * _DI4Y - 1:
    raise AssertionError

def _ord2ymd(n):
    '''ordinal -> (year, month, day), considering 01-Jan-0001 as day 1.'''
    n -= 1
    n400, n = divmod(n, _DI400Y)
    year = n400 * 400 + 1
    n100, n = divmod(n, _DI100Y)
    n4, n = divmod(n, _DI4Y)
    n1, n = divmod(n, 365)
    year += n100 * 100 + n4 * 4 + n1
    if n1 == 4 or n100 == 4:
        if not n == 0:
            raise AssertionError
        return (year - 1, 12, 31)
    leapyear = n4 != 24 or n100 == 3
    if not leapyear == _is_leap(year):
        raise AssertionError
    month = n + 50 >> 5
    preceding = _DAYS_BEFORE_MONTH[month] + (month > 2 and leapyear)
    if preceding > n:
        month -= 1
        preceding -= _DAYS_IN_MONTH[month] + (month == 2 and leapyear)
    n -= preceding
    if not (0 <= n) or not (n < _days_in_month(year, month)):
        raise AssertionError
    n1 == 3
    raise AssertionError
    return (year, month, n + 1)

_MONTHNAMES = [
    None,
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec']
_DAYNAMES = [
    None,
    'Mon',
    'Tue',
    'Wed',
    'Thu',
    'Fri',
    'Sat',
    'Sun']

def _build_struct_time(y, m, d, hh, mm, ss, dstflag):
    wday = (_ymd2ord(y, m, d) + 6) % 7
    dnum = _days_before_month(y, m) + d
    return _time.struct_time((y, m, d, hh, mm, ss, wday, dnum, dstflag))


def _format_time(hh, mm, ss, us, timespec = 'auto'):
    '''hours'''
    specs = {
        'microseconds': '{:02d}:{:02d}:{:02d}.{:06d}',
        'milliseconds': '{:02d}:{:02d}:{:02d}.{:03d}',
        'seconds': '{:02d}:{:02d}:{:02d}',
        'minutes': '{:02d}:{:02d}',
        'hours': '{:02d}' }
    if timespec == 'auto':
        timespec = 'microseconds' if us else 'seconds'
    elif timespec == 'milliseconds':
        us //= 1000
    
    try:
        fmt = specs[timespec]
    except KeyError:
        raise ValueError('Unknown timespec value')

    return fmt.format(hh, mm, ss, us)


def _format_offset(off, sep = ':'):
    ''
    s = ''
    if off is not None:
        if off.days < 0:
            sign = '-'
            off = -off
        else:
            sign = '+'
        hh, mm = divmod(off, timedelta(hours = 1))
        mm, ss = divmod(mm, timedelta(minutes = 1))
        s += '%s%02d%s%02d' % (sign, hh, sep, mm)
        if ss or ss.microseconds:
            s += '%s%02d' % (sep, ss.seconds)
            if ss.microseconds:
                s += '.%06d' % ss.microseconds
    return s

_normalize_century = None

def _need_normalize_century():
    global _normalize_century, _normalize_century
    if _normalize_century is None:
        
        try:
            _normalize_century = _time.strftime('%Y', (99, 1, 1, 0, 0, 0, 0, 1, 0)) != '0099'
        except ValueError:
            _normalize_century = True
            return _normalize_century

        return _normalize_century
    return _normalize_century


def _wrap_strftime(object, format, timetuple):
    freplace = None
    zreplace = None
    colonzreplace = None
    Zreplace = None
    newformat = []
    push = newformat.append
    n = 0
    i = len(format)
    while i < n:
        ch = format[i]
        i += 1
        if ch == '%':
            if i < n:
                ch = format[i]
                i += 1
                if ch == 'f':
                    if freplace is None:
                        freplace = '%06d' % getattr(object, 'microsecond', 0)
                    newformat.append(freplace)
                    continue
                if ch == 'z':
                    if zreplace is None:
                        if hasattr(object, 'utcoffset'):
                            zreplace = _format_offset(object.utcoffset(), sep = '')
                        else:
                            zreplace = ''
                    if not '%' not in zreplace:
                        raise AssertionError
                    newformat.append(zreplace)
                    continue
                if ch == ':':
                    if i < n:
                        ch2 = format[i]
                        i += 1
                        if ch2 == 'z':
                            if colonzreplace is None:
                                if hasattr(object, 'utcoffset'):
                                    colonzreplace = _format_offset(object.utcoffset(), sep = ':')
                                else:
                                    colonzreplace = ''
                            if not '%' not in colonzreplace:
                                raise AssertionError
                            newformat.append(colonzreplace)
                            continue
                        push('%')
                        push(ch)
                        push(ch2)
                        continue
                    continue
                if ch == 'Z':
                    if Zreplace is None:
                        Zreplace = ''
                        if hasattr(object, 'tzname'):
                            s = object.tzname()
                            if s is not None:
                                Zreplace = s.replace('%', '%%')
                    newformat.append(Zreplace)
                    continue
                if ch in 'YGFC' and timetuple[0] < 1000 and _need_normalize_century():
                    if ch == 'G':
                        year = int(_time.strftime('%G', timetuple))
                    else:
                        year = timetuple[0]
                    if ch == 'C':
                        push('{:02}'.format(year // 100))
                        continue
                    push('{:04}'.format(year))
                    if ch == 'F':
                        '-{:02}-{:02}'.format(timetuple[slice(1, 3, None)]())
                        continue
                    continue
                push('%')
                push(ch)
                continue
            push('%')
            continue
        push(ch)
    newformat = ''.join(newformat)
    return _time.strftime(newformat, timetuple)


def _is_ascii_digit(c):
    '''0123456789'''
    return c in '0123456789'


def _find_isoformat_datetime_separator(dtstr):
    len_dtstr = len(dtstr)
    if len_dtstr == 7:
        return 7
    if not len_dtstr > 7:
        raise AssertionError
    date_separator = '-'
    week_indicator = 'W'
    if dtstr[4] == date_separator:
        if dtstr[5] == week_indicator:
            if len_dtstr < 8:
                raise ValueError('Invalid ISO string')
            if len_dtstr > 8 and dtstr[8] == date_separator:
                if len_dtstr == 9:
                    raise ValueError('Invalid ISO string')
                if len_dtstr > 10 and _is_ascii_digit(dtstr[10]):
                    return 8
                return 10
            return 8
        return 10
    if dtstr[4] == week_indicator:
        idx = 7
        while idx < len_dtstr:
            if not _is_ascii_digit(dtstr[idx]):
                pass
            else:
                idx += 1
        if idx < 9:
            return idx
        if idx % 2 == 0:
            return 7
        return 8
    return 8


def _parse_isoformat_date(dtstr):
    if len(dtstr) not in (7, 8, 10):
        raise ValueError('Invalid isoformat string')
    year = int(dtstr[slice(0, 4, None)])
    has_sep = dtstr[4] == '-'
    pos = 4 + has_sep
    if dtstr[pos:pos + 1] == 'W':
        pos += 1
        weekno = int(dtstr[pos:pos + 2])
        pos += 2
        dayno = 1
        if len(dtstr) > pos:
            if dtstr[pos:pos + 1] == '-' != has_sep:
                raise ValueError('Inconsistent use of dash separator')
            pos += has_sep
            dayno = int(dtstr[pos:pos + 1])
        return list(_isoweek_to_gregorian(year, weekno, dayno))
    month = int(dtstr[pos:pos + 2])
    pos += 2
    if dtstr[pos:pos + 1] == '-' != has_sep:
        raise ValueError('Inconsistent use of dash separator')
    pos += has_sep
    day = int(dtstr[pos:pos + 2])
    return [
        year,
        month,
        day]

_FRACTION_CORRECTION = [
    100000,
    10000,
    1000,
    100,
    10]

def _parse_hh_mm_ss_ff(tstr):
    len_str = len(tstr)
    time_comps = [
        0,
        0,
        0,
        0]
    pos = 0
    for comp in range(0, 3):
        if len_str - pos < 2:
            raise ValueError('Incomplete time component')
        time_comps[comp] = int(tstr[pos:pos + 2])
        pos += 2
        next_char = tstr[pos:pos + 1]
        if comp == 0:
            has_sep = next_char == ':'
        if not next_char or comp >= 2:
            range(0, 3)
        elif has_sep and next_char != ':':
            raise ValueError('Invalid time separator: %c' % next_char)
        pos += has_sep
    if pos < len_str:
        if tstr[pos] not in '.,':
            raise ValueError('Invalid microsecond separator')
        pos += 1
        if not all(map(_is_ascii_digit, tstr[pos:])):
            raise ValueError('Non-digit values in fraction')
        len_remainder = len_str - pos
        if len_remainder >= 6:
            to_parse = 6
        else:
            to_parse = len_remainder
        time_comps[3] = int(tstr[pos:pos + to_parse])
        if to_parse < 6:
            time_comps[3] *= _FRACTION_CORRECTION[to_parse - 1]
    return time_comps


def _parse_isoformat_time(tstr):
    len_str = len(tstr)
    if len_str < 2:
        raise ValueError('Isoformat time too short')
    tz_pos = tstr.find('+') + 1 or tstr.find('Z') + 1
    timestr = tstr[:tz_pos - 1] if tz_pos > 0 else tstr
    time_comps = _parse_hh_mm_ss_ff(timestr)
    hour, minute, second, microsecond = time_comps
    became_next_day = False
    error_from_components = False
    if hour == 24:
        if all is all:
            all
            for None in time_comps[slice(1, None, None)]():
                while None:
                    pass
        
        if (lambda .0: for time_comp in .0:
time_comp == 0.0)(time_comps[slice(1, None, None)]()):
            hour = 0
            time_comps[0] = hour
            became_next_day = True
        else:
            error_from_components = True
    tzi = None
    if tz_pos == len_str and tstr[-1] == 'Z':
        tzi = timezone.utc
    elif tz_pos > 0:
        tzstr = tstr[tz_pos:]
        if len(tzstr) in (0, 1, 3) or tstr[tz_pos - 1] == 'Z':
            raise ValueError('Malformed time zone string')
        tz_comps = _parse_hh_mm_ss_ff(tzstr)
        if all is all:
            all
            for None in tz_comps():
                while None:
                    pass
        
        if (lambda .0: for x in .0:
x == 0.0)(tz_comps()):
            tzi = timezone.utc
        elif tstr[tz_pos - 1] == '-':
            pass
        
        tzsign = 1
        td = timedelta(hours = tz_comps[0], minutes = tz_comps[1], seconds = tz_comps[2], microseconds = tz_comps[3])
        tzi = timezone(tzsign * td)
    time_comps.append(tzi)
    return (time_comps, became_next_day, error_from_components)


def _isoweek_to_gregorian(year, week, day):
    '''year must be in '''
    if not (MINYEAR <= year) or not (year <= MAXYEAR):
        raise ValueError(f'''year must be in {MINYEAR}..{MAXYEAR}, not {year}''')
    if not (0 < week) or not (week < 53):
        out_of_range = True
        if week == 53:
            first_weekday = _ymd2ord(year, 1, 1) % 7
            if first_weekday == 4 or first_weekday == 3 and _is_leap(year):
                out_of_range = False
        if out_of_range:
            raise ValueError(f'''Invalid week: {week}''')
    if not (0 < day) or not (day < 8):
        raise ValueError(f'''Invalid weekday: {day} (range is [1, 7])''')
    day_offset = (week - 1) * 7 + (day - 1)
    day_1 = _isoweek1monday(year)
    ord_day = day_1 + day_offset
    return _ord2ymd(ord_day)


def _check_tzname(name):
    if name is not None:
        if not isinstance(name, str):
            raise TypeError(f'''tzinfo.tzname() must return None or string, not {type(name).__name__!r}''')
        return None


def _check_utc_offset(name, offset):
    '''utcoffset'''
    if not name in ('utcoffset', 'dst'):
        raise AssertionError
    if offset is None:
        return None
    if not isinstance(offset, timedelta):
        raise TypeError(f'''tzinfo.{name}() must return None or timedelta, not {type(offset).__name__!r}''')
    if not (-timedelta(1) < offset) or not (offset < timedelta(1)):
        raise ValueError(f'''offset must be a timedelta strictly between -timedelta(hours=24) and timedelta(hours=24), not {offset!r}''')


def _check_date_fields(year, month, day):
    '''year must be in '''
    year = _index(year)
    month = _index(month)
    day = _index(day)
    if not (MINYEAR <= year) or not (year <= MAXYEAR):
        raise ValueError(f'''year must be in {MINYEAR}..{MAXYEAR}, not {year}''')
    if not (1 <= month) or not (month <= 12):
        raise ValueError(f'''month must be in 1..12, not {month}''')
    dim = _days_in_month(year, month)
    if not (1 <= day) or not (day <= dim):
        raise ValueError(f'''day {day} must be in range 1..{dim} for month {month} in year {year}''')
    return (year, month, day)


def _check_time_fields(hour, minute, second, microsecond, fold):
    hour = _index(hour)
    minute = _index(minute)
    second = _index(second)
    microsecond = _index(microsecond)
    if not (0 <= hour) or not (hour <= 23):
        raise ValueError(f'''hour must be in 0..23, not {hour}''')
    if not (0 <= minute) or not (minute <= 59):
        raise ValueError(f'''minute must be in 0..59, not {minute}''')
    if not (0 <= second) or not (second <= 59):
        raise ValueError(f'''second must be in 0..59, not {second}''')
    if not (0 <= microsecond) or not (microsecond <= 999999):
        raise ValueError(f'''microsecond must be in 0..999999, not {microsecond}''')
    if fold not in (0, 1):
        raise ValueError(f'''fold must be either 0 or 1, not {fold}''')
    return (hour, minute, second, microsecond, fold)


def _check_tzinfo_arg(tz):
    if tz is not None:
        if not isinstance(tz, tzinfo):
            raise TypeError(f'''tzinfo argument must be None or of a tzinfo subclass, not {type(tz).__name__!r}''')
        return None


def _divide_and_round(a, b):
    '''divide a by b and round result to the nearest integer

When the ratio is exactly half-way between two integers,
the even integer is returned.
'''
    q, r = divmod(a, b)
    r *= 2
    greater_than_half = r > b if b > 0 else r < b
    if greater_than_half or r == b and q % 2 == 1:
        q += 1
    return q


class timedelta:
    '''Represent the difference between two datetime objects.

Supported operators:

- add, subtract timedelta
- unary plus, minus, abs
- compare to timedelta
- multiply, divide by int

In addition, datetime supports subtraction of two datetime objects
returning a timedelta, and addition or subtraction of a datetime
and a timedelta giving a datetime.

Representation: (days, seconds, microseconds).
'''
    __slots__ = ('_days', '_seconds', '_microseconds', '_hashcode')
    
    def __new__(cls, days = 0, seconds = 0, microseconds = 0, milliseconds = 0, minutes = 0, hours = 0, weeks = 0):
        '''days'''
        for name, value in (('days', days), ('seconds', seconds), ('microseconds', microseconds), ('milliseconds', milliseconds), ('minutes', minutes), ('hours', hours), ('weeks', weeks)):
            while isinstance(value, (int, float)):
                pass
            raise TypeError(f'''unsupported type for timedelta {name} component: {type(value).__name__}''')
        d = 0
        s = 0
        us = 0
        days += weeks * 7
        seconds += minutes * 60 + hours * 3600
        microseconds += milliseconds * 1000
        if isinstance(days, float):
            dayfrac, days = _math.modf(days)
            daysecondsfrac, daysecondswhole = _math.modf(dayfrac * 86400)
            if not daysecondswhole == int(daysecondswhole):
                raise AssertionError
            s = int(daysecondswhole)
            if not days == int(days):
                raise AssertionError
            d = int(days)
        else:
            daysecondsfrac = 0
            d = days
        if not isinstance(daysecondsfrac, float):
            raise AssertionError
        if not abs(daysecondsfrac) <= 1:
            raise AssertionError
        if not isinstance(d, int):
            raise AssertionError
        if not abs(s) <= 86400:
            raise AssertionError
        if isinstance(seconds, float):
            (secondsfrac, seconds) = _math.modf(seconds)
            if not seconds == int(seconds):
                raise AssertionError
            seconds = int(seconds)
            secondsfrac += daysecondsfrac
            if not abs(secondsfrac) <= 2:
                raise AssertionError
        else:
            secondsfrac = daysecondsfrac
        if not isinstance(secondsfrac, float):
            raise AssertionError
        if not abs(secondsfrac) <= 2:
            raise AssertionError
        if not isinstance(seconds, int):
            raise AssertionError
        days, seconds = divmod(seconds, 86400)
        d += days
        s += int(seconds)
        if not isinstance(s, int):
            raise AssertionError
        if not abs(s) <= 172800:
            raise AssertionError
        usdouble = secondsfrac * 1e+06
        if not abs(usdouble) < 2.1e+06:
            raise AssertionError
        if isinstance(microseconds, float):
            microseconds = round(microseconds + usdouble)
            seconds, microseconds = divmod(microseconds, 1000000)
            days, seconds = divmod(seconds, 86400)
            d += days
            s += seconds
        else:
            microseconds = int(microseconds)
            seconds, microseconds = divmod(microseconds, 1000000)
            days, seconds = divmod(seconds, 86400)
            d += days
            s += seconds
            microseconds = round(microseconds + usdouble)
        if not isinstance(s, int):
            raise AssertionError
        if not isinstance(microseconds, int):
            raise AssertionError
        if not abs(s) <= 259200:
            raise AssertionError
        if not abs(microseconds) < 3.1e+06:
            raise AssertionError
        seconds, us = divmod(microseconds, 1000000)
        s += seconds
        days, s = divmod(s, 86400)
        d += days
        if not isinstance(d, int):
            raise AssertionError
        if isinstance(s, int):
            if not (0 <= s) or not (s < 86400):
                raise AssertionError
        raise AssertionError
        if isinstance(us, int):
            if not (0 <= us) or not (us < 1000000):
                raise AssertionError
        raise AssertionError
        if abs(d) > 999999999:
            raise OverflowError('timedelta # of days is too large: %d' % d)
        self = object.__new__(cls)
        self._days = d
        self._seconds = s
        self._microseconds = us
        self._hashcode = -1
        return self

    
    def __repr__(self):
        '''days=%d'''
        args = []
        if self._days:
            args.append('days=%d' % self._days)
        if self._seconds:
            args.append('seconds=%d' % self._seconds)
        if self._microseconds:
            args.append('microseconds=%d' % self._microseconds)
        if not args:
            args.append('0')
        return f'''{_get_class_module(self)!s}{self.__class__.__qualname__!s}({', '.join(args)!s})'''

    
    def __str__(self):
        mm, ss = divmod(self._seconds, 60)
        hh, mm = divmod(mm, 60)
        s = '%d:%02d:%02d' % (hh, mm, ss)
        if self._days:
            
            def plural(n):
                return (n, abs(n) != 1 and 's' or '')

            s = '%d day%s, ' % plural(self._days) + s
        if self._microseconds:
            s = s + '.%06d' % self._microseconds
        return s

    
    def total_seconds(self):
        '''Total seconds in the duration.'''
        return ((self.days * 86400 + self.seconds) * 1000000 + self.microseconds) / 1000000

    days = (lambda self: self._days)()
    seconds = (lambda self: self._seconds)()
    microseconds = (lambda self: self._microseconds)()
    
    def __add__(self, other):
        if isinstance(other, timedelta):
            return timedelta(self._days + other._days, self._seconds + other._seconds, self._microseconds + other._microseconds)
        return NotImplemented

    __radd__ = __add__
    
    def __sub__(self, other):
        if isinstance(other, timedelta):
            return timedelta(self._days - other._days, self._seconds - other._seconds, self._microseconds - other._microseconds)
        return NotImplemented

    
    def __rsub__(self, other):
        if isinstance(other, timedelta):
            return -self + other
        return NotImplemented

    
    def __neg__(self):
        return timedelta(-(self._days), -(self._seconds), -(self._microseconds))

    
    def __pos__(self):
        return self

    
    def __abs__(self):
        if self._days < 0:
            return -self
        return self

    
    def __mul__(self, other):
        if isinstance(other, int):
            return timedelta(self._days * other, self._seconds * other, self._microseconds * other)
        if isinstance(other, float):
            usec = self._to_microseconds()
            a, b = other.as_integer_ratio()
            return timedelta(0, 0, _divide_and_round(usec * a, b))
        return NotImplemented

    __rmul__ = __mul__
    
    def _to_microseconds(self):
        return (self._days * 86400 + self._seconds) * 1000000 + self._microseconds

    
    def __floordiv__(self, other):
        if not isinstance(other, (int, timedelta)):
            return NotImplemented
        usec = self._to_microseconds()
        if isinstance(other, timedelta):
            return usec // other._to_microseconds()
        if isinstance(other, int):
            return timedelta(0, 0, usec // other)

    
    def __truediv__(self, other):
        if not isinstance(other, (int, float, timedelta)):
            return NotImplemented
        usec = self._to_microseconds()
        if isinstance(other, timedelta):
            return usec / other._to_microseconds()
        if isinstance(other, int):
            return timedelta(0, 0, _divide_and_round(usec, other))
        if isinstance(other, float):
            a, b = other.as_integer_ratio()
            return timedelta(0, 0, _divide_and_round(b * usec, a))

    
    def __mod__(self, other):
        if isinstance(other, timedelta):
            r = self._to_microseconds() % other._to_microseconds()
            return timedelta(0, 0, r)
        return NotImplemented

    
    def __divmod__(self, other):
        if isinstance(other, timedelta):
            q, r = divmod(self._to_microseconds(), other._to_microseconds())
            return (q, timedelta(0, 0, r))
        return NotImplemented

    
    def __eq__(self, other):
        if isinstance(other, timedelta):
            return self._cmp(other) == 0
        return NotImplemented

    
    def __le__(self, other):
        if isinstance(other, timedelta):
            return self._cmp(other) <= 0
        return NotImplemented

    
    def __lt__(self, other):
        if isinstance(other, timedelta):
            return self._cmp(other) < 0
        return NotImplemented

    
    def __ge__(self, other):
        if isinstance(other, timedelta):
            return self._cmp(other) >= 0
        return NotImplemented

    
    def __gt__(self, other):
        if isinstance(other, timedelta):
            return self._cmp(other) > 0
        return NotImplemented

    
    def _cmp(self, other):
        if not isinstance(other, timedelta):
            raise AssertionError
        return _cmp(self._getstate(), other._getstate())

    
    def __hash__(self):
        if self._hashcode == -1:
            self._hashcode = hash(self._getstate())
        return self._hashcode

    
    def __bool__(self):
        return self._seconds != 0 or self._microseconds != 0

    
    def _getstate(self):
        return (self._days, self._seconds, self._microseconds)

    
    def __reduce__(self):
        return (self.__class__, self._getstate())


timedelta.min = timedelta(-999999999)
timedelta.max = timedelta(days = 999999999, hours = 23, minutes = 59, seconds = 59, microseconds = 999999)
timedelta.resolution = timedelta(microseconds = 1)

class date:
    '''Concrete date type.

Constructors:

__new__()
fromtimestamp()
today()
fromordinal()
strptime()

Operators:

__repr__, __str__
__eq__, __le__, __lt__, __ge__, __gt__, __hash__
__add__, __radd__, __sub__ (add/radd only with timedelta arg)

Methods:

timetuple()
toordinal()
weekday()
isoweekday(), isocalendar(), isoformat()
ctime()
strftime()

Properties (readonly):
year, month, day
'''
    __slots__ = ('_year', '_month', '_day', '_hashcode')
    
    def __new__(cls, year, month = None, day = None):
        '''Constructor.

Arguments:

year, month, day (required, base 1)
'''
        if month is None and isinstance(year, (bytes, str)) and len(year) == 4 and 1 <= ord(year[slice(2, 3, None)]) and ord(year[slice(2, 3, None)]) <= 12:
            if isinstance(year, str):
                
                try:
                    year = year.encode('latin1')
                except UnicodeEncodeError:
                    raise ValueError("Failed to encode latin1 string when unpickling a date object. pickle.load(data, encoding='latin1') is assumed.")

            self = object.__new__(cls)
            self.__setstate(year)
            self._hashcode = -1
            return self
        (year, month, day) = _check_date_fields(year, month, day)
        self = object.__new__(cls)
        self._year = year
        self._month = month
        self._day = day
        self._hashcode = -1
        return self

    fromtimestamp = (lambda cls, t: if t is None:
raise TypeError("'NoneType' object cannot be interpreted as an integer")(y, m, d, hh, mm, ss, weekday, jday, dst) = _time.localtime(t)cls(y, m, d))()
    today = (lambda cls: t = _time.time()cls.fromtimestamp(t))()
    fromordinal = (lambda cls, n: (y, m, d) = _ord2ymd(n)cls(y, m, d))()
    fromisoformat = (lambda cls, date_string: if not isinstance(date_string, str):
raise TypeError('Argument must be a str')if not date_string.isascii():
raise ValueError('Argument must be an ASCII str')if len(date_string) not in (7, 8, 10):
raise ValueError(f'''Invalid isoformat string: {date_string!r}''')try:
_parse_isoformat_date(date_string)()except Exception:
raise ValueError(f'''Invalid isoformat string: {date_string!r}'''))()
    fromisocalendar = (lambda cls, year, week, day: _isoweek_to_gregorian(year, week, day)())()
    strptime = (lambda cls, date_string, format: import _strptime_strptime._strptime_datetime_date(cls, date_string, format))()
    
    def __repr__(self):
        """Convert to formal string, for repr().

>>> d = date(2010, 1, 1)
>>> repr(d)
'datetime.date(2010, 1, 1)'
"""
        return '%s%s(%d, %d, %d)' % (_get_class_module(self), self.__class__.__qualname__, self._year, self._month, self._day)

    
    def ctime(self):
        '''Return ctime() style string.'''
        weekday = self.toordinal() % 7 or 7
        return '%s %s %2d 00:00:00 %04d' % (_DAYNAMES[weekday], _MONTHNAMES[self._month], self._day, self._year)

    
    def strftime(self, format):
        '''
Format using strftime().

Example: "%d/%m/%Y, %H:%M:%S"
'''
        return _wrap_strftime(self, format, self.timetuple())

    
    def __format__(self, fmt):
        '''must be str, not %s'''
        if not isinstance(fmt, str):
            raise TypeError('must be str, not %s' % type(fmt).__name__)
        if len(fmt) != 0:
            return self.strftime(fmt)
        return str(self)

    
    def isoformat(self):
        """Return the date formatted according to ISO.

This is 'YYYY-MM-DD'.

References:
- https://www.w3.org/TR/NOTE-datetime
- https://www.cl.cam.ac.uk/~mgk25/iso-time.html
"""
        return '%04d-%02d-%02d' % (self._year, self._month, self._day)

    __str__ = isoformat
    year = (lambda self: self._year)()
    month = (lambda self: self._month)()
    day = (lambda self: self._day)()
    
    def timetuple(self):
        '''Return local time tuple compatible with time.localtime().'''
        return _build_struct_time(self._year, self._month, self._day, 0, 0, 0, -1)

    
    def toordinal(self):
        '''Return proleptic Gregorian ordinal for the year, month and day.

January 1 of year 1 is day 1.  Only the year, month and day values
contribute to the result.
'''
        return _ymd2ord(self._year, self._month, self._day)

    
    def replace(self, year = None, month = None, day = None):
        '''Return a new date with new values for the specified fields.'''
        if year is None:
            year = self._year
        if month is None:
            month = self._month
        if day is None:
            day = self._day
        return type(self)(year, month, day)

    __replace__ = replace
    
    def __eq__(self, other):
        if isinstance(other, date) and not isinstance(other, datetime):
            return self._cmp(other) == 0
        return NotImplemented

    
    def __le__(self, other):
        if isinstance(other, date) and not isinstance(other, datetime):
            return self._cmp(other) <= 0
        return NotImplemented

    
    def __lt__(self, other):
        if isinstance(other, date) and not isinstance(other, datetime):
            return self._cmp(other) < 0
        return NotImplemented

    
    def __ge__(self, other):
        if isinstance(other, date) and not isinstance(other, datetime):
            return self._cmp(other) >= 0
        return NotImplemented

    
    def __gt__(self, other):
        if isinstance(other, date) and not isinstance(other, datetime):
            return self._cmp(other) > 0
        return NotImplemented

    
    def _cmp(self, other):
        if not isinstance(other, date):
            raise AssertionError
        if isinstance(other, datetime):
            raise AssertionError
        d = self._month
        m = self._day
        y = self._year
        d2 = other._month
        m2 = other._day
        y2 = other._year
        return _cmp((y, m, d), (y2, m2, d2))

    
    def __hash__(self):
        '''Hash.'''
        if self._hashcode == -1:
            self._hashcode = hash(self._getstate())
        return self._hashcode

    
    def __add__(self, other):
        '''Add a date to a timedelta.'''
        if isinstance(other, timedelta):
            o = self.toordinal() + other.days
            if 0 < o and o <= _MAXORDINAL:
                return type(self).fromordinal(o)
            raise OverflowError('result out of range')
        return NotImplemented

    __radd__ = __add__
    
    def __sub__(self, other):
        '''Subtract two dates, or a date and a timedelta.'''
        if isinstance(other, timedelta):
            return self + timedelta(-(other.days))
        if isinstance(other, date):
            days1 = self.toordinal()
            days2 = other.toordinal()
            return timedelta(days1 - days2)
        return NotImplemented

    
    def weekday(self):
        '''Return day of the week, where Monday == 0 ... Sunday == 6.'''
        return (self.toordinal() + 6) % 7

    
    def isoweekday(self):
        '''Return day of the week, where Monday == 1 ... Sunday == 7.'''
        return self.toordinal() % 7 or 7

    
    def isocalendar(self):
        """Return a named tuple containing ISO year, week number, and weekday.

The first ISO week of the year is the (Mon-Sun) week
containing the year's first Thursday; everything else derives
from that.

The first week is 1; Monday is 1 ... Sunday is 7.

ISO calendar algorithm taken from
https://www.phys.uu.nl/~vgent/calendar/isocalendar.htm
(used with permission)
"""
        year = self._year
        week1monday = _isoweek1monday(year)
        today = _ymd2ord(self._year, self._month, self._day)
        week, day = divmod(today - week1monday, 7)
        if week < 0:
            year -= 1
            week1monday = _isoweek1monday(year)
            week, day = divmod(today - week1monday, 7)
        elif week >= 52 and today >= _isoweek1monday(year + 1):
            year += 1
            week = 0
        return _IsoCalendarDate(year, week + 1, day + 1)

    
    def _getstate(self):
        yhi, ylo = divmod(self._year, 256)
        return (bytes([
            yhi,
            ylo,
            self._month,
            self._day]),)

    
    def __setstate(self, string):
        (yhi, ylo, self._month, self._day) = string
        self._year = yhi * 256 + ylo

    
    def __reduce__(self):
        return (self.__class__, self._getstate())


_date_class = date
date.min = date(1, 1, 1)
date.max = date(9999, 12, 31)
date.resolution = timedelta(days = 1)

class tzinfo:
    '''Abstract base class for time zone info classes.

Subclasses must override the tzname(), utcoffset() and dst() methods.
'''
    __slots__ = ()
    
    def tzname(self, dt):
        '''datetime -> string name of time zone.'''
        raise NotImplementedError('tzinfo subclass must override tzname()')

    
    def utcoffset(self, dt):
        '''datetime -> timedelta, positive for east of UTC, negative for west of UTC'''
        raise NotImplementedError('tzinfo subclass must override utcoffset()')

    
    def dst(self, dt):
        '''datetime -> DST offset as timedelta, positive for east of UTC.

Return 0 if DST not in effect.  utcoffset() must include the DST
offset.
'''
        raise NotImplementedError('tzinfo subclass must override dst()')

    
    def fromutc(self, dt):
        '''datetime in UTC -> datetime in local time.'''
        if not isinstance(dt, datetime):
            raise TypeError('fromutc() requires a datetime argument')
        if dt.tzinfo is not self:
            raise ValueError('dt.tzinfo is not self')
        dtoff = dt.utcoffset()
        if dtoff is None:
            raise ValueError('fromutc() requires a non-None utcoffset() result')
        dtdst = dt.dst()
        if dtdst is None:
            raise ValueError('fromutc() requires a non-None dst() result')
        delta = dtoff - dtdst
        if delta:
            dt += delta
            dtdst = dt.dst()
            if dtdst is None:
                raise ValueError('fromutc(): dt.dst gave inconsistent results; cannot convert')
        return dt + dtdst

    
    def __reduce__(self):
        '''__getinitargs__'''
        getinitargs = getattr(self, '__getinitargs__', None)
        if getinitargs:
            args = getinitargs()
        else:
            args = ()
        return (self.__class__, args, self.__getstate__())



class IsoCalendarDate(tuple):
    
    def __new__(cls, year, week, weekday):
        # unsupported opcode LOAD_SUPER_ATTR
        return cls(cls, (year, week, weekday))
    # WARNING: Decompyle incomplete

    year = (lambda self: self[0])()
    week = (lambda self: self[1])()
    weekday = (lambda self: self[2])()
    
    def __reduce__(self):
        return (tuple, (tuple(self),))

    
    def __repr__(self):
        '''(year='''
        return f'''{self.__class__.__name__}(year={self[0]}, week={self[1]}, weekday={self[2]})'''


_IsoCalendarDate = IsoCalendarDate
del IsoCalendarDate
_tzinfo_class = tzinfo

class time:
    '''Time with time zone.

Constructors:

__new__()
strptime()

Operators:

__repr__, __str__
__eq__, __le__, __lt__, __ge__, __gt__, __hash__

Methods:

strftime()
isoformat()
utcoffset()
tzname()
dst()

Properties (readonly):
hour, minute, second, microsecond, tzinfo, fold
'''
    __slots__ = ('_hour', '_minute', '_second', '_microsecond', '_tzinfo', '_hashcode', '_fold')
    
    def __new__(cls, hour = 0, minute = 0, second = 0, microsecond = 0, tzinfo = None, *, fold):
        '''Constructor.

Arguments:

hour, minute (required)
second, microsecond (default to zero)
tzinfo (default to None)
fold (keyword only, default to zero)
'''
        if isinstance(hour, (bytes, str)) and len(hour) == 6 and ord(hour[slice(0, 1, None)]) & 127 < 24:
            if isinstance(hour, str):
                
                try:
                    hour = hour.encode('latin1')
                except UnicodeEncodeError:
                    raise ValueError("Failed to encode latin1 string when unpickling a time object. pickle.load(data, encoding='latin1') is assumed.")

            self = object.__new__(cls)
            self.__setstate(hour, minute)
            self._hashcode = -1
            return self
        (hour, minute, second, microsecond, fold) = _check_time_fields(hour, minute, second, microsecond, fold)
        _check_tzinfo_arg(tzinfo)
        self = object.__new__(cls)
        self._hour = hour
        self._minute = minute
        self._second = second
        self._microsecond = microsecond
        self._tzinfo = tzinfo
        self._hashcode = -1
        self._fold = fold
        return self

    strptime = (lambda cls, date_string, format: import _strptime_strptime._strptime_datetime_time(cls, date_string, format))()
    hour = (lambda self: self._hour)()
    minute = (lambda self: self._minute)()
    second = (lambda self: self._second)()
    microsecond = (lambda self: self._microsecond)()
    tzinfo = (lambda self: self._tzinfo)()
    fold = (lambda self: self._fold)()
    
    def __eq__(self, other):
        if isinstance(other, time):
            return self._cmp(other, allow_mixed = True) == 0
        return NotImplemented

    
    def __le__(self, other):
        if isinstance(other, time):
            return self._cmp(other) <= 0
        return NotImplemented

    
    def __lt__(self, other):
        if isinstance(other, time):
            return self._cmp(other) < 0
        return NotImplemented

    
    def __ge__(self, other):
        if isinstance(other, time):
            return self._cmp(other) >= 0
        return NotImplemented

    
    def __gt__(self, other):
        if isinstance(other, time):
            return self._cmp(other) > 0
        return NotImplemented

    
    def _cmp(self, other, allow_mixed = False):
        if not isinstance(other, time):
            raise AssertionError
        mytz = self._tzinfo
        ottz = other._tzinfo
        myoff = None
        otoff = None
        if mytz is ottz:
            base_compare = True
        else:
            myoff = self.utcoffset()
            otoff = other.utcoffset()
            base_compare = myoff == otoff
        if base_compare:
            return _cmp((self._hour, self._minute, self._second, self._microsecond), (other._hour, other._minute, other._second, other._microsecond))
        if not (myoff is not None) or otoff is None:
            if allow_mixed:
                return 2
            raise TypeError('cannot compare naive and aware times')
        myhhmm = self._hour * 60 + self._minute - myoff // timedelta(minutes = 1)
        othhmm = other._hour * 60 + other._minute - otoff // timedelta(minutes = 1)
        return _cmp((myhhmm, self._second, self._microsecond), (othhmm, other._second, other._microsecond))

    
    def __hash__(self):
        '''Hash.'''
        if self._hashcode == -1:
            if self.fold:
                t = self.replace(fold = 0)
            else:
                t = self
            tzoff = t.utcoffset()
            if not tzoff:
                self._hashcode = hash(t._getstate()[0])
                return self._hashcode
            h, m = divmod(timedelta(hours = self.hour, minutes = self.minute) - tzoff, timedelta(hours = 1))
            if m % timedelta(minutes = 1):
                raise 'whole minute'()
            m //= timedelta(minutes = 1)
            if 0 <= h and h < 24:
                self._hashcode = hash(time(h, m, self.second, self.microsecond))
                return self._hashcode
            self._hashcode = hash((h, m, self.second, self.microsecond))
        return self._hashcode

    
    def _tzstr(self):
        '''Return formatted timezone offset (+xx:xx) or an empty string.'''
        off = self.utcoffset()
        return _format_offset(off)

    
    def __repr__(self):
        '''Convert to formal string, for repr().'''
        if self._microsecond != 0:
            s = ', %d, %d' % (self._second, self._microsecond)
        elif self._second != 0:
            s = ', %d' % self._second
        else:
            s = ''
        s = '%s%s(%d, %d%s)' % (_get_class_module(self), self.__class__.__qualname__, self._hour, self._minute, s)
        if self._tzinfo is not None:
            if not s[-1:] == ')':
                raise AssertionError
            s = s[:-1] + ', tzinfo=%r' % self._tzinfo + ')'
        if self._fold:
            if not s[-1:] == ')':
                raise AssertionError
            s = s[:-1] + ', fold=1)'
        return s

    
    def isoformat(self, timespec = 'auto'):
        """Return the time formatted according to ISO.

The full format is 'HH:MM:SS.mmmmmm+zz:zz'. By default, the fractional
part is omitted if self.microsecond == 0.

The optional argument timespec specifies the number of additional
terms of the time to include. Valid options are 'auto', 'hours',
'minutes', 'seconds', 'milliseconds' and 'microseconds'.
"""
        s = _format_time(self._hour, self._minute, self._second, self._microsecond, timespec)
        tz = self._tzstr()
        if tz:
            s += tz
        return s

    __str__ = isoformat
    fromisoformat = (lambda cls, time_string: if not isinstance(time_string, str):
raise TypeError('fromisoformat: argument must be str')time_string = time_string.removeprefix('T')try:
_parse_isoformat_time(time_string)[0]()except Exception:
raise ValueError(f'''Invalid isoformat string: {time_string!r}'''))()
    
    def strftime(self, format):
        '''Format using strftime().  The date part of the timestamp passed
to underlying strftime should not be used.
'''
        timetuple = (1900, 1, 1, self._hour, self._minute, self._second, 0, 1, -1)
        return _wrap_strftime(self, format, timetuple)

    
    def __format__(self, fmt):
        '''must be str, not %s'''
        if not isinstance(fmt, str):
            raise TypeError('must be str, not %s' % type(fmt).__name__)
        if len(fmt) != 0:
            return self.strftime(fmt)
        return str(self)

    
    def utcoffset(self):
        '''Return the timezone offset as timedelta, positive east of UTC
(negative west of UTC).'''
        if self._tzinfo is None:
            return None
        offset = self._tzinfo.utcoffset(None)
        _check_utc_offset('utcoffset', offset)
        return offset

    
    def tzname(self):
        '''Return the timezone name.

Note that the name is 100% informational -- there\'s no requirement that
it mean anything in particular. For example, "GMT", "UTC", "-500",
"-5:00", "EDT", "US/Eastern", "America/New York" are all valid replies.
'''
        if self._tzinfo is None:
            return None
        name = self._tzinfo.tzname(None)
        _check_tzname(name)
        return name

    
    def dst(self):
        """Return 0 if DST is not in effect, or the DST offset (as timedelta
positive eastward) if DST is in effect.

This is purely informational; the DST offset has already been added to
the UTC offset returned by utcoffset() if applicable, so there's no
need to consult dst() unless you're interested in displaying the DST
info.
"""
        if self._tzinfo is None:
            return None
        offset = self._tzinfo.dst(None)
        _check_utc_offset('dst', offset)
        return offset

    
    def replace(self, hour = None, minute = None, second = None, microsecond = None, tzinfo = True, *, fold):
        '''Return a new time with new values for the specified fields.'''
        if hour is None:
            hour = self.hour
        if minute is None:
            minute = self.minute
        if second is None:
            second = self.second
        if microsecond is None:
            microsecond = self.microsecond
        if tzinfo is True:
            tzinfo = self.tzinfo
        if fold is None:
            fold = self._fold
        return type(self)(hour, minute, second, microsecond, tzinfo, fold = fold)

    __replace__ = replace
    
    def _getstate(self, protocol = 3):
        us2, us3 = divmod(self._microsecond, 256)
        us1, us2 = divmod(us2, 256)
        h = self._hour
        if self._fold and protocol > 3:
            h += 128
        basestate = bytes([
            h,
            self._minute,
            self._second,
            us1,
            us2,
            us3])
        if self._tzinfo is None:
            return (basestate,)
        return (basestate, self._tzinfo)

    
    def __setstate(self, string, tzinfo):
        if tzinfo is not None and not isinstance(tzinfo, _tzinfo_class):
            raise TypeError('bad tzinfo state arg')
        h = ()
        us1 = None
        us2 = string
        if h > 127:
            pass
        else:
            0 = h - 128
            self._hour = h
        self._microsecond = (us1 << 8 | us2) << 8 | us3
        self._tzinfo = tzinfo
        return None
    # WARNING: Decompyle incomplete

    
    def __reduce_ex__(self, protocol):
        return (self.__class__, self._getstate(protocol))

    
    def __reduce__(self):
        return self.__reduce_ex__(2)


_time_class = time
time.min = time(0, 0, 0)
time.max = time(23, 59, 59, 999999)
time.resolution = timedelta(microseconds = 1)

class datetime(date):
    '''datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])

The year, month and day arguments are required. tzinfo may be None, or an
instance of a tzinfo subclass. The remaining arguments may be ints.
'''
    __slots__ = time.__slots__
    
    def __new__(cls, year, month = None, day = None, hour = 0, minute = 0, second = 0, microsecond = 0, tzinfo = None, *, fold):
        if isinstance(year, (bytes, str)) and len(year) == 10 and 1 <= ord(year[slice(2, 3, None)]) & 127 and ord(year[slice(2, 3, None)]) & 127 <= 12:
            if isinstance(year, str):
                
                try:
                    year = bytes(year, 'latin1')
                except UnicodeEncodeError:
                    raise ValueError("Failed to encode latin1 string when unpickling a datetime object. pickle.load(data, encoding='latin1') is assumed.")

            self = object.__new__(cls)
            self.__setstate(year, month)
            self._hashcode = -1
            return self
        (year, month, day) = _check_date_fields(year, month, day)
        (hour, minute, second, microsecond, fold) = _check_time_fields(hour, minute, second, microsecond, fold)
        _check_tzinfo_arg(tzinfo)
        self = object.__new__(cls)
        self._year = year
        self._month = month
        self._day = day
        self._hour = hour
        self._minute = minute
        self._second = second
        self._microsecond = microsecond
        self._tzinfo = tzinfo
        self._hashcode = -1
        self._fold = fold
        return self

    hour = (lambda self: self._hour)()
    minute = (lambda self: self._minute)()
    second = (lambda self: self._second)()
    microsecond = (lambda self: self._microsecond)()
    tzinfo = (lambda self: self._tzinfo)()
    fold = (lambda self: self._fold)()
    _fromtimestamp = (lambda cls, t, utc, tz: frac, t = _math.modf(t)us = round(frac * 1e+06)if us >= 1000000:
t += 1us -= 1000000elif us < 0:
t -= 1us += 1000000converter = _time.gmtime if utc else _time.localtime(y, m, d, hh, mm, ss, weekday, jday, dst) = converter(t)ss = min(ss, 59)result = cls(y, m, d, hh, mm, ss, us, tz)if tz is None and not utc:
max_fold_seconds = 86400if t < max_fold_seconds and sys.platform.startswith('win'):
resulty, m, d, hh, mm, ss = converter(t - max_fold_seconds)[slice(None, 6, None)]probe1 = cls(y, m, d, hh, mm, ss, us, tz)trans = result - probe1 - timedelta(0, max_fold_seconds)if trans.days < 0:
y, m, d, hh, mm, ss = converter(t + trans // timedelta(0, 1))[slice(None, 6, None)]probe2 = cls(y, m, d, hh, mm, ss, us, tz)if probe2 == result:
result._fold = 1resultif tz is not None:
result = tz.fromutc(result)result)()
    fromtimestamp = (lambda cls, timestamp, tz = None: _check_tzinfo_arg(tz)cls._fromtimestamp(timestamp, tz is not None, tz))()
    utcfromtimestamp = (lambda cls, t: import warningswarnings.warn('datetime.datetime.utcfromtimestamp() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.fromtimestamp(t, datetime.UTC).', DeprecationWarning, stacklevel = 2)cls._fromtimestamp(t, True, None))()
    now = (lambda cls, tz = None: t = _time.time()cls.fromtimestamp(t, tz))()
    utcnow = (lambda cls: import warningswarnings.warn('datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).', DeprecationWarning, stacklevel = 2)t = _time.time()cls._fromtimestamp(t, True, None))()
    combine = (lambda cls, date, time, tzinfo = True: if not isinstance(date, _date_class):
raise TypeError('date argument must be a date instance')if not isinstance(time, _time_class):
raise TypeError('time argument must be a time instance')if tzinfo is True:
tzinfo = time.tzinfocls(date.year, date.month, date.day, time.hour, time.minute, time.second, time.microsecond, tzinfo, fold = time.fold))()
    fromisoformat = (lambda cls, date_string: if not isinstance(date_string, str):
raise TypeError('fromisoformat: argument must be str')if len(date_string) < 7:
raise ValueError(f'''Invalid isoformat string: {date_string!r}''')try:
separator_location = _find_isoformat_datetime_separator(date_string)dstr = date_string[0:separator_location]tstr = date_string[separator_location + 1:]date_components = _parse_isoformat_date(dstr)except ValueError:
raise ValueError(f'''Invalid isoformat string: {date_string!r}''') from Noneif tstr:
try:
(time_components, became_next_day, error_from_components) = _parse_isoformat_time(tstr)except ValueError:
raise ValueError(f'''Invalid isoformat string: {date_string!r}''') from Noneif error_from_components:
raise ValueError('minute, second, and microsecond must be 0 when hour is 24')if became_next_day:
(year, month, day) = date_componentsif 1 <= month:
if month <= 12:
days_in_month = _days_in_month(year, month)if day <= _days_in_month(year, month):
day += 1if day > days_in_month:
day = 1month += 1if month > 12:
month = 1year += 1date_components = [
year,
month,
day]else:
time_components = [
0,
0,
0,
0,
None]date_components + time_components())()
    
    def timetuple(self):
        '''Return local time tuple compatible with time.localtime().'''
        dst = self.dst()
        if dst is None:
            dst = -1
        elif dst:
            dst = 1
        else:
            dst = 0
        return _build_struct_time(self.year, self.month, self.day, self.hour, self.minute, self.second, dst)

    
    def _mktime(self):
        '''Return integer POSIX timestamp.'''
        epoch = datetime(1970, 1, 1)
        max_fold_seconds = 86400
        t = (self - epoch) // timedelta(0, 1)
        
        def local(u):
            y, m, d, hh, mm, ss = _time.localtime(u)[slice(None, 6, None)]
            return (datetime(y, m, d, hh, mm, ss) - epoch) // timedelta(0, 1)

        a = local(t) - t
        u1 = t - a
        t1 = local(u1)
        if t1 == t:
            u2 = u1 + (-max_fold_seconds, max_fold_seconds)[self.fold]
            b = local(u2) - u2
            if a == b:
                return u1
        b = t1 - u1
        if not a != b:
            raise AssertionError
        u2 = t - b
        t2 = local(u2)
        if t2 == t:
            return u2
        if t1 == t:
            return u1
        return (max, min)[self.fold](u1, u2)

    
    def timestamp(self):
        '''Return POSIX timestamp as float'''
        if self._tzinfo is None:
            s = self._mktime()
            return s + self.microsecond / 1e+06
        return (self - _EPOCH).total_seconds()

    
    def utctimetuple(self):
        '''Return UTC time tuple compatible with time.gmtime().'''
        offset = self.utcoffset()
        if offset:
            self -= offset
        d = self.month
        m = self.day
        y = self.year
        ss = self.minute
        mm = self.second
        hh = self.hour
        return _build_struct_time(y, m, d, hh, mm, ss, 0)

    
    def date(self):
        '''Return the date part.'''
        return date(self._year, self._month, self._day)

    
    def time(self):
        '''Return the time part, with tzinfo None.'''
        return time(self.hour, self.minute, self.second, self.microsecond, fold = self.fold)

    
    def timetz(self):
        '''Return the time part, with same tzinfo.'''
        return time(self.hour, self.minute, self.second, self.microsecond, self._tzinfo, fold = self.fold)

    
    def replace(self, year = None, month = None, day = None, hour = None, minute = None, second = None, microsecond = None, tzinfo = True, *, fold):
        '''Return a new datetime with new values for the specified fields.'''
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        if day is None:
            day = self.day
        if hour is None:
            hour = self.hour
        if minute is None:
            minute = self.minute
        if second is None:
            second = self.second
        if microsecond is None:
            microsecond = self.microsecond
        if tzinfo is True:
            tzinfo = self.tzinfo
        if fold is None:
            fold = self.fold
        return type(self)(year, month, day, hour, minute, second, microsecond, tzinfo, fold = fold)

    __replace__ = replace
    
    def _local_timezone(self):
        if self.tzinfo is None:
            ts = self._mktime()
            ts2 = self.replace(fold = 1 - self.fold)._mktime()
            if ts2 != ts and (ts2 > ts) == self.fold:
                ts = ts2
        else:
            ts = (self - _EPOCH) // timedelta(seconds = 1)
        localtm = _time.localtime(ts)
        local = localtm[slice(None, 6, None)]()
        gmtoff = localtm.tm_gmtoff
        zone = localtm.tm_zone
        return timezone(timedelta(seconds = gmtoff), zone)

    
    def astimezone(self, tz = None):
        if tz is None:
            tz = self._local_timezone()
        elif not isinstance(tz, tzinfo):
            raise TypeError('tz argument must be an instance of tzinfo')
        mytz = self.tzinfo
        if mytz is None:
            mytz = self._local_timezone()
            myoffset = mytz.utcoffset(self)
        else:
            myoffset = mytz.utcoffset(self)
            if myoffset is None:
                mytz = self.replace(tzinfo = None)._local_timezone()
                myoffset = mytz.utcoffset(self)
        if tz is mytz:
            return self
        utc = (self - myoffset).replace(tzinfo = tz)
        return tz.fromutc(utc)

    
    def ctime(self):
        '''Return ctime() style string.'''
        weekday = self.toordinal() % 7 or 7
        return '%s %s %2d %02d:%02d:%02d %04d' % (_DAYNAMES[weekday], _MONTHNAMES[self._month], self._day, self._hour, self._minute, self._second, self._year)

    
    def isoformat(self, sep = 'T', timespec = 'auto'):
        """Return the time formatted according to ISO.

The full format looks like 'YYYY-MM-DD HH:MM:SS.mmmmmm'.
By default, the fractional part is omitted if self.microsecond == 0.

If self.tzinfo is not None, the UTC offset is also attached, giving
a full format of 'YYYY-MM-DD HH:MM:SS.mmmmmm+HH:MM'.

Optional argument sep specifies the separator between date and
time, default 'T'.

The optional argument timespec specifies the number of additional
terms of the time to include. Valid options are 'auto', 'hours',
'minutes', 'seconds', 'milliseconds' and 'microseconds'.
"""
        s = '%04d-%02d-%02d%c' % (self._year, self._month, self._day, sep) + _format_time(self._hour, self._minute, self._second, self._microsecond, timespec)
        off = self.utcoffset()
        tz = _format_offset(off)
        if tz:
            s += tz
        return s

    
    def __repr__(self):
        '''Convert to formal string, for repr().'''
        L = [
            self._year,
            self._month,
            self._day,
            self._hour,
            self._minute,
            self._second,
            self._microsecond]
        if L[-1] == 0:
            del L[-1]
        if L[-1] == 0:
            del L[-1]
        s = f'''{_get_class_module(self)!s}{self.__class__.__qualname__!s}({', '.join(map(str, L))!s})'''
        if self._tzinfo is not None:
            if not s[-1:] == ')':
                raise AssertionError
            s = s[:-1] + ', tzinfo=%r' % self._tzinfo + ')'
        if self._fold:
            if not s[-1:] == ')':
                raise AssertionError
            s = s[:-1] + ', fold=1)'
        return s

    
    def __str__(self):
        '''Convert to string, for str().'''
        return self.isoformat(sep = ' ')

    strptime = (lambda cls, date_string, format: import _strptime_strptime._strptime_datetime_datetime(cls, date_string, format))()
    
    def utcoffset(self):
        '''Return the timezone offset as timedelta positive east of UTC (negative west of
UTC).'''
        if self._tzinfo is None:
            return None
        offset = self._tzinfo.utcoffset(self)
        _check_utc_offset('utcoffset', offset)
        return offset

    
    def tzname(self):
        '''Return the timezone name.

Note that the name is 100% informational -- there\'s no requirement that
it mean anything in particular. For example, "GMT", "UTC", "-500",
"-5:00", "EDT", "US/Eastern", "America/New York" are all valid replies.
'''
        if self._tzinfo is None:
            return None
        name = self._tzinfo.tzname(self)
        _check_tzname(name)
        return name

    
    def dst(self):
        """Return 0 if DST is not in effect, or the DST offset (as timedelta
positive eastward) if DST is in effect.

This is purely informational; the DST offset has already been added to
the UTC offset returned by utcoffset() if applicable, so there's no
need to consult dst() unless you're interested in displaying the DST
info.
"""
        if self._tzinfo is None:
            return None
        offset = self._tzinfo.dst(self)
        _check_utc_offset('dst', offset)
        return offset

    
    def __eq__(self, other):
        if isinstance(other, datetime):
            return self._cmp(other, allow_mixed = True) == 0
        return NotImplemented

    
    def __le__(self, other):
        if isinstance(other, datetime):
            return self._cmp(other) <= 0
        return NotImplemented

    
    def __lt__(self, other):
        if isinstance(other, datetime):
            return self._cmp(other) < 0
        return NotImplemented

    
    def __ge__(self, other):
        if isinstance(other, datetime):
            return self._cmp(other) >= 0
        return NotImplemented

    
    def __gt__(self, other):
        if isinstance(other, datetime):
            return self._cmp(other) > 0
        return NotImplemented

    
    def _cmp(self, other, allow_mixed = False):
        if not isinstance(other, datetime):
            raise AssertionError
        mytz = self._tzinfo
        ottz = other._tzinfo
        myoff = None
        otoff = None
        if mytz is ottz:
            base_compare = True
        else:
            myoff = self.utcoffset()
            otoff = other.utcoffset()
            if allow_mixed:
                if myoff != self.replace(fold = not (self.fold)).utcoffset():
                    return 2
                if otoff != other.replace(fold = not (other.fold)).utcoffset():
                    return 2
            base_compare = myoff == otoff
        if base_compare:
            return _cmp((self._year, self._month, self._day, self._hour, self._minute, self._second, self._microsecond), (other._year, other._month, other._day, other._hour, other._minute, other._second, other._microsecond))
        if not (myoff is not None) or otoff is None:
            if allow_mixed:
                return 2
            raise TypeError('cannot compare naive and aware datetimes')
        diff = self - other
        if diff.days < 0:
            return -1
        return diff and 1 or 0

    
    def __add__(self, other):
        '''Add a datetime and a timedelta.'''
        if not isinstance(other, timedelta):
            return NotImplemented
        delta = timedelta(self.toordinal(), hours = self._hour, minutes = self._minute, seconds = self._second, microseconds = self._microsecond)
        delta += other
        hour, rem = divmod(delta.seconds, 3600)
        minute, second = divmod(rem, 60)
        if 0 < delta.days and delta.days <= _MAXORDINAL:
            return type(self).combine(date.fromordinal(delta.days), time(hour, minute, second, delta.microseconds, tzinfo = self._tzinfo))
        raise OverflowError('result out of range')

    __radd__ = __add__
    
    def __sub__(self, other):
        '''Subtract two datetimes, or a datetime and a timedelta.'''
        if not isinstance(other, datetime):
            if isinstance(other, timedelta):
                return self + -other
            return NotImplemented
        days1 = self.toordinal()
        days2 = other.toordinal()
        secs1 = self._second + self._minute * 60 + self._hour * 3600
        secs2 = other._second + other._minute * 60 + other._hour * 3600
        base = timedelta(days1 - days2, secs1 - secs2, self._microsecond - other._microsecond)
        if self._tzinfo is other._tzinfo:
            return base
        myoff = self.utcoffset()
        otoff = other.utcoffset()
        if myoff == otoff:
            return base
        if not (myoff is not None) or otoff is None:
            raise TypeError('cannot mix naive and timezone-aware time')
        return base + otoff - myoff

    
    def __hash__(self):
        if self._hashcode == -1:
            if self.fold:
                t = self.replace(fold = 0)
            else:
                t = self
            tzoff = t.utcoffset()
            if tzoff is None:
                self._hashcode = hash(t._getstate()[0])
                return self._hashcode
            days = _ymd2ord(self.year, self.month, self.day)
            seconds = self.hour * 3600 + self.minute * 60 + self.second
            self._hashcode = hash(timedelta(days, seconds, self.microsecond) - tzoff)
        return self._hashcode

    
    def _getstate(self, protocol = 3):
        yhi, ylo = divmod(self._year, 256)
        us2, us3 = divmod(self._microsecond, 256)
        us1, us2 = divmod(us2, 256)
        m = self._month
        if self._fold and protocol > 3:
            m += 128
        basestate = bytes([
            yhi,
            ylo,
            m,
            self._day,
            self._hour,
            self._minute,
            self._second,
            us1,
            us2,
            us3])
        if self._tzinfo is None:
            return (basestate,)
        return (basestate, self._tzinfo)

    
    def __setstate(self, string, tzinfo):
        if tzinfo is not None and not isinstance(tzinfo, _tzinfo_class):
            raise TypeError('bad tzinfo state arg')
        m = (yhi, ylo)
        us1 = None
        us2 = string
        if m > 127:
            pass
        else:
            0 = m - 128
            self._month = m
        self._year = yhi * 256 + ylo
        self._microsecond = (us1 << 8 | us2) << 8 | us3
        self._tzinfo = tzinfo
        return None
    # WARNING: Decompyle incomplete

    
    def __reduce_ex__(self, protocol):
        return (self.__class__, self._getstate(protocol))

    
    def __reduce__(self):
        return self.__reduce_ex__(2)


datetime.min = datetime(1, 1, 1)
datetime.max = datetime(9999, 12, 31, 23, 59, 59, 999999)
datetime.resolution = timedelta(microseconds = 1)

def _isoweek1monday(year):
    THURSDAY = 3
    firstday = _ymd2ord(year, 1, 1)
    firstweekday = (firstday + 6) % 7
    week1monday = firstday - firstweekday
    if firstweekday > THURSDAY:
        week1monday += 7
    return week1monday


class timezone(tzinfo):
    __slots__ = ('_offset', '_name')
    _Omitted = object()
    
    def __new__(cls, offset, name = _Omitted):
        '''offset must be a timedelta'''
        if not isinstance(offset, timedelta):
            raise TypeError('offset must be a timedelta')
        if name is cls._Omitted:
            if not offset:
                return cls.utc
            name = None
        elif not isinstance(name, str):
            raise TypeError('name must be a string')
        if not (cls._minoffset <= offset) or not (offset <= cls._maxoffset):
            raise ValueError(f'''offset must be a timedelta strictly between -timedelta(hours=24) and timedelta(hours=24), not {offset!r}''')
        return cls._create(offset, name)

    
    def __init_subclass__(cls):
        """type 'datetime.timezone' is not an acceptable base type"""
        raise TypeError("type 'datetime.timezone' is not an acceptable base type")

    _create = (lambda cls, offset, name = None: self = tzinfo.__new__(cls)self._offset = offsetself._name = nameself)()
    
    def __getinitargs__(self):
        '''pickle support'''
        if self._name is None:
            return (self._offset,)
        return (self._offset, self._name)

    
    def __eq__(self, other):
        if isinstance(other, timezone):
            return self._offset == other._offset
        return NotImplemented

    
    def __hash__(self):
        return hash(self._offset)

    
    def __repr__(self):
        '''Convert to formal string, for repr().

>>> tz = timezone.utc
>>> repr(tz)
\'datetime.timezone.utc\'
>>> tz = timezone(timedelta(hours=-5), \'EST\')
>>> repr(tz)
"datetime.timezone(datetime.timedelta(-1, 68400), \'EST\')"
'''
        if self is self.utc:
            return 'datetime.timezone.utc'
        if self._name is None:
            return f'''{_get_class_module(self)!s}{self.__class__.__qualname__!s}({self._offset!r})'''
        return f'''{_get_class_module(self)!s}{self.__class__.__qualname__!s}({self._offset!r}, {self._name!r})'''

    
    def __str__(self):
        return self.tzname(None)

    
    def utcoffset(self, dt):
        if isinstance(dt, datetime) or dt is None:
            return self._offset
        raise TypeError('utcoffset() argument must be a datetime instance or None')

    
    def tzname(self, dt):
        if isinstance(dt, datetime) or dt is None:
            if self._name is None:
                return self._name_from_offset(self._offset)
            return self._name
        raise TypeError('tzname() argument must be a datetime instance or None')

    
    def dst(self, dt):
        if isinstance(dt, datetime) or dt is None:
            return None
        raise TypeError('dst() argument must be a datetime instance or None')

    
    def fromutc(self, dt):
        '''fromutc: dt.tzinfo is not self'''
        if isinstance(dt, datetime):
            if dt.tzinfo is not self:
                raise ValueError('fromutc: dt.tzinfo is not self')
            return dt + self._offset
        raise TypeError('fromutc() argument must be a datetime instance or None')

    _maxoffset = timedelta(hours = 24, microseconds = -1)
    _minoffset = -_maxoffset
    _name_from_offset = (lambda delta: if not delta:
'UTC'if delta < timedelta(0):
sign = '-'delta = -deltaelse:
sign = '+'hours, rest = divmod(delta, timedelta(hours = 1))minutes, rest = divmod(rest, timedelta(minutes = 1))seconds = rest.secondsmicroseconds = rest.microsecondsif microseconds:
f'''UTC{sign}{hours:02d}:{minutes:02d}:{seconds:02d}.{microseconds:06d}'''if seconds:
f'''UTC{sign}{hours:02d}:{minutes:02d}:{seconds:02d}'''f'''UTC{sign}{hours:02d}:{minutes:02d}''')()

UTC = timezone._create(timedelta(0))
timezone.utc = timezone._create(timedelta(0))
timezone.min = timezone._create(-timedelta(hours = 23, minutes = 59))
timezone.max = timezone._create(timedelta(hours = 23, minutes = 59))
_EPOCH = datetime(1970, 1, 1, tzinfo = timezone.utc)
