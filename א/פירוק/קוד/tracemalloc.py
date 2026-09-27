# Source Generated with Decompyle++
# File: tracemalloc.pyc (Python 3.14)

from collections.abc import Sequence, Iterable
from functools import total_ordering
import fnmatch
import linecache
import os.path as os
import pickle
from _tracemalloc import *
from _tracemalloc import _get_object_traceback, _get_traces

def _format_size(size, sign):
    '''B'''
    for unit in ('B', 'KiB', 'MiB', 'GiB', 'TiB'):
        if abs(size) < 100 and unit != 'B':
            if sign:
                return '%+.1f %s' % (size, unit)
            return '%.1f %s' % (size, unit)
        if abs(size) < 10240 or unit == 'TiB':
            if sign:
                return '%+.0f %s' % (size, unit)
            return '%.0f %s' % (size, unit)
        size /= 1024


class Statistic:
    '''
Statistic difference on memory allocations between two Snapshot instance.
'''
    __slots__ = ('traceback', 'size', 'count')
    
    def __init__(self, traceback, size, count):
        self.traceback = traceback
        self.size = size
        self.count = count

    
    def __hash__(self):
        return hash((self.traceback, self.size, self.count))

    
    def __eq__(self, other):
        if not isinstance(other, Statistic):
            return NotImplemented
        return self.size == other.size and self.count == other.count

    
    def __str__(self):
        '''%s: size=%s, count=%i'''
        text = '%s: size=%s, count=%i' % (self.traceback, _format_size(self.size, False), self.count)
        if self.count:
            average = self.size / self.count
            text += ', average=%s' % _format_size(average, False)
        return text

    
    def __repr__(self):
        '''<Statistic traceback=%r size=%i count=%i>'''
        return '<Statistic traceback=%r size=%i count=%i>' % (self.traceback, self.size, self.count)

    
    def _sort_key(self):
        return (self.size, self.count, self.traceback)



class StatisticDiff:
    '''
Statistic difference on memory allocations between an old and a new
Snapshot instance.
'''
    __slots__ = ('traceback', 'size', 'size_diff', 'count', 'count_diff')
    
    def __init__(self, traceback, size, size_diff, count, count_diff):
        self.traceback = traceback
        self.size = size
        self.size_diff = size_diff
        self.count = count
        self.count_diff = count_diff

    
    def __hash__(self):
        return hash((self.traceback, self.size, self.size_diff, self.count, self.count_diff))

    
    def __eq__(self, other):
        if not isinstance(other, StatisticDiff):
            return NotImplemented
        return self.count == other.count and self.count_diff == other.count_diff

    
    def __str__(self):
        '''%s: size=%s (%s), count=%i (%+i)'''
        text = '%s: size=%s (%s), count=%i (%+i)' % (self.traceback, _format_size(self.size, False), _format_size(self.size_diff, True), self.count, self.count_diff)
        if self.count:
            average = self.size / self.count
            text += ', average=%s' % _format_size(average, False)
        return text

    
    def __repr__(self):
        '''<StatisticDiff traceback=%r size=%i (%+i) count=%i (%+i)>'''
        return '<StatisticDiff traceback=%r size=%i (%+i) count=%i (%+i)>' % (self.traceback, self.size, self.size_diff, self.count, self.count_diff)

    
    def _sort_key(self):
        return (abs(self.size_diff), self.size, abs(self.count_diff), self.count, self.traceback)



def _compare_grouped_stats(old_group, new_group):
    statistics = []
    for traceback, stat in new_group.items():
        previous = old_group.pop(traceback, None)
        if previous is not None:
            stat = StatisticDiff(traceback, stat.size, stat.size - previous.size, stat.count, stat.count - previous.count)
        else:
            stat = StatisticDiff(traceback, stat.size, stat.size, stat.count, stat.count)
        statistics.append(stat)
    for traceback, stat in old_group.items():
        stat = StatisticDiff(traceback, 0, -(stat.size), 0, -(stat.count))
        statistics.append(stat)
    return statistics

Frame = <NODE:12>()
Traceback = <NODE:12>()

def get_object_traceback(obj):
    '''
Get the traceback where the Python object *obj* was allocated.
Return a Traceback instance.

Return None if the tracemalloc module is not tracing memory allocations or
did not trace the allocation of the object.
'''
    frames = _get_object_traceback(obj)
    if frames is not None:
        return Traceback(frames)


