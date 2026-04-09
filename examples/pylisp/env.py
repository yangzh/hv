"""LISP environment: domains, reserved symbols, lexicon, and storage."""

from __future__ import annotations

from kongming_rs import hv, memory
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

# High seed for the PCG RNG used to generate cons cell sparkles.
# ASCII "LISP" = 0x4C 0x49 0x53 0x50 → packed as a 32-bit big-endian integer.
_RNG_SEED_HIGH: int = 0x4C495350


class LispEnv:
    """The LISP environment: storage, reserved symbols, and lexicon.

    Args:
        model: Model constant (default MODEL_64K_8BIT).
        namespace: User namespace for cons/fn domains (default "default").
        path: If given, use Fjall disk-backed storage at this path.
    """

    def __init__(
        self,
        model: int = MODEL_64K_8BIT,
        namespace: str | None = None,
        path: str | None = None,
    ) -> None:
        ns = namespace or DEFAULT_NAMESPACE
        self.model = model

        # Domains (all under the LISP prefix: λ)
        self.sym_domain = hv.Domain.with_prefix(_LISP_PREFIX, "sym")
        self.cons_domain = hv.Domain.with_prefix(_LISP_PREFIX, ns)
        self.fn_domain = hv.Domain.with_prefix(_LISP_PREFIX, f"{ns}.fn")

        # PCG-based RNG for generating unique cons cell sparkles.
        self._rng = hv.SparseOperation(model, _RNG_SEED_HIGH, hv.curr_time_as_seed())

        if path is not None:
            import os
            self.storage = memory.Embedded(model, os.path.join(path, "lisp.db"))
        else:
            self.storage = memory.InMemory(model)

        # Reserved symbols
        self.t = hv.Sparkle.from_prewired(model, self.sym_domain, _TRUE)
        self.f = hv.Sparkle.from_prewired(model, self.sym_domain, _FALSE)
        self.nil = hv.Sparkle.from_prewired(model, self.sym_domain, _NIL)
        self.lhs = hv.Sparkle.from_prewired(model, self.sym_domain, _LEFT)
        self.rhs = hv.Sparkle.from_prewired(model, self.sym_domain, _RIGHT)

        # McCarthy's 7 original primitives
        self.sym_quote = hv.Sparkle.from_word(model, self.sym_domain, "QUOTE")
        self.sym_atom = hv.Sparkle.from_word(model, self.sym_domain, "ATOM")
        self.sym_eq = hv.Sparkle.from_word(model, self.sym_domain, "EQ")
        self.sym_car = hv.Sparkle.from_word(model, self.sym_domain, "CAR")
        self.sym_cdr = hv.Sparkle.from_word(model, self.sym_domain, "CDR")
        self.sym_cons = hv.Sparkle.from_word(model, self.sym_domain, "CONS")
        self.sym_cond = hv.Sparkle.from_word(model, self.sym_domain, "COND")

        # Special forms
        self.sym_lambda = hv.Sparkle.from_word(model, self.sym_domain, "LAMBDA")
        self.sym_label = hv.Sparkle.from_word(model, self.sym_domain, "LABEL")
        self.sym_define = hv.Sparkle.from_word(model, self.sym_domain, "DEFINE")

        # Bidirectional lexicon
        self.name_to_sparkle: dict[str, hv.Sparkle] = {}
        self.hash_to_name: dict[int, str] = {}

        # Register reserved symbols and builtins.
        for name, sparkle in [
            ("T", self.t),
            ("F", self.f),
            ("NIL", self.nil),
            ("CAR", self.sym_car),
            ("CDR", self.sym_cdr),
            ("CONS", self.sym_cons),
            ("EQ", self.sym_eq),
            ("ATOM", self.sym_atom),
            ("QUOTE", self.sym_quote),
            ("DEFINE", self.sym_define),
            ("COND", self.sym_cond),
            ("LAMBDA", self.sym_lambda),
            ("LABEL", self.sym_label),
        ]:
            self.register_symbol(name, sparkle)

    def register_symbol(self, name: str, sparkle: hv.Sparkle) -> None:
        """Register a new symbol: add to lexicon and store in substrate."""
        self.name_to_sparkle[name] = sparkle
        self.hash_to_name[sparkle.stable_hash()] = name
        self.storage.store_chunk(sparkle)

    def name_of(self, hb: HyperBinary) -> str | None:
        return self.hash_to_name.get(hb.stable_hash())

    def sparkle_of(self, name: str) -> hv.Sparkle | None:
        return self.name_to_sparkle.get(name)

    def random_sparkle(self) -> hv.Sparkle:
        """Generate a random Sparkle in the cons domain (PCG-based)."""
        return hv.Sparkle.from_seed(self.model, self.cons_domain, self._rng.uint64())

    def is_similar(self, a: HyperBinary, b: HyperBinary) -> bool:
        return hv.overlap(a, b) > hv.thres_noise(self.model)

    # Public API (matches Rust PyLispEnv)

    def eval(self, expr_str: str) -> str:
        """Parse and evaluate (single step), return display string."""
        from . import evaluator, printer, reader

        return printer.display(self, evaluator.ev(self, reader.parse(self, expr_str)))

    def eval_full(self, expr_str: str) -> str:
        """Parse and evaluate until stable, return display string."""
        from . import evaluator, printer, reader

        return printer.display(
            self, evaluator.ev_until_done(self, reader.parse(self, expr_str))
        )

    def parse_display(self, expr_str: str) -> str:
        """Parse and display without evaluating."""
        from . import printer, reader

        return printer.display(self, reader.parse(self, expr_str))
