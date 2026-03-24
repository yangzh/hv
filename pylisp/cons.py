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
    a_bound = hv.bind(a, env.lhs)
    b_bound = hv.bind(b, env.rhs)
    return hv.bundle(seed, a_bound, b_bound)


def cons(env: LispEnv, a: HyperBinary, b: HyperBinary) -> hv.Sparkle:
    """Create a cons cell (a . b). Returns the id Sparkle."""
    id = env.fresh_id()
    seed = hv.Seed128(id.domain().id(), id.pod().seed())
    cell = cons_parcel(env, seed, a, b)
    env.substrate.store(id, code=cell)
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
    """Check if a value is an atom (not a cons cell)."""
    if not isinstance(v, hv.Sparkle):
        return True
    if v.domain().id() != env.cons_domain.id():
        return True
    return env.substrate.get_code(v) is None


def _lookup_cell(env: LispEnv, id: hv.Sparkle) -> HyperBinary:
    """Look up a cons cell's encoded content by its id."""
    cell = env.substrate.get_code(id)
    if cell is not None:
        return cell
    raise ValueError(f"cons cell not found: {id.stable_hash():#018x}")


def cleanup(env: LispEnv, probe: HyperBinary) -> HyperBinary:
    """Denoise a vector by finding the best match via near-neighbor search."""
    sel = memory.nns(memory.with_code(probe))
    return memory.first_picked(env.substrate.new_view(), sel)
