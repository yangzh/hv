# Models

See [Concepts: Models](../../../concepts/models.md) for the full overview.

## Model Enum

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
model0 = hv.MODEL_64K_8BIT

model1 = hv.MODEL_1M_10BIT
```
{{#endtab}}
{{#tab name="Go"}}
```go
model0 := api.Model_MODEL_64K_8BIT

model1 := api.Model_MODEL_1M_10BIT
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let model0 = Model::Model64k8bit;

let model1 = Model::Model1m10bit;
```
{{#endtab}}
{{#endtabs}}

## Model Functions

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
hv.width(hv.MODEL_1M_10BIT)           # total dimensions
hv.cardinality(hv.MODEL_1M_10BIT)     # ON bit count
hv.sparsity(hv.MODEL_1M_10BIT)        # sparsity
hv.segment_size(hv.MODEL_1M_10BIT)    # dimensions per segment
```
{{#endtab}}
{{#tab name="Go"}}
```go
hv.Width(hv.MODEL_1M_10BIT)           // total dimensions
hv.Cardinality(hv.MODEL_1M_10BIT)     // ON bit count
hv.Sparsity(hv.MODEL_1M_10BIT)        // sparsity
hv.SegmentSize(hv.MODEL_1M_10BIT)     // dimensions per segment
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let model = Model::Model1m10bit;
model.width()             // total dimensions
model.cardinality()       // ON bit count
model.sparsity()          // sparsity
model.segment_size()      // dimensions per segment
```
{{#endtab}}
{{#endtabs}}

See also: [SparseOperation](sparse_operation.md) — Model + seeded RNG for deterministic vector generation.
