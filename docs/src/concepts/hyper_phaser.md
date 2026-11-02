# HyperPhaser

A **HyperPhaser** bundles a stream of observations, much like a [Learner](learner.md) does — but it reads each offset as a **phase** rather than as a label, and that one change of interpretation changes its character throughout.

Recall from [Hypervectors](hypervectors.md#sparse-binary-representation) that a sparse-segmented vector is *already* a list of phasors: the offset of the ON bit within its segment is a discretized phase around the unit circle. A Learner treats that offset as an opaque identity and only ever asks whether two of them match. A HyperPhaser takes the phasor reading literally — it superposes unit phasors and keeps the resulting angle.

For segment $s$ of a vector with segment size $W$, an observation contributing offset $o_{sj}$ with weight $w_j$ enters as a unit phasor at angle $\theta_{sj} = 2\pi o_{sj} / W$, and the accumulator holds the complex sum:

$$z_s = \sum_j w_j e^{\mathrm{i}\theta_{sj}}$$

This is **FHRR** — Plate's complex-valued VSA — expressed in the offset representation kongming already uses. The stored offset for segment $s$ is simply $\arg(z_s)$ quantized back onto the ring, so the result is an ordinary sparse-segmented vector that composes under [bind](operators.md) like any other.

## What it estimates

Comparing two phasor bundles estimates the **cosine between the weight vectors underneath them**:

$$\cos(z_A, z_B) \approx \frac{\langle w_A, w_B \rangle}{\|w_A\|_2 \, \|w_B\|_2}$$

The reason is that independent phases cancel on average: the cross terms between unrelated observations vanish, leaving only the mass the two bundles genuinely share. Each segment is one noisy estimate of that quantity, and averaging over $M$ of them tightens the estimate with standard error $\sim 1/\sqrt{M}$.

That single fact sets the expectations. The readout is **scale-free** — re-presenting the same data changes the magnitudes but not the angles, so it does not drift. It is **flat in the number of distinct observations**, because a cosine cares about alignment rather than how many things contributed. And it sharpens with larger $M$, where the extra segments buy *ranking resolution* rather than fidelity: a pairwise comparison is already unbiased at small $M$, but telling the best match from the tenth-best among many thousands of candidates needs the tighter error.

## Accumulating versus sampling

The contrast with a Learner is the useful way to hold this. A Learner is a **sample**: each write draws on randomness to claim a share of a fixed budget of $M$ segments. A HyperPhaser is an **accumulator**: every write adds deterministically into every segment.

| | Learner 💫 | HyperPhaser 🧭 |
|---|---|---|
| write | reservoir sampling, draws randomness | deterministic and linear |
| repeated observation | a fresh draw | identical to one write at double weight |
| a member owning less than $1/M$ | invisible, it won no segments | still moves every segment |
| compared by | Hamming distance | [Lee distance](hypervectors.md#lee-distance-the-graded-alternative) |

Determinism and linearity are what make the small shares survive. Because a Learner is a sample, a member too faint to win a single segment is simply absent from it; because a phasor accumulates, even a tiny weight nudges every angle a little, and the bundle as a whole still carries it.

## Why Lee, and never overlap

Treating offsets as phases changes which [distance measure](hypervectors.md#similarity-and-distance-measure) is meaningful, and this is the sharpest practical consequence of the whole idea.

Two phasors one ring step apart are *maximally similar*, yet they share no exact offset. Overlap and Hamming distance are blind to that: they are binary per segment, so they read those two phasors as no more related than a pair on opposite sides of the circle. **Lee distance** reads the circular gap instead, and on unit phasors it induces the same ranking as the complex cosine, being monotone in the phase gap over the half-period.

So a phasor bundle must be compared by Lee, and must **not** be fed to the overlap-keyed [near-neighbor search](near_neighbor_search.md) — the index would answer at chance. Because the bytes of a phasor vector are indistinguishable from any other sparse-segmented vector's, nothing but its type can carry that warning, which is why the published form gets its own hint rather than borrowing an existing one.

## Two forms, one direction

The accumulator and the thing you store are deliberately separate.

A **HyperPhaser** is the trainable form: a dense complex accumulator holding $M$ components, each with an angle *and* a magnitude. It is not itself a hypervector and has no wire format. The magnitude matters while training — it is a per-segment **confidence**, recording how much the contributing phases reinforced or cancelled there, and a segment whose phases nearly cancelled holds an angle decided by rounding residuals rather than by evidence. It also behaves as per-segment plasticity.

**Phasers** is the published form: one quantized angle per segment, the same size and packing as any other sparse-segmented vector. Exporting crosses from one to the other, **one way** and keeping angles only — so the per-segment confidences live on the accumulator, and a caller who wants them keeps them alongside deliberately.

Jump to the API reference for [HyperPhaser & Phasers](../api/hv/phasers.md).
