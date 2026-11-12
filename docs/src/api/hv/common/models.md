# Models

A model is named for its segment size in bits: `MODEL_8BIT` divides the space into
segments of 256 offsets, and carries 256 of them. The binary width follows from that
one number (65,536 here) and is deliberately not part of the name — it describes the
binary form alone, and says nothing about a [HyperPhaser](../hyper_phaser.md) over the
same model.

See [Concepts: Hypervectors](../../../concepts/hypervectors.md#model-properties) for the full overview.

## Model Enum

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
model0 = hv.MODEL_8BIT

model1 = hv.MODEL_10BIT
```
{{#endtab}}
{{#endtabs}}

## Model Functions

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
hv.width(hv.MODEL_10BIT)           # total dimensions
hv.cardinality(hv.MODEL_10BIT)     # ON bit count
hv.sparsity(hv.MODEL_10BIT)        # sparsity
hv.segment_size(hv.MODEL_10BIT)    # dimensions per segment
```
{{#endtab}}
{{#endtabs}}

See also: [SparseOperation](sparse_operation.md) — Model + seeded RNG for deterministic vector generation.
