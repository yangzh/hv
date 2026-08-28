# Dependency Parser

Everything in this book so far — Sparkles, composites, learners, pools,
near-neighbor search — was built for a purpose: a demonstration that VSA can offer a unique and novel perspective in cognitive computing / AI.

This chapter serves that purpose: a **dependency parser** in which the entire language model *is* a hypervector substrate.

Unlike traditional NLP with heavy reliance on explicit frequency tables, and unlike neural nets where gradients are computed via backpropagation, our training/inference features:

- A transparent representation of the underlying language models that encourages inspection and powers incremental improvements;
- The language models are generic in the sense that new languages can be added without idiosyncrasy or much tweaking;
- An efficient representation far more compact than existing models, see [Evaluations](evaluations.md);
- An efficient computation with mostly binary operations, no need for floating-point computations or expensive GPUs.

Wernicke’s area in the brain is widely believed to host the generic neural circuitry for language understanding: the solution I hope to present here will be the computational counterpart of it. 

The project is divided into the following pages:

| Section | Description |
|---------|-------------|
| [Introduction](intro.md) | This project at a glance |
| [Training](training.md) | Building language models |
| [Decoding](decoding.md) | Viterbi retrieval under a beam |
| [Evaluations](evaluations.md) | Held-out quality, speed, and footprint |
| [Discussions](discussions.md) | Discussions, improvements, capacity, etc. |
