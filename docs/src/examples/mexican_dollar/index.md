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

Full script: [`mexican_dollar.py`](https://github.com/yangzh/hv/blob/main/examples/mexican_dollar/mexican_dollar.py). The essence — each country is a bundle of role ⊗ filler pairs, and one release + one bind answers the analogy:

```python
us_record = hv.bundle(hv.Seed128.random(so),
    hv.bind(country_code, usa), hv.bind(capital, dc), hv.bind(currency, dollar))
# ... mexico_record, sweden_record likewise ...

transfer_to_mexico = hv.release(mexico_record, us_record)
mexican_dollar = hv.bind(dollar, transfer_to_mexico)

hv.overlap(mexican_dollar, peso)    # 32/32 — the answer
hv.overlap(mexican_dollar, dollar)  #  2    — noise
hv.overlap(mexican_dollar, krona)   #  0    — noise
```

The same transfer answers "the Washington DC of Mexico?" (→ mexico_city, 29/32) and, via `release(sweden_record, us_record)`, "the Dollar of Sweden?" (→ krona, 26/32).

## Code (with AnalogicalReasoner)

Full script: [`mexican_dollar_memory.py`](https://github.com/yangzh/hv/blob/main/examples/mexican_dollar/mexican_dollar_memory.py). When the country records live in storage — filler terminals plus one [Octopus](../../api/hv/octopus.md) per country, staged via the producer API — `analogical_reasoner` does the transfer for you:

```python
result = memory.first_picked(view,
    memory.nns(
        memory.analogical_reasoner(
            memory.with_code(mex_code), src=us_code, feature=fillers["USD"])))
print(result.id)  # → ✨:🌱MXN
```

`analogical_reasoner` computes the transfer vector `feature ⊗ inverse(src)` internally and uses [near-neighbor search](../../concepts/near_neighbor_search.md) to find the best match in memory — no manual algebra needed.

## Why It Works

The transfer vector $T = \text{Mexico} \oslash \text{US}$ captures the *structural mapping* between the two records. When applied to any filler from the US record, it maps it to the corresponding filler in the Mexico record — because the role-filler binding structure is preserved by the algebra.

This is a form of **analogical reasoning**: no explicit rules, no lookup tables — just algebraic operations on high-dimensional vectors.

## See Also

- [Concepts: Operators](../../concepts/operators.md) — algebraic foundations
- [Operators](../../api/hv/operators.md) — bind, release, bundle
- [Octopus](../../api/hv/octopus.md) — key-value composite used for country records
- [Memory: Selectors](../../api/memory/selectors.md) — `analogical_reasoner`, `nns`, `with_code`
- [Near-neighbor search](../../concepts/near_neighbor_search.md) — how the reasoner finds answers
