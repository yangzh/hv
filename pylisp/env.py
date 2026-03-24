"""LISP environment: domains, reserved symbols, lexicon, and substrate."""

from __future__ import annotations

import random
from typing import Union

from kongming_rs import hv, memory, HvError, REASON_NOT_FOUND
from kongming_rs.api.v1.hv_pb2 import (
    MODEL_64K_8BIT,
    DomainPrefix,
    Prewired,
)

from .types import HyperBinary

# Proto enum shortcuts for readability.
_LISP_PREFIX: int = DomainPrefix.E.Value("LISP")
_NIL: int = Prewired.E.Value("NIL")
_TRUE: int = Prewired.E.Value("TRUE")
_FALSE: int = Prewired.E.Value("FALSE")
_LEFT: int = Prewired.E.Value("LEFT")
_RIGHT: int = Prewired.E.Value("RIGHT")

DEFAULT_NAMESPACE: str = "default"


class LispSubstrate:
    """Storage layer for the LISP environment.

    All data lives in the substrate (InMemory or Fjall). Two kinds of
    chunks are stored:

    - **Symbols and cons cell pointers** — stored via ``put()``, which
      also indexes them for near-neighbor search (NNS). The ``cleanup()``
      function uses NNS to denoise a noisy vector back to the nearest
      known sparkle.
    - **Cons cell content** (the Parcel encoding of ``(a . b)``) — stored
      as a companion chunk in a separate ``code_domain`` with the same
      pod as the cons pointer. Retrievable via ``get_code()``.
    """

    def __init__(
        self,
        model: int,
        code_domain: hv.Domain,
        inner: Union[memory.InMemory, memory.Fjall],
    ) -> None:
        self._inner = inner
        self._code_domain: hv.Domain = code_domain
        self._model: int = model

    def new_view(self) -> memory.SubstrateView:
        return self._inner.new_view()

    def store(self, id: hv.Sparkle, code: HyperBinary | None = None) -> None:
        """Store a chunk in the substrate (indexed for NNS).

        If *code* is provided, it is stored as a companion chunk in
        ``code_domain`` with the same pod, retrievable via ``get_code()``.
        """
        self._inner.put(id)
        if code is not None and not hv.equal(id, code):
            code_key = hv.Sparkle(self._model, self._code_domain, id.pod())
            with self._inner.new_mutable_view() as view:
                view.write_chunk(code_key, code=code)

    def get_code(self, id: hv.Sparkle) -> HyperBinary | None:
        """Retrieve the encoding for *id* from the code domain.

        Returns None if the id has no stored encoding (i.e., it's a symbol).
        Propagates all other exceptions.
        """
        with self._inner.new_view() as view:
            try:
                return view.read_chunk(self._code_domain, id.pod())
            except HvError as e:
                if e.code == REASON_NOT_FOUND:
                    return None
                raise


