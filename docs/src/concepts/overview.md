# Concepts

The ideas behind this library, independent of any particular language binding. Start here for the mental model; jump to the [API Reference](../api/hv/overview.md) for the concrete surface and practical usage.

<div class="callout callout-note">
<div class="callout-title">Note</div>

Hyperdimensional Computing (HDC) and **Vector Symbolic Architectures (VSA)** are two names for the same field. These docs use VSA when referring to the algebra of operators.

</div>

| Concept | Description |
|---------|-------------|
| [Hypervectors](hypervectors.md) | High-dimensional vectors, similarity, and distance |
| [Operators](operators.md) | Bind and bundle: the algebra of composition |
| [Composites](composites.md) | Structures built from the primitives |
| [Near-neighbor search](near_neighbor_search.md) | Highly efficient retrieval of relevant entries |
| [Learner](learner.md) | Hebbian learning over a stream of experience: bedrock for intelligent behaviors |
| [LearnerPool](learner_pool.md) | Pooled Learners sharing a fixed budget elastically |
