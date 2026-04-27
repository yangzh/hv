"""Tests for the pure-Python LISP interpreter (kongming.pylisp).

Mirrors rust/kongming-lisp/tests/integration.rs for feature parity.
"""

import tempfile

import pytest
from kongming.lisp import LispEnv

# ── Parse / display ──────────────────────────────────────────────────


def test_cons_car_cdr_roundtrip():
    env = LispEnv()
    assert env.parse_display("(A B C)") == "(A B C)"


# ── McCarthy's 7 primitives ──────────────────────────────────────────


def test_quote():
    env = LispEnv()
    assert env.eval("(QUOTE (A B C))") == "(A B C)"


def test_car_quote():
    env = LispEnv()
    assert env.eval("(CAR (QUOTE (A B C)))") == "A"


def test_cdr_quote():
    env = LispEnv()
    assert env.eval("(CDR (QUOTE (A B C)))") == "(B C)"


def test_atom_true():
    env = LispEnv()
    assert env.eval("(ATOM (QUOTE A))") == "T"


def test_atom_false():
    env = LispEnv()
    assert env.eval("(ATOM (QUOTE (A B)))") == "F"


def test_eq_true():
    env = LispEnv()
    assert env.eval("(EQ (QUOTE A) (QUOTE A))") == "T"


def test_eq_false():
    env = LispEnv()
    assert env.eval("(EQ (QUOTE A) (QUOTE B))") == "F"


def test_cons_eval():
    env = LispEnv()
    assert env.eval("(CONS (QUOTE A) (QUOTE B))") == "(A . B)"


def test_cond():
    env = LispEnv()
    assert (
        env.eval("(COND ((EQ (QUOTE A) (QUOTE B)) (QUOTE NO)) (T (QUOTE YES)))")
        == "YES"
    )


# ── Lambda / Define / Label ──────────────────────────────────────────


def test_lambda_identity():
    env = LispEnv()
    assert env.eval_full("((LAMBDA (X) X) (QUOTE A))") == "A"


def test_lambda_car():
    env = LispEnv()
    assert env.eval_full("((LAMBDA (X) (CAR X)) (QUOTE (A B)))") == "A"


def test_define_and_call():
    env = LispEnv()
    env.eval("(DEFINE SECOND (LAMBDA (L) (CAR (CDR L))))")
    assert env.eval("(SECOND (QUOTE (A B C)))") == "B"


def test_define_last():
    env = LispEnv()
    env.eval(
        "(DEFINE LAST (LAMBDA (L) ((LABEL REC (LAMBDA (X) "
        "(COND ((ATOM (CDR X)) (CAR X)) (T (REC (CDR X)))))) L)))"
    )
    assert env.eval_full("(LAST (QUOTE (A B C)))") == "C"


# ── Fjall backend ────────────────────────────────────────────────────


def test_fjall_basic_roundtrip():
    import os

    with tempfile.TemporaryDirectory() as d:
        env = LispEnv(path=os.path.join(d, "lisp.db"))
        assert env.eval("(CAR (QUOTE (A B C)))") == "A"
        assert env.eval("(CDR (QUOTE (A B C)))") == "(B C)"


def test_fjall_define_and_call():
    import os

    with tempfile.TemporaryDirectory() as d:
        env = LispEnv(path=os.path.join(d, "lisp.db"))
        env.eval("(DEFINE SECOND (LAMBDA (L) (CAR (CDR L))))")
        assert env.eval("(SECOND (QUOTE (X Y Z)))") == "Y"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
