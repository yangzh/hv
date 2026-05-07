Each attractor conceptually provides "the center of attraction" for candidates: the NNS accepts one or more attractors, to perform the actual near-neighbor search work, by interacting with underlying associative index.

Implementation-wise, attractors are specialized selectors.

# Forward attractors

Roughly forward attractors try to find parts from a given a composite.

| Attractor | Query | Attracts |
|-----------|-------|-------|
| **SetMembersAttractor** | Releases SET_MARKER from a Set | All members of the Set |
| **SequenceMemberAttractor** | Releases with SEQUENCE_MARKER + positional marker | Sequence member at a specific position |
| **WithCodeModifier(octopus, ¬key)** | Binds the Octopus code with the inverse of `key` | Octopus value for that key (the "tentacle" pattern) |

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
memory.set_members(memory.by_item_key("sets", "my_set"))

memory.sequence_member(memory.by_item_key("seqs", "my_seq"), pos=2)

# Tentacle pattern: get the value at a key from an Octopus.
key = hv.Sparkle(model, "", "name")
memory.with_code_modifier(
    memory.by_item_key("records", "person"),
    hv.inverse(key))
```
{{#endtab}}
{{#endtabs}}

# Reverse Attractors

Roughly reverse attractors try to locate composites given a part.

| Attractor | Modifier | Attracts |
|-----------|-------|-------|
| `WithIDModifier(member, SET_MARKER@d)` | `Bind(member.id, SET_MARKER@d)` | All Sets in domain `d` containing the member |
| `WithIDModifier(member, SEQ_MARKER@d ⊗ Step^pos)` | `Bind(member.id, …)` | All Sequences in domain `d` with member at `pos` |
| `WithIDModifier(value, Sparkle(key))` | `Bind(value.id, Sparkle(key))` | Octopuses with that key/value pair |

`WithIDModifier(inner, modifier)` runs `inner.select`, then for each chunk
`c` it yields, replaces `c.code` with `Bind(c.id, modifier)`. The composite
recipes for the three reverse-attractor cases are stable patterns — the
caller precomputes the marker / step / key vector once and reuses it.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# All Sets in domain "sets" that contain "cat".
set_marker = hv.Sparkle(model, "sets", hv.PREWIRED_SET_MARKER)
memory.with_id_modifier(
    memory.by_item_key("animals", "cat"),
    set_marker)

# All Sequences in domain "seqs" with "cat" at position 0.
seq_marker = hv.Sparkle(model, "seqs", hv.PREWIRED_SEQUENCE_MARKER)
step = hv.Sparkle(model, "", hv.PREWIRED_STEP)
memory.with_id_modifier(
    memory.by_item_key("animals", "cat"),
    hv.bind(seq_marker, step.power(0)))

# All Octopuses with key="color" and value pointing at the "red" terminal.
key = hv.Sparkle(model, "", "color")
memory.with_id_modifier(
    memory.by_item_key("colors", "red"),
    key)
```
{{#endtab}}
{{#endtabs}}

# Analogical Reasoning

`WithCodeModifier(dst, Bind(feature, inverse(src)))` performs analogical reasoning ("A is to B as C is to ?"): for each chunk `c` yielded by `dst`, it computes `Bind(c.code, feature, inverse(src))`. NNS then finds the nearest match.

Given the analogy "king is to queen as man is to ?":

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
king   = hv.Sparkle(model, "role", "king")
queen  = hv.Sparkle(model, "role", "queen")
man    = hv.Sparkle(model, "role", "man")

# src = king (known source), feature = queen (known relation), dst = man.
# Modifier = queen ⊗ inverse(king); applied to man → produces a code
# overlapping with "woman".
memory.nns(
    memory.with_code_modifier(
        memory.with_code(man),
        hv.bind(queen, hv.inverse(king))))
```
{{#endtab}}
{{#endtabs}}
