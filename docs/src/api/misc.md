# Misc

## HyperBinary Interface

All vector types (SparseSegmented, Sparkle, Set, Sequence, Octopus, Knot, Parcel, Cyclone, Learner) conform to a common interface. In Go this is the `HyperBinary` interface; in Rust it is the `HyperBinary` trait. The two implementations are kept at **feature parity**.

{{#tabs}}
{{#tab name="Go"}}
```go
type HyperBinary interface {
    Model() api.Model
    Width() uint32
    Cardinality() uint32
    Hint() api.HyperBinaryProto_Hint
    StableHash() uint64
    Core() SparseSegmented
    Domain() Domain
    Pod() Pod
    Exponent() int32
    Power(p int32) HyperBinary
    Clone() HyperBinary

    // Display: String() returns compact emoji form;
    // Repr() returns detailed YAML/proto form.
    // Both are part of the interface in Go.
    fmt.Stringer
    Repr() string

    // Serialization is part of the interface in Go.
    ToProto(ctx context.Context) (*api.HyperBinaryProto, error)
}
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
pub trait HyperBinary: std::fmt::Display {
    fn model(&self) -> Model;
    fn width(&self) -> u32;
    fn cardinality(&self) -> u32;
    fn hint(&self) -> HyperBinaryHint;
    fn stable_hash(&self) -> u64;
    fn core(&self) -> SparseSegmented;
    fn domain(&self) -> &Domain;
    fn pod(&self) -> &Pod;
    fn exponent(&self) -> i32;
    fn power(&self, p: i32) -> HyperBinaryKind;
    fn clone_hb(&self) -> HyperBinaryKind;

    // Display: via the std::fmt::Display supertrait (shown above).
    // No separate Repr(); use Debug derive or per-type formatting.

    // Serialization: to_proto() / from_proto() are inherent methods
    // on each concrete type, not part of the trait.
}
```

In Rust, concrete types are wrapped in `HyperBinaryKind` (an enum) for dynamic dispatch instead of Go's interface boxing.
{{#endtab}}
{{#endtabs}}

In Python, there is no explicit interface — all types expose the same methods (`model()`, `stable_hash()`, `core()`, `power()`, etc.) by convention.

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
