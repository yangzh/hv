# Learner 💫

Learners are designed to perform online bundling for a stream of observations, in the form of Hebbian-style learning.

The total storage / processing budget is fixed — what matters is the distribution of weights among observed vectors.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
learner = hv.Learner(model, hv.Seed128(0, 42))

# a randomly-initialized learner.
learner = hv.Learner.random(so)
```
{{#endtab}}
{{#tab name="Go"}}
```go
learner := hv.NewLearner(model, hv.NewSeed128(0, 42), nil)

// a randomly-initialized learner.
learner := hv.NewRandomLearner(so)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let mut learner = Learner::new(model, Seed128::new(0, 42), None);

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

learner.support(a)           # overlap above the chance baseline, saturating at 0
learner.weight(a)            # support, normalized to [0.0, 1.0]
learner.unique_estimated()   # distinct patterns held

learner.stable_hash()        # content hash
learner.core()               # SparseSegmented snapshot of the content
```
{{#endtab}}
{{#tab name="Go"}}
```go
learner.Age()                // uint64
learner.Blank()              // bool: nothing observed yet

learner.Support(a)           // uint32: overlap above chance, saturating at 0
learner.Weight(a)            // float64 in [0, 1]
learner.UniqueEstimated()    // float64: distinct patterns held

learner.StableHash()         // uint64
learner.Core()               // SparseSegmented
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
learner.age()                // u64
learner.blank()              // bool: nothing observed yet

learner.support(&a)          // u32: overlap above chance, saturating at 0
learner.weight(&a)           // f64 in [0, 1]
learner.unique_estimated()   // f64: distinct patterns held

learner.stable_hash()        // u64
learner.core()               // SparseSegmented
```
{{#endtab}}
{{#endtabs}}

<div class="callout callout-warning">
<div class="callout-title">Probing an untrained learner</div>

`Support` and `Weight` require content to probe against: calling either on a
blank learner (`age == 0`) is a contract violation and panics (a
`PanicException` in Python). Check `age()` first when a learner may be
untrained. `UniqueEstimated` is defined everywhere and returns `0` for a
blank learner.
</div>

## Cached Observations

A young Learner does not build its working buffer immediately. It **caches the
observations themselves** — a small list of (vector, weight) pairs — and only
materializes the buffer once the list outgrows its per-model capacity. A cached
observation is a recipe, typically far smaller than a full offsets buffer, so
young learners cost a fraction of what they used to in memory and on the wire.

Two behaviors follow directly:

- **Repeats are free.** Bundling a pattern the learner already holds bumps that
  entry's weight instead of re-bundling it. A learner that sees the same pattern
  a thousand times still holds one entry, and never materializes at all.
- **The unique count is exact** while observations stay cached:
  `unique_estimated()` reports the distinct entry count rather than an overlap
  proxy.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
learner.has_cached_data()    # True while observations are still cached

for entry in learner.cached_data():
    print(entry)             # the cached observations, in arrival order

learner.compact()            # drop cached materializations (content unchanged)
```
{{#endtab}}
{{#tab name="Go"}}
```go
learner.HasCachedData()      // bool

for i, entry := range learner.CachedData() {
    fmt.Println(i, entry)    // the cached observations, in arrival order
}

learner.Compact()            // drop cached materializations (content unchanged)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
learner.has_cached_data();   // bool

for (i, entry) in learner.cached_data() {
    println!("{i} {entry}"); // the cached observations, in arrival order
}

learner.compact();           // drop cached materializations (content unchanged)
```
{{#endtab}}
{{#endtabs}}

<div class="callout callout-note">
<div class="callout-title">Materialization is invisible</div>

Whether a learner is still caching observations or has already materialized its
buffer changes nothing observable: `core()`, `stable_hash()`, `support()` and
serialization all return the same answers either way. The distinction is purely
about when the work is done — see
[lazy materialization](types.md#lazy-materialization).
</div>
