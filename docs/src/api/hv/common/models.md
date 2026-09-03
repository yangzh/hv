# Models

See [Concepts: Hypervectors](../../../concepts/hypervectors.md#model-properties) for the full overview.

## Model Enum

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
model0 = hv.MODEL_64K_8BIT

model1 = hv.MODEL_1M_10BIT
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
{{#endtabs}}

See also: [SparseOperation](sparse_operation.md) — Model + seeded RNG for deterministic vector generation.
