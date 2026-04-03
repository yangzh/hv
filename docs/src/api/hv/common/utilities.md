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
{{#tab name="Go"}}
```go
hv.Overlap(a, b)         // Overlap

hv.Hamming(a, b)         // Hamming distance

hv.Equal(a, b)           // Equality check
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
overlap(&a.core(), &b.core())   // Overlap

hamming(&a.core(), &b.core())   // Hamming distance
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
{{#tab name="Go"}}
```go
v := hv.NewSparkleIdentity(model)

hv.IsIdentity(v)    // True if v is an identity vector
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
v.is_identity()     // True if v is an identity vector
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
{{#tab name="Go"}}
```go
hv.Hash64FromString("hello")     // uint64
hv.Hash64FromBytes(raw)          // uint64
hv.Hash64FromMessage(protoMsg)   // uint64 — hash from protobuf message
hv.CurrTimeAsSeed()              // uint64
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
hash64_from_string("hello")      // u64
hash64_from_bytes(&raw)          // u64
curr_time_as_seed()              // u64
KONGMING_STUDIO_SEED             // u64
```
{{#endtab}}
{{#endtabs}}
