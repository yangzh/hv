# Composites

Composites combine multiple hypervectors into higher-level conceptual structures. Each composite type uses a different combination strategy, preserving different semantics between its members.

All composites follow the same contract (interface in Go and traits in Rust) and can be hierarchically nested: for example, a Set can contain Sparkles, Knots, or even other Sets.

## Sparkle ✨: the primitive

Before any composite, there is the **Sparkle** ✨ — the atomic, *named* hypervector everything below is built upon. A raw [SparseSegmented 🍡](../api/hv/sparse_segmented.md) is just a bit pattern, and a Sparkle ✨ is that pattern with an identity:

$$S = \text{expand}(D, P)$$

where $D$ (the **Domain**) is a semantic namespace — "animals", "role", "country" — and $P$ (the **Pod**) names the individual within it: a word, a numeric seed, a prewired constant.

The (Domain, Pod) seed deterministically expands into the vector, so the same triple (model, domain, pod) yields the same Sparkle ✨ in every run and every engine — Go, Rust, and Python are bit-identical. 

For this reason, only domain and pod are needed, instead of the raw per-segment offsets, which is a significant saving both on-wire and on-storage.

Two properties that carry the most weight:

- Distinct Sparkles ✨ are always **quasi-orthogonal**, without any central orchestration. They can be safely used as bricks for high-level construction;
- The markers and keys in the formulas below — $S_{marker}$, $S_{step}$, $K_i$ — are themselves Sparkles. The whole composite algebra bootstraps from this one primitive type.

Use when: you need a stable, deterministic identity for an atomic concept — a word, a role, an entity — as a leaf for the composites below.

Check out [code snippets](../api/hv/sparkle.md) from the API reference.

## Set 🫧

An **unordered** collection of concepts. 

$$S = S_{marker} \otimes (\sum_{i,\oplus} M_i)$$

where $S_{marker}$ is a special marker to distinguish the set itself from its individual members.

Use when: you need to represent "these things together" without order.

Check out [code snippets](../api/hv/set.md) from the API reference.

## Sequence 📿

An **ordered** collection. 

$$S = S_{marker} \otimes (\sum_{i,\oplus} M_i \otimes S_{step}^{i})$$

where $S_{step}$ is a generic hypervector for positional encoding.

$S_{marker}$ is a special marker to distinguish a sequence from its individual members.

Use when: order matters (e.g., words in a sentence, events in time).

Check out [code snippets](../api/hv/sequence.md) from the API reference.

## Octopus 🐙

A **key-value** structure. Each key (a string) is converted to a Sparkle ✨ and bound with its corresponding value before bundling.

$$S = \sum_{i,\oplus} K_i \otimes V_i$$

Use when: you need to represent structured records with named attributes.

Check out [code snippets](../api/hv/octopus.md) from the API reference.

## Knot 🪢

The result of **binding** (multiplicative composition) of hypervectors. 

$$S = \prod_{i,\otimes} M_i$$

Unlike [direct bind operator](operators.md#bind), Knot 🪢 keeps tracking of its members for serialization and introspection.

Use when: you need a reversible association between concepts.

Check out [code snippets](../api/hv/knot.md) from the API reference.

## Parcel 🎁

The result of **bundling** (additive composition) of hypervectors. 

$$S = \sum_{i,\oplus} M_i$$

Unlike [direct bundle operator](operators.md#bundle), Parcel 🎁 keeps tracking of its members for serialization and introspection.

Use when: you need a superposition of concepts, with optional weights.

Check out [code snippets](../api/hv/parcel.md) from the API reference.

## Dart 🎯

A **one-directional reference** between two hypervectors.

$$P = A \otimes B^{-1} = A \oslash B$$

A Dart 🎯 encodes a directed link from a source `A` to a destination `B` — the direction is semantic (*from → to*), while algebraically the link is recoverable from either end. Dart 🎯 is the structured wrapper for the [release](operators.md#release).

Given the Dart 🎯 of $P$:

$$ A = P \otimes B $$ 
$$ B = P^{-1} \otimes A $$

Use when: you need a directed link — edges, mappings, "from→to" relations — where either endpoint can still be recovered given the other.

Check out [code snippets](../api/hv/dart.md) from the API reference.

## Summary

| Type | Composition | Order? | Use Case |
|------|------------|--------|----------|
| **Sparkle** | Primitive — seed expansion, no members | — | Named atomic identities |
| **Set** | Bundle + marker | No | Unordered groups |
| **Sequence** | Positional-bind + bundle + marker | Yes | Ordered lists |
| **Octopus** | Key-bind + bundle | No | Key-value records |
| **Knot** | Bind (multiply) | No | Associations |
| **Parcel** | Bundle (add) | No | Superpositions, weighted or unweighted |
| **Dart** | Release | Directional | One-directional references |
