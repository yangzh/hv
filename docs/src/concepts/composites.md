# Composites

Composites combine multiple hypervectors into higher-level structures. Each composite type uses a different combination strategy, preserving different kinds of relationships between its members.

All composites follows the same contract (interface in Go and traits in Rust) and can be nested — a Set can contain Sparkles, Knots, or even other Sets.

## Set

An **unordered** collection of concepts. 

$$S = S_{marker} \otimes (\sum_{i,\oplus} M_i)$$

where $S_{marker}$ is a special marker to distinguish a set from its individual members. 

This mark is tuned for the domain, so that it will be shared among all sets within the same domain. 

Use when: you need to represent "these things together" without order.

Check out [code snippets](../api/hv/set.md) from the API reference.

## Sequence

An **ordered** collection. 

$$S = S_{marker} \otimes (\sum_{i,\oplus} M_i \otimes S_{step}^{i})$$

where $S_{step}$ is a generic hypervector for positional encoding.

$S_{marker}$ is a special marker to distinguish a sequence from its individual members. This mark is tuned for the domain, so that it will be shared among all sequences within the same domain. 

Use when: order matters (e.g., words in a sentence, events in time).

Check out [code snippets](../api/hv/sequence.md) from the API reference.

## Octopus

A **key-value** structure. Each key (a string) is converted to a Sparkle and bound with its corresponding value before bundling.

$$S = \sum_{i,\oplus} K_i \otimes V_i$$

Use when: you need to represent structured records with named attributes.

Check out [code snippets](../api/hv/octopus.md) from the API reference.

## Knot

The result of **binding** (multiplicative composition) of hypervectors. 

$$S = \prod_{i,\otimes} M_i$$

Binding is reversible: given a Knot of A and B, you can recover A by releasing B (binding with B's inverse).

Use when: you need a reversible association between concepts.

Check out [code snippets](../api/hv/knot.md) from the API reference.

## Parcel

The result of **bundling** (additive composition). 

$$S = \sum_{i,\oplus} M_i$$

Unlike direct bundling, Parcel keeps tracking of its members for serialization and introspection.

Use when: you need a superposition of concepts, with optional weights.

Check out [code snippets](../api/hv/parcel.md) from the API reference.

## Pointer

A **one-directional reference** between two hypervectors.

$$P = A \otimes B^{-1}$$

A Pointer encodes a directed link from a source `A` to a destination `B`. Given the pointer and either endpoint, the other endpoint can be recovered: `P ⊗ B` recovers `A`, and `A ⊗ P^{-1}` recovers `B`.

Pointer is the structured wrapper for the [release](../api/hv/operators.md#release) operation — `Release(A, B)` returns a Pointer with `A` as source and `B` as destination.

Use when: you need a reversible directional link (e.g., representing edges, mappings, or "from→to" relations).

Check out [code snippets](../api/hv/pointer.md) from the API reference.

## Summary

| Type | Composition | Order? | Use Case |
|------|------------|--------|----------|
| **Set** | Bundle + marker | No | Unordered groups |
| **Sequence** | Positional-bind + bundle + marker | Yes | Ordered lists |
| **Octopus** | Key-bind + bundle | Partial (by key) | Key-value records |
| **Knot** | Bind (multiply) | No | Reversible associations |
| **Parcel** | Bundle (add) | No | superpositions, weighted or unweighted |
| **Pointer** | Bind A with Inv(B) | Directional | One-directional references |
