# Associative Index

The **Associative Index** is a semantic index that enables fast similarity-based lookup over stored hypervectors. It is the mechanism that turns a key-value substrate into an associative memory — one where retrieval is by *content similarity*, not by exact content or key match.

## Relationship to Near Neighbor Search

The Associative Index is the backbone of [Near Neighbor Search](near_neighbor_search.md). The NNS selector uses attractors to generate query vectors, probes the index for candidates, and returns results ranked by relevance.
