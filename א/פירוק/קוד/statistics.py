# Source Generated with Decompyle++
# File: statistics.pyc (Python 3.14)


def __annotate__(format):
    if format > 2:
        raise NotImplementedError
    if 0 in __conditional_annotations__:
        pass
    return {
        '_sqrt_bit_width': int }

__conditional_annotations__ = {}
__doc__ = '\nBasic statistics module.\n\nThis module provides functions for calculating statistics of data, including\naverages, variance, and standard deviation.\n\nCalculating averages\n--------------------\n\n==================  ==================================================\nFunction            Description\n==================  ==================================================\nmean                Arithmetic mean (average) of data.\nfmean               Fast, floating-point arithmetic mean.\ngeometric_mean      Geometric mean of data.\nharmonic_mean       Harmonic mean of data.\nmedian              Median (middle value) of data.\nmedian_low          Low median of data.\nmedian_high         High median of data.\nmedian_grouped      Median, or 50th percentile, of grouped data.\nmode                Mode (most common value) of data.\nmultimode           List of modes (most common values of data).\nquantiles           Divide data into intervals with equal probability.\n==================  ==================================================\n\nCalculate the arithmetic mean ("the average") of data:\n\n>>> mean([-1.0, 2.5, 3.25, 5.75])\n2.625\n\n\nCalculate the standard median of discrete data:\n\n>>> median([2, 3, 4, 5])\n3.5\n\n\nCalculate the median, or 50th percentile, of data grouped into class intervals\ncentred on the data values provided. E.g. if your data points are rounded to\nthe nearest whole number:\n\n>>> median_grouped([2, 2, 3, 3, 3, 4])  #doctest: +ELLIPSIS\n2.8333333333...\n\nThis should be interpreted in this way: you have two data points in the class\ninterval 1.5-2.5, three data points in the class interval 2.5-3.5, and one in\nthe class interval 3.5-4.5. The median of these data points is 2.8333...\n\n\nCalculating variability or spread\n---------------------------------\n\n==================  =============================================\nFunction            Description\n==================  =============================================\npvariance           Population variance of data.\nvariance            Sample variance of data.\npstdev              Population standard deviation of data.\nstdev               Sample standard deviation of data.\n==================  =============================================\n\nCalculate the standard deviation of sample data:\n\n>>> stdev([2.5, 3.25, 5.5, 11.25, 11.75])  #doctest: +ELLIPSIS\n4.38961843444...\n\nIf you have previously calculated the mean, you can pass it as the optional\nsecond argument to the four "spread" functions to avoid recalculating it:\n\n>>> data = [1, 2, 2, 4, 4, 4, 5, 6]\n>>> mu = mean(data)\n>>> pvariance(data, mu)\n2.5\n\n\nStatistics for relations between two inputs\n-------------------------------------------\n\n==================  ====================================================\nFunction            Description\n==================  ====================================================\ncovariance          Sample covariance for two variables.\ncorrelation         Pearson\'s correlation coefficient for two variables.\nlinear_regression   Intercept and slope for simple linear regression.\n==================  ====================================================\n\nCalculate covariance, Pearson\'s correlation, and simple linear regression\nfor two inputs:\n\n>>> x = [1, 2, 3, 4, 5, 6, 7, 8, 9]\n>>> y = [1, 2, 3, 1, 2, 3, 1, 2, 3]\n>>> covariance(x, y)\n0.75\n>>> correlation(x, y)  #doctest: +ELLIPSIS\n0.31622776601...\n>>> linear_regression(x, y)  #doctest:\nLinearRegression(slope=0.1, intercept=1.5)\n\n\nExceptions\n----------\n\nA single exception is defined: StatisticsError is a subclass of ValueError.\n\n'
__all__ = [
    'NormalDist',
    'StatisticsError',
    'correlation',
    'covariance',
    'fmean',
    'geometric_mean',
    'harmonic_mean',
    'kde',
    'kde_random',
    'linear_regression',
    'mean',
    'median',
    'median_grouped',
    'median_high',
    'median_low',
    'mode',
    'multimode',
    'pstdev',
    'pvariance',
    'quantiles',
    'stdev',
    'variance']
import math
import numbers
import random
import sys
from fractions import Fraction
from decimal import Decimal
from itertools import count, groupby, repeat
from bisect import bisect_left, bisect_right
from math import hypot, sqrt, fabs, exp, erfc, tau, log, fsum, sumprod
from math import isfinite, isinf, pi, cos, sin, tan, cosh, asin, atan, acos
from functools import reduce
from operator import itemgetter
from collections import Counter, namedtuple, defaultdict
_SQRT2 = sqrt(2)
_random = random

class StatisticsError(ValueError):
    pass


def mean(data):
    '''Return the sample arithmetic mean of data.

>>> mean([1, 2, 3, 4, 4])
2.8

>>> from fractions import Fraction as F
>>> mean([F(3, 7), F(1, 21), F(5, 3), F(1, 3)])
Fraction(13, 21)

>>> from decimal import Decimal as D
>>> mean([D("0.5"), D("0.75"), D("0.625"), D("0.375")])
Decimal(\'0.5625\')

If ``data`` is empty, StatisticsError will be raised.

'''
    (T, total, n) = _sum(data)
    if n < 1:
        raise StatisticsError('mean requires at least one data point')
    return _convert(total / n, T)


def fmean(data, weights = None):
    '''Convert data to floats and compute the arithmetic mean.

This runs faster than the mean() function and it always returns a float.
If the input dataset is empty, it raises a StatisticsError.

>>> fmean([3.5, 4.0, 5.25])
4.25

'''
    if weights is None:
        
        try:
            n = len(data)
        except TypeError:
            counter = count()
            total = fsum(map(itemgetter(0), zip(data, counter)))
            n = next(counter)

        total = fsum(data)
        if not n:
            raise StatisticsError('fmean requires at least one data point')
        return total / n
    if not isinstance(weights, (list, tuple)):
        weights = list(weights)
    
    try:
        num = sumprod(data, weights)
    except ValueError:
        raise StatisticsError('data and weights must be the same length')

    den = fsum(weights)
    if not den:
        raise StatisticsError('sum of weights must be non-zero')
    return num / den


def geometric_mean(data):
    '''Convert data to floats and compute the geometric mean.

Raises a StatisticsError if the input dataset is empty
or if it contains a negative value.

Returns zero if the product of inputs is zero.

No special efforts are made to achieve exact results.
(However, this may change in the future.)

>>> round(geometric_mean([54, 24, 36]), 9)
36.0

'''
    n = 0
    found_zero = False
    
    def count_positive(iterable):
        for n, x in enumerate(iterable, start = 1):
            if x > 0 or math.isnan(x):
                yield x
                enumerate(iterable, start = 1)
                continue
            if x == 0:
                found_zero = True
                continue
            raise StatisticsError('No negative inputs allowed', x)

    total = fsum(map(log, count_positive(data)))
    if not n:
        raise StatisticsError('Must have a non-empty dataset')
    if math.isnan(total):
        return math.nan
    if found_zero:
        if total == math.inf:
            return math.nan
        return 0
    return exp(total / n)


