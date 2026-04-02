# Producers

**ChunkProducers** are write builders that create and persist chunks in the substrate. Each producer encapsulates the logic for constructing a specific type of chunk.

## The ChunkProducer Interface

{{#tabs global="lang"}}
{{#tab name="Python"}}
In Python, producers are opaque objects created by factory functions (`terminal`, `from_set_members`, etc.) and consumed by `mem_set`.

```python
producer = memory.terminal("fruits", "apple")
with storage.new_mutable_view() as view:
    memory.mem_set(view, producer)
```
{{#endtab}}
{{#tab name="Go"}}
```go
type ChunkProducer interface {
    fmt.Stringer

    // Produce generates a Chunk and writes it into the view.
    // Returns the produced Chunk, or nil for update-only producers.
    // The view decides when/how to commit the written results.
    Produce(ctx context.Context, view SubstrateMutableView) (Chunk, error)

    // ToProto serializes this producer for storage or wire transport.
    ToProto(ctx context.Context) (*api.ChunkProducerProto, error)
}
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
pub trait ChunkProducer: std::fmt::Display {
    /// Produce a chunk and write it into the view.
    /// `index` is passed separately to avoid borrow conflicts
    /// with the mutable view.
    fn produce(
        &self,
        view: &mut dyn SubstrateMutableView,
        index: Option<&dyn AssociativeIndex>,
    ) -> Result<Chunk, HvError>;

    /// Convert to protobuf representation.
    fn to_proto(&self) -> Result<ChunkProducerProto, HvError>;
}
```
{{#endtab}}
{{#endtabs}}

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
    domain, pod, memory.PNote("an apple")).Produce(ctx, view)
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
    domain, pod, memory.PNote("a learner")).Produce(ctx, view)
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
    domain, pod, members, memory.PNote("fruit set")).Produce(ctx, view)
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
    domain, pod, members, 0, memory.PNote("greeting")).Produce(ctx, view)
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
    domain, pod, keys, values, memory.PNote("object")).Produce(ctx, view)
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
    learnerSel, observedSel, 1).Produce(ctx, view)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let chunk = cluster_updater(learner_sel, observed_sel, 1, args).produce(&mut *view, index.as_deref())?;
```
{{#endtab}}
{{#endtabs}}

### SemanticUpdater

Similar to ClusterUpdater but bundles the observed chunk's *code* (not identity) into the Learner.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_mutable_view() as view:
    memory.mem_set(view, memory.semantic_updater(
        learner=memory.by_item_key("learners", "my_learner"),
        observed=memory.by_item_key("fruits", "apple"),
    ))
```
{{#endtab}}
{{#tab name="Go"}}
```go
chunk, err := memory.SemanticUpdater(
    learnerSel, observedSel, 1).Produce(ctx, view)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let chunk = semantic_updater(learner_sel, observed_sel, 1, args).produce(&mut *view, index.as_deref())?;
```
{{#endtab}}
{{#endtabs}}
