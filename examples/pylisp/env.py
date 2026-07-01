"""LISP environment: domains, reserved symbols, lexicon, and storage."""

from __future__ import annotations

from kongming import hv, memory

from .types import HyperBinary

# Constant shortcuts for readability (all exposed as IntEnum members on hv).
_LISP_PREFIX: int = hv.DOMAIN_PREFIX_LISP
_NIL: int = hv.PREWIRED_NIL
_TRUE: int = hv.PREWIRED_TRUE
_FALSE: int = hv.PREWIRED_FALSE
_LEFT: int = hv.PREWIRED_LEFT
_RIGHT: int = hv.PREWIRED_RIGHT

DEFAULT_NAMESPACE: str = "default"

# High seed for the PCG RNG used to generate cons cell sparkles.
# ASCII "LISP" = 0x4C 0x49 0x53 0x50 → packed as a 32-bit big-endian integer.
_RNG_SEED_HIGH: int = 0x4C495350


class LispEnv:
    """VSA-based LISP environment: storage, reserved symbols, and lexicon.

    Pure-Python parallel of the Rust ``kongming_rs.lisp.LispEnv``. Every
    data structure is a hypervector; every operation is VSA algebra.
    """

    def __init__(
        self,
        model: int = hv.MODEL_64K_8BIT,
        namespace: str | None = None,
        path: str | None = None,
    ) -> None:
        """Construct a fresh LISP environment.

        Args:
            model (int, optional): Model constant (e.g. ``hv.MODEL_64K_8BIT``).
                Defaults to ``hv.MODEL_64K_8BIT``.
            namespace (str, optional): User namespace for the cons / fn
                domains. Defaults to ``"default"``.
            path (str, optional): If given, use disk-backed storage at this
                path; otherwise use in-memory storage.
        """
        ns = namespace or DEFAULT_NAMESPACE
        self.model = model

        # Domains (all under the LISP prefix: λ)
        self.sym_domain = hv.Domain.from_prefix_and_name(_LISP_PREFIX, "sym")
        self.cons_domain = hv.Domain.from_prefix_and_name(_LISP_PREFIX, ns)
        self.fn_domain = hv.Domain.from_prefix_and_name(_LISP_PREFIX, f"{ns}.fn")

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
        """Register a new symbol: add to the lexicon and store in the substrate.

        Args:
            name (str): The symbol's printable name.
            sparkle (hv.Sparkle): The hypervector that backs the symbol.

        Postconditions:
            - ``name_of(sparkle)`` and ``sparkle_of(name)`` both round-trip.
            - The sparkle is persisted in ``self.storage``.
        """
        self.name_to_sparkle[name] = sparkle
        self.hash_to_name[sparkle.stable_hash()] = name
        self.storage.put(memory.Chunk(sparkle))

    def name_of(self, hb: HyperBinary) -> str | None:
        """Return the registered symbol name for a hypervector.

        Args:
            hb (HyperBinary): A hypervector to look up.

        Returns:
            Optional[str]: the symbol name, or ``None`` if no symbol is
                registered for ``hb``.
        """
        return self.hash_to_name.get(hb.stable_hash())

    def sparkle_of(self, name: str) -> hv.Sparkle | None:
        """Return the registered Sparkle for a symbol name.

        Args:
            name (str): The symbol name to look up.

        Returns:
            Optional[hv.Sparkle]: the Sparkle, or ``None`` if no symbol is
                registered under ``name``.
        """
        return self.name_to_sparkle.get(name)

    def random_sparkle(self) -> hv.Sparkle:
        """Generate a random Sparkle in the cons domain.

        Each call advances the PCG-based RNG, producing a fresh sparkle.

        Returns:
            hv.Sparkle: a uniquely-seeded random Sparkle.

        Postconditions:
            - The internal RNG state advances.
        """
        return hv.Sparkle.from_seed(self.model, self.cons_domain, self._rng.uint64())

    def is_similar(self, a: HyperBinary, b: HyperBinary) -> bool:
        """Return whether two hypervectors are above the noise threshold.

        Args:
            a (HyperBinary): Left operand.
            b (HyperBinary): Right operand.

        Returns:
            bool: True iff ``overlap(a, b) > thres_noise(model)``.
        """
        return hv.overlap(a, b) > hv.thres_noise(self.model)

    # Public API (matches Rust PyLispEnv)

    def eval(self, expr_str: str) -> str:
        """Parse and evaluate `expr_str` once, returning the display form.

        Args:
            expr_str (str): An S-expression to evaluate.

        Returns:
            str: pretty-printed result.
        """
        from . import evaluator, printer, reader

        return printer.display(self, evaluator.ev(self, reader.parse(self, expr_str)))

    def eval_full(self, expr_str: str) -> str:
        """Parse and evaluate `expr_str` repeatedly until it stabilizes.

        Useful for expressions that require multiple evaluation passes
        (e.g. recursive ``LABEL``-based functions).

        Args:
            expr_str (str): An S-expression to evaluate to a fixed point.

        Returns:
            str: pretty-printed final result.
        """
        from . import evaluator, printer, reader

        return printer.display(
            self, evaluator.ev_until_done(self, reader.parse(self, expr_str))
        )

    def parse_display(self, expr_str: str) -> str:
        """Parse and pretty-print `expr_str` without evaluating it.

        Args:
            expr_str (str): An S-expression to parse.

        Returns:
            str: the parsed structure rendered as a string.
        """
        from . import printer, reader

        return printer.display(self, reader.parse(self, expr_str))
