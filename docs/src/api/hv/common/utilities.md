# Utilities

## Similarity

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
hv.overlap(a, b)    # Overlap

hv.hamming(a, b)    # Hamming distance

hv.equal(a, b)      # Equality check
```
{{#endtab}}
{{#endtabs}}

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
