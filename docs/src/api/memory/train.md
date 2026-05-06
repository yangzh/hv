# Train 🚂🚃🚃🚃

A doubly-linked, payload-carrying chunk data structure built on Octopus chunks. The train is a *train of carriages* — each carriage 🚃 carries one payload chunk, and carriages couple to their neighbors at LEFT ⬅️ / RIGHT ➡️.

## Shape

A train occupies its own 64-bit `train_domain`. The structure has two kinds of chunks:

- **Sentinel locomotive 🚂** — the chunk at `(train_domain, P0)`. Anchors both ends of the train. Its `LEFT` slot points at the leftmost carriage, its `RIGHT` slot at the rightmost. Its `PAYLOAD` slot is identity (no payload).
- **Carriage 🚃** — a chunk at `(train_domain, carriage_pod)` for some non-zero pod. Each carriage is a specialized Octopus with four slots:
    - `PAYLOAD` 📨 — points at the actual payload chunk in item memory (`Sparkle(payload_domain, payload_pod)`). Always non-identity.
    - `LEFT` ⬅️ — id-Sparkle of the previous carriage, or identity if leftmost.
    - `RIGHT` ➡️ — id-Sparkle of the next carriage, or identity if rightmost.
    - `CHILDREN` 👨‍👩‍👧‍👦 — optional pointer at a child structure (typically the sentinel of a child train). Identity when no children are attached.

A 3-carriage train (payloads `A`, `B`, `C` in left-to-right order):

```text
       🚂                🚃                🚃                🚃
   ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
   │ sentinel │ <--> │    A     │ <--> │    B     │ <--> │    C     │
   │  pod=P0  │      │ pod=p_A  │      │ pod=p_B  │      │ pod=p_C  │
   └──────────┘      └──────────┘      └──────────┘      └──────────┘
```

Each box is one Octopus chunk. Each `<-->` between adjacent boxes represents one bidirectional `LEFT`/`RIGHT` pointer pair. The slot values inside each chunk are:

| Chunk | `PAYLOAD` | `LEFT` | `RIGHT` | `CHILDREN` |
|-------|-----------|--------|---------|------------|
| sentinel 🚂 (`pod=P0`) | identity ⊥ | leftmost (A) | rightmost (C) | identity ⊥ (or a child structure) |
| carriage A             | `Sparkle(A*)` | identity ⊥ | carriage B | identity ⊥ (or a child structure) |
| carriage B             | `Sparkle(B*)` | carriage A | carriage C | identity ⊥ (or a child structure) |
| carriage C             | `Sparkle(C*)` | carriage B | identity ⊥ | identity ⊥ (or a child structure) |

Where `A*`, `B*`, `C*` are the actual payload chunks living elsewhere in item memory.

The sentinel's `LEFT`/`RIGHT` are **anchor pointers** (jumps directly to the leftmost / rightmost), not neighbor pointers. The carriages' `LEFT`/`RIGHT` are conventional neighbor pointers.

## Pushing

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
storage.mem_set(
    memory.train_appender(
        train_domain, memory.with_sparkle(payload_domain, "A")))

storage.mem_set(
    memory.train_prepender(
        train_domain, memory.with_sparkle(payload_domain, "Z")))
