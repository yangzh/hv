# LearnerPool

> **DRAFT — placeholder.** Structure only; content to be filled in.

**LearnerPool** is an aggregate over member [Learners](../api/hv/learner.md) for improved scalability.

<!-- TODO: one-paragraph motivation — the per-Learner capacity ceiling, and
     what pooling members buys (capacity that scales with the roster, not
     with a single bundle's bandwidth). -->

## Why a pool

<!-- TODO: the saturation cliff of a single Learner; hub addresses; why
     one-Learner-per-address wastes low-fan-out addresses and starves
     high-fan-out ones. -->

## Access circles

<!-- TODO: address → circle of members; τ and the Poisson(1) overlap model;
     adaptive, margin-driven circle sizing (one criterion: diversity margin
     vs 2θ); saturation semantics (a fixed roster refuses writes when every
     member is full). -->

## Write with signature

<!-- TODO: addr ⊗ data storage; discriminative vs generative reads;
     per-member scans and the access-circle read. -->

## Reading from a pool

<!-- TODO: support / noise floor; released members as attractors. -->

## Persistence

<!-- TODO: the self-describing sentinel (kongming.api.v1.LearnerPoolProto),
     member chunks, memory.load_learner_pool / LoadLearnerPool. -->

## API at a glance

<!-- TODO: table across Go / Rust / Python once the surface settles. -->

Jump to the API reference: *TODO — link once the LearnerPool API page exists.*
