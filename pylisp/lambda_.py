"""Lambda calculus: curried application and beta-reduction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kongming_rs import hv

from . import cons as cons_mod
from .types import HyperBinary

if TYPE_CHECKING:
    from .env import LispEnv



def evlamb(env: LispEnv, lambda_expr: HyperBinary, args: list[HyperBinary]) -> HyperBinary:
    """Apply a lambda expression to arguments (curried, one at a time)."""
    current = lambda_expr
    for arg in args:
        current = _evlambcurry(env, current, arg)

    if _is_lambda(env, current):
        return current
    from .evaluator import ev
    return ev(env, current)


def _evlambcurry(env: LispEnv, lambda_expr: HyperBinary, arg: HyperBinary) -> HyperBinary:
    """Apply one argument to a lambda via curried beta-reduction."""
    _lambda_tag = cons_mod.car(env, lambda_expr)  # LAMBDA
    rest = cons_mod.cdr(env, lambda_expr)
    params = cons_mod.car(env, rest)
    body_rest = cons_mod.cdr(env, rest)
    body = cons_mod.car(env, body_rest)

    first_param = cons_mod.car(env, params)
    remaining_params = cons_mod.cdr(env, params)

    new_body = evshorn(env, body, first_param, arg)

    if cons_mod.is_atom(env, remaining_params) and hv.equal(remaining_params, env.nil):
        return new_body
    else:
        # Rebuild: (LAMBDA remaining_params new_body)
        body_list = cons_mod.cons(env, new_body, env.nil)
        params_and_body = cons_mod.cons(env, remaining_params, body_list)
        return cons_mod.cons(env, env.sym_lambda, params_and_body)


def evshorn(env: LispEnv, expr: HyperBinary, param: HyperBinary, arg: HyperBinary) -> HyperBinary:
    """Recursive tree-walk substitution (beta-reduction).

    Respects variable shadowing: if expr is (LAMBDA (params...) body)
    and param appears among the formal parameters, the body is left
    unchanged.
    """
    if hv.equal(expr, param):
        return arg

    if cons_mod.is_atom(env, expr):
        return expr

    car_val = cons_mod.car(env, expr)
    cdr_val = cons_mod.cdr(env, expr)

    # Respect shadowing
    if hv.equal(car_val, env.sym_lambda):
        if not cons_mod.is_atom(env, cdr_val):
            formal_params = cons_mod.car(env, cdr_val)
            if _param_in_list(env, param, formal_params):
                return expr

    new_car = evshorn(env, car_val, param, arg)
    new_cdr = evshorn(env, cdr_val, param, arg)
    return cons_mod.cons(env, new_car, new_cdr)


def _param_in_list(env: LispEnv, param: HyperBinary, lst: HyperBinary) -> bool:
    """Check whether param appears in a LISP list of formal parameters."""
    if cons_mod.is_atom(env, lst):
        return hv.equal(lst, param)
    try:
        head: HyperBinary = cons_mod.car(env, lst)
    except Exception:
        return False
    if hv.equal(head, param):
        return True
    try:
        tail = cons_mod.cdr(env, lst)
    except Exception:
        return False
    return _param_in_list(env, param, tail)


def _is_lambda(env: LispEnv, expr: HyperBinary) -> bool:
    """Check if expression is (LAMBDA ...)."""
    if cons_mod.is_atom(env, expr):
        return False
    try:
        head = cons_mod.car(env, expr)
        return hv.equal(head, env.sym_lambda)
    except Exception:
        return False