```
{{#endtab}}
{{#tab name="Go"}}
```go
p.Memory.Set(ctx, memory.TrainAppender(trainDomain, payloadSelector))
p.Memory.Set(ctx, memory.TrainPrepender(trainDomain, payloadSelector))
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
storage.set(producers::train_appender(train_domain, payload_selector, args))?;
storage.set(producers::train_prepender(train_domain, payload_selector, args))?;
```
{{#endtab}}
{{#endtabs}}

Each push rewrites **up to three chunks** atomically through one mutable view:

1. The new carriage at `(train_domain, fresh_pod)`.
2. The previous tail/head carriage, with its tail-side neighbor link updated to the new carriage. (Skipped on the first push, when the train is empty.)
3. The sentinel, with its tail-side anchor pointer updated to the new carriage. The head-side pointer is updated only when the train transitions from empty to one element.

The sentinel is auto-created on the first push — no separate "init train" step is needed.

> ⚠️ **Single-writer per train.** Concurrent pushes from independent mutable views on the same train WILL race on the sentinel and on the previous tail/head — last-write wins, with dropped pushes possible. Callers expecting concurrent appenders must synchronize externally (e.g., serialize through a single goroutine/task, or take an external lock keyed on `train_domain`). Reads through a `View` are always snapshot-consistent per chunk.

### Mid-train insertion: `TrainInsertAfter` / `TrainInsertBefore`

`TrainAppender` and `TrainPrepender` are thin wrappers over the more general `TrainInsertAfter` / `TrainInsertBefore`, which take a *reference carriage selector* instead of a domain. The new carriage is wedged on the chosen side of the reference. The train domain is taken from the resolved reference carriage.

| Reference carriage | `TrainInsertAfter` | `TrainInsertBefore` |
|--------------------|--------------------|---------------------|
| sentinel 🚂 (`TrainCarriage(domain)`) | append (new rightmost) | prepend (new leftmost) |
| member carriage X | wedge between X and X.right | wedge between X.left and X |

Sentinel-as-reference is the wraparound bookend case: since the sentinel sits on both ends of the train, "after the sentinel" means "right of the rightmost," and "before the sentinel" means "left of the leftmost." On an empty train, either becomes the first and only member.

Each insert rewrites:

1. The new carriage.
2. The carriage on each side whose neighbor link points at the new one (one rewrite for end-inserts, two for mid-train inserts).
3. The sentinel, only when its anchor pointer changes (i.e., the new carriage becomes the leftmost or rightmost).

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Mid-train: wedge M between B and C.
storage.mem_set(memory.train_insert_after(
    memory.train_carriage(train_domain, b_pod),
    memory.with_sparkle(payload_domain, "M"),
))

# Sentinel-as-ref: equivalent to train_appender.
storage.mem_set(memory.train_insert_after(
    memory.train_carriage(train_domain),
    memory.with_sparkle(payload_domain, "tail"),
))
```
{{#endtab}}
{{#tab name="Go"}}
```go
p.Memory.Set(ctx, memory.TrainInsertAfter(
    memory.TrainCarriage(trainDomain, &bPod), payloadSelector))

p.Memory.Set(ctx, memory.TrainInsertBefore(
    memory.TrainCarriage(trainDomain, nil), payloadSelector))
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
storage.set(producers::train_insert_after(
    Box::new(train_carriage(train_domain.clone(), Some(b_pod))),
    payload_selector,
    args,
))?;
```
{{#endtab}}
{{#endtabs}}

## Empty check: `TrainIsEmpty`

A direct query that reads the sentinel and reports whether both `LEFT` and `RIGHT` anchors are identity. A train whose sentinel hasn't been written yet (never touched) is also reported empty — no auto-init.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
with storage.new_view() as view:
    if memory.train_is_empty(view, train_domain):
        print("nothing to process")
```
{{#endtab}}
{{#tab name="Go"}}
```go
view := p.Memory.Substrate().NewView(nil)
defer view.Discard()
empty, err := memory.TrainIsEmpty(ctx, view, trainDomain)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let view = substrate.new_view(None);
let empty = memory::train::train_is_empty(&*view, &train_domain)?;
```
{{#endtab}}
{{#endtabs}}

## Iterating — cursor-straddle semantics

`TrainForward` / `TrainBackward` walk the train, yielding each carriage's *payload chunk*. The starting point is itself a Selector — pass `TrainCarriage(domain)` (with no pod) to start from the sentinel for a full-train iteration, or `TrainCarriage(domain, pod)` to start from a specific carriage.

**The cursor straddles between elements**, similar to Java's `ListIterator` or C++'s `std::list::iterator`:

- `start` is the cursor; iteration is **exclusive of `start`'s own payload**.
- When `start` resolves to the sentinel, iteration covers the whole train (sentinel acts as both before-leftmost and after-rightmost).
- When `start` resolves to a member carriage, iteration yields the elements *strictly after* it in the chosen direction; the start carriage's own payload is NOT yielded.

| `start` | `TrainForward` yields | `TrainBackward` yields |
|---------|----------------------|------------------------|
| sentinel | leftmost, …, rightmost | rightmost, …, leftmost |
| carriage X | X.right, X.right.right, … | X.left, X.left.left, … |

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Whole-train iteration from the sentinel.
for chunk in storage.mem_get(
    memory.train_forward(memory.train_carriage(train_domain))):
    print(chunk.note)

# From a specific carriage onward (exclusive of that carriage).
for chunk in storage.mem_get(
    memory.train_backward(memory.train_carriage(train_domain, carriage_pod))):
    print(chunk.note)
```
{{#endtab}}
{{#tab name="Go"}}
```go
// Whole-train iteration.
for c := range memory.SelectorIter(ctx, view,
    memory.TrainForward(memory.TrainCarriage(trainDomain, nil))) {
    fmt.Println(c.Note)
}

// From a specific carriage onward (exclusive).
for c := range memory.SelectorIter(ctx, view,
    memory.TrainBackward(memory.TrainCarriage(trainDomain, &carriagePod))) {
    fmt.Println(c.Note)
}
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let sel = train_forward(Box::new(train_carriage(train_domain.clone(), None)));
let sel = train_backward(Box::new(train_carriage(
    train_domain.clone(),
    Some(carriage_pod),
)));
```
{{#endtab}}
{{#endtabs}}

### Single-step shorthands: `TrainNext` / `TrainPrev`

`TrainNext(start)` is shorthand for `Range(0, 1, TrainForward(start))` — the next single payload from the cursor's position. `TrainPrev(start)` is the backward mirror. They follow the same exclusive-start rule.

| Cursor | `TrainNext` yields | `TrainPrev` yields |
|--------|--------------------|--------------------|
| sentinel | leftmost carriage's payload | rightmost carriage's payload |
| carriage X | X's right neighbor's payload (or empty if X is rightmost) | X's left neighbor's payload (or empty if X is leftmost) |

```python
# Peek at the front / back of the train.
front = next(iter(storage.mem_get(
    memory.train_next(memory.train_carriage(train_domain))))).note
back  = next(iter(storage.mem_get(
    memory.train_prev(memory.train_carriage(train_domain))))).note
```

### Iteration rule (implementation)

Each step:

1. **Integrity** — sentinel is identified by `pod == P0`. The sentinel MUST have an identity `PAYLOAD`; a carriage MUST have a non-identity `PAYLOAD`. Either violation returns `FailedPrecondition` (the train is malformed).
2. **Advance** — on a carriage, follow the matching-direction key (`RIGHT` for forward, `LEFT` for backward) to the next neighbor. On the sentinel, follow the *opposite*-direction key — sentinel's `LEFT`/`RIGHT` are anchor pointers, so the opposite key takes you to the appropriate end.
3. **Yield** — yield the chunk you advanced to. Stop when the next pointer is identity.

The advance-then-yield order is what makes the iteration exclusive of `start`.

## Hierarchy: the `CHILDREN` slot

Each carriage's `CHILDREN` 👨‍👩‍👧‍👦 slot can point at the sentinel of another train (or any other chunk). Attach one at push time via the `children` argument; query it via the `TrainChildren(parent)` selector.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Push a parent carriage whose CHILDREN points at a child train's sentinel.
storage.mem_set(memory.train_appender(
    parent_domain,
    memory.with_sparkle(payload_domain, "B"),
    children=memory.train_carriage(child_domain),
))

# Walk the child train from the parent.
for chunk in storage.mem_get(
    memory.train_forward(
        memory.train_children(
            memory.train_carriage(parent_domain, parent_carriage_pod)))):
    print(chunk.note)
```
{{#endtab}}
{{#tab name="Go"}}
```go
// Push parent carriage with CHILDREN attached.
p.Memory.Set(ctx, memory.TrainAppender(
    parentDomain, payloadSelector,
    memory.PChildren(memory.TrainCarriage(childDomain, nil)),
))

// Walk the child train.
for c := range memory.SelectorIter(ctx, view,
    memory.TrainForward(memory.TrainChildren(
        memory.TrainCarriage(parentDomain, &parentCarriagePod)))) {
    fmt.Println(c.Note)
}
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
// Build args with children attached.
let mut args = chunk_producer_proto::Args::default();
args.children = Some(Box::new(train_carriage(child_domain, None).to_proto()?));
storage.set(producers::train_appender(parent_domain, payload_sel, args))?;

// Walk the child train.
let sel = train_forward(Box::new(train_children(Box::new(
    train_carriage(parent_domain, Some(parent_carriage_pod)),
))));
```
{{#endtab}}
{{#endtabs}}

`TrainChildren(parent)` yields zero chunks (no error) when the parent has identity `CHILDREN` or is missing entirely. Hierarchical traversal is the caller's job — walk a parent train, recurse into `TrainChildren` on each carriage.
