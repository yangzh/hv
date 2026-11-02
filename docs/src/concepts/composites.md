# Composites

Composites combine multiple hypervectors into higher-level conceptual structures. Each composite type uses a different combination strategy, preserving different semantics between its members.

## Sparkle ✨: the primitive

Before any composite, there is the **Sparkle** ✨: the atomic, *seeded* hypervector everything below is built upon.

A raw [SparseSegmented 🍡](../api/hv/sparse_segmented.md) is just a bit pattern. A Sparkle ✨ is a deterministic hypervector built from a seed of two parts:

- the **Domain** — a semantic namespace, such as "animals", "role", or "country";
- the **Pod** — the individual within it: a word, a numeric seed, or a constant pre-defined by the package.

That pair seeds an underlying RNG (random number generator), which deterministically produces the vector's offsets. The same model, domain and pod therefore yield the same Sparkle ✨ in every run and every engine, with Go, Rust, and Python bit-identical. Carrying that seed instead of the raw per-segment offsets is also a significant saving, both on the wire and in storage.

Two properties that carry the most weight:

- The tuple of (Domain, Pod) can be treated as the **unique identity** for the Sparkle ✨;
- Distinct Sparkles ✨ are always **nearly orthogonal**, without any central orchestration. They can be safely used as bricks for high-level construction;

This one primitive is also what the composite algebra is built from: the markers and keys in the formulas below — $S_{marker}$, $S_{step}$, $K_i$ — are themselves Sparkles ✨, so every structure on this page bootstraps from the same type.

Use when: you need a stable, deterministic identity for an atomic concept, like a word, a role, an entity, or as a leaf for the composites below.

Check out [code snippets](../api/hv/sparkle.md) from the API reference.

## Set 🫧

An **unordered** collection of concepts.

$$S = S_{marker} \otimes (\sum_{i,\oplus} M_i)$$

where $S_{marker}$ is a special marker (predefined Sparkle ✨) that causes the different encoding between individual element $A$ and the set $\{A\}$.

Use when: you need to represent "these things together" without order.

Check out [code snippets](../api/hv/set.md) from the API reference.

## Sequence 📿

An **ordered** collection.

$$S = S_{marker} \otimes (\sum_{i,\oplus} M_i \otimes S_{step}^{i})$$

where $S_{step}$ is a special marker (predefined Sparkle ✨) for positional encoding.

$S_{marker}$ is a special marker such that an element $A$ and the sequence $[A]$ are encoded differently.

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

$$P = T^{-1} \otimes H = H \oslash T$$

A Dart 🎯 is "thrown" from a tail `T` to a head `H` — the direction is semantic (*`T` → `H`*), while algebraically the link is recoverable from either end. Dart 🎯 is the structured wrapper for the [release](operators.md#release).

Given the Dart 🎯 of $P=H \oslash T$:

$$ H = P \otimes T $$

$$ T = P^{-1} \otimes H $$

Use when: you need a directed link — edges, mappings, "from→to" relations — where either endpoint can still be recovered given the other.

Check out [code snippets](../api/hv/dart.md) from the API reference.

## Summary

All composites follow the same contract (interface in Go and traits in Rust) and can be hierarchically nested: for example, a Set can contain Sparkles, Knots, or even other Sets.

Here are some of the important subtypes of hypervectors supported in this package:

| Type | Composition | Order? | Use Case |
|------|------------|--------|----------|
| **SparseSegmented** | None — raw per-segment offsets | — | The materialized form every other type reduces to |
| **Sparkle** | Primitive — seed expansion, no members | — | Named atomic identities |
| **Set** | set of primitives | No | Unordered groups |
| **Sequence** | sequence of primitives | Yes | Ordered lists |
| **Octopus** | Key-bind + bundle | No | Key-value records |
| **Knot** | Bind (multiply) | No | Associations |
| **Parcel** | Bundle (add) | No | Superpositions, weighted or unweighted |
| **Dart** | Release | Directional | One-directional references |
| [**Learner**](learner.md) | Online bundling | No | Learning distributions: frequencies, co-occurrence |
| **Point** | Fractional Power Encoding | — | Positions in a continuous frame |
| **Phasers** | Phasor superposition, exported from a HyperPhaser | No | Comparing bundles by [Lee distance](hypervectors.md#lee-distance-the-graded-alternative) |
