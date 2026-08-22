# Learner

A **Learner** performs online bundling over a stream of observations, in the style of Hebbian learning: each incoming pattern claims a share of a fixed representational budget, weighted by how often it is seen. Nothing is stored verbatim and nothing is ever appended — the Learner is a single hypervector whose content *is* the weighted superposition of everything it has experienced, and recovery is by overlap: frequent patterns read back strongly, rare ones faintly, unseen ones at chance level.

## A fixed budget

The budget is what gives a Learner its character. Because the total signal is conserved, every new distinct pattern dilutes the ones already resident; a Learner is not a container that fills but a distribution that sharpens or flattens. This makes it ideal for learning *distributions* — transition frequencies, co-occurrence statistics, prototypes — and gives it a natural capacity: past a few dozen distinct patterns (at typical sparsities), individual signals sink toward the noise floor. Aggregates like [LearnerPool](learner_pool.md) exist to lift that ceiling.

## Diversity vs repetition

What fills a Learner is *diversity*, the unique count of experience, instead of simple repetition: re-bundling a known pattern re-distributes weight already committed, while each genuinely new pattern dilutes all residents.

## Cached observations

A Learner does not commit to its fixed budget on the first observation. While it
holds only a handful of distinct patterns it caches the observations themselves —
the vectors and their weights — and composes the superposition on demand. Past a
per-model capacity it materializes the budget once and behaves exactly as
described above.

This makes the diversity-versus-repetition distinction structural rather than
statistical. A repeated pattern is recognized as one the Learner already holds
and simply gains weight: nothing is re-bundled, nothing is diluted, and a
Learner fed one pattern a thousand times still holds exactly one. While
observations are cached the unique count is therefore exact, not estimated —
and young Learners, which is most of them in a large substrate, cost a fraction
of a materialized vector to hold and to store.

Jump to the API reference for [Learner](../api/hv/learner.md).
