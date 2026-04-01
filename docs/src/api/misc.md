# Misc

Utility functions that don't belong to a specific type.

## Shortcuts

{{#tabs}}
{{#tab name="Python"}}
```python
hv.d0()       # Default Domain (id=0)
hv.p0()       # Default Pod (seed=0)
```
{{#endtab}}
{{#tab name="Go"}}
```go
hv.D0()       // Default Domain
hv.P0()       // Default Pod
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
Domain::default_domain()  // D0
Pod::default_pod()        // P0
```
{{#endtab}}
{{#endtabs}}

## Hash Utilities

{{#tabs}}
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

## Identity Check

{{#tabs}}
{{#tab name="Python"}}
```python
hv.is_identity(v)   # True if v is an identity vector
```
{{#endtab}}
{{#tab name="Go"}}
```go
hv.IsIdentity(v)    // bool
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
v.is_identity()     // bool
```
{{#endtab}}
{{#endtabs}}

## Serialization

{{#tabs}}
{{#tab name="Python"}}
```python
# HyperBinary → protobuf bytes
msg = hv.to_message(sparkle)

# protobuf bytes → HyperBinary
obj = hv.from_message(msg)

# raw proto bytes → HyperBinary
obj = hv.from_proto_bytes(data)

# proto bytes → YAML string (for debugging)
hv.format_to_yaml(data)
```
{{#endtab}}
{{#tab name="Go"}}
```go
// HyperBinary → proto
pb, err := sparkle.ToProto(ctx)

// YAML formatting
yaml := hv.FormatToYaml(protoMsg)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
// HyperBinary → proto
let pb = sparkle.to_proto();

// proto → HyperBinary
let sparkle = Sparkle::from_proto(&pb)?;
```
{{#endtab}}
{{#endtabs}}

## Frame Analysis

Functions for analyzing sets of hypervectors as geometric frames.

{{#tabs}}
{{#tab name="Python"}}
```python
hv.frame_inner_product(set_a, set_b)  # inner product between two sets
hv.frame_cross(set_a, set_b)          # cross-overlap between sets
hv.frame_correlation(set_a, set_b)    # normalized correlation
hv.frame_cross_noise(set_a, set_b)    # cross-noise level
hv.frame_coefficient(hbs, probe)      # coefficient of probe in set
```
{{#endtab}}
{{#tab name="Go"}}
```go
hv.FrameInnerProduct(hc0, hc1)   // float64
hv.FrameCross(hc0, hc1)          // float64
hv.FrameCorrelation(hc0, hc1)    // float64
hv.FrameCrossNoise(hc0, hc1)     // float64
hv.FrameCoefficient(hc, probe)   // float64
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
frame_inner_product(&set_a, &set_b)   // f64
frame_cross(&set_a, &set_b)           // f64
frame_correlation(&set_a, &set_b)     // f64
frame_cross_noise(&set_a, &set_b)     // f64
frame_coefficient(&hbs, &probe)       // f64
```
{{#endtab}}
{{#endtabs}}
