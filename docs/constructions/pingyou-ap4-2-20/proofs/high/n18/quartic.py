"""Exact arithmetic in Q(alpha), alpha the positive real root of alpha**4 = 2.

There are no floating point tolerances in this module.  A field element is
stored uniquely as four Fractions in the basis (1, alpha, alpha**2, alpha**3).
Its sign is decided by successively refining a *rational* enclosure of alpha.
Because x**4 - 2 is irreducible over Q, only four zero coefficients represent
zero, and every other sign computation eventually terminates.

The interval and decimal methods return certified outward bounds.  __float__
is supplied solely for display and must not be used to certify inequalities.
This module has no dependencies outside the Python standard library.
"""

from fractions import Fraction
from functools import lru_cache, total_ordering
from math import isqrt


def _fraction(value):
    """Convert a rational input; floats mean their exact binary value."""
    return value if isinstance(value, Fraction) else Fraction(value)


@lru_cache(maxsize=128)
def _root_interval(kind, precision):
    denominator = (1 << precision) if kind == "bits" else 10**precision
    # floor(sqrt(floor(sqrt(n)))) = floor(n**(1/4)), using integers only.
    radicand = 2 * denominator**4
    lower_numerator = isqrt(isqrt(radicand))
    # The root is irrational, so both endpoints are strict.
    assert lower_numerator**4 < radicand < (lower_numerator + 1)**4
    return (Fraction(lower_numerator, denominator),
            Fraction(lower_numerator + 1, denominator))


def root_interval(bits=128, digits=None):
    """A strict rational enclosure of alpha; ``digits`` overrides ``bits``."""
    kind, precision = ("bits", bits) if digits is None else ("digits", digits)
    if not isinstance(precision, int) or precision < 0:
        raise ValueError("Root precision must be a nonnegative integer")
    return _root_interval(kind, precision)


def _value_interval(coeffs, alpha_lo, alpha_hi):
    lower = upper = coeffs[0]
    power_lo = power_hi = Fraction(1)
    for coefficient in coeffs[1:]:
        power_lo *= alpha_lo
        power_hi *= alpha_hi
        if coefficient >= 0:
            lower += coefficient * power_lo
            upper += coefficient * power_hi
        else:
            lower += coefficient * power_hi
            upper += coefficient * power_lo
    return lower, upper


@lru_cache(maxsize=4096)
def _inverse_coeffs(coeffs):
    a, b, c, d = coeffs
    if not any(coeffs):
        raise ZeroDivisionError("Zero has no inverse in Q(alpha)")
    # First take the norm under alpha -> -alpha, then the norm of Q(sqrt(2)).
    e = a*a + 2*c*c - 4*b*d
    f = 2*a*c - b*b - 2*d*d
    denominator = e*e - 2*f*f
    assert denominator != 0  # irreducibility, for every nonzero input
    return ((a*e - 2*c*f) / denominator,
            (-b*e + 2*d*f) / denominator,
            (c*e - a*f) / denominator,
            (-d*e + b*f) / denominator)


def _fixed_decimal(integer, places):
    sign = "-" if integer < 0 else ""
    digits = str(abs(integer))
    if places == 0:
        return sign + digits
    digits = digits.zfill(places + 1)
    return sign + digits[:-places] + "." + digits[-places:]


def _floor_fraction(value):
    return value.numerator // value.denominator


