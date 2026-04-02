# Composites

Composites combine multiple hypervectors into higher-level structures. Each composite type uses a different combination strategy, preserving different kinds of relationships between its members.

All composites implement the HyperBinary interface and can be nested — a Set can contain Sparkles, Knots, or even other Sets.

## Set

An **unordered** collection of concepts. 

$$S = S_{marker} \otimes (\sum_{i,\oplus} M_i)$$

where $S_{marker}$ is a special marker to distinguish a set from its individual members. 

This mark is tuned for the domain, so that it WILL be shared among all sets within the same domain. 

Use when: you need to represent "these things together" without order.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
s = hv.Set(domain, pod, [member_a, member_b, member_c])
```
{{#endtab}}
{{#tab name="Go"}}
```go
s := hv.NewSet(domain, pod, memberA, memberB, memberC)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let s = Set::new(domain, pod, &members);
```
{{#endtab}}
{{#endtabs}}

## Sequence

An **ordered** collection. 

$$S = S_{marker} \otimes (\sum_{i,\oplus} M_i \otimes S_{step}^{i})$$

where $S_{step}$ is a generic hypervector for positional encoding.

$S_{marker}$ is a special marker to distinguish a sequence from its individual members. This mark is tuned for the domain, so that it WILL be shared among all sequences within the same domain. 

Use when: order matters (e.g., words in a sentence, events in time).

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
seq = hv.Sequence(domain, pod, 0, [first, second, third])
```
{{#endtab}}
{{#tab name="Go"}}
```go
seq := hv.NewSequence(domain, pod, 0, first, second, third)
// start=0 means positions are 0, 1, 2
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let seq = Sequence::new(domain, pod, 0, &members);
```
{{#endtab}}
{{#endtabs}}

## Octopus

A **key-value** structure. Each key (a string) is converted to a Sparkle and bound with its corresponding value before bundling.

$$S = \sum_{i,\oplus} K_i \otimes V_i$$

Use when: you need to represent structured records with named attributes.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
oct = hv.Octopus(domain, pod, ["color", "shape"], [red, circle])
```
{{#endtab}}
{{#tab name="Go"}}
```go
oct := hv.NewOctopus(domain, pod, []string{"color", "shape"}, red, circle)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let oct = Octopus::new(domain, pod, &["color", "shape"], &values);
```
{{#endtab}}
{{#endtabs}}

## Knot

The result of **binding** (multiplicative composition) of hypervectors. 

$$S = \prod_{i,\otimes} M_i$$

Binding is reversible: given a Knot of A and B, you can recover A by releasing B (binding with B's inverse).

Use when: you need a reversible association between concepts.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```Python
# Not exported
```
{{#endtab}}
{{#tab name="Go"}}
```go
k := hv.Bind(role, filler)
recovered := hv.Release(k, role) // ≈ filler
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let k = bind_hb(&[role, filler]);
```
{{#endtab}}
{{#endtabs}}

## Parcel

The result of **bundling** (additive composition). 

$$S = \sum_{i,\oplus} M_i$$

Unlike direct bundling, Parcel tracks its members for serialization and introspection.

Use when: you need a superposition of concepts with optional weights.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
p = hv.bundle(hv.Seed128(10, 1), member_a, member_b)
```
{{#endtab}}
{{#tab name="Go"}}
```go
p := hv.Bundle(seed, memberA, memberB)
// or with weights:
p := hv.NewWeightedParcel(domain, pod, []float64{0.7, 0.3}, memberA, memberB)
```
{{#endtab}}
{{#endtabs}}

## Cyclone

A **periodic** permutation vector where `power(v, period) == identity`. Useful for encoding cyclic structures (e.g., days of the week, hours).

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
c = hv.Cyclone(model, domain, pod, 7)  # period=7
# c.power(7) ≈ identity
```
{{#endtab}}
{{#tab name="Go"}}
```go
c := hv.NewCyclone(model, domain, pod, 7) // period=7
// c.Power(7) == identity
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let c = Cyclone::new(model, domain, pod, 7);
```
{{#endtab}}
{{#endtabs}}

## Summary

| Type | Composition | Order? | Use Case |
|------|------------|--------|----------|
| **Set** | Bundle + marker | No | Unordered groups |
| **Sequence** | Positional-bind + bundle + marker | Yes | Ordered lists |
| **Octopus** | Key-bind + bundle | Partial (by key) | Key-value records |
| **Knot** | Bind (multiply) | No | Reversible associations |
| **Parcel** | Bundle (add) | No | superpositions, weighted or unweighted |
| **Cyclone** | Periodic permutation | N/A | Cyclic encodings |
