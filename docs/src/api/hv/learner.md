# Learner 💫

Performs online bundling for a stream of observations, implementing Hebbian-style learning. The total weight budget is fixed — what matters is the distribution of weights among observed vectors.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
learner = hv.Learner(model, "domain", seed)

# From SparseOperation
learner = hv.Learner.random(so)
```
{{#endtab}}
{{#tab name="Go"}}
```go
learner := hv.NewLearner(model, domain, pod)

// From Seed128
learner := hv.NewLearnerWithSeed(model, seed128)

// From SparseOperation
learner := hv.NewRandomLearner(so)

// Full restore (with age, pcg, buffer)
learner := hv.NewLearnerFull(model, domain, pod, age, pcg, buffer)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let mut learner = Learner::new(model, domain, pod);

// From seed
let mut learner = Learner::with_seed(model, seed_high, seed_low);

// From SparseOperation
let mut learner = Learner::random(&mut so);

// Full restore
let mut learner = Learner::full(model, domain, pod, age, buffer);
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
learner.BundleSet(hbs)                      // entire HyperBinarySet
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
learner.bundle(&observation)?;              // single observation
learner.bundle_multiple(&observation, 3)?;  // with weight multiplier
learner.bundle_set(&hbs)?;                  // entire HyperBinarySet
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
learner.Revitalize(age)   // reset age to speed up future learning
learner.Core()            // SparseSegmented — current learned state
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
learner.age()             // u32
learner.weight(&probe)    // f64
learner.revitalize(age);  // reset age
learner.core()            // SparseSegmented
```
{{#endtab}}
{{#endtabs}}
