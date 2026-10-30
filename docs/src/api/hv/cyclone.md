# Cyclone 🌀

A **periodic** hypervector: raising it to its own period gives back the
identity.

$$P^{\,\text{period}} = I$$

That makes it the natural carrier for anything cyclic — a phase of the day, a
position within a repeating window, a step in a loop — where you want position
$k$ and position $k + \text{period}$ to be the *same* vector rather than merely
similar.

## How it works

`power` scales every offset, and a Cyclone is built so that every offset is a
multiple of

$$b = \frac{W}{\text{period}}$$

for segment size $W$. Raising to the `period` therefore sends each offset to a
multiple of $W$, which is $0$ on the ring — the identity, exactly and for every
segment at once.

This is also why the period must **divide** the segment size: otherwise no such
$b$ exists and the constructor refuses with `impossible periodic vector`.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# W = 1024 for the 1M/10-bit model, so the period must divide 1024.
c = hv.Cyclone(model, hv.Seed128(hv.Domain("clock"), hv.Pod("hour")), 64)

c.period()      # 64

hv.Cyclone(model, seed, 100)   # ValueError: impossible periodic vector
```
{{#endtab}}
{{#endtabs}}

## The defining property

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
hv.is_identity(c.power(64, 1))    # True  — a full turn
hv.is_identity(c.power(32, 1))    # False — half a turn is not
```
{{#endtab}}
{{#endtabs}}

Powers below the period are distinct vectors, so `c.power(k, 1)` enumerates
`period` positions around the cycle before returning to where it started.

## Seeded versus default

The seed decides the *shape*, not the period:

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# A real seed: offsets are random multiples of b.
c = hv.Cyclone(model, hv.Seed128(hv.Domain("clock"), hv.Pod("hour")), 64)

# The default (zero) seed: a characteristic SAWTOOTH, offset = b * segment.
c = hv.Cyclone(model, hv.Seed128(hv.d0(), hv.p0()), 64)
list(c.core().offsets())[:6]      # [0, 16, 32, 48, 64, 80]
```
{{#endtab}}
{{#endtabs}}

Use a real seed for anything you want orthogonal to other cyclones. The
sawtooth is deterministic and shared by every default-seeded Cyclone of the same
model and period, which makes it useful for tests and visualization and
unsuitable as a distinct identity.

## See also

- [Operators](operators.md) — `power`, which is what the periodicity rests on.
- [Sequence 📿](sequence.md) — for ordered, non-repeating structure.
