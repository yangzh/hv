Each attractor conceptually provides "the center of attraction" for candidates: the NNS accepts one or more attractors, to perform the actual near-neighor search work, by interacting with underlying associative index.

Implementation-wise, attrctors are specialized selectors.

# Forward attractors

| Attractor | Query | Attracts |
|-----------|-------|-------|
| **SetMembersAttractor** | Releases SET_MARKER from a Set | All members of the Set |
| **SequenceMemberAttractor** | Releases with SEQUENCE_MARKER + positional marker | Sequence member at a specific position |
| **TentacleAttractor** | Release with key | Octopus value for a given key |

Roughly forward attractors try to find parts from a given a composite.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
memory.set_members(memory.by_item_key("sets", "my_set"))
memory.sequence_member(memory.by_item_key("seqs", "my_seq"), pos=2)
memory.tentacle(memory.by_item_key("records", "person"), key="name")
```
{{#endtab}}
{{#endtabs}}

# Reverse Attractors

| Attractor | Query | Attracts |
|-----------|-------|-------|
| **SetAttractor** | Binds member with SET_MARKER | All Sets that contain a given member |
| **SequenceAttractor** | Binds member with SEQUENCE_MARKER + position | All Sequences containing a member at a specific position |
| **OctopusAttractor** | Binds value with key | Octopuses with a key-value pair |

Roughly reverse attractors try to locate composites given a part.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
memory.set_attractor(memory.by_item_key("animals", "cat"), "sets")
memory.sequence_attractor(memory.by_item_key("animals", "cat"), pos=0, domain="seqs")
memory.octopus_attractor(key="color", value=memory.by_item_key("colors", "red"))
```
{{#endtab}}
{{#endtabs}}

# Analogical Reasoner

Analogical reasoner tries to perform analogical reasoning, like "A is to B as C is to ?".


Given the analogy "king is to queen as man is to ?"

{{#tabs global="lang"}}
{{#tab name="Python"}}
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
{{#endtab}}
{{#endtabs}}
