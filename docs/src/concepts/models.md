# Models

A **Model** defines the sparsity configuration for all hypervectors in a system. It determines the total number of dimensions (width), how those dimensions are divided into segments, and therefore the storage and compute characteristics.

**NOTE**: for simplicity, We will use functions names from Python. However, the counterparts from Go / Rust can be found by consulting their respective references.

## Available Models

| Model | Width | Sparsity Bits | Segment Size | Cardinality (ON bits) |
|-------|-------|---------------|-------------|----------------------|
| `MODEL_64K_8BIT` | 65,536 | 8 | 256 | 256 |
| `MODEL_1M_10BIT` | 1,048,576 | 10 | 1,024 | 1,024 |
| `MODEL_16M_12BIT` | 16,777,216 | 12 | 4,096 | 4,096 |
| `MODEL_256M_14BIT` | 268,435,456 | 14 | 16,384 | 16,384 |
| `MODEL_4G_16BIT` | 4,294,967,296 | 16 | 65,536 | 65,536 |

## Model properties

All model functions take a Model enum value and return the derived property:

| Function | Description |
|----------|-------------|
| `width` | Total dimension count (`2^width_bits`) |
| `sparsity` | Fraction of ON bits (`1 / segment_size`) |
| `cardinality` | Number of ON bits (= number of segments) |
| `segment_size` | Dimensions per segment |

## How to Choose a Model

- **`MODEL_64K_8BIT`**: Fast prototyping, tiny memory footprint. Good for tests and small-scale experiments.
- **`MODEL_1M_10BIT`**: General-purpose, small memory footprint. 
- **`MODEL_16M_12BIT`**: General-purpose, Balances performance and storage.
- **`MODEL_256M_14BIT` / `MODEL_4G_16BIT`**: Very high capacity. Used when the concept space is extremely large.

Larger models provide more orthogonal space (lower collision probability) at the cost of more memory per vector.

Also note that the storage per hypervector estimation only applies to **SparseSegmented** (and a few other types) where we want to store the raw offsets. **Sparkle**, for example, only stores the random seeds (128 bit for now) so that the offsets can be computed on-the-fly during serialization time. Composite types (such as **Set**, **Sequence**) typically contain reference to member **Sparkle** instances, and typically cost much less storage than a **SparseSegmented** instance.