def harmonic_mean(data, weights = None):
    '''Return the harmonic mean of data.

The harmonic mean is the reciprocal of the arithmetic mean of the
reciprocals of the data.  It can be used for averaging ratios or
rates, for example speeds.

Suppose a car travels 40 km/hr for 5 km and then speeds-up to
60 km/hr for another 5 km. What is the average speed?

    >>> harmonic_mean([40, 60])
    48.0

Suppose a car travels 40 km/hr for 5 km, and when traffic clears,
speeds-up to 60 km/hr for the remaining 30 km of the journey. What
is the average speed?

    >>> harmonic_mean([40, 60], weights=[5, 30])
    56.0

If ``data`` is empty, or any element is less than zero,
``harmonic_mean`` will raise ``StatisticsError``.

'''
    if iter(data) is data:
        data = list(data)
    errmsg = 'harmonic mean does not support negative values'
    n = len(data)
    if n < 1:
        raise StatisticsError('harmonic_mean requires at least one data point')
    if n == 1 and weights is None:
        x = data[0]
        if isinstance(x, (numbers.Real, Decimal)):
            if x < 0:
                raise StatisticsError(errmsg)
            return x
        raise TypeError('unsupported type')
    if weights is None:
        weights = repeat(1, n)
        sum_weights = n
    elif iter(weights) is weights:
        weights = list(weights)
    if len(weights) != n:
        raise StatisticsError('Number of weights does not match data size')
    (_, sum_weights, _) = (lambda .0: for w in .0:
w.0)(_fail_neg(weights, errmsg)())
    
    try:
        data = _fail_neg(data, errmsg)
        (T, total, count) = (lambda .0: for w, x in .0:
w / x if w else 0.0)(zip(weights, data)())
    except ZeroDivisionError:
        return 0

    if total <= 0:
        raise StatisticsError('Weighted sum must be positive')
    return _convert(sum_weights / total, T)


