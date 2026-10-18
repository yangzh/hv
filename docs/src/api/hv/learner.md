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
{{#endtabs}}

## Feeding Observations

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
learner.bundle(a)                 # single observation

learner.bundle_multiple(b, 3)     # three whole observations

# Below one observation. Weights are numerators over hv.mass_denominator(model),
# so a quarter-observation is that denominator // 4.
learner.bundle_fractional(c, hv.mass_denominator(model) // 4)
```
{{#endtab}}
{{#endtabs}}

## Inspection

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
learner.age()                # how many bundle calls, whatever weight they carried
learner.mass_numerator()     # accumulated weight, in units of 1/mass_denominator
learner.blank()              # bool: whether this learner is blank (nothing observed yet)

learner.model()              # identity accessors: model / domain / pod
learner.domain()
learner.pod()

learner.support(a)           # overlap above the chance baseline, clamped at 0
learner.barycentric(a)       # a's share of the accumulated weight; unbiased, so
                             # it reads negative below chance (clamp at the call
                             # site if you need a non-negative share)

learner.mass(a)              # a's accumulated weight, in WHOLE observations
learner.mass_fractional(a)   # ... and exactly, as a numerator
```
{{#endtab}}
{{#endtabs}}

<div class="callout callout-warning">
<div class="callout-title">Probing an untrained learner</div>

`Support` and `Barycentric` require content to probe against: calling either on a
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
