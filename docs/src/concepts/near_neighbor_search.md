# Near Neighbor Search

**Near Neighbor Search (NNS)** generally retrieves chunks from the storage substrate in the increasing order of Hamming distance (from a query).

As we mentioned [earlier](hypervectors.md#similarity-and-distance-measure), this is equivalent to a strictly descreasing order of overlap (between query and candidate). If overlap encodes the semantic relevance, this translates to a list of semantically similar candidates. It leverages an underlying Associative Index for efficient recovery of candidates.

The **Associative Index** is a semantic index that enables fast similarity-based lookup over stored hypervectors. Conceptually it turns a key-value substrate (item memory) into an associative memory — one where retrieval is by *content similarity*, not by exact content or key match.

Unlike approximate nearest neighbor methods (LSH, HNSW, etc.), the NNS module can computes **exact** overlap counts via the associative index. There is no approximation error and no index-specific parameters to tune.

This NNS module has a constant time complexity, with help from associative index. The secret sauce is the efficient random-access to underlying index.

Jump to API reference for Near-Neighbor Search [here](../api/memory/selectors/near_neighbor.md).