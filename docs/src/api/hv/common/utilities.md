# Utilities

## Similarity

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
hv.overlap(a, b)        # Overlap: segments where the two agree, 0..M

hv.hamming(a, b)        # Hamming distance: 2 * (M - overlap), 0..2M

hv.lee_distance(a, b)   # Lee distance: mean circular gap, 0..W/2

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
| `Phasers` | **never** — raises, two phasors one step apart share no offset yet are nearly identical | **yes** — it is the native metric |

Lee is reported **per segment**: the sum divided by `M`. That keeps it
comparable across models — chance is `W/4` and the diameter `W/2` whatever `M`
is. Two consequences worth knowing:

- shifting *every* offset by one is Lee `1`, but the full Hamming diameter `2M`;
- the division truncates, so a gap confined to a handful of segments reads `0`.
  The resolution is one ring step, which suits a population readout and not the
  separation of near-identical vectors.

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
