# Mexican Dollar

The "What's the Dollar of Mexico?" problem is a classic demonstration of analogical reasoning with hypervectors. It shows how structured knowledge about countries can be encoded, and how algebraic operations can answer analogy questions without explicit programming.

## The Problem

Given knowledge about three countries:

| Country | Code | Capital | Currency |
|---------|------|---------|----------|
| USA | USA | Washington DC | Dollar |
| Mexico | MEX | Mexico City | Peso |
| Sweden | SWE | Stockholm | Krona |

We want to answer questions like:
- "What is the Dollar of Mexico?" → **Peso**
- "What is the Washington DC of Mexico?" → **Mexico City**
- "What is the Dollar of Sweden?" → **Krona**

## How It Works

Each country is encoded as a bundled set of role-filler bindings:

$$\text{US} = \sum_{\oplus} \left( \text{code} \otimes \text{usa},\; \text{capital} \otimes \text{dc},\; \text{currency} \otimes \text{dollar} \right)$$

$$\text{Mexico} = \sum_{\oplus} \left( \text{code} \otimes \text{mex},\; \text{capital} \otimes \text{mexico\_city},\; \text{currency} \otimes \text{peso} \right)$$

To find "the Dollar of Mexico", we compute a **transfer vector** from US to Mexico:

$$T_{\text{US} \to \text{Mexico}} = \text{Mexico} \oslash \text{US}$$

Then apply it to Dollar:

$$\text{result} = \text{dollar} \otimes T_{\text{US} \to \text{Mexico}}$$

The result will have high overlap with **Peso** — the analogical answer.

## Code

```python
from kongming_rs import hv

model = hv.MODEL_64K_8BIT
so = hv.SparseOperation(model, 42, 0)

# Create role markers
country_code = hv.Sparkle.with_word(model, "role", "country_code")
capital      = hv.Sparkle.with_word(model, "role", "capital")
currency     = hv.Sparkle.with_word(model, "role", "currency")

# Create fillers
usa         = hv.Sparkle.random("country", so)
mex         = hv.Sparkle.random("country", so)
swe         = hv.Sparkle.random("country", so)
dc          = hv.Sparkle.random("capital", so)
mexico_city = hv.Sparkle.random("capital", so)
stockholm   = hv.Sparkle.random("capital", so)
dollar      = hv.Sparkle.random("currency", so)
peso        = hv.Sparkle.random("currency", so)
krona       = hv.Sparkle.random("currency", so)

# Encode each country as role-filler bundles
us_record = hv.bundle(hv.Seed128(1, 0),
    hv.bind(country_code, usa),
    hv.bind(capital, dc),
    hv.bind(currency, dollar),
)
mexico_record = hv.bundle(hv.Seed128(2, 0),
    hv.bind(country_code, mex),
    hv.bind(capital, mexico_city),
    hv.bind(currency, peso),
)
sweden_record = hv.bundle(hv.Seed128(3, 0),
    hv.bind(country_code, swe),
    hv.bind(capital, stockholm),
    hv.bind(currency, krona),
)

# Transfer vector: Mexico / US
transfer_to_mexico = hv.release(mexico_record, us_record)

# "What's the Dollar of Mexico?"
mexican_dollar = hv.bind(dollar, transfer_to_mexico)
print(f"peso overlap:  {hv.overlap(mexican_dollar, peso)}")    # high!
print(f"dollar overlap: {hv.overlap(mexican_dollar, dollar)}")  # ~1 (noise)
print(f"krona overlap:  {hv.overlap(mexican_dollar, krona)}")   # ~1 (noise)

# "What's the Washington DC of Mexico?"
mexican_dc = hv.bind(dc, transfer_to_mexico)
print(f"mexico_city overlap: {hv.overlap(mexican_dc, mexico_city)}")  # high!

# Transfer to Sweden works the same way
transfer_to_sweden = hv.release(sweden_record, us_record)
swedish_dollar = hv.bind(dollar, transfer_to_sweden)
print(f"krona overlap: {hv.overlap(swedish_dollar, krona)}")  # high!
```

## Why It Works

The transfer vector $T = \text{Mexico} \oslash \text{US}$ captures the *structural mapping* between the two records. When applied to any filler from the US record, it maps it to the corresponding filler in the Mexico record — because the role-filler binding structure is preserved by the algebra.

This is a form of **analogical reasoning**: no explicit rules, no lookup tables — just algebraic operations on high-dimensional vectors.

## See Also

- [Operators](../api/hv/operators.md) — bind, release, bundle
- [Concepts: Operators](../concepts/operators.md) — algebraic foundations
