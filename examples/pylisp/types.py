"""Shared type aliases for the pylisp package."""

from typing import Any

# Any HyperBinary type (Sparkle, Knot, Parcel, Set, Sequence, Octopus, etc.).
# Python's PyO3 bindings accept any of these interchangeably via duck typing.
HyperBinary = Any
