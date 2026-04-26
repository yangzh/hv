"""S-expression pretty-printer: hypervector → readable string."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kongming import hv

from . import cons as cons_mod
from .types import HyperBinary

if TYPE_CHECKING:
    from .env import LispEnv


def display(env: LispEnv, v: HyperBinary) -> str:
    """Convert a hypervector back to a readable S-expression string."""
    if cons_mod.is_atom(env, v):
        name = env.name_of(v)
        if name is not None:
            return name
        return f"#{v.stable_hash():#018x}"

    if not isinstance(v, hv.Sparkle):
        return f"#{v.stable_hash():#018x}"

    parts = []
    current = v
    while True:
        try:
            car_val = cons_mod.car(env, current)
        except Exception:
            break
        parts.append(display(env, car_val))
        try:
            cdr_val = cons_mod.cdr(env, current)
        except Exception:
            break
        if cons_mod.is_atom(env, cdr_val):
            if hv.equal(cdr_val, env.nil):
                break
            else:
                parts.append(".")
                parts.append(display(env, cdr_val))
                break
        if isinstance(cdr_val, hv.Sparkle):
            current = cdr_val
        else:
            parts.append(".")
            parts.append(display(env, cdr_val))
            break

    return f"({' '.join(parts)})"
