# Near Neighbor Search

**Near Neighbor Search (NNS)** retrieves chunks from the storage substrate in increasing order of Hamming distance (from a query).

As we mentioned [earlier](hypervectors.md#similarity-and-distance-measure), this is equivalent to strictly descending overlap (between query and candidate). Overlap generally encodes semantic relevance, and this translates to a list of semantically relevant candidates, from most relevant to random chance.

This NNS module has linear time complexity (with respect to the entry count indexed) with a very low constant — in expectation only a few tally operations per stored entry — so query cost grows gently with the number of entries in the storage substrate.

It leverages an underlying Associative Index for efficient recovery of candidates. The **Associative Index** is a semantic index that enables fast similarity-based lookup over stored hypervectors. Conceptually it turns a key-value substrate into an associative memory — one where retrieval is by *content similarity*, not by exact content or key match. 

Unlike approximate nearest neighbor methods (LSH, HNSW, etc.), the choice of sparse and binary hypervectors makes this exact and efficient. The NNS module computes **exact** overlap counts via the associative index. There is no approximation error and no index-specific parameters to tune.

Jump to the API reference for [Near-Neighbor Search](../api/memory/selectors/near_neighbor.md).