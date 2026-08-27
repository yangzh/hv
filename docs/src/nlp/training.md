# Training: capture, not optimization

One pass over the corpus captures three families of evidence into a single
per-language [LearnerPool](../concepts/learner_pool.md), kept disjoint by
address domain:

| family | address → content | answers at decode time |
|--------|-------------------|------------------------|
| **out** | sibling edge → next sibling edge | "after this edge, what comes next at this level?" |
| **down** | child edge → parent edge | "whose child is this?" (the climb toward the root) |
| **obs** | surface text → leaf edge | "which grammar edges has this word appeared in?" |

Alongside the pool, ordinary chunks record the open-class inventory: feats,
edges, tokens (an [Octopus](../concepts/composites.md#octopus-🐙) of
feats/lemma/text), and named entities. Every write is a `bundle` — seeing
the same transition twice simply deepens its weight. There is no
optimization loop; frequency *is* the statistic.

## See also

- [Composites](../concepts/composites.md) — Sequences and Octopuses the representation is made of.
- [LearnerPool](../concepts/learner_pool.md) — the capacity substrate the parser trains into.
- [Near-neighbor search](../concepts/near_neighbor_search.md) — the
  retrieval layer under the climb.
