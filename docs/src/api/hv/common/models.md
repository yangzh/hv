# Models

See [Concepts: Models](../../../concepts/models.md) for the full overview.

## Model Enum

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
model = hv.MODEL_64K_8BIT
model = hv.MODEL_1M_10BIT
model = hv.MODEL_16M_12BIT
model = hv.MODEL_256M_14BIT
model = hv.MODEL_4G_16BIT
```
{{#endtab}}
{{#tab name="Go"}}
```go
model := api.Model_MODEL_64K_8BIT
model := api.Model_MODEL_1M_10BIT
model := api.Model_MODEL_16M_12BIT
model := api.Model_MODEL_256M_14BIT
model := api.Model_MODEL_4G_16BIT
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let model = Model::Model64k8bit;
let model = Model::Model1m10bit;
let model = Model::Model16m12bit;
let model = Model::Model256m14bit;
let model = Model::Model4g16bit;
```
{{#endtab}}
{{#endtabs}}

## Model Functions

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
hv.width(model)           # total dimensions
hv.cardinality(model)     # ON bit count
hv.sparsity(model)        # sparsity ratio
hv.segment_size(model)    # dimensions per segment
hv.segment_mask(model)    # bitmask for in-segment offset
hv.width_bits(model)      # log2(width)
hv.sparsity_bits(model)   # log2(segment_size)
```
{{#endtab}}
{{#tab name="Go"}}
```go
hv.Width(model)           // uint32
hv.Cardinality(model)     // uint32
hv.Sparsity(model)        // float64
hv.SegmentSize(model)     // uint32
hv.SegmentMask(model)     // uint32
hv.WidthBits(model)       // uint8
hv.SparsityBits(model)    // uint8
hv.OffsetsTotalByte(model)// uint32
hv.RandomOverlap(model)   // uint32
hv.ThresNoise(model)      // uint32
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
model.width()             // u32
model.cardinality()       // u32
model.sparsity()          // f64
model.segment_size()      // u32
model.segment_mask()      // u32
model.width_bits()        // u8
model.sparsity_bits()     // u8
model.offsets_total_byte() // u32
model.random_overlap()    // u32
model.thres_noise()       // u32
model.to_segment_offset(idx) // (u32, u32)
model.from_segment_offset(seg, offset) // u32
```
{{#endtab}}
{{#endtabs}}

See also: [SparseOperation](sparse_operation.md) — Model + seeded RNG for deterministic vector generation.