class LispEnv:
    """The LISP environment: substrate, reserved symbols, and lexicon.

    Args:
        model: Model constant (default MODEL_64K_8BIT).
        path: If given, use Fjall disk-backed storage at this path.
        namespace: User namespace for cons/fn domains (default "lisp.default").
    """

    def __init__(
        self,
        model: int = MODEL_64K_8BIT,
        path: str | None = None,
        namespace: str | None = None,
    ) -> None:
        ns = namespace or DEFAULT_NAMESPACE
        self.model: int = model

        # Domains (all under the LISP prefix: λ)
        self.sym_domain: hv.Domain = hv.Domain.with_prefix(_LISP_PREFIX, "sym")
        self.cons_domain: hv.Domain = hv.Domain.with_prefix(_LISP_PREFIX, ns)
        self.fn_domain: hv.Domain = hv.Domain.with_prefix(_LISP_PREFIX, f"{ns}.fn")
        code_domain = hv.Domain.with_prefix(_LISP_PREFIX, f"{ns}.code")

        if path is not None:
            self.substrate = LispSubstrate(model, code_domain, memory.Fjall(model, path))
        else:
            self.substrate = LispSubstrate(model, code_domain, memory.InMemory(model))

        # Reserved symbols
        self.t: hv.Sparkle = hv.Sparkle.from_prewired(model, self.sym_domain, _TRUE)
        self.f: hv.Sparkle = hv.Sparkle.from_prewired(model, self.sym_domain, _FALSE)
        self.nil: hv.Sparkle = hv.Sparkle.from_prewired(model, self.sym_domain, _NIL)
        self.lhs: hv.Sparkle = hv.Sparkle.from_prewired(model, self.sym_domain, _LEFT)
        self.rhs: hv.Sparkle = hv.Sparkle.from_prewired(model, self.sym_domain, _RIGHT)

        # McCarthy's 7 original primitives
        self.sym_quote: hv.Sparkle = hv.Sparkle.from_word(model, self.sym_domain, "QUOTE")
        self.sym_atom: hv.Sparkle = hv.Sparkle.from_word(model, self.sym_domain, "ATOM")
        self.sym_eq: hv.Sparkle = hv.Sparkle.from_word(model, self.sym_domain, "EQ")
        self.sym_car: hv.Sparkle = hv.Sparkle.from_word(model, self.sym_domain, "CAR")
        self.sym_cdr: hv.Sparkle = hv.Sparkle.from_word(model, self.sym_domain, "CDR")
        self.sym_cons: hv.Sparkle = hv.Sparkle.from_word(model, self.sym_domain, "CONS")
        self.sym_cond: hv.Sparkle = hv.Sparkle.from_word(model, self.sym_domain, "COND")

        # Special forms
        self.sym_lambda: hv.Sparkle = hv.Sparkle.from_word(model, self.sym_domain, "LAMBDA")
        self.sym_label: hv.Sparkle = hv.Sparkle.from_word(model, self.sym_domain, "LABEL")
        self.sym_define: hv.Sparkle = hv.Sparkle.from_word(model, self.sym_domain, "DEFINE")

        # Bidirectional lexicon
        self.name_to_sparkle: dict[str, hv.Sparkle] = {}
        self.hash_to_name: dict[int, str] = {}

        # Register reserved symbols
        for name, sparkle in [("T", self.t), ("F", self.f), ("NIL", self.nil)]:
            self._register_symbol(name, sparkle)

        # Register builtins
        for name, sparkle in [
            ("CAR", self.sym_car), ("CDR", self.sym_cdr), ("CONS", self.sym_cons),
            ("EQ", self.sym_eq), ("ATOM", self.sym_atom), ("QUOTE", self.sym_quote),
            ("DEFINE", self.sym_define), ("COND", self.sym_cond),
            ("LAMBDA", self.sym_lambda), ("LABEL", self.sym_label),
        ]:
            self._register_symbol(name, sparkle)

    def _register_symbol(self, name: str, sparkle: hv.Sparkle) -> None:
        self.name_to_sparkle[name] = sparkle
        self.hash_to_name[sparkle.stable_hash()] = name
        self.substrate.store(sparkle)

    def name_of(self, hb: HyperBinary) -> str | None:
        return self.hash_to_name.get(hb.stable_hash())

    def sparkle_of(self, name: str) -> hv.Sparkle | None:
        return self.name_to_sparkle.get(name)

    def fresh_id(self) -> hv.Sparkle:
        """Generate a fresh unique Sparkle id for a cons cell."""
        seed = random.getrandbits(64)
        return hv.Sparkle.from_seed(self.model, self.cons_domain, seed)

    def is_similar(self, a: HyperBinary, b: HyperBinary) -> bool:
        return hv.overlap(a, b) > hv.thres_noise(self.model)

    # Public API (matches Rust PyLispEnv)

    def eval(self, expr_str: str) -> str:
        """Parse and evaluate (single step), return display string."""
        from . import reader, evaluator, printer
        parsed = reader.parse(self, expr_str)
        result = evaluator.ev(self, parsed)
        return printer.display(self, result)

    def eval_full(self, expr_str: str) -> str:
        """Parse and evaluate until stable, return display string."""
        from . import reader, evaluator, printer
        parsed = reader.parse(self, expr_str)
        result = evaluator.ev_until_done(self, parsed)
        return printer.display(self, result)

    def parse_display(self, expr_str: str) -> str:
        """Parse and display without evaluating."""
        from . import reader, printer
        parsed = reader.parse(self, expr_str)
        return printer.display(self, parsed)
