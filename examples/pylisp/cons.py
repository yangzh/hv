"""Cons cell implementation using hypervector algebra.

A cons cell (a . b) is encoded as:
    cell = bundle(bind(a, lhs), bind(b, rhs))

The cell is stored under a fresh random id. Extraction:
    car(id) = release(cell, lhs) → cleanup
    cdr(id) = release(cell, rhs) → cleanup
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from kongming_rs import hv, memory

from .types import HyperBinary

if TYPE_CHECKING:
    from .env import LispEnv


def cons_parcel(
    env: LispEnv, seed: hv.Seed128, a: HyperBinary, b: HyperBinary
) -> hv.Parcel:
    """Build a cons-encoded Parcel: bundle(bind(a, lhs), bind(b, rhs))."""
    return hv.bundle(seed, hv.bind(a, env.lhs), hv.bind(b, env.rhs))


def cons(env: LispEnv, a: HyperBinary, b: HyperBinary) -> hv.Sparkle:
    """Create a cons cell (a . b). Returns the id Sparkle."""
    id = env.random_sparkle()
    cell = cons_parcel(env, hv.Seed128(id.domain().id(), id.pod().seed()), a, b)
    env.storage.store_chunk(id, code=cell)
    return id


def car(env: LispEnv, id: hv.Sparkle) -> HyperBinary:
    """Extract the car (first element) of a cons cell."""
    cell = _lookup_cell(env, id)
    released = hv.release(cell, env.lhs)
    return cleanup(env, released)


def cdr(env: LispEnv, id: hv.Sparkle) -> HyperBinary:
    """Extract the cdr (second element) of a cons cell."""
    cell = _lookup_cell(env, id)
    released = hv.release(cell, env.rhs)
    return cleanup(env, released)


def is_atom(env: LispEnv, v: HyperBinary) -> bool:
    """Check if a value is an atom (not a cons cell).

    Cons cells are always created in cons_domain via random_sparkle().
    Anything outside that domain is an atom.
    """
    if not isinstance(v, hv.Sparkle):
        return True
    return v.domain().id() != env.cons_domain.id()


def _lookup_cell(env: LispEnv, id: hv.Sparkle) -> HyperBinary:
    """Look up a cons cell's encoded content by its id."""
    chunk = env.storage.get(id.domain(), id.pod())
    return chunk.code


def cleanup(env: LispEnv, probe: HyperBinary) -> HyperBinary:
    """Denoise a vector by finding the best match via NNS.

    Returns the chunk id (not code), matching Rust's ``chunk.id`` pattern.
    """
    sel = memory.nns(memory.with_code(probe))
    chunk = memory.first_picked(env.storage.new_view(), sel)
    return chunk.id
