# Notebook Quick Start

This guide walks through using Kongming HV in a Jupyter notebook, cell by cell.

| Section | Description |
|---------|-------------|
| [Notebook Platforms](platforms.md) | Setup differences between Jupyter, Colab, and Binder |
| [Interactive Notebooks](notebooks.md) | Links to existing notebooks |
| [Walkthrough](walkthrough.md) | Step-by-step: vocabulary, similarity, learning, binding |

## Tips

- **Reproducibility**: Use fixed seeds in `SparseOperation` for deterministic results across reruns.
- **Visualization**: Use `pandas` DataFrames for overlap matrices — they render nicely in Jupyter.
- **Performance**: The Rust backend is fast. Building 10,000 vectors takes under a second on `MODEL_64K_8BIT`.
- **Model choice**: Start with `MODEL_64K_8BIT` for exploration. Switch to `MODEL_1M_10BIT` or larger for production workloads.
