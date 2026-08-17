# Learner

A **Learner** performs online bundling over a stream of observations, in the style of Hebbian learning: each incoming pattern claims a share of a fixed representational budget, weighted by how often it is seen. Nothing is stored verbatim and nothing is ever appended — the Learner is a single hypervector whose content *is* the weighted superposition of everything it has experienced, and recovery is by overlap: frequent patterns read back strongly, rare ones faintly, unseen ones at chance level.

## A fixed budget

The budget is what gives a Learner its character. Because the total signal is conserved, every new distinct pattern dilutes the ones already resident; a Learner is not a container that fills but a distribution that sharpens or flattens. This makes it ideal for learning *distributions* — transition frequencies, co-occurrence statistics, prototypes — and gives it a natural capacity: past a few dozen distinct patterns (at typical sparsities), individual signals sink toward the noise floor. Aggregates like [LearnerPool](learner_pool.md) exist to lift that ceiling.

## Diversity vs repetition

What fills a Learner is *diversity*, the unique count of experience, instead of simple repetition: re-bundling a known pattern re-distributes weight already committed, while each genuinely new pattern dilutes all residents.

Jump to the API reference for [Learner](../api/hv/learner.md).
