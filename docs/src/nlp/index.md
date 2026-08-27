# Dependency Parser

Everything in this book so far — Sparkles, composites, learners, pools,
near-neighbor search — was built for a purpose: a demonstration that VSA can offer a unique and novel perspective in cognitive computing / AI.

This chapter serves that purpose: a **dependency parser** in which the entire language model *is* a hypervector substrate.

Unlike traditional NLP where explicit frequency tables are stored, and unlike neural nets where gradients are computed via backpropagation, our training is performed in a single pass, and parsing is associative retrieval under a beam.

What it is:
- A transparent representation of the underlying language models that encourages inspection and powers incremental improvements;
- Furthermore, the language model is generic, in the sense that new languages can be added without much idiosyncrasy or tweaks;
- An efficient representation far more compact than existing models;
- An efficient computation with mostly binary operations, no need for floating-point computations or expensive GPUs.

Wernicke’s area in the brain is widely believed to be the generic neural circuitry for language understanding. The solution I hope to present here is the computational counterpart. 

The project is divided into the following pages:

| Section | Description |
|---------|-------------|
| [Introduction](intro.md) | This project at a glance |
| [Training](training.md) | Building language models |
| [Decoding](decoding.md) | Viterbi retrieval under a beam |
| [Evaluations](evaluations.md) | Held-out quality, ablations, footprint |
| [Discussions](discussions.md) | Discussions, improvements, capacity, etc. |
