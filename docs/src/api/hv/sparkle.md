# Sparkle ✨

Sparkles are the atomic building block for higher-level constructs. Domain is a logical namespace that groups related Sparkle instances. Pod acts as the secondary identifier for a Sparkle instance.

Sparkle is **deterministic**: the same (domain, pod) pair always produces the same offsets, across all sessions and engines. For this reason, the (model, domain, pod) triple uniquely identifies a Sparkle, and we store the triple rather than the raw offsets for huge space saving.

## Sparkle Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# From a word string
s0 = hv.Sparkle.from_word(model, "animals", "cat")

# From a numeric seed
s1 = hv.Sparkle.from_seed(model, "animals", 42)

# From a prewired enum
s2 = hv.Sparkle.from_prewired(model, "animals", hv.PREWIRED_SET_MARKER)

# Identity vector
s3 = hv.Sparkle.identity(model)

# Random (from SparseOperation)
so = hv.SparseOperation(hv.MODEL_1M_10BIT, 0, 42)
s4 = hv.Sparkle.random("animals", so)

# From domain + pod directly — primary constructor
s5 = hv.Sparkle(model, "animals", pod)
```
{{#endtab}}
{{#endtabs}}

## Key Methods

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
s0.model()         # Model enum
s0.stable_hash()   # Deterministic and unique hash
s0.exponent()      # Current exponent, as (numerator, denominator): (1, 1) for a base vector

s0_square=s0.power(2)     # Returns p-th power (new Sparkle)
hv.equal(s0, s0_square)   # s0_square = s0^2, different from original s0.

s0_half=s0.power(1, 2)          # Fractional power: s0^(1/2)
s0_half=s0.power(1, denominator_ls=1)   # Same as above, denominator as 2**ls

core0=s0.core()     # Returns underlying SparseSegmented
core0.offsets()    # The raw offsets for each segment.
```
{{#endtab}}
{{#endtabs}}

<div class="callout callout-note">
<div class="callout-title">Note</div>

`power(0)` returns the identity vector (serialized in the canonical
`SparseSegmented` nil-offsets form). Only `Sparkle` and `SparseSegmented`
support `power(0)` — every other type has no identity-vector concept and
rejects it. `power(-1)` returns the inverse.
</div>

## Fractional powers

`power()` takes an optional denominator, so the exponent can be fractional instead of an whole integer. Each offset is scaled by `numerator / denominator` and
truncated toward zero, which places `s^(1/2)` "half way" along the permutation
that `power(1)` walks in one step.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
s = hv.Sparkle.from_word(model, "pos", "step")

s.power(1, 2).exponent()    # (1, 2)
s.power(-3, 4).exponent()   # (-3, 4) — the sign always rides on the numerator
s.power(6, 2).exponent()    # (3, 1) — reduced to lowest terms, so this is the
                            #          integer power, and takes the integer path

# A fractional power is near-orthogonal to the base AND to the integer powers.
hv.overlap(s, s.power(1, 2))            # ≈ 0
hv.overlap(s.power(1, 2), s.power(2))   # ≈ 0

print(s.power(1, 2))        # ✨:🔗pos,🌱step,💪1/2
print(s.power(-3, 4))       # ✨:🔗pos,🌱step,💪-3/4
```
{{#endtab}}
{{#endtabs}}

The exponent is always kept in lowest terms with the sign on the numerator, so
`power(6, 2)` and `power(3)` are the same vector, and `exponent()` never reports
an unreduced pair.

### `denominator_ls`: the denominator as a shift

`power()` also accepts `denominator_ls`, which spells the denominator as
`2 ** denominator_ls`. It is consulted first; `denominator` applies only when
`denominator_ls` is unspecified. So `power(1, denominator_ls=3)` is exactly `power(1, 8)`.

The two forms produce identical results, but the power-of-two computation can be cheaper, as the scaling runs on an integer path. On the wire it encodes as a small shift rather than a full integer as well.

<div class="callout callout-warning">
<div class="callout-title">Fractional powers are lossy once materialized</div>

Scaling truncates toward zero, so a fractional power discards information that a
later power cannot restore. Whether that loss actually happens depends on when
the vector is computed:

```python
s  = hv.Sparkle.from_word(model, "pos", "step")   # lazy
ss = s.core()                                     # materialized

hv.overlap(s,  s.power(1, 2).power(2, 1))    # full — exact round trip
hv.overlap(ss, ss.power(1, 2).power(2, 1))   # ≈ half — offsets were truncated
```

`Sparkle` and the composites are lazy: `power()` folds the exponent into the
recipe, so `1/2` then `2/1` cancels to `1/1` *before* anything is computed, and
the round trip is exact. `SparseSegmented` is materialized, so each `power()`
rewrites the offsets immediately and the truncation is permanent.

Prefer composing exponents on a lazy vector and materializing once at the end.

Note that `core()` is that materialization step: it computes the offsets with
every pending exponent folded in, so the result reports `exponent() == (1, 1)`.
See [the exponent is always 1](sparse_segmented.md#the-exponent-is-always-1).
</div>

## Pretty-printing

{{#tabs global="lang"}}
{{#tab name="Python"}}
```Python
# Pretty-printing, or s.__str__()
print(s0)
# ✨:🔗animals,🌱cat

# More detailed information, or s.__repr__()
s
# hint: SPARKLE
# model: MODEL_1M_10BIT
# stable_hash: 9725717137035622833
# domain:
#   name: animals
# pod:
#   word: cat
```
{{#endtab}}
{{#endtabs}}

During pretty-printing of Sparkle instances, you may notice special emoji for domain / pods.

<div class="callout callout-tip">
<div class="callout-title">emojis for domain / pod</div>

| Emoji | Variant | Example |
|-------|---------|---------|
| 🔗 | named domain| `🔗animals`, `🔗PREFIX.name` |
| 🌐 | numeric domain | `🌐0x..c862` |
| 🌱 | named pod | `🌱cat` |
| 🫛 | numeric pod | `🫛0x..80e4` |
| 🍀 | pre-defined pod | `🍀SET_MARKER` |
| 💪 | Exponent / Power | `💪3`, `💪-1`, `💪1/2`, `💪-3/4` |

**Identity vectors** display as `IDENT` (e.g., `✨IDENT`).

</div>

<div class="callout callout-note">
<div class="callout-title">Note</div>

The underlying offsets are lazily generated from a seeded PRNG. Only the seeds are stored in serialization, which is a significant storage saving.

</div>