def median(data):
    '''Return the median (middle value) of numeric data.

When the number of data points is odd, return the middle data point.
When the number of data points is even, the median is interpolated by
taking the average of the two middle values:

>>> median([1, 3, 5])
3
>>> median([1, 3, 5, 7])
4.0

'''
    data = sorted(data)
    n = len(data)
    if n == 0:
        raise StatisticsError('no median for empty data')
    if n % 2 == 1:
        return data[n // 2]
    i = n // 2
    return (data[i - 1] + data[i]) / 2


def median_low(data):
    '''Return the low median of numeric data.

When the number of data points is odd, the middle value is returned.
When it is even, the smaller of the two middle values is returned.

>>> median_low([1, 3, 5])
3
>>> median_low([1, 3, 5, 7])
3

'''
    data = sorted(data)
    n = len(data)
    if n == 0:
        raise StatisticsError('no median for empty data')
    if n % 2 == 1:
        return data[n // 2]
    return data[n // 2 - 1]


def median_high(data):
    '''Return the high median of data.

When the number of data points is odd, the middle value is returned.
When it is even, the larger of the two middle values is returned.

>>> median_high([1, 3, 5])
3
>>> median_high([1, 3, 5, 7])
5

'''
    data = sorted(data)
    n = len(data)
    if n == 0:
        raise StatisticsError('no median for empty data')
    return data[n // 2]


def median_grouped(data, interval = 1):
    '''Estimates the median for numeric data binned around the midpoints
of consecutive, fixed-width intervals.

The *data* can be any iterable of numeric data with each value being
exactly the midpoint of a bin.  At least one value must be present.

The *interval* is width of each bin.

For example, demographic information may have been summarized into
consecutive ten-year age groups with each group being represented
by the 5-year midpoints of the intervals:

    >>> demographics = Counter({
    ...    25: 172,   # 20 to 30 years old
    ...    35: 484,   # 30 to 40 years old
    ...    45: 387,   # 40 to 50 years old
    ...    55:  22,   # 50 to 60 years old
    ...    65:   6,   # 60 to 70 years old
    ... })

The 50th percentile (median) is the 536th person out of the 1071
member cohort.  That person is in the 30 to 40 year old age group.

The regular median() function would assume that everyone in the
tricenarian age group was exactly 35 years old.  A more tenable
assumption is that the 484 members of that age group are evenly
distributed between 30 and 40.  For that, we use median_grouped().

    >>> data = list(demographics.elements())
    >>> median(data)
    35
    >>> round(median_grouped(data, interval=10), 1)
    37.5

The caller is responsible for making sure the data points are separated
by exact multiples of *interval*.  This is essential for getting a
correct result.  The function does not check this precondition.

Inputs may be any numeric type that can be coerced to a float during
the interpolation step.

'''
    data = sorted(data)
    n = len(data)
    if not n:
        raise StatisticsError('no median for empty data')
    x = data[n // 2]
    i = bisect_left(data, x)
    j = bisect_right(data, x, lo = i)
    
    try:
        interval = float(interval)
        x = float(x)
    except ValueError:
        raise TypeError('Value cannot be converted to a float')

    L = x - interval / 2
    cf = i
    f = j - i
    return L + interval * (n / 2 - cf) / f


def mode(data):
    '''Return the most common data point from discrete or nominal data.

``mode`` assumes discrete data, and returns a single value. This is the
standard treatment of the mode as commonly taught in schools:

    >>> mode([1, 1, 2, 3, 3, 3, 3, 4])
    3

This also works with nominal (non-numeric) data:

    >>> mode(["red", "blue", "blue", "red", "green", "red", "red"])
    \'red\'

If there are multiple modes with same frequency, return the first one
encountered:

    >>> mode([\'red\', \'red\', \'green\', \'blue\', \'blue\'])
    \'red\'

If *data* is empty, ``mode``, raises StatisticsError.

'''
    pairs = Counter(iter(data)).most_common(1)
    
    try:
        return pairs[0][0]
    except IndexError:
        raise StatisticsError('no mode for empty data') from None



def multimode(data):
    """Return a list of the most frequently occurring values.

Will return more than one result if there are multiple modes
or an empty list if *data* is empty.

>>> multimode('aabbbbbbbbcc')
['b']
>>> multimode('aabbbbccddddeeffffgg')
['b', 'd', 'f']
>>> multimode('')
[]

"""
    counts = Counter(iter(data))
    if not counts:
        return []
    maxcount = max(counts.values())
    return None
# WARNING: Decompyle incomplete


def variance(data, xbar = None):
    '''Return the sample variance of data.

data should be an iterable of Real-valued numbers, with at least two
values. The optional argument xbar, if given, should be the mean of
the data. If it is missing or None, the mean is automatically calculated.

Use this function when your data is a sample from a population. To
calculate the variance from the entire population, see ``pvariance``.

Examples:

>>> data = [2.75, 1.75, 1.25, 0.25, 0.5, 1.25, 3.5]
>>> variance(data)
1.3720238095238095

If you have already calculated the mean of your data, you can pass it as
the optional second argument ``xbar`` to avoid recalculating it:

>>> m = mean(data)
>>> variance(data, m)
1.3720238095238095

This function does not check that ``xbar`` is actually the mean of
``data``. Giving arbitrary values for ``xbar`` may lead to invalid or
impossible results.

Decimals and Fractions are supported:

>>> from decimal import Decimal as D
>>> variance([D("27.5"), D("30.25"), D("30.25"), D("34.5"), D("41.75")])
Decimal(\'31.01875\')

>>> from fractions import Fraction as F
>>> variance([F(1, 6), F(1, 2), F(5, 3)])
Fraction(67, 108)

'''
    T, ss, c, n = _ss(data, xbar)
    if n < 2:
        raise StatisticsError('variance requires at least two data points')
    return _convert(ss / (n - 1), T)


def pvariance(data, mu = None):
    '''Return the population variance of ``data``.

data should be a sequence or iterable of Real-valued numbers, with at least one
value. The optional argument mu, if given, should be the mean of
the data. If it is missing or None, the mean is automatically calculated.

Use this function to calculate the variance from the entire population.
To estimate the variance from a sample, the ``variance`` function is
usually a better choice.

Examples:

>>> data = [0.0, 0.25, 0.25, 1.25, 1.5, 1.75, 2.75, 3.25]
>>> pvariance(data)
1.25

If you have already calculated the mean of the data, you can pass it as
the optional second argument to avoid recalculating it:

>>> mu = mean(data)
>>> pvariance(data, mu)
1.25

Decimals and Fractions are supported:

>>> from decimal import Decimal as D
>>> pvariance([D("27.5"), D("30.25"), D("30.25"), D("34.5"), D("41.75")])
Decimal(\'24.815\')

>>> from fractions import Fraction as F
>>> pvariance([F(1, 4), F(5, 4), F(1, 2)])
Fraction(13, 72)

'''
    T, ss, c, n = _ss(data, mu)
    if n < 1:
        raise StatisticsError('pvariance requires at least one data point')
    return _convert(ss / n, T)


def stdev(data, xbar = None):
    '''Return the square root of the sample variance.

See ``variance`` for arguments and other details.

>>> stdev([1.5, 2.5, 2.5, 2.75, 3.25, 4.75])
1.0810874155219827

'''
    T, ss, c, n = _ss(data, xbar)
    if n < 2:
        raise StatisticsError('stdev requires at least two data points')
    mss = ss / (n - 1)
    
    try:
        mss_numerator = mss.numerator
        mss_denominator = mss.denominator
    except AttributeError:
        raise ValueError('inf or nan encountered in data')

    if issubclass(T, Decimal):
        return _decimal_sqrt_of_frac(mss_numerator, mss_denominator)
    return _float_sqrt_of_frac(mss_numerator, mss_denominator)


def pstdev(data, mu = None):
    '''Return the square root of the population variance.

See ``pvariance`` for arguments and other details.

>>> pstdev([1.5, 2.5, 2.5, 2.75, 3.25, 4.75])
0.986893273527251

'''
    T, ss, c, n = _ss(data, mu)
    if n < 1:
        raise StatisticsError('pstdev requires at least one data point')
    mss = ss / n
    
    try:
        mss_numerator = mss.numerator
        mss_denominator = mss.denominator
    except AttributeError:
        raise ValueError('inf or nan encountered in data')

    if issubclass(T, Decimal):
        return _decimal_sqrt_of_frac(mss_numerator, mss_denominator)
    return _float_sqrt_of_frac(mss_numerator, mss_denominator)


def covariance(x, y):
    '''Covariance

Return the sample covariance of two inputs *x* and *y*. Covariance
is a measure of the joint variability of two inputs.

>>> x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> y = [1, 2, 3, 1, 2, 3, 1, 2, 3]
>>> covariance(x, y)
0.75
>>> z = [9, 8, 7, 6, 5, 4, 3, 2, 1]
>>> covariance(x, z)
-7.5
>>> covariance(z, x)
-7.5

'''
    n = len(x)
    if len(y) != n:
        raise StatisticsError('covariance requires that both inputs have same number of data points')
    if n < 2:
        raise StatisticsError('covariance requires at least two data points')
    xbar = fsum(x) / n
    ybar = fsum(y) / n
    
    def <genexpr>(.0):
        for yi in .0:
            yield yi - ybar
            .0

    sxy = x()(<genexpr>, y())
    return sxy / (n - 1)


def correlation(x, y, *, method):
    '''Pearson\'s correlation coefficient

Return the Pearson\'s correlation coefficient for two inputs. Pearson\'s
correlation coefficient *r* takes values between -1 and +1. It measures
the strength and direction of a linear relationship.

>>> x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> y = [9, 8, 7, 6, 5, 4, 3, 2, 1]
>>> correlation(x, x)
1.0
>>> correlation(x, y)
-1.0

If *method* is "ranked", computes Spearman\'s rank correlation coefficient
for two inputs.  The data is replaced by ranks.  Ties are averaged
so that equal values receive the same rank.  The resulting coefficient
measures the strength of a monotonic relationship.

Spearman\'s rank correlation coefficient is appropriate for ordinal
data or for continuous data that doesn\'t meet the linear proportion
requirement for Pearson\'s correlation coefficient.

'''
    n = len(x)
    if len(y) != n:
        raise StatisticsError('correlation requires that both inputs have same number of data points')
    if n < 2:
        raise StatisticsError('correlation requires at least two data points')
    if method not in frozenset({'linear', 'ranked'}):
        raise ValueError(f'''Unknown method: {method!r}''')
    if method == 'ranked':
        start = (n - 1) / -2
        x = _rank(x, start = start)
        y = _rank(y, start = start)
    else:
        xbar = fsum(x) / n
        ybar = fsum(y) / n
        
        try:
            for xi in x:
                pass
        xi = None
        
        try:
            for yi in y:
                pass
        yi = x


        x = []
        xi = xi
        
        try:
            for yi in y:
                pass
        yi = x

        y = []
        yi = yi
    sxy = sumprod(x, y)
    sxx = sumprod(x, x)
    syy = sumprod(y, y)
    
    try:
        return sxy / _sqrtprod(sxx, syy)
    except ZeroDivisionError:
        raise StatisticsError('at least one of the inputs is constant')

    
    try:
        for xi in x:
            pass
    xi = None
    
    try:
        for yi in y:
            pass
    yi = x


# WARNING: Decompyle incomplete

LinearRegression = namedtuple('LinearRegression', ('slope', 'intercept'))

def linear_regression(x, y, *, proportional):
    '''Slope and intercept for simple linear regression.

Return the slope and intercept of simple linear regression
parameters estimated using ordinary least squares. Simple linear
regression describes relationship between an independent variable
*x* and a dependent variable *y* in terms of a linear function:

    y = slope * x + intercept + noise

where *slope* and *intercept* are the regression parameters that are
estimated, and noise represents the variability of the data that was
not explained by the linear regression (it is equal to the
difference between predicted and actual values of the dependent
variable).

The parameters are returned as a named tuple.

>>> x = [1, 2, 3, 4, 5]
>>> noise = NormalDist().samples(5, seed=42)
>>> y = [3 * x[i] + 2 + noise[i] for i in range(5)]
>>> linear_regression(x, y)  #doctest: +ELLIPSIS
LinearRegression(slope=3.17495..., intercept=1.00925...)

If *proportional* is true, the independent variable *x* and the
dependent variable *y* are assumed to be directly proportional.
The data is fit to a line passing through the origin.

Since the *intercept* will always be 0.0, the underlying linear
function simplifies to:

    y = slope * x + noise

>>> y = [3 * x[i] + noise[i] for i in range(5)]
>>> linear_regression(x, y, proportional=True)  #doctest: +ELLIPSIS
LinearRegression(slope=2.90475..., intercept=0.0)

'''
    n = len(x)
    if len(y) != n:
        raise StatisticsError('linear regression requires that both inputs have same number of data points')
    if n < 2:
        raise StatisticsError('linear regression requires at least two data points')
    if not proportional:
        xbar = fsum(x) / n
        ybar = fsum(y) / n
        
        try:
            for xi in x:
                pass
        xi = None

        x = []
        xi = xi
        y = y()
    sxy = sumprod(x, y) + 0
    sxx = sumprod(x, x)
    
    try:
        slope = sxy / sxx
    except ZeroDivisionError:
        raise StatisticsError('x is constant')

    intercept = 0 if proportional else ybar - slope * xbar
    return LinearRegression(slope = slope, intercept = intercept)
# WARNING: Decompyle incomplete

_kernel_specs = { }

def register(*kernels):
    """Load the kernel's pdf, cdf, invcdf, and support into _kernel_specs."""
    
    def deco(builder):
        '''pdf'''
        spec = dict(zip(('pdf', 'cdf', 'invcdf', 'support'), builder()))
        for kernel in kernels:
            _kernel_specs[kernel] = spec
        return builder

    return deco

normal_kernel = (lambda : sqrt2pi = sqrt(2 * pi)neg_sqrt2 = -sqrt(2)
pdf = lambda t: exp(-0.5 * t * t) / sqrt2pi
cdf = lambda t: 0.5 * erfc(t / neg_sqrt2)
invcdf = lambda t: _normal_dist_inv_cdf(t, 0, 1)support = None(pdf, cdf, invcdf, support))()
logistic_kernel = (lambda : 
pdf = lambda t: 0.5 / (1 + cosh(t))
cdf = lambda t: 1 - 1 / (exp(t) + 1)
invcdf = lambda p: log(p / (1 - p))support = None(pdf, cdf, invcdf, support))()
sigmoid_kernel = (lambda : c1 = 1 / pic2 = 2 / pic3 = pi / 2
pdf = lambda t: c1 / cosh(t)
cdf = lambda t: c2 * atan(exp(t))
invcdf = lambda p: log(tan(p * c3))support = None(pdf, cdf, invcdf, support))()
rectangular_kernel = (lambda : 
pdf = lambda t: 0.5
cdf = lambda t: 0.5 * t + 0.5
invcdf = lambda p: 2 * p - 1support = 1(pdf, cdf, invcdf, support))()
triangular_kernel = (lambda : 
pdf = lambda t: 1 - abs(t)
cdf = lambda t: t * t * 0.5 if t < 0 else -0.5 + t + 0.5
invcdf = lambda p: if p < 0.5:
sqrt(2 * p) - 11 - sqrt(2 - 2 * p)support = 1(pdf, cdf, invcdf, support))()
parabolic_kernel = (lambda : 
pdf = lambda t: 0.75 * (1 - t * t)
cdf = lambda t: sumprod((-0.25, 0.75, 0.5), (t ** 3, t, 1))
invcdf = lambda p: 2 * cos((acos(2 * p - 1) + pi) / 3)support = 1(pdf, cdf, invcdf, support))()

def _newton_raphson(f_inv_estimate, f, f_prime, tolerance = 1e-12):
    
    def f_inv(y):
        '''Return x such that f(x) ≈ y within the specified tolerance.'''
        x = f_inv_estimate(y)
        diff = f(x) - y
        while abs(f(x) - y) > tolerance:
            x -= diff / f_prime(x)
        return x

    return f_inv


def _quartic_invcdf_estimate(p):
    sign, p = (1, p) if p <= 0.5 else (-1, 1 - p)
    if p < 0.0106:
        return ((2 * p) ** 0.3838 - 1) * sign
    x = (2 * p) ** 0.425887 - 1
    if p < 0.499:
        x += 0.0268187 * sin(7.10175 * p + 2.73231)
    return x * sign

quartic_kernel = (lambda : 
pdf = lambda t: 0.9375 * (1 - t * t) ** 2
cdf = lambda t: sumprod((0.1875, -0.625, 0.9375, 0.5), (t ** 5, t ** 3, t, 1))invcdf = _newton_raphson(_quartic_invcdf_estimate, f = cdf, f_prime = pdf)support = 1(pdf, cdf, invcdf, support))()

def _triweight_invcdf_estimate(p):
    sign, p = (1, p) if p <= 0.5 else (-1, 1 - p)
    x = (2 * p) ** 0.340022 - 1
    if not (1e-05 < p) or p < 0.499:
        pass
    else:
        return x * sign
    x -= 0.033 * sin(1.07 * tau * (p - 0.035))
    return x * sign

triweight_kernel = (lambda : 
pdf = lambda t: 1.09375 * (1 - t * t) ** 3
cdf = lambda t: sumprod((-0.15625, 0.65625, -1.09375, 1.09375, 0.5), (t ** 7, t ** 5, t ** 3, t, 1))invcdf = _newton_raphson(_triweight_invcdf_estimate, f = cdf, f_prime = pdf)support = 1(pdf, cdf, invcdf, support))()
cosine_kernel = (lambda : c1 = pi / 4c2 = pi / 2
pdf = lambda t: c1 * cos(c2 * t)
cdf = lambda t: 0.5 * sin(c2 * t) + 0.5
invcdf = lambda p: 2 * asin(2 * p - 1) / pisupport = 1(pdf, cdf, invcdf, support))()
del register
del normal_kernel
del logistic_kernel
del sigmoid_kernel
del rectangular_kernel
del triangular_kernel
del parabolic_kernel
del quartic_kernel
del triweight_kernel
del cosine_kernel

def kde(data, h, kernel = 'normal', *, cumulative):
    """Kernel Density Estimation:  Create a continuous probability density
function or cumulative distribution function from discrete samples.

The basic idea is to smooth the data using a kernel function
to help draw inferences about a population from a sample.

The degree of smoothing is controlled by the scaling parameter h
which is called the bandwidth.  Smaller values emphasize local
features while larger values give smoother results.

The kernel determines the relative weights of the sample data
points.  Generally, the choice of kernel shape does not matter
as much as the more influential bandwidth smoothing parameter.

Kernels that give some weight to every sample point:

   normal (gauss)
   logistic
   sigmoid

Kernels that only give weight to sample points within
the bandwidth:

   rectangular (uniform)
   triangular
   parabolic (epanechnikov)
   quartic (biweight)
   triweight
   cosine

If *cumulative* is true, will return a cumulative distribution function.

A StatisticsError will be raised if the data sequence is empty.

Example
-------

Given a sample of six data points, construct a continuous
function that estimates the underlying probability density:

    >>> sample = [-2.1, -1.3, -0.4, 1.9, 5.1, 6.2]
    >>> f_hat = kde(sample, h=1.5)

Compute the area under the curve:

    >>> area = sum(f_hat(x) for x in range(-20, 20))
    >>> round(area, 4)
    1.0

Plot the estimated probability density function at
evenly spaced points from -6 to 10:

    >>> for x in range(-6, 11):
    ...     density = f_hat(x)
    ...     plot = ' ' * int(density * 400) + 'x'
    ...     print(f'{x:2}: {density:.3f} {plot}')
    ...
    -6: 0.002 x
    -5: 0.009    x
    -4: 0.031             x
    -3: 0.070                             x
    -2: 0.111                                             x
    -1: 0.125                                                   x
     0: 0.110                                            x
     1: 0.086                                   x
     2: 0.068                            x
     3: 0.059                        x
     4: 0.066                           x
     5: 0.082                                 x
     6: 0.082                                 x
     7: 0.058                        x
     8: 0.028            x
     9: 0.009    x
    10: 0.002 x

Estimate P(4.5 < X <= 7.5), the probability that a new sample value
will be between 4.5 and 7.5:

    >>> cdf = kde(sample, h=1.5, cumulative=True)
    >>> round(cdf(7.5) - cdf(4.5), 2)
    0.22

References
----------

Kernel density estimation and its application:
https://www.itm-conferences.org/articles/itmconf/pdf/2018/08/itmconf_sam2018_00037.pdf

Kernel functions in common use:
https://en.wikipedia.org/wiki/Kernel_(statistics)#kernel_functions_in_common_use

Interactive graphical demonstration and exploration:
https://demonstrations.wolfram.com/KernelDensityEstimation/

Kernel estimation of cumulative distribution function of a random variable with bounded support
https://www.econstor.eu/bitstream/10419/207829/1/10.21307_stattrans-2016-037.pdf

"""
    n = len(data)
    if not n:
        raise StatisticsError('Empty data sequence')
    if not isinstance(data[0], (int, float)):
        raise TypeError('Data sequence must contain ints or floats')
    if h <= 0:
        raise StatisticsError(f'''Bandwidth h must be positive, not h={h!r}''')
    kernel_spec = _kernel_specs.get(kernel)
    if kernel_spec is None:
        raise StatisticsError(f'''Unknown kernel name: {kernel!r}''')
    K = kernel_spec['pdf']
    W = kernel_spec['cdf']
    support = kernel_spec['support']
    if support is None:
        
        def pdf(x):
            return (lambda .0: for x_i in .0:
K((x - x_i) / h).0)(data()) / (len(data) * h)

        
        def cdf(x):
            return (lambda .0: for x_i in .0:
W((x - x_i) / h).0)(data()) / len(data)

    else:
        sample = sorted(data)
        bandwidth = h * support
        
        def pdf(x):
            if len(data) != n:
                sample = sorted(data)
                n = len(data)
            i = bisect_left(sample, x - bandwidth)
            j = bisect_right(sample, x + bandwidth)
            supported = sample[i:j]
            return (lambda .0: for x_i in .0:
K((x - x_i) / h).0)(supported()) / (n * h)

        
        def cdf(x):
            if len(data) != n:
                sample = sorted(data)
                n = len(data)
            i = bisect_left(sample, x - bandwidth)
            j = bisect_right(sample, x + bandwidth)
            supported = sample[i:j]
            return (lambda .0: for x_i in .0:
W((x - x_i) / h).0)(supported(), i) / n

    if cumulative:
        cdf.__doc__ = f'''CDF estimate with h={h!r} and kernel={kernel!r}'''
        return cdf
    pdf.__doc__ = f'''PDF estimate with h={h!r} and kernel={kernel!r}'''
    return pdf


def kde_random(data, h, kernel = 'normal', *, seed):
    '''Return a function that makes a random selection from the estimated
probability density function created by kde(data, h, kernel).

Providing a *seed* allows reproducible selections within a single
thread.  The seed may be an integer, float, str, or bytes.

A StatisticsError will be raised if the *data* sequence is empty.

Example:

>>> data = [-2.1, -1.3, -0.4, 1.9, 5.1, 6.2]
>>> rand = kde_random(data, h=1.5, seed=8675309)
>>> new_selections = [rand() for i in range(10)]
>>> [round(x, 1) for x in new_selections]
[0.7, 6.2, 1.2, 6.9, 7.0, 1.8, 2.5, -0.5, -1.8, 5.6]

'''
    n = len(data)
    if not n:
        raise StatisticsError('Empty data sequence')
    if not isinstance(data[0], (int, float)):
        raise TypeError('Data sequence must contain ints or floats')
    if h <= 0:
        raise StatisticsError(f'''Bandwidth h must be positive, not h={h!r}''')
    kernel_spec = _kernel_specs.get(kernel)
    if kernel_spec is None:
        raise StatisticsError(f'''Unknown kernel name: {kernel!r}''')
    invcdf = kernel_spec['invcdf']
    prng = _random.Random(seed)
    random = prng.random
    choice = prng.choice
    
    def rand():
        return choice(data) + h * invcdf(random())

    rand.__doc__ = f'''Random KDE selection with h={h!r} and kernel={kernel!r}'''
    return rand


def quantiles(data, *, n, method):
    '''Divide *data* into *n* continuous intervals with equal probability.

Returns a list of (n - 1) cut points separating the intervals.

Set *n* to 4 for quartiles (the default).  Set *n* to 10 for deciles.
Set *n* to 100 for percentiles which gives the 99 cuts points that
separate *data* in to 100 equal sized groups.

The *data* can be any iterable containing sample.
The cut points are linearly interpolated between data points.

If *method* is set to *inclusive*, *data* is treated as population
data.  The minimum value is treated as the 0th percentile and the
maximum value is treated as the 100th percentile.

'''
    if n < 1:
        raise StatisticsError('n must be at least 1')
    data = sorted(data)
    ld = len(data)
    if ld < 2:
        if ld == 1:
            return data * (n - 1)
        raise StatisticsError('must have at least one data point')
    if method == 'inclusive':
        m = ld - 1
        result = []
        for i in range(1, n):
            j, delta = divmod(i * m, n)
            interpolated = (data[j] * (n - delta) + data[j + 1] * delta) / n
            result.append(interpolated)
        return result
    if method == 'exclusive':
        m = ld + 1
        result = []
        for i in range(1, n):
            j = i * m // n
            if j < 1:
                pass
            elif j > ld - 1:
                pass
            
            j = j
            delta = i * m - j * n
            interpolated = (data[j - 1] * (n - delta) + data[j] * delta) / n
            result.append(interpolated)
        return result
    raise ValueError(f'''Unknown method: {method!r}''')


class NormalDist:
    '''Normal distribution of a random variable'''
    __slots__ = {
        '_sigma': 'Standard deviation of a normal distribution',
        '_mu': 'Arithmetic mean of a normal distribution' }
    
    def __init__(self, mu = 0, sigma = 1):
        '''NormalDist where mu is the mean and sigma is the standard deviation.'''
        if sigma < 0:
            raise StatisticsError('sigma must be non-negative')
        self._mu = float(mu)
        self._sigma = float(sigma)

    from_samples = (lambda cls, data: _mean_stdev(data)())()
    
    def samples(self, n, *, seed):
        '''Generate *n* samples for a given mean and standard deviation.'''
        rnd = random.random if seed is None else random.Random(seed).random
        inv_cdf = _normal_dist_inv_cdf
        mu = self._mu
        sigma = self._sigma
        return None
    # WARNING: Decompyle incomplete

    
    def pdf(self, x):
        '''Probability density function.  P(x <= X < x+dx) / dx'''
        variance = self._sigma * self._sigma
        if not variance:
            raise StatisticsError('pdf() not defined when sigma is zero')
        diff = x - self._mu
        return exp(diff * diff / (-2 * variance)) / sqrt(tau * variance)

    
    def cdf(self, x):
        '''Cumulative distribution function.  P(X <= x)'''
        if not self._sigma:
            raise StatisticsError('cdf() not defined when sigma is zero')
        return 0.5 * erfc((self._mu - x) / (self._sigma * _SQRT2))

    
    def inv_cdf(self, p):
        '''Inverse cumulative distribution function.  x : P(X <= x) = p

Finds the value of the random variable such that the probability of
the variable being less than or equal to that value equals the given
probability.

This function is also called the percent point function or quantile
function.
'''
        if p <= 0 or p >= 1:
            raise StatisticsError('p must be in the range 0.0 < p < 1.0')
        return _normal_dist_inv_cdf(p, self._mu, self._sigma)

    
    def quantiles(self, n = 4):
        '''Divide into *n* continuous intervals with equal probability.

Returns a list of (n - 1) cut points separating the intervals.

Set *n* to 4 for quartiles (the default).  Set *n* to 10 for deciles.
Set *n* to 100 for percentiles which gives the 99 cuts points that
separate the normal distribution in to 100 equal sized groups.
'''
        return None
    # WARNING: Decompyle incomplete

    
    def overlap(self, other):
        '''Compute the overlapping coefficient (OVL) between two normal distributions.

Measures the agreement between two normal probability distributions.
Returns a value between 0.0 and 1.0 giving the overlapping area in
the two underlying probability density functions.

    >>> N1 = NormalDist(2.4, 1.6)
    >>> N2 = NormalDist(3.2, 2.0)
    >>> N1.overlap(N2)
    0.8035050657330205
'''
        if not isinstance(other, NormalDist):
            raise TypeError('Expected another NormalDist instance')
        Y = self
        X = other
        if (Y._sigma, Y._mu) < (X._sigma, X._mu):
            Y = Y
            X = X
        Y_var = X.variance
        X_var = Y.variance
        if not X_var or not Y_var:
            raise StatisticsError('overlap() not defined when sigma is zero')
        dv = Y_var - X_var
        dm = fabs(Y._mu - X._mu)
        if not dv:
            return erfc(dm / (2 * X._sigma * _SQRT2))
        a = X._mu * Y_var - Y._mu * X_var
        b = X._sigma * Y._sigma * sqrt(dm * dm + dv * log(Y_var / X_var))
        x1 = (a + b) / dv
        x2 = (a - b) / dv
        return 1 - (fabs(Y.cdf(x1) - X.cdf(x1)) + fabs(Y.cdf(x2) - X.cdf(x2)))

    
    def zscore(self, x):
        '''Compute the Standard Score.  (x - mean) / stdev

Describes *x* in terms of the number of standard deviations
above or below the mean of the normal distribution.
'''
        if not self._sigma:
            raise StatisticsError('zscore() not defined when sigma is zero')
        return (x - self._mu) / self._sigma

    mean = (lambda self: self._mu)()
    median = (lambda self: self._mu)()
    mode = (lambda self: self._mu)()
    stdev = (lambda self: self._sigma)()
    variance = (lambda self: self._sigma * self._sigma)()
    
    def __add__(x1, x2):
        '''Add a constant or another NormalDist instance.

If *other* is a constant, translate mu by the constant,
leaving sigma unchanged.

If *other* is a NormalDist, add both the means and the variances.
Mathematically, this works only if the two distributions are
independent or if they are jointly normally distributed.
'''
        if isinstance(x2, NormalDist):
            return NormalDist(x1._mu + x2._mu, hypot(x1._sigma, x2._sigma))
        return NormalDist(x1._mu + x2, x1._sigma)

    
    def __sub__(x1, x2):
        '''Subtract a constant or another NormalDist instance.

If *other* is a constant, translate by the constant mu,
leaving sigma unchanged.

If *other* is a NormalDist, subtract the means and add the variances.
Mathematically, this works only if the two distributions are
independent or if they are jointly normally distributed.
'''
        if isinstance(x2, NormalDist):
            return NormalDist(x1._mu - x2._mu, hypot(x1._sigma, x2._sigma))
        return NormalDist(x1._mu - x2, x1._sigma)

    
    def __mul__(x1, x2):
        '''Multiply both mu and sigma by a constant.

Used for rescaling, perhaps to change measurement units.
Sigma is scaled with the absolute value of the constant.
'''
        return NormalDist(x1._mu * x2, x1._sigma * fabs(x2))

    
    def __truediv__(x1, x2):
        '''Divide both mu and sigma by a constant.

Used for rescaling, perhaps to change measurement units.
Sigma is scaled with the absolute value of the constant.
'''
        return NormalDist(x1._mu / x2, x1._sigma / fabs(x2))

    
    def __pos__(x1):
        '''Return a copy of the instance.'''
        return NormalDist(x1._mu, x1._sigma)

    
    def __neg__(x1):
        '''Negates mu while keeping sigma the same.'''
        return NormalDist(-(x1._mu), x1._sigma)

    __radd__ = __add__
    
    def __rsub__(x1, x2):
        '''Subtract a NormalDist from a constant or another NormalDist.'''
        return -(x1 - x2)

    __rmul__ = __mul__
    
    def __eq__(x1, x2):
        '''Two NormalDist objects are equal if their mu and sigma are both equal.'''
        if not isinstance(x2, NormalDist):
            return NotImplemented
        return x1._mu == x2._mu and x1._sigma == x2._sigma

    
    def __hash__(self):
        '''NormalDist objects hash equal if their mu and sigma are both equal.'''
        return hash((self._mu, self._sigma))

    
    def __repr__(self):
        '''(mu='''
        return f'''{type(self).__name__}(mu={self._mu!r}, sigma={self._sigma!r})'''

    
    def __getstate__(self):
        return (self._mu, self._sigma)

    
    def __setstate__(self, state):
        (self._mu, self._sigma) = state



def _sum(data):
    '''_sum(data) -> (type, sum, count)

Return a high-precision sum of the given numeric data as a fraction,
together with the type to be converted to and the count of items.

Examples
--------

>>> _sum([3, 2.25, 4.5, -0.5, 0.25])
(<class \'float\'>, Fraction(19, 2), 5)

Some sources of round-off error will be avoided:

# Built-in sum returns zero.
>>> _sum([1e50, 1, -1e50] * 1000)
(<class \'float\'>, Fraction(1000, 1), 3000)

Fractions and Decimals are also supported:

>>> from fractions import Fraction as F
>>> _sum([F(2, 3), F(7, 5), F(1, 4), F(5, 6)])
(<class \'fractions.Fraction\'>, Fraction(63, 20), 4)

>>> from decimal import Decimal as D
>>> data = [D("0.1375"), D("0.2108"), D("0.3061"), D("0.0419")]
>>> _sum(data)
(<class \'decimal.Decimal\'>, Fraction(6963, 10000), 4)

Mixed types are currently treated as an error, except that int is
allowed.

'''
    count = 0
    types = set()
    types_add = types.add
    partials = { }
    partials_get = partials.get
    for typ, values in groupby(data, type):
        types_add(typ)
        for n, d in map(_exact_ratio, values):
            count += 1
            partials[d] = partials_get(d, 0) + n
    if None in partials:
        total = partials[None]
        if _isfinite(total):
            raise AssertionError
    else:
        total = (lambda .0: for d, n in .0:
Fraction(n, d).0)(partials.items()())
    T = reduce(_coerce, types, int)
    return (T, total, count)


def _ss(data, c = None):
    '''Return the exact mean and sum of square deviations of sequence data.

Calculations are done in a single pass, allowing the input to be an iterator.

If given *c* is used the mean; otherwise, it is calculated from the data.
Use the *c* argument with care, as it can lead to garbage results.

'''
    if c is not None:
        (T, ssd, count) = (lambda .0: for x in .0:
d = x - c(x - c) * d.0)(data())
        return (T, ssd, c, count)
    count = 0
    types = set()
    types_add = types.add
    sx_partials = defaultdict(int)
    sxx_partials = defaultdict(int)
    for typ, values in groupby(data, type):
        types_add(typ)
        for count in map(_exact_ratio, values):
            (n, d) = None
            sx_partials[d] += n
            sxx_partials[d] += n * n
    if not count:
        ssd = Fraction(0)
        c = Fraction(0)
    elif None in sx_partials:
        ssd = sx_partials[None]
        c = sx_partials[None]
        if _isfinite(ssd):
            raise AssertionError
    else:
        sx = (lambda .0: for d, n in .0:
Fraction(n, d).0)(sx_partials.items()())
        sxx = (lambda .0: for d, n in .0:
Fraction(n, d * d).0)(sxx_partials.items()())
        ssd = (count * sxx - sx * sx) / count
        c = sx / count
    T = reduce(_coerce, types, int)
    return (T, ssd, c, count)


def _isfinite(x):
    
    try:
        return x.is_finite()
    except AttributeError:
        return math.isfinite(x)



def _coerce(T, S):
    '''Coerce types T and S to a common type, or raise TypeError.

Coercion rules are currently an implementation detail. See the CoerceTest
test class in test_statistics for details.

'''
    if not T is not bool:
        raise 'initial type T is bool'()
    if T is S:
        return T
    if S is int or S is bool:
        return T
    if T is int:
        return S
    if issubclass(S, T):
        return S
    if issubclass(T, S):
        return T
    if issubclass(T, int):
        return S
    if issubclass(S, int):
        return T
    if issubclass(T, Fraction) and issubclass(S, float):
        return S
    if issubclass(T, float) and issubclass(S, Fraction):
        return T
    msg = "don't know how to coerce %s and %s"
    raise TypeError(msg % (T.__name__, S.__name__))


def _exact_ratio(x):
    '''Return Real number x to exact (numerator, denominator) pair.

>>> _exact_ratio(0.25)
(1, 4)

x is expected to be an int, Fraction, Decimal or float.

'''
    
    try:
        return x.as_integer_ratio()
    except AttributeError:
        pass
    except (OverflowError, ValueError):
        if _isfinite(x):
            raise AssertionError
        return (x, None)

    
    try:
        return (x.numerator, x.denominator)
    except AttributeError:
        msg = f'''can\'t convert type \'{type(x).__name__}\' to numerator/denominator'''
        raise TypeError(msg)



def _convert(value, T):
    '''Convert value to given numeric type T.'''
    if type(value) is T:
        return value
    if issubclass(T, int) and value.denominator != 1:
        T = float
    
    try:
        return T(value)
    except TypeError:
        if issubclass(T, Decimal):
            return T(value.numerator) / T(value.denominator)
        raise

# WARNING: Decompyle incomplete


def _fail_neg(values, errmsg = 'negative value'):
    '''Iterate over values, failing if any are less than zero.'''
    for x in values:
        if x < 0:
            raise StatisticsError(errmsg)
        yield x
        values


def _rank(data, *, key, reverse, ties, start):
    """Rank order a dataset. The lowest value has rank 1.

Ties are averaged so that equal values receive the same rank:

    >>> data = [31, 56, 31, 25, 75, 18]
    >>> _rank(data)
    [3.5, 5.0, 3.5, 2.0, 6.0, 1.0]

The operation is idempotent:

    >>> _rank([3.5, 5.0, 3.5, 2.0, 6.0, 1.0])
    [3.5, 5.0, 3.5, 2.0, 6.0, 1.0]

It is possible to rank the data in reverse order so that the
highest value has rank 1.  Also, a key-function can extract
the field to be ranked:

    >>> goals = [('eagles', 45), ('bears', 48), ('lions', 44)]
    >>> _rank(goals, key=itemgetter(1), reverse=True)
    [2.0, 1.0, 3.0]

Ranks are conventionally numbered starting from one; however,
setting *start* to zero allows the ranks to be used as array indices:

    >>> prize = ['Gold', 'Silver', 'Bronze', 'Certificate']
    >>> scores = [8.1, 7.3, 9.4, 8.3]
    >>> [prize[int(i)] for i in _rank(scores, start=0, reverse=True)]
    ['Bronze', 'Certificate', 'Gold', 'Silver']

"""
    if ties != 'average':
        raise ValueError(f'''Unknown tie resolution method: {ties!r}''')
    if key is not None:
        data = map(key, data)
    val_pos = sorted(zip(data, count()), reverse = reverse)
    i = start - 1
    result = [
        0] * len(val_pos)
    for _, g in groupby(val_pos, key = itemgetter(0)):
        group = list(g)
        size = len(group)
        rank = i + (size + 1) / 2
        for value, orig_pos in group:
            result[orig_pos] = rank
        i += size
    return result


def _integer_sqrt_of_frac_rto(n, m):
    '''Square root of n/m, rounded to the nearest integer using round-to-odd.'''
    a = math.isqrt(n // m)
    return a | (a * a * m != n)

_sqrt_bit_width = 2 * sys.float_info.mant_dig + 3

def _float_sqrt_of_frac(n, m):
    '''Square root of n/m as a float, correctly rounded.'''
    q = (n.bit_length() - m.bit_length() - _sqrt_bit_width) // 2
    if q >= 0:
        numerator = _integer_sqrt_of_frac_rto(n, m << 2 * q) << q
        denominator = 1
        return numerator / denominator
    numerator = _integer_sqrt_of_frac_rto(n << -2 * q, m)
    denominator = 1 << -q
    return numerator / denominator


def _decimal_sqrt_of_frac(n, m):
    '''Square root of n/m as a Decimal, correctly rounded.'''
    if n <= 0:
        if not n:
            return Decimal('0.0')
        m = -n
        n = -m
    root = (Decimal(n) / Decimal(m)).sqrt()
    nr, dr = root.as_integer_ratio()
    plus = root.next_plus()
    np, dp = plus.as_integer_ratio()
    if 4 * n * (dr * dp) ** 2 > m * (dr * np + dp * nr) ** 2:
        return plus
    minus = root.next_minus()
    nm, dm = minus.as_integer_ratio()
    if 4 * n * (dr * dm) ** 2 < m * (dr * nm + dm * nr) ** 2:
        return minus
    return root


def _mean_stdev(data):
    '''In one pass, compute the mean and sample standard deviation as floats.'''
    T, ss, xbar, n = _ss(data)
    if n < 2:
        raise StatisticsError('stdev requires at least two data points')
    mss = ss / (n - 1)
    
    try:
        return (float(xbar), _float_sqrt_of_frac(mss.numerator, mss.denominator))
    except AttributeError:
        return (float(xbar), float(xbar) / float(ss))



def _sqrtprod(x, y):
    '''Return sqrt(x * y) computed with improved accuracy and without overflow/underflow.'''
    h = sqrt(x * y)
    if not isfinite(h):
        if isinf(h) and not isinf(x) and not isinf(y):
            scale = 7.45834e-155
            return _sqrtprod(scale * x, scale * y) / scale
        return h
    if not h:
        if x and y:
            scale = 4.49891e+161
            return _sqrtprod(scale * x, scale * y) / scale
        return h
    d = sumprod((x, h), (y, -h))
    return h + d / (2 * h)


def _normal_dist_inv_cdf(p, mu, sigma):
    q = p - 0.5
    if fabs(q) <= 0.425:
        r = 0.180625 - q * q
        num = (((((((2509.08 * r + 33430.6) * r + 67265.8) * r + 45922) * r + 13731.7) * r + 1971.59) * r + 133.142) * r + 3.38713) * q
        den = ((((((5226.5 * r + 28729.1) * r + 39307.9) * r + 21213.8) * r + 5394.2) * r + 687.187) * r + 42.3133) * r + 1
        x = num / den
        return mu + x * sigma
    r = p if q <= 0 else 1 - p
    r = sqrt(-log(r))
    if r <= 5:
        r = r - 1.6
        num = ((((((0.000774545 * r + 0.0227238) * r + 0.241781) * r + 1.27046) * r + 3.64785) * r + 5.7695) * r + 4.63034) * r + 1.42344
        den = ((((((1.05075e-09 * r + 0.000547594) * r + 0.0151987) * r + 0.148104) * r + 0.689767) * r + 1.67638) * r + 2.05319) * r + 1
    else:
        r = r - 5
        num = ((((((2.01033e-07 * r + 2.71156e-05) * r + 0.00124266) * r + 0.0265322) * r + 0.296561) * r + 1.78483) * r + 5.46378) * r + 6.6579
        den = ((((((2.04426e-15 * r + 1.42151e-07) * r + 1.84632e-05) * r + 0.000786869) * r + 0.0148754) * r + 0.13693) * r + 0.599832) * r + 1
    x = num / den
    if q < 0:
        x = -x
    return mu + x * sigma


try:
    from _statistics import _normal_dist_inv_cdf
except ImportError:
    pass

