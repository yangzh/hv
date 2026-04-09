"""S-expression reader: tokenize → parse → hypervector representation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from kongming_rs import hv

from . import cons as cons_mod
from .types import HyperBinary

if TYPE_CHECKING:
    from .env import LispEnv


def tokenize(input_str: str) -> list[str]:
    """Tokenize an S-expression string."""
    return input_str.replace("(", " ( ").replace(")", " ) ").split()


def parse(env: LispEnv, input_str: str) -> HyperBinary:
    """Parse an S-expression string into a hypervector representation."""
    tokens = tokenize(input_str)
    if not tokens:
        raise ValueError("empty input")
    return _parse_tokens(env, tokens)


def _parse_tokens(env: LispEnv, tokens: list[str]) -> HyperBinary:
    if not tokens:
        raise ValueError("unexpected EOF")
    token = tokens.pop(0)
    if token == "(":
        return _parse_list(env, tokens)
    elif token == ")":
        raise ValueError("unexpected )")
    else:
        return _parse_atom(env, token)


def _parse_list(env: LispEnv, tokens: list[str]) -> HyperBinary:
    elements = []
    while True:
        if not tokens:
            raise ValueError("missing )")
        if tokens[0] == ")":
            tokens.pop(0)
            break
        if tokens[0] == ".":
            tokens.pop(0)
            cdr_val = _parse_tokens(env, tokens)
            if not tokens or tokens[0] != ")":
                raise ValueError("missing ) after dotted pair")
            tokens.pop(0)
            return _build_list_with_cdr(env, elements, cdr_val)
        elements.append(_parse_tokens(env, tokens))
    return _build_list_with_cdr(env, elements, env.nil)


def _build_list_with_cdr(env: LispEnv, elements: list[HyperBinary], cdr_val: HyperBinary) -> HyperBinary:
    result = cdr_val
    for elem in reversed(elements):
        result = cons_mod.cons(env, elem, result)
    return result


def _parse_atom(env: LispEnv, token: str) -> hv.Sparkle:
    upper = token.upper()
    existing = env.sparkle_of(upper)
    if existing is not None:
        return existing
    sparkle = hv.Sparkle.from_word(env.model, env.sym_domain, upper)
    env.register_symbol(upper, sparkle)
    return sparkle
