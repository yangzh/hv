"""Pure-Python LISP interpreter built on hyperdimensional computing.

Feature-identical to the Rust implementation in kongming_rs.lisp.
Uses kongming_rs.hv and kongming_rs.memory for hypervector operations.
"""

from .env import LispEnv

__all__ = ["LispEnv"]
