# Future directions

## Coarse-to-fine: evidence that pools

Fine-grained edge identities are precise but fragment: most addresses are
seen once, so a *structurally* common transition can be *featurally* novel
and find no evidence at all. The parser therefore also captures each
transition under a **coarse class** — the same edge projected onto just
`{part of speech, relation, headness}` — into coarse address domains within
the same pool.

At decode time the coarse tier is a calibrated **backoff**: only when the
fine read admits nothing is the candidate's coarse class consulted, its
support discounted, with the noise floor as the admission bar and ghosts
still the final fallback. Measured on held-out text, this single tier
recovers a large share of the transitions fine-grained capture misses —
the classic coarse-to-fine idea (Charniak–Johnson; Petrov), rebuilt on
superposition instead of grammars.
