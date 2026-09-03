# Learner 💫

Learners are designed to perform online bundling for a stream of observations, in the form of Hebbian learning.

The representational budget is fixed, in the form of segment count $M$ from a single hypervector: what matters is the distribution of weights among observed vectors.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
learner = hv.Learner(model, hv.Seed128(0, 42))

# age-1 learner that starts having seen `obs`.
learner = hv.Learner(model, hv.Seed128(0, 42), initial=obs)

# optional keyword-only rng_hint pins the RNG backend (default: process-wide).
learner = hv.Learner(model, hv.Seed128(0, 42), rng_hint=hv.RNG_PHILOX_4X64)

# a randomly-initialized learner.
learner = hv.Learner.random(so)
```
{{#endtab}}
{{#tab name="Go"}}
```go
// rngHint 0 falls back to the process default.
learner := hv.NewLearner(model, hv.NewSeed128(0, 42), 0, nil)

// age-1 learner that starts having seen `obs`.
learner := hv.NewLearner(model, hv.NewSeed128(0, 42), 0, obs)

// a randomly-initialized learner.
learner := hv.NewRandomLearner(so)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
// rng_hint None falls back to the process default.
let mut learner = Learner::new(model, Seed128::new(0, 42), None, None);

// age-1 learner that starts having seen `obs`.
let mut learner = Learner::new(model, Seed128::new(0, 42), None, Some(obs.kind()));

// a randomly-initialized learner.
let mut learner = Learner::random(&mut so);
```
{{#endtab}}
{{#endtabs}}

## Feeding Observations

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
learner.bundle(a)                 # single observation

learner.bundle_multiple(b, 3)     # with weight multiplier
```
{{#endtab}}
{{#tab name="Go"}}
```go
learner.Bundle(a)                 // single observation

learner.BundleMultiple(b, 3)      // with weight multiplier
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
learner.bundle(&a)?;              // single observation

learner.bundle_multiple(&b, 3)?;  // with weight multiplier
```
{{#endtab}}
{{#endtabs}}

## Inspection

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
learner.age()                # total observed weight (int)
learner.blank()              # bool: whether this learner is blank (nothing observed yet)

learner.model()              # identity accessors: model / domain / pod
learner.domain()
learner.pod()

learner.support(a)           # overlap above the chance baseline, saturating at 0
learner.weight(a)            # support, normalized to [0.0, 1.0]
```
{{#endtab}}
{{#tab name="Go"}}
```go
learner.Age()                // uint64
learner.Blank()              // bool: nothing observed yet

learner.Support(a)           // uint32: overlap above chance, saturating at 0
learner.Weight(a)            // float64 in [0, 1]
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
learner.age()                // u64
learner.blank()              // bool: nothing observed yet

learner.support(&a)          // u32: overlap above chance, saturating at 0
learner.weight(&a)           // f64 in [0, 1]
```
{{#endtab}}
{{#endtabs}}

<div class="callout callout-warning">
<div class="callout-title">Probing an untrained learner</div>

`Support` and `Weight` require content to probe against: calling either on a
blank learner is a contract violation and panics (a
`PanicException` in Python); check `blank()` first.
</div>

## Deferred Observations

A young Learner does not need to build its raw buffer immediately: instead it **defers** the observations themselves as a small list of (vector, weight) pairs, and only materializes the buffer once keeping the list no longer pays. A deferred observation is a recipe, typically far smaller than a full offsets buffer, so young learners cost a fraction of a materialized buffer, in memory and on the wire.

This also implies:

- **Repeats are free.** Bundling a pattern the learner already holds bumps that entry's weight when the recipes match lazily (`EqualLazy`); a repeat arriving in a different representation may land as a fresh entry. A learner that sees the same pattern a thousand times still holds one entry, and never materializes at all.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
learner.has_deferred_data()  # True while observations are still deferred

for entry in learner.deferred_data():
    print(entry)             # the deferred observations, in arrival order

learner.compact()            # drop incidental materializations (content unchanged)
```
{{#endtab}}
{{#endtabs}}

<div class="callout callout-note">
<div class="callout-title">Materialization is transparent</div>

Whether a learner is still deferring observations or has already materialized its buffer changes nothing observable. The distinction is purely internal: refer to
[lazy materialization](types.md#lazy-materialization).
</div>

## See also

- [Learner concepts](../../concepts/learner.md) — the fixed budget,
  diversity vs. repetition.
- [LearnerPool](learner_pool.md) — pooled Learners behind address-keyed
  access circles.
