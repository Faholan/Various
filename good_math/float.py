"""Better floating-point operations."""
import math
import typing as t


class FloatAdd:
    """Represent multiple floats kept as-is for precision."""

    def __init__(self, *values: t.Union[float, int]):
        """Initialize the Float addition."""
        self._values = values

    def __add__(self, other: object) -> "FloatAdd":
        """Add two floats."""
        if isinstance(other, (float, int)):
            return FloatAdd(*self._values, other)

        if isinstance(other, FloatAdd):
            return FloatAdd(*self._values, *other._values)

        return NotImplemented

    @property
    def value(self) -> float:
        """Get the value of the sum."""
        return math.fsum(self._values)
