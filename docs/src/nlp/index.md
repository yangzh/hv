# Language Parser

Everything in this book so far: Sparkles, composites, Learners, pools,
near-neighbor search, was built for a purpose: a demostration that the VSA can offer an unique and novel perspective in cognitive computing / AI.

This chapter serves that purpose: a **dependency parser** in which the entire language model *is* a hypervector substrate.

Unlike traditional NLP, there are no weight matrices. Unlike neural nets, there are no gradients and back propagation. Training is a single pass of training corpus, and parsing is associative retrieval under a beam.

What it is:
- A transparent representation for the underlying language models that encourages inspections and enables incremental improvements;
- An efficient representation that is roughly more than 10x compact than existing models;
- An efficient computation with mostly binary operations, no need for complex float-point computations and expensive GPUs;
- A truly language-agnostic solution: new languages can be added without much idiosyncrasy and tweaks, like a generic neural circuitry, or some sorts of meta-language.

| Section | Description |
|---------|-------------|
| [Background](background.md) | Where this sits: parsing, VSA, and prior art |
| [Introduction](intro.md) | The parser at a glance |
| [Training](training.md) | Training as capture — the out/down/obs pool families |
| [Decoding](decoding.md) | Retrieval under a beam — climb, graft, ghosts, Viterbi |
| [Discussions](discussions.md) | Why this shape — superposition capacity, determinism, unified storage |
| [Future directions](future.md) | Coarse-to-fine evidence pooling, and beyond |
