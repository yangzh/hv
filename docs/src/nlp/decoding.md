# Decoding

Decoding inverts training: tokens arrive one at a time, and the linguistic parser must recover the most likely sequence of states that could have emitted them, then convert that sequence back into a dependency tree. The engine is a Viterbi beam over the hierarchical state space, and this page walks one token's journey through each step.

## What the decoder carries

Between tokens, the decoder maintains a **beam**: the $K$ best hypotheses so far. Each surviving state itself is a spine, the hierarchical path of the *previous* token, plus its accumulated Viterbi score $\alpha$. True to form, the beam slice itself is stored as a superposition of all surviving state vectors, weighted by their confidence, plus a parallel bundle of **backpointers** recording where each state came from.

At the start of a sentence the beam holds a single seed state anchored at
`BEGIN`, and each primed language contributes its own seed — the beam
arbitrates between languages on evidence alone, with no explicit language switch anywhere in the engine: we have a natural way to handle multi-lingual tokens.

## Decoding cycle

### 1. Start as a candidate leaf

The surface text is hashed into its observation identity, and the *obs*
family answers: *which leaf edges may have emitted/realized this word?* Each answer is a candidate leaf, already weighted by observation frequency.

### 2. Climb

From each candidate leaf, the decoder climbs the *down* family: each hop
reads "whose child is this edge?" and yields the plausible parents, again
frequency-weighted. The result is a set of extended **candidate spines**, each carrying a joint observation confidence.

### 3. Graft and score

Each candidate spine may attach to each beam state at any layer of that state's spine. For every (prev_state, layer, candidate) triple, admission is a single question to the *out* family: *does the candidate's top edge follow the prev_state's edge at this layer?* The answer becomes the transition confidence. Two structural rules apply:

- **The root gate.** Layer zero hosts only root edges; a mid-tree edge
  proposing itself as a new root is structurally illegal and is dropped
  without a read. Genuine root openings get a uniform prior instead — this is the flip side of `BEGIN` being untrained (see
  [Training](training.md#the-sentinels-begin-and-end)).
- **The conclusion discount.** Grafting at layer L implicitly closes every existing layer below L: each close-pending level pays its *measured* END cost. An expected closing costs almost nothing, a surprising one costs considerably more. This is how the decoder balances "attach deep, continue the phrase" against "attach high, close the clause" with statistics instead of heuristics.

The candidate's score is then the classic Viterbi:

$$ \alpha = \alpha_{prev} \times P_{transition} \times P_{observation}$$ 

### 4. Ghosts

If *no* real placement survived anywhere in the beam — an out-of-vocabulary word, or a simple typo — the decoder asks each beam state's leaf edge for its *predictions* without observations. The best few become **ghost** candidates, priced at the noise floor, participating in continuing the beam.

One guard applies: a ghost is purely prediction, not an observation, so any named-entity claim it carries is checked against the actual input text and stripped on mismatch — no phantom entities.

### 5. Select

All admitted hypotheses, real and ghost, are ranked together by $\alpha$ and only the top $K$ survive. The new states are bundled with their backpointers and the cycle begins.

## Backtrace

When the sentence ends, the best-scoring endpoint is unwound through the
backpointers, recovering the winning state sequence: one spine per token, in order. This is the Viterbi answer: the most likely path through
the state space, given everything observed so far.

### Reassembly

The spine sequence is folded back into a dependency tree: tokens are bucketed by their parent edge, the `is_head` marker identifies exactly the head member of each subtree, to which all other members attach. Along the way each token's lemma is recovered from its trained token record, and entity spans are re-emitted from the carried annotations. The output is the same artifact the teacher produced: a full dependency parse.

## Properties worth noticing

- **Streaming:** one token in, one beam update; the carried state (of the decoder) is the superposition of surviving hypotheses, fixed size regardless of sentence length and hypothesis count.
- **Inspectable:** every admission, discount, and ranking above is an integer you can print: there is no layer of the decision you cannot open.

## See also

- [LearnerPool](../concepts/learner_pool.md) — the access-circle reads under every step.
