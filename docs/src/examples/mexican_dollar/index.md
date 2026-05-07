# Mexican Dollar

> Standalone scripts: [`mexican_dollar.py`](https://github.com/yangzh/hv/blob/main/examples/mexican_dollar/mexican_dollar.py) | [`mexican_dollar_memory.py`](https://github.com/yangzh/hv/blob/main/examples/mexican_dollar/mexican_dollar_memory.py)

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

$$\text{Sweden} = \sum_{\oplus} \left( \text{code} \otimes \text{swe},\; \text{capital} \otimes \text{stockholm},\; \text{currency} \otimes \text{krona} \right)$$

To find "the Dollar of Mexico", we compute a **transfer vector** from US to Mexico:

$$T_{\text{US} \to \text{Mexico}} = \text{Mexico} \oslash \text{US}$$

Then apply it to Dollar:

$$\text{result} = \text{dollar} \otimes T_{\text{US} \to \text{Mexico}}$$

The result will have high overlap with **Peso** — the analogical answer.

The same transfer works for Sweden:

$$T_{\text{US} \to \text{Sweden}} = \text{Sweden} \oslash \text{US}$$

$$\text{result} = \text{dollar} \otimes T_{\text{US} \to \text{Sweden}} \approx \text{krona}$$

## Code (Manual)

The algebraic approach — compute the transfer vector directly:

```python
from kongming import hv

model = hv.MODEL_64K_8BIT
so = hv.SparseOperation(model, "knowledge", 0)

# Create role markers
country_code = hv.Sparkle.from_word(model, "role", "country_code")
capital      = hv.Sparkle.from_word(model, "role", "capital")
currency     = hv.Sparkle.from_word(model, "role", "currency")

# Create fillers
usa         = hv.Sparkle.from_word(model, "country", "usa")
mex         = hv.Sparkle.from_word(model, "country", "mex")
swe         = hv.Sparkle.from_word(model, "country", "swe")
dc          = hv.Sparkle.from_word(model, "capital", "dc")
mexico_city = hv.Sparkle.from_word(model, "capital", "mexico_city")
stockholm   = hv.Sparkle.from_word(model, "capital", "stockholm")
dollar      = hv.Sparkle.from_word(model, "currency", "dollar")
peso        = hv.Sparkle.from_word(model, "currency", "peso")
krona       = hv.Sparkle.from_word(model, "currency", "krona")

# Encode each country as role-filler bundles
us_record = hv.bundle(hv.Seed128.random(so),
    hv.bind(country_code, usa),
    hv.bind(capital, dc),
    hv.bind(currency, dollar),
)
mexico_record = hv.bundle(hv.Seed128.random(so),
    hv.bind(country_code, mex),
    hv.bind(capital, mexico_city),
    hv.bind(currency, peso),
)
sweden_record = hv.bundle(hv.Seed128.random(so),
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

## Code (with WithCodeModifier)

When records are stored in memory (as [Octopus](../../api/hv/octopus.md) composites), `with_code_modifier` applies the precomputed transfer vector to each candidate:

```python
from kongming import hv, memory

model = hv.MODEL_64K_8BIT
store = memory.InMemory(model)

keys = ["capital", "currency", "country_code"]

# Store individual fillers — NNS needs them as searchable items
fillers = {}
for word in ["dc", "USD", "USA", "mexicoCity", "MXN", "MEX",
             "stockholm", "SEK", "SWE"]:
    s = hv.Sparkle.from_word(model, 0, word)
    store.put(s)
    fillers[word] = s

# Store country records as Octopus composites
store.put(hv.Octopus(
    hv.Seed128("country", "USA"), keys,
    fillers["dc"], fillers["USD"], fillers["USA"],
))
store.put(hv.Octopus(
    hv.Seed128("country", "MEX"), keys,
    fillers["mexicoCity"], fillers["MXN"], fillers["MEX"],
))
store.put(hv.Octopus(
    hv.Seed128("country", "SWE"), keys,
    fillers["stockholm"], fillers["SEK"], fillers["SWE"],
))

# Retrieve stored records
us_code  = store.get("country", "USA").code
mex_code = store.get("country", "MEX").code
swe_code = store.get("country", "SWE").code

view = store.new_view()

# "What is the USD of Mexico?"
result = memory.first_picked(view,
    memory.nns(
        memory.with_code_modifier(
            memory.with_code(mex_code),
            hv.bind(fillers["USD"], hv.inverse(us_code)),
        )
    )
)
print(result.id)  # → ✨:🌱MXN

# "What is the Washington DC of Mexico?"
result = memory.first_picked(view,
    memory.nns(
        memory.with_code_modifier(
            memory.with_code(mex_code),
            hv.bind(fillers["dc"], hv.inverse(us_code)),
        )
    )
)
print(result.id)  # → ✨:🌱mexicoCity

# "What is the Dollar of Sweden?"
result = memory.first_picked(view,
    memory.nns(
        memory.with_code_modifier(
            memory.with_code(swe_code),
            hv.bind(fillers["USD"], hv.inverse(us_code)),
        )
    )
)
print(result.id)  # → ✨:🌱SEK
```

The caller computes the transfer vector `feature ⊗ inverse(src)` once;
`with_code_modifier` applies it to each candidate code, and [near-neighbor search](../concepts/near_neighbor_search.md) finds the best match in memory.

## Why It Works

The transfer vector $T = \text{Mexico} \oslash \text{US}$ captures the *structural mapping* between the two records. When applied to any filler from the US record, it maps it to the corresponding filler in the Mexico record — because the role-filler binding structure is preserved by the algebra.

This is a form of **analogical reasoning**: no explicit rules, no lookup tables — just algebraic operations on high-dimensional vectors.

## See Also

- [Concepts: Operators](../concepts/operators.md) — algebraic foundations
- [Operators](../../api/hv/operators.md) — bind, release, bundle
- [Octopus](../../api/hv/octopus.md) — key-value composite used for country records
- [Memory: Selectors](../../api/memory/selectors.md) — `with_code_modifier`, `nns`, `with_code`
- [Near-neighbor search](../concepts/near_neighbor_search.md) — how the reasoner finds answers
