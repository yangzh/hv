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
learner := hv.NewLearner(model, hv.NewSeed128(0, 42))

// a randomly-initialized learner.
learner := hv.NewRandomLearner(so)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let mut learner = Learner::new(model, Seed128::new(0, 42));

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
learner.age()             # number of observations seen

learner.weight(a)     # implicit weight for a probe vector
```
{{#endtab}}
{{#tab name="Go"}}
```go
learner.Age()             // uint32

learner.Weight(a)     // float64
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
learner.age()             // u32

learner.weight(&a)    // f64
```
{{#endtab}}
{{#endtabs}}
