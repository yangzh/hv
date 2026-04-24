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
{{#tab name="Go"}}
```go
seq := hv.NewSequence(hv.NewSeed128(0, 42), 1, first, second, third)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let seq = Sequence::new(Seed128::new(0, 42), 1, members);
```
{{#endtab}}
{{#endtabs}}

## In-place edits: Append / Prepend / Reset

`Append`, `Prepend`, and `Reset` all **mutate the Sequence in place** —
clone first if you need to preserve the original.

- `Append(more...)` — add members at the end. `start` is unchanged.
- `Prepend(more...)` — add members at the front; `start` decrements by
  `len(more)` so existing members keep their positional binding.
- `Reset(start)` — shift the starting index. No-op when `start` equals
  the current start.

After any of these, `seq` equals what you'd get by building a fresh
`NewSequence(seed, new_start, all_members...)` — the domain/pod seed is
preserved.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
import copy

seq = hv.Sequence(hv.Seed128(0, 42), a, b, c)

# Append / Prepend are variadic and mutate in place.
seq.append(d, e)            # seq now [a, b, c, d, e]
seq.prepend(x, y)           # seq now [x, y, a, b, c, d, e], start -= 2
seq.reset(10)               # shift the starting index to 10

# To preserve the original, clone first:
base = hv.Sequence(hv.Seed128(0, 42), a, b, c)
s1 = copy.copy(base)
s1.append(d)                # base is untouched
```
{{#endtab}}
{{#tab name="Go"}}
```go
seq := hv.NewSequence(hv.NewSeed128(0, 42), 0, a, b, c)

seq.Append(d, e)            // seq now [a, b, c, d, e]
seq.Prepend(x, y)           // seq now [x, y, a, b, c, d, e], start -= 2
seq.Reset(10)               // shift the starting index to 10

// To preserve the original, clone first (Clone returns HyperBinary):
base := hv.NewSequence(hv.NewSeed128(0, 42), 0, a, b, c)
s1 := base.Clone().(hv.Sequence)
s1.Append(d)                // base is untouched
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let mut seq = Sequence::new(Seed128::new(0, 42), 0, vec![a, b, c]);

seq.append(vec![d, e]);      // seq now [a, b, c, d, e]
seq.prepend(vec![x, y]);     // seq now [x, y, a, b, c, d, e], start -= 2
seq.reset(10);               // shift the starting index to 10

// To preserve the original, clone first:
let base = Sequence::new(Seed128::new(0, 42), 0, vec![a, b, c]);
let mut s1 = base.clone();
s1.append(vec![d]);          // base is untouched
```
{{#endtab}}
{{#endtabs}}