def _ceil_fraction(value):
    return -((-value.numerator) // value.denominator)


@total_ordering
class Q4:
    """Immutable exact quartic field element.

    Q4(a, b, c, d) and Q4([a, b, c, d]) mean a+b*alpha+c*alpha**2+d*alpha**3.
    Rational inputs (including fraction strings such as '3/7') are accepted.
    """

    __slots__ = ("_coeffs",)

    def __init__(self, a=0, b=0, c=0, d=0):
        if isinstance(a, Q4):
            if any((b, c, d)):
                raise TypeError("A Q4 copy cannot have additional coefficients")
            coefficients = a.coeffs
        elif isinstance(a, (tuple, list)):
            if len(a) != 4 or any((b, c, d)):
                raise ValueError("Expected exactly four coefficients")
            coefficients = tuple(map(_fraction, a))
        else:
            coefficients = tuple(map(_fraction, (a, b, c, d)))
        object.__setattr__(self, "_coeffs", coefficients)

    def __setattr__(self, name, value):
        raise AttributeError("Q4 elements are immutable")

    @property
    def coeffs(self):
        return self._coeffs

    def as_fraction(self):
        """Return the exact rational value, or raise if it is irrational."""
        if any(self.coeffs[1:]):
            raise ValueError("This field element is not rational")
        return self.coeffs[0]

    @classmethod
    def from_json(cls, coefficients):
        """Decode the four rational coefficient strings from ``to_json``."""
        return cls(coefficients)

    def to_json(self):
        return [str(coefficient) for coefficient in self.coeffs]

    @staticmethod
    def _coerce(value):
        return value if isinstance(value, Q4) else Q4(value)

    def __repr__(self):
        return "Q4(" + ", ".join(repr(str(c)) for c in self.coeffs) + ")"

    def __hash__(self):
        # Equal rational Q4 and Fraction values must also have equal hashes.
        return hash(self.coeffs) if any(self.coeffs[1:]) else hash(self.coeffs[0])

    def __bool__(self):
        return any(self.coeffs)

    def __eq__(self, other):
        try:
            other = self._coerce(other)
        except (TypeError, ValueError, ZeroDivisionError):
            return NotImplemented
        return self.coeffs == other.coeffs

    def __lt__(self, other):
        try:
            other = self._coerce(other)
        except (TypeError, ValueError, ZeroDivisionError):
            return NotImplemented
        return (self - other).sign() < 0

    def __neg__(self):
        return Q4(tuple(-c for c in self.coeffs))

    def __pos__(self):
        return self

    def __abs__(self):
        return -self if self.sign() < 0 else self

    def __add__(self, other):
        other = self._coerce(other)
        return Q4(tuple(a + b for a, b in zip(self.coeffs, other.coeffs)))

    __radd__ = __add__

    def __sub__(self, other):
        return self + -self._coerce(other)

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        result = [Fraction(0)] * 7
        for i, a in enumerate(self.coeffs):
            if a:
                for j, b in enumerate(other.coeffs):
                    if b:
                        result[i + j] += a*b
        for degree in range(6, 3, -1):
            result[degree - 4] += 2*result[degree]
        return Q4(result[:4])

    __rmul__ = __mul__

    def inverse(self):
        return Q4(_inverse_coeffs(self.coeffs))

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()

    def __rtruediv__(self, other):
        return self._coerce(other) * self.inverse()

    def __pow__(self, exponent):
        if not isinstance(exponent, int):
            return NotImplemented
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result, base = Q4(1), self
        while exponent:
            if exponent & 1:
                result *= base
            base *= base
            exponent >>= 1
        return result

    def __float__(self):
        """Approximation for display only, never a certification primitive."""
        return sum(float(c) * 2**(degree/4) for degree, c in enumerate(self.coeffs))

    def interval(self, bits=128, digits=None):
        """Certified rational bounds; rational values return equal endpoints."""
        if not any(self.coeffs[1:]):
            return self.coeffs[0], self.coeffs[0]
        return _value_interval(self.coeffs, *root_interval(bits, digits))

    def sign(self):
        """Exact -1, 0 or +1, with unbounded adaptive rational refinement."""
        if not self:
            return 0
        if not any(self.coeffs[1:]):
            return 1 if self.coeffs[0] > 0 else -1
        precision = 32
        while True:
            lower, upper = self.interval(bits=precision)
            if lower > 0:
                return 1
            if upper < 0:
                return -1
            precision *= 2

    def _decimal(self, places, upper):
        if not isinstance(places, int) or places < 0:
            raise ValueError("Decimal places must be a nonnegative integer")
        scale = 10**places
        rounding = _ceil_fraction if upper else _floor_fraction
        if not any(self.coeffs[1:]):
            integer = rounding(self.coeffs[0] * scale)
        else:
            precision = max(32, 4*places + 16)
            while True:
                lower, higher = self.interval(bits=precision)
                left, right = rounding(lower*scale), rounding(higher*scale)
                if left == right:
                    integer = left
                    break
                precision *= 2
        return _fixed_decimal(integer, places)

    def ceil_decimal(self, places):
        """Smallest multiple of 10**(-places) >= self, as a fixed decimal."""
        return self._decimal(places, upper=True)

    def floor_decimal(self, places):
        """Largest multiple of 10**(-places) <= self, as a fixed decimal."""
        return self._decimal(places, upper=False)


Field = Q4
ZERO = Q4(0)
ONE = Q4(1)
ALPHA = Q4(0, 1)


def dot(a, b):
    if len(a) != len(b):
        raise ValueError("Dot-product vectors must have equal lengths")
    return sum((Q4(x)*y for x, y in zip(a, b)), ZERO)


def cross(a, b):
    if len(a) != 3 or len(b) != 3:
        raise ValueError("Cross-product vectors must have length three")
    return tuple(Q4(a[(i + 1) % 3])*b[(i + 2) % 3]
                 - Q4(a[(i + 2) % 3])*b[(i + 1) % 3] for i in range(3))


def minus(a, b):
    if len(a) != len(b):
        raise ValueError("Vectors must have equal lengths")
    return tuple(Q4(x) - y for x, y in zip(a, b))
