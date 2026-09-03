# Training

Training turns a corpus of parsed sentences into a substrate, in a single pass.

This page walks the training pipeline conceptually: from raw text to what, exactly, ends up as a fully-functional language model.

## Preparing the corpus

For reference, we used 4231 English and 4231 Chinese sentences from the public Wikipedia corpus for training. The training itself can be done on a single MacBook Air in ~12 minutes.

### Preparing the text

The corpus starts as plain text, one batch per language: curated sentences covering the vocabulary and constructions the model should absorb and later generalize in typical decoding scenarios.

The text is split into individual sentences up front, and each sentence is handed to the annotation step on its own, one sentence per request.

### Bootstrapping the parsed trees

![Stanford's stanza](images/stanza_snapshot.png)

A teacher parser (i.e., stanza) annotates each incoming sentence: tokens, part of speech, lemma, morphological features, named-entity spans, and the head arc that makes the dependency tree. The annotated sentences are stored as compact per-language archives: training doesn't need the live parser or the raw text, for efficiency reasons.

Beyond various annotations, the training pipeline further constructs a dependency tree per sentence. The tree has a single ROOT, with each leaf node mapping to a surface token and each arc annotated with its dependency relation, following the Universal Dependencies conventions.

## From trees to spines

The local grammar and syntactic dependency are captured by the **nodes** and **edges** of the dependency tree.

A **feats** captures a unique combination of rich linguistic features, such as part-of-speech, lemma, incoming dependency label, and structural markers such as `is_head` (indicating whether this token is the head among its siblings, under their common parent). An **edge**, on the other hand, is the *parent and child feats pair*, as a deterministic [Sparkle](../concepts/composites.md#sparkle--the-primitive) instance.

Each surface token is ultimately emitted by its **spine**, the hierarchy of interlocked **edges** from the root down. Siblings under a subtree share **edges** up to the subtree root, before diverging into their unique edges. 

Within the [state-space](intro.md#state-space-models-generally) setup, the **latent state at token t** is that token's spine, namely its full hierarchical path in the tree, from the root edge down to its leaf. Concretely, a state is a [Sequence](../concepts/composites.md#sequence-📿) whose members are the spine's edges.

Three properties make this state space feasible where classical HMMs can choke: 

- **Representation of states:** the space of possible spines is combinatorially vast, which hypervectors have no problem handling. A state, at its core, is conceptually just another hypervector, sharing the same shape as any other state, with a potentially different length. Practically, thanks to [lazy materialization](../api/hv/types.md#lazy-materialization), composing a state on the fly reduces to simple 
bookkeeping, with very little extra cost;
- **No tabulation:** instead of highly sparse frequency tables, a learner is a far more natural representation for encoding probabilities, only at cells where transitions do happen. Furthermore, [LearnerPool](../concepts/learner_pool.md) offers an elegant solution for the high dynamic range of fan-outs;
- **Content-addressable by construction:** two surface tokens emitted by the same grammatical path share the same state, by construction: that identity is what lets transition statistics pool.

The downstream inference task, naturally, is to recover the most likely sequence of states/spines, before reconstructing the dependency tree.

Looking back, hierarchical inference over such a state space is a generic problem, applicable well beyond linguistic parsing: anywhere the potential state space is too immense to tabulate. A robust training/inference pipeline that accommodates a vast and rich state space is a valuable by-product of this project in its own right. 

## What is learned

Two kinds of learning/writes happen, side by side.

**The inventory** — ordinary chunks, written once (create-if-missing, idempotent across repeats):

- every distinct **feats**: the collection of all known combinations of linguistic features in a language;
- every distinct **edge**: its parent-and-child pair of **feats**;
- every distinct **token** — an [Octopus](../concepts/composites.md#octopus-🐙) containing feats, lemma, and surface text (this is where the lemma can be recovered from the surface token at decode time);
- every **named entity** (see below).

**The statistics** — writes into one per-language
[LearnerPool](../concepts/learner_pool.md), three conceptual families:

| family | address → content | answers at decode time |
|--------|-------------------|------------------------|
| **out** | sibling edge → next sibling edge | "after this edge, what comes next at this level?" |
| **down** | first-child edge → parent edge | "whose child is this?", which supports the exploration/climb upward |
| **obs** | surface text → leaf edge | "which leaf **edges** can emit this surface token?" |

Every occurrence adds an extra piece of information, and the frequency *is* the statistic: a transition seen a thousand times reads back a thousand times stronger than one seen once, at least in principle.

Nothing is normalized at training time, as a self-normalization process is at play: observations compete for a [Learner](../concepts/learner.md#the-fixed-representational-budget)'s fixed representational budget, so read-back strengths are effectively relative probabilities.

### The sentinels: BEGIN and END

Every sibling chain is conceptually bracketed:
`BEGIN → e₁ → e₂ → … → END`. The two brackets are treated very differently,
and the asymmetry is deliberate:

**END is trained.** The last child's out-transition to `END` is recorded like any other, so every edge carries a *measured* probability that its chain closes after it, which is needed by the decoder.

**BEGIN is not trained** as a transition source. "How do chains open?" has enormous fan-out at fine granularity (thousands of distinct edges): one address accumulating a transition to every chain-opening edge in the corpus would saturate its pool members and the statistic would drown. Instead, chains open through the *down* family — the first child's edge is the parent's climb anchor.

So BEGIN's information **is actually trained and recorded** in the **down** family instead of the **out** family. Every *down* entry is implicitly a BEGIN target: an edge that begins a subtree under its parent (the sentence root is merely the outermost instance). The same relation is addressed from the opposite — and favorable — low-fan-out side: sharded per parent across thousands of addresses instead of concentrated at one — and the decoder recovers the chain-opening probability hop-wise through observation confidence.

### Named entities

Entities get special treatment because they behave like single tokens with internal structure. Entity members carry the entity's **signature** (a content hash), so entity-internal edges are distinct identities — "York" under "New York" is not confused with a generic proper-noun attachment.

An entity's internal membership is trained exactly once, as the members are fixed for each named entity, by definition.

## See also

- [Composites](../concepts/composites.md): encoding sequences and hierarchical states
- [Learner](../concepts/learner.md): encoding transition probabilities
- [LearnerPool](../concepts/learner_pool.md): accommodating the high dynamic range of fan-outs
