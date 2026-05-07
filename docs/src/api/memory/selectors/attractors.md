Each attractor conceptually provides "the center of attraction" for candidates: the NNS accepts one or more attractors, to perform the actual near-neighbor search work, by interacting with underlying associative index.

Implementation-wise, attractors are specialized selectors.

# Forward attractors

Roughly forward attractors try to find parts from a given a composite.

| Attractor | Query | Attracts |
|-----------|-------|-------|
| **SetMembersAttractor** | Releases SET_MARKER from a Set | All members of the Set |
| **SequenceMemberAttractor** | Releases with SEQUENCE_MARKER + positional marker | Sequence member at a specific position |
| **TentacleAttractor** | Release with key | Octopus value for a given key |

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

Roughly reverse attractors try to locate composites given a part.

| Attractor | Query | Attracts |
|-----------|-------|-------|
| **SetAttractor** | Binds member with SET_MARKER | All Sets that contain a given member |
| **SequenceAttractor** | Binds member with SEQUENCE_MARKER + position | All Sequences containing the given member at a specific position |
| **OctopusAttractor** | Binds value with key | Octopuses with a given key-value pair |

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
memory.set_attractor(memory.by_item_key("animals", "cat"), domain="sets")

memory.sequence_attractor(memory.by_item_key("animals", "cat"), pos=0, domain="seqs")

# NOTE the value is specified with another selector.
memory.octopus_attractor(key="color", value=memory.by_item_key("colors", "red"))
```
{{#endtab}}
{{#endtabs}}

# Analogical Reasoner

Analogical reasoner tries to perform analogical reasoning, like "A is to B as C is to ?".


Given the analogy "king is to queen as man is to ?"

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
king   = hv.Sparkle(model, "role", "king")
queen  = hv.Sparkle(model, "role", "queen")
man    = hv.Sparkle(model, "role", "man")

# Analogy: "king is to queen as man is to ?"
#   src     = king   (the known source of the relationship)
#   feature = queen  (the known feature/attribute of src)
#   dst     = man    (the target; we want to find its corresponding feature)
#
# The attractor computes: dst ⊗ feature ⊗ src⁻¹
# This produces a code that should overlap with "woman"
memory.nns(
    memory.analogical_reasoner(memory.with_code(man), src=king, feature=queen)
)
```
{{#endtab}}
{{#endtabs}}
