"""Single-step evaluator implementing McCarthy's original LISP semantics."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .types import HyperBinary

from kongming_rs import hv

from . import cons as cons_mod
from . import lambda_

if TYPE_CHECKING:
    from .env import LispEnv



def _eq(a: HyperBinary, b: HyperBinary) -> bool:
    return hv.equal(a, b)


def ev(env: LispEnv, expr: HyperBinary) -> HyperBinary:
    """Single-step evaluator."""
    if cons_mod.is_atom(env, expr):
        return expr

    head: HyperBinary = cons_mod.car(env, expr)
    tail: HyperBinary = cons_mod.cdr(env, expr)

    # QUOTE
    if _eq(head, env.sym_quote):
        return cons_mod.car(env, tail)

    # LAMBDA — return as-is
    if _eq(head, env.sym_lambda):
        return expr

    # COND
    if _eq(head, env.sym_cond):
        return _eval_cond(env, tail)

    # DEFINE
    if _eq(head, env.sym_define):
        return _eval_define(env, tail)

    # LABEL
    if _eq(head, env.sym_label):
        return _eval_label(env, tail)

    # CAR
    if _eq(head, env.sym_car):
        arg: HyperBinary = cons_mod.car(env, tail)
        evaled: HyperBinary = ev(env, arg)
        return cons_mod.car(env, evaled)

    # CDR
    if _eq(head, env.sym_cdr):
        arg = cons_mod.car(env, tail)
        evaled = ev(env, arg)
        return cons_mod.cdr(env, evaled)

    # CONS
    if _eq(head, env.sym_cons):
        first_arg: HyperBinary = cons_mod.car(env, tail)
        rest: HyperBinary = cons_mod.cdr(env, tail)
        second_arg: HyperBinary = cons_mod.car(env, rest)
        ev_first: HyperBinary = ev(env, first_arg)
        ev_second: HyperBinary = ev(env, second_arg)
        return cons_mod.cons(env, ev_first, ev_second)

    # EQ
    if _eq(head, env.sym_eq):
        first_arg = cons_mod.car(env, tail)
        rest = cons_mod.cdr(env, tail)
        second_arg = cons_mod.car(env, rest)
        ev_first = ev(env, first_arg)
        ev_second = ev(env, second_arg)
        return env.t if _eq(ev_first, ev_second) else env.f

    # ATOM
    if _eq(head, env.sym_atom):
        arg = cons_mod.car(env, tail)
        evaled = ev(env, arg)
        return env.t if cons_mod.is_atom(env, evaled) else env.f

    # Check if head is a defined function
    lambda_expr: HyperBinary | None = _lookup_function(env, head)
    if lambda_expr is not None:
        args: list[HyperBinary] = _collect_list(env, tail)
        evaled_args: list[HyperBinary] = [ev(env, a) for a in args]
        return lambda_.evlamb(env, lambda_expr, evaled_args)

    # Inline lambda application: ((LAMBDA ...) args...)
    if not cons_mod.is_atom(env, head):
        head_head: HyperBinary = cons_mod.car(env, head)
        if _eq(head_head, env.sym_lambda):
            args = _collect_list(env, tail)
            evaled_args = [ev(env, a) for a in args]
            return lambda_.evlamb(env, head, evaled_args)
        # Inline LABEL application: ((LABEL name fn) args...)
        if _eq(head_head, env.sym_label):
            evaled_head: HyperBinary = _eval_label(env, cons_mod.cdr(env, head))
            new_expr: hv.Sparkle = cons_mod.cons(env, evaled_head, tail)
            return ev(env, new_expr)

    # Otherwise, evaluate head and try again
    evaled_head = ev(env, head)
    if not _eq(evaled_head, head):
        new_expr = cons_mod.cons(env, evaled_head, tail)
        return ev(env, new_expr)

    return expr


def ev_until_done(env: LispEnv, expr: HyperBinary) -> HyperBinary:
    """Evaluate an expression until it stabilizes (max 100 iterations)."""
    current: HyperBinary = expr
    for _ in range(100):
        if cons_mod.is_atom(env, current):
            return current

        if isinstance(current, hv.Sparkle):
            try:
                head: HyperBinary = cons_mod.car(env, current)
                if _eq(head, env.sym_quote) or _eq(head, env.sym_lambda):
                    return current
            except Exception:
                pass

        next_val: HyperBinary = ev(env, current)
        if _eq(next_val, current):
            return current
        current = next_val
    return current


def _eval_cond(env: LispEnv, clauses: HyperBinary) -> HyperBinary:
    """Evaluate a COND expression."""
    if cons_mod.is_atom(env, clauses):
        return env.nil

    clause: HyperBinary = cons_mod.car(env, clauses)
    rest: HyperBinary = cons_mod.cdr(env, clauses)

    test: HyperBinary = cons_mod.car(env, clause)
    test_result: HyperBinary = ev(env, test)

    if _eq(test_result, env.t):
        consequent_list: HyperBinary = cons_mod.cdr(env, clause)
        consequent: HyperBinary = cons_mod.car(env, consequent_list)
        return ev(env, consequent)

    return _eval_cond(env, rest)


def _eval_define(env: LispEnv, args: HyperBinary) -> HyperBinary:
    """Evaluate a DEFINE expression."""
    name: HyperBinary = cons_mod.car(env, args)
    rest: HyperBinary = cons_mod.cdr(env, args)
    lambda_expr: HyperBinary = cons_mod.car(env, rest)

    name_str: str = env.name_of(name) or "?"
    fn_sparkle: hv.Sparkle = hv.Sparkle.from_word(env.model, env.fn_domain, name_str)
    seed = hv.Seed128(fn_sparkle.domain().id(), fn_sparkle.pod().seed())
    cell: hv.Parcel = cons_mod.cons_parcel(env, seed, name, lambda_expr)
    env.substrate.store(fn_sparkle, code=cell)

    return env.nil


def _eval_label(env: LispEnv, args: HyperBinary) -> HyperBinary:
    """Evaluate a LABEL expression."""
    label_name: HyperBinary = cons_mod.car(env, args)
    rest: HyperBinary = cons_mod.cdr(env, args)
    body: HyperBinary = cons_mod.car(env, rest)

    body_list: hv.Sparkle = cons_mod.cons(env, body, env.nil)
    name_and_body: hv.Sparkle = cons_mod.cons(env, label_name, body_list)
    label_form: hv.Sparkle = cons_mod.cons(env, env.sym_label, name_and_body)

    return lambda_.evshorn(env, body, label_name, label_form)


def _lookup_function(env: LispEnv, head: HyperBinary) -> HyperBinary | None:
    """Look up a function definition by name. Returns lambda expr or None."""
    name: str | None = env.name_of(head)
    if name is None:
        return None
    fn_sparkle: hv.Sparkle = hv.Sparkle.from_word(env.model, env.fn_domain, name)
    cell: HyperBinary | None = env.substrate.get_code(fn_sparkle)
    if cell is None:
        return None
    released: HyperBinary = hv.release(cell, env.rhs)
    return cons_mod.cleanup(env, released)


def _collect_list(env: LispEnv, list_val: HyperBinary) -> list[HyperBinary]:
    """Collect a LISP list into a Python list of elements."""
    result: list[HyperBinary] = []
    current: HyperBinary = list_val
    for _ in range(100):
        if cons_mod.is_atom(env, current):
            break
        result.append(cons_mod.car(env, current))
        current = cons_mod.cdr(env, current)
    return result
