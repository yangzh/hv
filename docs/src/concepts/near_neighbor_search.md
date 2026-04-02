# Near Neighbor Search

**Near Neighbor Search (NNS)** generally retrieves chunks from the storage substrate in the increasing order of Hamming distance (from a query).

As we mentioned [earlier](hypervectors.md#similarity-and-distance-measure), this is equivalent to a strictly descreasing order of overlap (between query and candidate). If overlap encodes the semantic relevance, this translates to a list of semantically similar candidates. It leverages the [Associative Index](#associative-index) for efficient recovery of candidates.

## Attractors

Each attractor conceptually provides "the center of attraction" for candidates: the NNS accepts one or more attractors.

| Attractor | Query | Attracts |
|-----------|-------|-------|
| **SetMembersAttractor** | Releases SET_MARKER from a Set | All members of the Set |
| **SequenceMemberAttractor** | Releases with SEQUENCE_MARKER + positional marker | Sequence member at a specific position |
| **TentacleAttractor** | Release with key | Octopus value for a given key |
| **SetAttractor** | Binds member with SET_MARKER | All Sets that contain a given member |
| **SequenceAttractor** | Binds member with SEQUENCE_MARKER + position | All Sequences containing a member at a specific position |
| **OctopusAttractor** | Binds value with key | Octopuses with a key-value pair |
| **AnalogicalReasoner** | Binds with feature and inverse source | Analogical counterparts |

### Forward vs. Reverse Attractors

- **Forward attractors** (SetMembers, SequenceMember, Tentacle): given a composite, find its parts
- **Reverse attractors** (Set, Sequence, Octopus): given a part, find composites containing it
- **Analogical**: given "A is to B as C is to ?", find "?"

## Example: Analogical Reasoning

Given the analogy "king is to queen as man is to ?":

```
king   = Sparkle("role", "king")
queen  = Sparkle("role", "queen")
man    = Sparkle("role", "man")

// The attractor computes: man ⊗ queen ⊗ king⁻¹
// This produces a code that should overlap with "woman"
NearNeighborSearch(
    attractors = [AnalogicalReasoner(source=king, feature=queen, target=man)]
)
```

The attractor binds the target with the relationship (feature $\otimes$ source$^{-1}$), producing a code that — by the algebra of hypervectors — will have high overlap with the analogical answer.

## Performance

This NNS module has a constant time complexity, with help from [Associative Index](associative_index.md). The secret sauce is the efficient random-access to underlying index.

## Accuracy

Unlike approximate nearest neighbor methods (LSH, HNSW, etc.), this NNS module can computes **exact** overlap counts via the associative index. There is no approximation error and no index-specific parameters to tune.

## Associative Index

The **Associative Index** is a semantic index that enables fast similarity-based lookup over stored hypervectors. Conceptually it turns a key-value substrate (item memory) into an associative memory — one where retrieval is by *content similarity*, not by exact content or key match.
