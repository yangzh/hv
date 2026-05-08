# Producers

**ChunkProducers** are write builders that create and persist chunks in the substrate. Each producer encapsulates the logic for constructing a specific type of chunk.

<div class="callout callout-note">
<div class="callout-title">Note</div>
Some producers only update existing chunks (e.g., <code>ClusterUpdater</code>) without creating new ones. In those cases, <code>Produce</code> returns the updated chunk rather than a newly created one.
</div>

## Producer Options

Producer options are additional information supplied to producer constructor to tweak behavior.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# `note` indiciates additional note for the new terminal chunk.
memory.new_terminal("d", "p", note="annotation")

# `semantic_indexing` indicates we need to index the semantic code 
# (on top of the id vector).
memory.from_set_members("d", "p", members, semantic_indexing=True)
```
{{#endtab}}
{{#endtabs}}

## Concrete Producers

### NewTerminal

Creates a chunk whose code equals its identity (a bare Sparkle). Useful for registering atoms/symbols.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    memory.mem_set(view, memory.new_terminal("fruits", "apple", note="an apple"))
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

### FromSourceDest

Creates a [Pointer 👉](../hv/pointer.md) chunk — a directional reference from a `source` chunk to a `dest` chunk. Both selectors must resolve to a single chunk; the produced Pointer's bit-level value is `source.id ⊗ Inv(dest.id)`.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    memory.mem_set(
        view,
        memory.from_source_dest(
            "edges", "earth_to_moon",
            memory.by_item_key("planets", "earth"),
            memory.by_item_key("planets", "moon"),
        ))
```
{{#endtab}}
{{#tab name="Go"}}
```go
memory.FromSourceDest(
    hv.NewDomain("edges"), hv.NewPodFromWord("earth_to_moon"),
    memory.WithChunks(earth),
    memory.WithChunks(moon),
).Produce(ctx, view)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let producer = producers::from_source_dest(
    Domain::from_name("edges"),
    Pod::from_word("earth_to_moon"),
    Box::new(selector_impls::with_chunks(vec![earth])),
    Box::new(selector_impls::with_chunks(vec![moon])),
    args,
);
```
{{#endtab}}
{{#endtabs}}

### ClusterUpdater

Feeds an observed chunk into an existing Learner, updating its accumulated code via bundling. The bundle multiplier defaults to 1; pass an explicit override (`multiple=N` in Python) to fold the same observation in repeatedly.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    # With explicit multiplier:
    memory.mem_set(view,
        memory.cluster_updater(
            learner=memory.by_item_key("learners", "my_learner"),
            observed=memory.by_item_key("fruits", "apple"),
            multiple=3,
        ))
```
{{#endtab}}
{{#endtabs}}