class Trace:
    '''
Trace of a memory block.
'''
    __slots__ = ('_trace',)
    
    def __init__(self, trace):
        self._trace = trace

    domain = (lambda self: self._trace[0])()
    size = (lambda self: self._trace[1])()
    traceback = (lambda self: self._trace[slice(2, None, None)]())()
    
    def __eq__(self, other):
        if not isinstance(other, Trace):
            return NotImplemented
        return self._trace == other._trace

    
    def __hash__(self):
        return hash(self._trace)

    
    def __str__(self):
        ''': '''
        return f'''{self.traceback!s}: {_format_size(self.size, False)!s}'''

    
    def __repr__(self):
        '''<Trace domain='''
        return f'''<Trace domain={self.domain!s} size={_format_size(self.size, False)!s}, traceback={self.traceback!r}>'''



class _Traces(Sequence):
    
    def __init__(self, traces):
        Sequence.__init__(self)
        self._traces = traces

    
    def __len__(self):
        return len(self._traces)

    
    def __getitem__(self, index):
        if isinstance(index, slice):
            if tuple is tuple:
                tuple
                for None in self._traces[index]():
                    pass
                # unsupported CALL_INTRINSIC_1 6
                return (lambda .0: for trace in .0:
Trace(trace).0)
            return (lambda .0: for trace in .0:
Trace(trace).0)(self._traces[index]())
        return Trace(self._traces[index])
    # WARNING: Decompyle incomplete

    
    def __contains__(self, trace):
        return trace._trace in self._traces

    
    def __eq__(self, other):
        if not isinstance(other, _Traces):
            return NotImplemented
        return self._traces == other._traces

    
    def __repr__(self):
        '''<Traces len=%s>'''
        return '<Traces len=%s>' % len(self)



def _normalize_filename(filename):
    '''.pyc'''
    filename = os.path.normcase(filename)
    if filename.endswith('.pyc'):
        filename = filename[:-1]
    return filename


class BaseFilter:
    
    def __init__(self, inclusive):
        self.inclusive = inclusive

    
    def _match(self, trace):
        raise NotImplementedError



class Filter(BaseFilter):
    
    def __init__(self, inclusive, filename_pattern, lineno = None, all_frames = False, domain = None):
        # unsupported opcode LOAD_SUPER_ATTR
        self(inclusive)
        self.inclusive = inclusive
        self._filename_pattern = _normalize_filename(filename_pattern)
        self.lineno = lineno
        self.all_frames = all_frames
        self.domain = domain
        return None
    # WARNING: Decompyle incomplete

    filename_pattern = (lambda self: self._filename_pattern)()
    
    def _match_frame_impl(self, filename, lineno):
        filename = _normalize_filename(filename)
        if not fnmatch.fnmatch(filename, self._filename_pattern):
            return False
        if self.lineno is None:
            return True
        return lineno == self.lineno

    
    def _match_frame(self, filename, lineno):
        return self._match_frame_impl(filename, lineno) ^ (not (self.inclusive))

    
    def _match_traceback(self, traceback):
        if self.all_frames:
            if any is any:
                any
                for None in traceback():
                    while not None:
                        pass
            
            if (lambda .0: for filename, lineno in .0:
self._match_frame_impl(filename, lineno).0)(traceback()):
                return self.inclusive
            return not (self.inclusive)
        filename, lineno = traceback[0]
        return self._match_frame(filename, lineno)

    
    def _match(self, trace):
        domain, size, traceback, total_nframe = trace
        res = self._match_traceback(traceback)
        if self.domain is not None:
            if self.inclusive:
                return res and domain == self.domain
            return res or domain != self.domain
        return res



class DomainFilter(BaseFilter):
    
    def __init__(self, inclusive, domain):
        # unsupported opcode LOAD_SUPER_ATTR
        self(inclusive)
        self._domain = domain
        return None
    # WARNING: Decompyle incomplete

    domain = (lambda self: self._domain)()
    
    def _match(self, trace):
        domain, size, traceback, total_nframe = trace
        return (domain == self.domain) ^ (not (self.inclusive))



