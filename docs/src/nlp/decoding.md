# Decoding: retrieval under a beam

Parsing inverts the capture. Tokens arrive one at a time, and a Viterbi
beam carries the best partial parses:

1. **Climb** — the incoming word's text anchors into the *obs* family, then
   climbs the *down* family hop by hop, reconstructing candidate spines
   (leaf up to a plausible ancestor). Each hop is an access-circle read.
2. **Graft** — each candidate spine may attach to each beam state at any
   layer of its spine. Admission is evidence: the *out* pool's `support`
   for "this edge follows that one." Grafting low also closes every level
   above the graft point, each paying its measured probability of ending
   (the `END` statistics captured during training).
3. **Ghosts** — when no real observation admits (an unseen word, a typo),
   the beam consults the leaf's *out* predictions and proposes the likely
   next edges as placeholders, priced at the noise floor.
4. **Select** — classic Viterbi: score = previous score × transition
   support × observation strength; keep the top-K states; backtrace at the
   end of the sentence and reassemble the winning spines into a tree.

Every decision along the way is an overlap count you can print and inspect
— the parser has no opaque layers.
