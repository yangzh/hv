# Sequence 📿

An ordered collection of hypervectors with positional encoding. See [Composites: Sequence](../../concepts/composites.md#sequence) for the conceptual overview.

## Constructor

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Constructing a sequence, with logical index start at 1 (default to 0).
seq = hv.Sequence(hv.Seed128(0, 42), first, second, third, start=1)
```
{{#endtab}}
{{#endtabs}}

## Derived Sequences: Append / Prepend / Reset

`Append`, `Prepend`, and `Reset` all **return a new Sequence** — a
Sequence is an immutable value, so the receiver is never changed.

- `Append(more...)` — members added at the end. `start` is unchanged.
- `Prepend(more...)` — members added at the front; `start` decrements by
  `len(more)` so existing members keep their positional binding.
- `Reset(start)` — shift the starting index. Returns an equal Sequence
  when `start` equals the current start.

The result equals what you'd get by building a fresh
`NewSequence(seed, new_start, all_members...)` — the domain/pod seed is
preserved.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
seq = hv.Sequence(hv.Seed128(0, 42), a, b, c)

# Append / Prepend are variadic and return new Sequences.
s1 = seq.append(d, e)       # [a, b, c, d, e]; seq unchanged
s2 = seq.prepend(x, y)      # [x, y, a, b, c], start -= 2; seq unchanged
s3 = seq.reset(10)          # starting index 10; seq unchanged
```
{{#endtab}}
{{#endtabs}}
