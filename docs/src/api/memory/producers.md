# Producers

**ChunkProducers** are write builders that create and persist chunks in the substrate. Each producer encapsulates the logic for constructing a specific type of chunk.

Note: some producers only update existing chunks (e.g., `ClusterUpdater`) without creating new ones. In those cases, `Produce` returns the updated chunk rather than a newly created one.

## Producer Options

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
memory.terminal("d", "p", note="annotation")
memory.from_set_members("d", "p", members, semantic_indexing=True)
```
{{#endtab}}
{{#tab name="Go"}}
```go
memory.PNote("annotation")           // Set note
memory.PExtra(protoMsg)              // Set extra payload
memory.PSemanticIndexing(true)       // Enable associative index impression
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
{{#tab name="Go"}}
```go
chunk, err := memory.NewTerminal(
    domain, pod, memory.PNote("an apple")).Produce(ctx, mv)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let chunk = new_terminal(domain, pod, args).produce(&mut *view, index.as_deref())?;
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
{{#tab name="Go"}}
```go
chunk, err := memory.NewLearner(
    domain, pod, memory.PNote("a learner")).Produce(ctx, mv)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let chunk = new_learner(domain, pod, args).produce(&mut *view, index.as_deref())?;
```
{{#endtab}}
{{#endtabs}}

### FromSetMembers

Creates a Set from stored members.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    members = memory.by_item_domain("fruits")
    memory.mem_set(view, memory.from_set_members("sets", "fruit_set", members))
```
{{#endtab}}
{{#tab name="Go"}}
```go
chunk, err := memory.FromSetMembers(
    domain, pod, members, memory.PNote("fruit set")).Produce(ctx, mv)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let chunk = from_set_members(domain, pod, members, args).produce(&mut *view, index.as_deref())?;
```
{{#endtab}}
{{#endtabs}}

### FromSequenceMembers

Creates a Sequence from stored members with positional encoding.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    members = memory.joiner(
        memory.by_item_key("words", "hello"),
        memory.by_item_key("words", "world"),
    )
    memory.mem_set(view, memory.from_sequence_members("seqs", "greeting", members, start=0))
```
{{#endtab}}
{{#tab name="Go"}}
```go
chunk, err := memory.FromSequenceMembers(
    domain, pod, members, 0, memory.PNote("greeting")).Produce(ctx, mv)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let chunk = from_sequence_members(domain, pod, members, 0, args).produce(&mut *view, index.as_deref())?;
```
{{#endtab}}
{{#endtabs}}

### FromKeyValues

Creates an Octopus (key-value composite) from keys and value selectors.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    values = memory.joiner(
        memory.by_item_key("colors", "red"),
        memory.by_item_key("shapes", "circle"),
    )
    memory.mem_set(view, memory.from_key_values(
        "records", "obj1", keys=["color", "shape"], values=values,
    ))
```
{{#endtab}}
{{#tab name="Go"}}
```go
chunk, err := memory.FromKeyValues(
    domain, pod, keys, values, memory.PNote("object")).Produce(ctx, mv)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let chunk = from_key_values(domain, pod, keys, values, args).produce(&mut *view, index.as_deref())?;
```
{{#endtab}}
{{#endtabs}}

### ClusterUpdater

Feeds an observed chunk into an existing Learner, updating its accumulated code via bundling.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    memory.mem_set(view, memory.cluster_updater(
        learner=memory.by_item_key("learners", "my_learner"),
        observed=memory.by_item_key("fruits", "apple"),
        multiple=1,
    ))
```
{{#endtab}}
{{#tab name="Go"}}
```go
chunk, err := memory.ClusterUpdater(
    learnerSel, observedSel, 1).Produce(ctx, mv)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let chunk = cluster_updater(learner_sel, observed_sel, 1, args).produce(&mut *view, index.as_deref())?;
```
{{#endtab}}
{{#endtabs}}
