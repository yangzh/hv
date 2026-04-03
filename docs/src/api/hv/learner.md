# Learner 💫

Learners are designed to perform online bundling for a stream of observations, for Hebbian-style learning.

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
learner.bundle(observation)                 # single observation

learner.bundle_multiple(observation, 3)     # with weight multiplier
```
{{#endtab}}
{{#tab name="Go"}}
```go
learner.Bundle(observation)                 // single observation

learner.BundleMultiple(observation, 3)      // with weight multiplier
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
learner.bundle(&observation)?;              // single observation

learner.bundle_multiple(&observation, 3)?;  // with weight multiplier
```
{{#endtab}}
{{#endtabs}}

## Inspection

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
learner.age()             # number of observations seen

learner.weight(probe)     # implicit weight for a probe vector
```
{{#endtab}}
{{#tab name="Go"}}
```go
learner.Age()             // uint32

learner.Weight(probe)     // float64
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
learner.age()             // u32

learner.weight(&probe)    // f64
```
{{#endtab}}
{{#endtabs}}
