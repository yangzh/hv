# Composites

Composites combine multiple hypervectors into higher-level structures. Each composite type uses a different combination strategy, preserving different kinds of relationships between its members.

All composites implement the HyperBinary interface and can be nested — a Set can contain Sparkles, Knots, or even other Sets.

## Set

An **unordered** collection of concepts. 

$$S = S_{marker} \otimes (\sum_{i,\oplus} M_i)$$

where $S_{marker}$ is a special marker to distinguish a set from its individual members. 

This mark is tuned for the domain, so that it WILL be shared among all sets within the same domain. 

Use when: you need to represent "these things together" without order.

Jump to API reference for Set [here](../api/hv/set.md).

## Sequence

An **ordered** collection. 

$$S = S_{marker} \otimes (\sum_{i,\oplus} M_i \otimes S_{step}^{i})$$

where $S_{step}$ is a generic hypervector for positional encoding.

$S_{marker}$ is a special marker to distinguish a sequence from its individual members. This mark is tuned for the domain, so that it WILL be shared among all sequences within the same domain. 

Use when: order matters (e.g., words in a sentence, events in time).

Jump to API reference for Sequence [here](../api/hv/sequence.md).

## Octopus

A **key-value** structure. Each key (a string) is converted to a Sparkle and bound with its corresponding value before bundling.

$$S = \sum_{i,\oplus} K_i \otimes V_i$$

Use when: you need to represent structured records with named attributes.

Jump to API reference for Octopus [here](../api/hv/octopus.md).

## Knot

The result of **binding** (multiplicative composition) of hypervectors. 

$$S = \prod_{i,\otimes} M_i$$

Binding is reversible: given a Knot of A and B, you can recover A by releasing B (binding with B's inverse).

Use when: you need a reversible association between concepts.

Jump to API reference for Knot [here](../api/hv/knot.md).

## Parcel

The result of **bundling** (additive composition). 

$$S = \sum_{i,\oplus} M_i$$

Unlike direct bundling, Parcel tracks its members for serialization and introspection.

Use when: you need a superposition of concepts with optional weights.

Jump to API reference for Parcel [here](../api/hv/parcel.md).

## Summary

| Type | Composition | Order? | Use Case |
|------|------------|--------|----------|
| **Set** | Bundle + marker | No | Unordered groups |
| **Sequence** | Positional-bind + bundle + marker | Yes | Ordered lists |
| **Octopus** | Key-bind + bundle | Partial (by key) | Key-value records |
| **Knot** | Bind (multiply) | No | Reversible associations |
| **Parcel** | Bundle (add) | No | superpositions, weighted or unweighted |
