# Learner

A **Learner** performs online bundling over a stream of observations, in the style of Hebbian learning: each incoming pattern claims a share of a fixed representational budget, weighted by how often it is seen. 

Conceptually the Learner itself is a single hypervector whose content *is* the weighted superposition of everything it has experienced, and recovery via the near-neighbor-search module, NNS: frequent patterns read back with higher overlap, rare ones faintly with lower overlap and unseen ones at chance level.

## The fixed representational budget

A Learner is not a pure container for all experiences but a distribution that sharpens or flattens, which makes it ideal for learning *distributions*: transition frequencies, co-occurrence statistics — and gives it a natural capacity, beyond which no experiences can be reliably recovered.

To give you a concrete example, an 8bit learner, at its core, is a sparse binary hypervector with $256$ segments, each containing a single ON bit. Given the inherent noise, only a few dozen unique patterns can survive the dilution and maintain recognizable weights to be picked up by the [NNS module](near_neighbor_search.md).

This representational budget ($M$ segments) is what gives a Learner its character, and most critically, the limitation we will address later in [LearnerPool](learner_pool.md#fixed-resource-consumption).

Jump to the API reference for [Learner](../api/hv/learner.md).
