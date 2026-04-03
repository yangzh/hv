# Producers

**ChunkProducers** are write builders that create and persist chunks in the substrate. Each producer encapsulates the logic for constructing a specific type of chunk.

<div class="callout callout-note">
<div class="callout-title">Note</div>
Some producers only update existing chunks (e.g., <code>ClusterUpdater</code>) without creating new ones. In those cases, <code>Produce</code> returns the updated chunk rather than a newly created one.
</div>

## Producer Options

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
memory.terminal("d", "p", note="annotation")
memory.from_set_members("d", "p", members, semantic_indexing=True)
```
{{#endtab}}
{{#endtabs}}

## Concrete Producers

### Terminal

Creates a chunk whose code equals its identity (a bare Sparkle). Useful for registering atoms/symbols.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    memory.mem_set(view, memory.terminal("fruits", "apple", note="an apple"))
```
{{#endtab}}
{{#endtabs}}

### NewLearner

Creates a fresh Learner chunk for online learning.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    memory.mem_set(view, memory.new_learner("learners", "my_learner", note="a learner"))
```
{{#endtab}}
{{#endtabs}}

### FromSetMembers

Creates a Set from stored members.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    memory.mem_set(
        view, 
        memory.from_set_members(
            "sets",
            "fruit_set", 
            memory.by_item_domain("fruits"),
        ))
```
{{#endtab}}
{{#endtabs}}

### FromSequenceMembers

Creates a Sequence from stored members with positional encoding.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    memory.mem_set(
        view, 
        memory.from_sequence_members(
            "seqs",
            "greeting", 
            memory.joiner(
                memory.by_item_key("words", "hello"),
                memory.by_item_key("words", "world"),
            ),
            start=0),
    )
```
{{#endtab}}
{{#endtabs}}

### FromKeyValues

Creates an Octopus (key-value composite) from keys and value selectors.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    memory.mem_set(
        view, 
        memory.from_key_values(
            "records",
            "obj1", 
            keys=["color", "shape"], 
            values=memory.joiner(
                memory.by_item_key("colors", "red"),
                memory.by_item_key("shapes", "circle"),
            ),
        ))
```
{{#endtab}}
{{#endtabs}}

### ClusterUpdater

Feeds an observed chunk into an existing Learner, updating its accumulated code via bundling.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    memory.mem_set(view, 
        memory.cluster_updater(
            learner=memory.by_item_key("learners", "my_learner"),
            observed=memory.by_item_key("fruits", "apple"),
            multiple=1,
        ))
```
{{#endtab}}
{{#endtabs}}