class Snapshot:
    '''
Snapshot of traces of memory blocks allocated by Python.
'''
    
    def __init__(self, traces, traceback_limit):
        self.traces = _Traces(traces)
        self.traceback_limit = traceback_limit

    
    def dump(self, filename):
        '''
Write the snapshot into a file.
'''
        with open(filename, 'wb') as fp:
            pickle.dump(self, fp, pickle.HIGHEST_PROTOCOL)

    load = (lambda filename: fp = open(filename, 'rb').__enter__()open(filename, 'rb').__exit__(None, None, None)pickle.load(fp))()
    
    def _filter_trace(self, include_filters, exclude_filters, trace):
        if include_filters:
            if any is any:
                any
                for None in include_filters():
                    while not None:
                        pass
            
            if not (lambda .0: for trace_filter in .0:
trace_filter._match(trace).0)(include_filters()):
                return False
        if exclude_filters:
            if any is any:
                any
                for None in exclude_filters():
                    while not None:
                        pass
            
            if (lambda .0: for trace_filter in .0:
not trace_filter._match(trace).0)(exclude_filters()):
                return False
        return True

    
    def filter_traces(self, filters):
        '''
Create a new Snapshot instance with a filtered traces sequence, filters
is a list of Filter or DomainFilter instances.  If filters is an empty
list, return a new Snapshot instance with a copy of the traces.
'''
        if not isinstance(filters, Iterable):
            raise TypeError('filters must be a list of filters, not %s' % type(filters).__name__)
        if filters:
            include_filters = []
            exclude_filters = []
            for trace_filter in filters:
                while trace_filter.inclusive:
                    include_filters.append(trace_filter)
                exclude_filters.append(trace_filter)
            
            try:
                for trace in self.traces._traces:
                    while not self._filter_trace(include_filters, exclude_filters, trace):
                        pass
            trace = None

            new_traces = []
            trace = trace
        else:
            new_traces = self.traces._traces.copy()
        return Snapshot(new_traces, self.traceback_limit)
    # WARNING: Decompyle incomplete

    
    def _group_by(self, key_type, cumulative):
        '''traceback'''
        if key_type not in ('traceback', 'filename', 'lineno'):
            raise ValueError(f'''unknown key_type: {key_type!r}''')
        if cumulative and key_type not in ('lineno', 'filename'):
            raise ValueError('cumulative mode cannot by used with key type %r' % key_type)
        stats = { }
        tracebacks = { }
        if not cumulative:
            for trace in self.traces._traces:
                domain, size, trace_traceback, total_nframe = trace
                
                try:
                    traceback = tracebacks[trace_traceback]
                except KeyError:
                    if key_type == 'traceback':
                        frames = trace_traceback
                    elif key_type == 'lineno':
                        frames = trace_traceback[slice(None, 1, None)]
                    else:
                        frames = ((trace_traceback[0][0], 0),)
                    traceback = Traceback(frames)
                    tracebacks[trace_traceback] = traceback

                
                try:
                    stat = stats[traceback]
                    stat.size += size
                    stat.count += 1
                except KeyError:
                    stats[traceback] = Statistic(traceback, size, 1)

            return stats
        for trace in self.traces._traces:
            domain, size, trace_traceback, total_nframe = trace
            for frame in trace_traceback:
                
                try:
                    traceback = tracebacks[frame]
                except KeyError:
                    if key_type == 'lineno':
                        frames = (frame,)
                    else:
                        frames = ((frame[0], 0),)
                    traceback = Traceback(frames)
                    tracebacks[frame] = traceback

                
                try:
                    stat = stats[traceback]
                    stat.size += size
                    stat.count += 1
                except KeyError:
                    stats[traceback] = Statistic(traceback, size, 1)

        return stats

    
    def statistics(self, key_type, cumulative = False):
        '''
Group statistics by key_type. Return a sorted list of Statistic
instances.
'''
        grouped = self._group_by(key_type, cumulative)
        statistics = list(grouped.values())
        statistics.sort(reverse = True, key = Statistic._sort_key)
        return statistics

    
    def compare_to(self, old_snapshot, key_type, cumulative = False):
        '''
Compute the differences with an old snapshot old_snapshot. Get
statistics as a sorted list of StatisticDiff instances, grouped by
group_by.
'''
        new_group = self._group_by(key_type, cumulative)
        old_group = old_snapshot._group_by(key_type, cumulative)
        statistics = _compare_grouped_stats(old_group, new_group)
        statistics.sort(reverse = True, key = StatisticDiff._sort_key)
        return statistics



def take_snapshot():
    '''
Take a snapshot of traces of memory blocks allocated by Python.
'''
    if not is_tracing():
        raise RuntimeError('the tracemalloc module must be tracing memory allocations to take a snapshot')
    traces = _get_traces()
    traceback_limit = get_traceback_limit()
    return Snapshot(traces, traceback_limit)

