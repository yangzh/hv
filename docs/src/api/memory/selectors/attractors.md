Each attractor conceptually provides "the center of attraction" for candidates: the NNS accepts one or more attractors, to perform the actual near-neighbor search work, by interacting with underlying associative index.

# Forward attractors

Roughly forward attractors try to find parts from a given a composite.

| Attractor | Modifier | Attracts |
|-----------|-------|-------|
| **SetMembersAttractor** | runtime, depends on `selected.code.domain` | All members of the Set |
| **SequenceMemberAttractor** | runtime, depends on `selected.code.domain` | Sequence member at a specific position |
| **TentacleAttractor(model, octopus, key)** | `inverse(Sparkle(model, "", key))` | Octopus value for that key |

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
memory.set_members(memory.by_item_key("sets", "my_set"))

memory.sequence_member(memory.by_item_key("seqs", "my_seq"), pos=2)

memory.tentacle(model, memory.by_item_key("records", "person"), "name")
```
{{#endtab}}
{{#endtabs}}

# Reverse Attractors

Roughly reverse attractors try to locate composites given a part.

| Attractor | Modifier | Attracts |
|-----------|-------|-------|
| **SetAttractor(model, member, candidate)** | `Sparkle(SET_MARKER @ candidate)` | All Sets in domain `candidate` containing `member` |
| **SequenceAttractor(model, member, pos, candidate)** | `Bind(SEQ_MARKER @ candidate, Step^pos)` | All Sequences in `candidate` with `member` at `pos` |
| **OctopusAttractor(model, key, value)** | `Sparkle(model, "", key)` | Octopuses with that key/value pair |

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
memory.set_attractor(model, memory.by_item_key("animals", "cat"), "sets")

memory.sequence_attractor(model, memory.by_item_key("animals", "cat"), 0, "seqs")

memory.octopus_attractor(model, "color", memory.by_item_key("colors", "red"))
```
{{#endtab}}
{{#endtabs}}

# Analogical Reasoning

Given the analogy "king is to queen as man is to ?":

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
# src = king, feature = queen, dst = man.
# Modifier = queen ⊗ inverse(king); applied to man → "woman".
memory.nns(
    memory.analogical_reasoner(memory.with_code(man), king, queen))
```
{{#endtab}}
{{#endtabs}}
