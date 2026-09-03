# Learner

A **Learner** performs online bundling over a stream of observations, in the style of Hebbian learning: each incoming pattern claims a share of a fixed representational budget, weighted by how often it is seen. 

Conceptually the Learner itself is a single hypervector whose content *is* the weighted superposition of everything it has experienced, and recovery is by overlap (e.g. via the near-neighbor-search module, NNS): frequent patterns read back strongly, rare ones faintly, unseen ones at chance level.

## The fixed representational budget

The representational budget is what gives a Learner its character and the limitation we will address later in [LearnerPool](learner_pool.md#fixed-resource-consumption).

A Learner is not a pure container for all experiences but a distribution that sharpens or flattens, which makes it ideal for learning *distributions*: transition frequencies, co-occurrence statistics — and gives it a natural capacity, beyond which no experiences can be reliably recovered.

To give you a concrete example, an 8bit learner, at its core, is a sparse binary hypervector with $256$ segments, each containing a single ON bit. Given the inherent noise, only a few dozen unique patterns can survive the dilution and maintain recognizable weights to be picked up by the [NNS module](near_neighbor_search.md).

## Diversity vs repetition

What fills a Learner is the *diversity* of its past experiences, the unique count of experienced patterns (and their frequencies), instead of simple repetition. 

To make this plain, observing a repeated pattern mostly re-distributes weight already committed, while each genuinely novel pattern makes its mark by diluting all existing residents.

Jump to the API reference for [Learner](../api/hv/learner.md).
