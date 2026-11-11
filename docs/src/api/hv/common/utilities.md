# Utilities

## Similarity

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
hv.overlap(a, b)        # Overlap: segments where the two agree, 0..M

hv.hamming(a, b)        # Hamming distance: 2 * (M - overlap), 0..2M

hv.lee_distance(a, b)   # Lee distance: mean circular gap, 0..W/2

hv.alignment(a, b)      # Cosine similarity in angle space, -1..1

hv.equal(a, b)          # Equality check
```
{{#endtab}}
{{#endtabs}}

`overlap` and `hamming` carry the same information. A disagreeing segment flips
two bits — one off, one on — so `hamming == 2 * (M - overlap)` exactly, and
`overlap == M - hamming // 2` back. Reach for whichever reads better; neither
is more precise than the other.

`lee_distance` is the graded one, and it answers a different question.
Where Hamming asks only *whether* two segments disagree, Lee asks how far apart their
offsets sit on the ring of `W` positions. That matters only where an offset
carries an **ordinal** meaning:

| | use Hamming/overlap | use Lee |
|---|---|---|
| `Sparkle`, `Learner`, composites | **yes** — offsets are unrelated random draws, so "how far" is noise | no |
| `Point` (fractional-power encoding) | yes, but it collapses to noise as positions separate | **yes** — graded in the coordinate gap |
| a `HyperPhaser.quantize()` result | **no** — two phasors one step apart share no offset yet are nearly identical | **yes** — the offsets are phases |

Lee is reported **per segment**: the sum divided by `M`. That keeps it
comparable across models — chance is `W/4` and the diameter `W/2` whatever `M`
is. Two consequences worth knowing:

- shifting *every* offset by one is Lee `1`, but the full Hamming diameter `2M`;
- the division truncates, so a gap confined to a handful of segments reads `0`.
  The resolution is one ring step, which suits a population readout and not the
  separation of near-identical vectors.

`alignment` reads the same ring gap as Lee and aggregates it the other way —
cosines rather than angles:

$$\text{alignment}(x, y) = \frac{1}{M} \sum_i \text{Re}\big(\chi(x_i)\,
\overline{\chi(y_i)}\big), \qquad \chi(o) = e^{2\pi i o / W}$$

It is **cosine similarity exactly**: every segment contributes a unit phasor, so $\|x\| = \|y\| = \sqrt{M}$ and the $1/M$ is precisely the normalization $1/(\|x\|\|y\|)$. From there, `1 - alignment` is cosine distance (not a metric) and $\arccos(\text{alignment})/\pi$ is the angular distance (which is). Use it when the natural answer is an inner product rather than a distance; `lee_distance` stays the integer metric.

Being a mean of cosines rather than a mean of angles, it does not determine Lee
and Lee does not determine it — the two can order a pair differently, and
neither is wrong.

## Identity Check

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
v=hv.Sparkle.identity(model)

hv.is_identity(v)   # True if v is an identity vector
```
{{#endtab}}
{{#endtabs}}

## Hash Utilities

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
hv.hash64_from_string("hello")   # deterministic u64 hash from string
hv.hash64_from_bytes(b"\x01\x02") # deterministic u64 hash from bytes
hv.curr_time_as_seed()            # current time as a u64 seed
hv.kongming_studio_seed()         # fixed studio seed constant
```
{{#endtab}}
{{#endtabs}}
