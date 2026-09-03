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
s0.exponent()      # Current exponent (1 for base vector)

s0_square=s0.power(2)     # Returns p-th power (new Sparkle)
hv.equal(s0, s0_square)   # s0_square = s0^2, different from original s0.
       
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
| 💪 | Exponent / Power | `💪3`, `💪-1` |

**Identity vectors** display as `IDENT` (e.g., `✨IDENT`).

</div>

<div class="callout callout-note">
<div class="callout-title">Note</div>

The underlying offsets are lazily generated from a seeded PRNG. Only the seeds are stored in serialization, which is a significant storage saving.

</div>