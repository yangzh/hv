# Selectors

**ChunkSelectors** are composable query builders for reading chunks from the substrate. Each selector defines how to find and return matching chunks.

## The ChunkSelector Interface

{{#tabs global="lang"}}
{{#tab name="Python"}}
In Python, selectors are opaque objects created by factory functions (`by_item_key`, `nns`, etc.) and consumed by helpers like `first_picked`. There is no explicit interface to implement.

```python
sel = memory.by_item_key("animals", "cat")
code = memory.first_picked(view, sel)
```
{{#endtab}}
{{#tab name="Go"}}
```go
type ChunkSelector interface {
    fmt.Stringer

    // Select scans the view and calls eachOp for each matching chunk.
    // Returns nil if no matches (callback is simply not called).
    // Wrap with NotFoundLabeler to get ErrNotFound instead.
    Select(ctx context.Context, view SubstrateView, eachOp OnSelectedChunk) error

    // ToProto serializes this selector for storage or wire transport.
    ToProto(ctx context.Context) (*api.ChunkSelectorProto, error)
}

// Callback signature for each matched chunk.
type OnSelectedChunk func(ctx context.Context, chunk Chunk, extra *api.SelectorExtra) error
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
pub trait ChunkSelector: std::fmt::Display {
    /// Scan the view and forward each matching chunk to `each`.
    fn select(
        &self,
        view: &dyn SubstrateView,
        each: &mut dyn FnMut(&Chunk, Option<&SelectorExtra>) -> Result<(), HvError>,
    ) -> Result<(), HvError>;

    /// Convert to protobuf representation.
    fn to_proto(&self) -> Result<ChunkSelectorProto, HvError>;
}
```
{{#endtab}}
{{#endtabs}}

## Working with Results

### FirstPicked — get the first match

Returns the first chunk matching the selector. Returns an error if nothing is found.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Returns the code (HyperBinary) of the first match
code = memory.first_picked(view, selector)

# Returns the full Chunk object (with .id, .code, .note, .extra)
chunk = memory.first_picked_chunk(view, selector)
print(chunk.id, chunk.code, chunk.note)
```
{{#endtab}}
{{#tab name="Go"}}
```go
chunk, extra, err := memory.FirstPicked(ctx, view, selector)
// chunk is a Chunk; extra contains idx and weight (from NNS)
// err is ErrNotFound if no match
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let (chunk, extra) = first_picked(&*view, &selector)?;
// Returns HvError::NotFound if no match
```
{{#endtab}}
{{#endtabs}}

### Iterator — iterate all matches

{{#tabs global="lang"}}
{{#tab name="Python"}}
Not available as iterator in Python. Use `mem_get()` for batch reads.
{{#endtab}}
{{#tab name="Go"}}
```go
for chunk, extra := range memory.SelectorIter(ctx, view, selector) {
    fmt.Println(chunk.ID, chunk.Code, extra)
}
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let chunks = select_all(&*view, &selector)?;
for chunk in &chunks {
    println!("{} {:?}", chunk.id, chunk.code);
}
```
{{#endtab}}
{{#endtabs}}

### mem_get — high-level batch read

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
results = storage.mem_get(selector)
for hv in results:
    print(hv)
```
{{#endtab}}
{{#tab name="Go"}}
```go
chunks, err := m.Get(ctx, selector)
for _, c := range chunks {
    fmt.Println(c)
}
```
{{#endtab}}
{{#endtabs}}

### Raw Select — callback-based

{{#tabs global="lang"}}
{{#tab name="Python"}}
Not directly exposed in Python. Use `first_picked()` or `mem_get()` instead.
{{#endtab}}
{{#tab name="Go"}}
```go
selector.Select(ctx, view, func(ctx context.Context, chunk memory.Chunk, extra *api.SelectorExtra) error {
    fmt.Println(chunk.ID, chunk.Code)
    return nil // return non-nil error to stop iteration
})
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
selector.select(&*view, &mut |chunk, extra| {
    println!("{}", chunk.id);
    Ok(()) // return Err to stop iteration
})?;
```
{{#endtab}}
{{#endtabs}}

## Note on Python Selector Consumption

In Python, selectors passed to combinators (`range_sel`, `nns`, `joiner`, etc.) are **consumed** — they cannot be reused after being passed. This mirrors Rust's move semantics. Attempting to reuse a consumed selector raises `ValueError`.

## Concrete Selectors

### ByItemKey

Exact lookup by domain + pod.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
sel = memory.by_item_key("animals", "cat")
```
{{#endtab}}
{{#tab name="Go"}}
```go
sel := memory.ByItemKey(domain, pod)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let sel = by_item_key(domain, pod);
```
{{#endtab}}
{{#endtabs}}

### ByItemDomain

All chunks in a given domain (prefix scan).

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
sel = memory.by_item_domain("animals")
```
{{#endtab}}
{{#tab name="Go"}}
```go
sel := memory.ByItemDomain(domain)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let sel = by_item_domain(domain);
```
{{#endtab}}
{{#endtabs}}

### WithCode / WithSparkle

Literal selector — returns a hypervector directly, no storage lookup.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
sel = memory.with_code(some_hv)
sel = memory.with_sparkle("animals", "cat")
```
{{#endtab}}
{{#tab name="Go"}}
```go
sel := memory.WithCode(someHV)
sel := memory.WithDomainPod(domain, pod)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let sel = with_code(some_hv);
let sel = with_domain_pod(domain, pod);
```
{{#endtab}}
{{#endtabs}}

### Joiner

Union of multiple selectors — returns first result from each.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
sel = memory.joiner(
    memory.by_item_key("animals", "cat"),
    memory.by_item_key("animals", "dog"),
)
```
{{#endtab}}
{{#tab name="Go"}}
```go
sel := memory.Joiner(
    memory.ByItemKey(domainCat, podCat),
    memory.ByItemKey(domainDog, podDog),
)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let sel = joiner(vec![
    Box::new(by_item_key(domain_cat, pod_cat)),
    Box::new(by_item_key(domain_dog, pod_dog)),
]);
```
{{#endtab}}
{{#endtabs}}

### Range

Limits results to `[start, start+limit)`. `limit=0` means no limit.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
sel = memory.range_sel(memory.by_item_domain("animals"), start=0, limit=10)
```
{{#endtab}}
{{#tab name="Go"}}
```go
sel := memory.Range(0, 10, memory.ByItemDomain(domain))
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let sel = range_selector(0, 10, Box::new(by_item_domain(domain)));
```
{{#endtab}}
{{#endtabs}}

### OnlyDomain

Filters inner selector results by domain.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
sel = memory.only_domain("animals", inner_selector)
```
{{#endtab}}
{{#tab name="Go"}}
```go
sel := memory.OnlyDomain(domain, innerSelector)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let sel = only_domain(domain, Box::new(inner));
```
{{#endtab}}
{{#endtabs}}

### NNS (Near-Neighbor Search)

Wraps one or more attractors to perform [near-neighbor search](../../concepts/near_neighbor_search.md).

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
result = memory.first_picked(view, memory.nns(
    memory.set_members(memory.by_item_key("sets", "my_set")),
))
```
{{#endtab}}
{{#tab name="Go"}}
```go
result, _, err := memory.FirstPicked(ctx, view, memory.NearNeighborSearch(
    memory.SetMembersAttractor(memory.ByItemKey(setDomain, setPod)),
))
```
{{#endtab}}
{{#endtabs}}

## Attractors

Attractors are specialized selectors that provide query codes for NNS. They are always wrapped in `nns()`.

### Forward — given a composite, find its parts

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
memory.set_members(memory.by_item_key("sets", "my_set"))
memory.sequence_member(memory.by_item_key("seqs", "my_seq"), pos=2)
memory.tentacle(memory.by_item_key("records", "person"), key="name")
```
{{#endtab}}
{{#tab name="Go"}}
```go
memory.SetMembersAttractor(memory.ByItemKey(setDomain, setPod))
memory.SequenceMemberAttractor(memory.ByItemKey(seqDomain, seqPod), 2)
memory.TentacleAttractor(memory.ByItemKey(octDomain, octPod), "name")
```
{{#endtab}}
{{#endtabs}}

### Reverse — given a part, find composites containing it

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
memory.set_attractor(memory.by_item_key("animals", "cat"), "sets")
memory.sequence_attractor(memory.by_item_key("animals", "cat"), pos=0, domain="seqs")
memory.octopus_attractor(key="color", value=memory.by_item_key("colors", "red"))
```
{{#endtab}}
{{#tab name="Go"}}
```go
memory.SetAttractor(memory.ByItemKey(animalDomain, catPod), setDomain)
memory.SequenceAttractor(memory.ByItemKey(animalDomain, catPod), 0, seqDomain)
memory.OctopusAttractor("color", memory.ByItemKey(colorDomain, redPod))
```
{{#endtab}}
{{#endtabs}}

### AnalogicalReasoner

"feature is to src as ? is to dst"

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
memory.analogical_reasoner(
    dst=memory.by_item_key("roles", "man"),
    src=king_hv,
    feature=queen_hv,
)
```
{{#endtab}}
{{#tab name="Go"}}
```go
memory.AnalogicalReasoner(
    memory.ByItemKey(roleDomain, manPod),
    kingHV, queenHV,
)
```
{{#endtab}}
{{#endtabs}}
