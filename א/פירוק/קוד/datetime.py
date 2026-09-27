# Source Generated with Decompyle++
# File: datetime.pyc (Python 3.14)

'''Specific date/time and related types.

See https://data.iana.org/time-zones/tz-link.html for
time zone and DST data sources.
'''

try:
    from _datetime import *
except ImportError:
    from _pydatetime import *

__all__ = ('date', 'datetime', 'time', 'timedelta', 'timezone', 'tzinfo', 'MINYEAR', 'MAXYEAR', 'UTC')
