# Deque 🚂🚃🚃🚃

A doubly-linked, payload-carrying chunk data structure built on Octopus chunks. The deque is a *train of carriages* — each carriage 🚃 carries one payload chunk, and carriages couple to their neighbors at LEFT ⬅️ / RIGHT ➡️.

## Shape

A deque occupies its own 64-bit `deque_domain`. The structure has two kinds of chunks:

- **Sentinel locomotive 🚂** — the chunk at `(deque_domain, P0)`. Anchors both ends of the train. Its `LEFT` slot points at the leftmost carriage, its `RIGHT` slot at the rightmost. Its `PAYLOAD` slot is identity (no payload).
- **Carriage 🚃** — a chunk at `(deque_domain, carriage_pod)` for some non-zero pod. Each carriage is a specialized Octopus with four slots:
    - `PAYLOAD` 📨 — points at the actual payload chunk in item memory (`Sparkle(payload_domain, payload_pod)`). Always non-identity.
    - `LEFT` ⬅️ — id-Sparkle of the previous carriage, or identity if leftmost.
    - `RIGHT` ➡️ — id-Sparkle of the next carriage, or identity if rightmost.
    - `CHILDREN` 👨‍👩‍👧‍👦 — optional pointer at a child structure (typically the sentinel of a child deque). Identity when no children are attached.

A 3-carriage deque (payloads `A`, `B`, `C` in left-to-right order):

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
    memory.deque_appender(
        deque_domain, memory.with_sparkle(payload_domain, "A")))

storage.mem_set(
    memory.deque_prepender(
        deque_domain, memory.with_sparkle(payload_domain, "Z")))
```
{{#endtab}}
{{#tab name="Go"}}
```go
p.Memory.Set(ctx, memory.DequeAppender(dequeDomain, payloadSelector))
p.Memory.Set(ctx, memory.DequePrepender(dequeDomain, payloadSelector))
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
storage.set(producers::deque_appender(deque_domain, payload_selector, args))?;
storage.set(producers::deque_prepender(deque_domain, payload_selector, args))?;
```
{{#endtab}}
{{#endtabs}}

Each push rewrites **up to three chunks** atomically through one mutable view:

1. The new carriage at `(deque_domain, fresh_pod)`.
2. The previous tail/head carriage, with its tail-side neighbor link updated to the new carriage. (Skipped on the first push, when the deque is empty.)
3. The sentinel, with its tail-side anchor pointer updated to the new carriage. The head-side pointer is updated only when the deque transitions from empty to one element.

The sentinel is auto-created on the first push — no separate "init deque" step is needed.

> ⚠️ **Single-writer per deque.** Concurrent pushes from independent mutable views on the same deque WILL race on the sentinel and on the previous tail/head — last-write wins, with dropped pushes possible. Callers expecting concurrent appenders must synchronize externally (e.g., serialize through a single goroutine/task, or take an external lock keyed on `deque_domain`). Reads through a `View` are always snapshot-consistent per chunk.

### Mid-deque insertion: `DequeInsertAfter` / `DequeInsertBefore`

`DequeAppender` and `DequePrepender` are thin wrappers over the more general `DequeInsertAfter` / `DequeInsertBefore`, which take a *reference carriage selector* instead of a domain. The new carriage is wedged on the chosen side of the reference. The deque domain is taken from the resolved reference carriage.

| Reference carriage | `DequeInsertAfter` | `DequeInsertBefore` |
|--------------------|--------------------|---------------------|
| sentinel 🚂 (`DequeCarriage(domain)`) | append (new rightmost) | prepend (new leftmost) |
| member carriage X | wedge between X and X.right | wedge between X.left and X |

Sentinel-as-reference is the wraparound bookend case: since the sentinel sits on both ends of the train, "after the sentinel" means "right of the rightmost," and "before the sentinel" means "left of the leftmost." On an empty deque, either becomes the first and only member.

Each insert rewrites:

1. The new carriage.
2. The carriage on each side whose neighbor link points at the new one (one rewrite for end-inserts, two for mid-deque inserts).
3. The sentinel, only when its anchor pointer changes (i.e., the new carriage becomes the leftmost or rightmost).

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Mid-deque: wedge M between B and C.
storage.mem_set(memory.deque_insert_after(
    memory.deque_carriage(deque_domain, b_pod),
    memory.with_sparkle(payload_domain, "M"),
))

# Sentinel-as-ref: equivalent to deque_appender.
storage.mem_set(memory.deque_insert_after(
    memory.deque_carriage(deque_domain),
    memory.with_sparkle(payload_domain, "tail"),
))
```
{{#endtab}}
{{#tab name="Go"}}
```go
p.Memory.Set(ctx, memory.DequeInsertAfter(
    memory.DequeCarriage(dequeDomain, &bPod), payloadSelector))

p.Memory.Set(ctx, memory.DequeInsertBefore(
    memory.DequeCarriage(dequeDomain, nil), payloadSelector))
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
storage.set(producers::deque_insert_after(
    Box::new(deque_carriage(deque_domain.clone(), Some(b_pod))),
    payload_selector,
    args,
))?;
```
{{#endtab}}
{{#endtabs}}

## Iterating — cursor-straddle semantics

`DequeForward` / `DequeBackward` walk the train, yielding each carriage's *payload chunk*. The starting point is itself a Selector — pass `DequeCarriage(domain)` (with no pod) to start from the sentinel for a full-deque iteration, or `DequeCarriage(domain, pod)` to start from a specific carriage.

**The cursor straddles between elements**, similar to Java's `ListIterator` or C++'s `std::list::iterator`:

- `start` is the cursor; iteration is **exclusive of `start`'s own payload**.
- When `start` resolves to the sentinel, iteration covers the whole deque (sentinel acts as both before-leftmost and after-rightmost).
- When `start` resolves to a member carriage, iteration yields the elements *strictly after* it in the chosen direction; the start carriage's own payload is NOT yielded.

| `start` | `DequeForward` yields | `DequeBackward` yields |
|---------|----------------------|------------------------|
| sentinel | leftmost, …, rightmost | rightmost, …, leftmost |
| carriage X | X.right, X.right.right, … | X.left, X.left.left, … |

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Whole-deque iteration from the sentinel.
for chunk in storage.mem_get(
    memory.deque_forward(memory.deque_carriage(deque_domain))):
    print(chunk.note)

# From a specific carriage onward (exclusive of that carriage).
for chunk in storage.mem_get(
    memory.deque_backward(memory.deque_carriage(deque_domain, carriage_pod))):
    print(chunk.note)
```
{{#endtab}}
{{#tab name="Go"}}
```go
// Whole-deque iteration.
for c := range memory.SelectorIter(ctx, view,
    memory.DequeForward(memory.DequeCarriage(dequeDomain, nil))) {
    fmt.Println(c.Note)
}

// From a specific carriage onward (exclusive).
for c := range memory.SelectorIter(ctx, view,
    memory.DequeBackward(memory.DequeCarriage(dequeDomain, &carriagePod))) {
    fmt.Println(c.Note)
}
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let sel = deque_forward(Box::new(deque_carriage(deque_domain.clone(), None)));
let sel = deque_backward(Box::new(deque_carriage(
    deque_domain.clone(),
    Some(carriage_pod),
)));
```
{{#endtab}}
{{#endtabs}}

### Single-step shorthands: `DequeNext` / `DequePrev`

`DequeNext(start)` is shorthand for `Range(0, 1, DequeForward(start))` — the next single payload from the cursor's position. `DequePrev(start)` is the backward mirror. They follow the same exclusive-start rule.

| Cursor | `DequeNext` yields | `DequePrev` yields |
|--------|--------------------|--------------------|
| sentinel | leftmost carriage's payload | rightmost carriage's payload |
| carriage X | X's right neighbor's payload (or empty if X is rightmost) | X's left neighbor's payload (or empty if X is leftmost) |

```python
# Peek at the front / back of the deque.
front = next(iter(storage.mem_get(
    memory.deque_next(memory.deque_carriage(deque_domain))))).note
back  = next(iter(storage.mem_get(
    memory.deque_prev(memory.deque_carriage(deque_domain))))).note
```

### Iteration rule (implementation)

Each step:

1. **Integrity** — sentinel is identified by `pod == P0`. The sentinel MUST have an identity `PAYLOAD`; a carriage MUST have a non-identity `PAYLOAD`. Either violation returns `FailedPrecondition` (the deque is malformed).
2. **Advance** — on a carriage, follow the matching-direction key (`RIGHT` for forward, `LEFT` for backward) to the next neighbor. On the sentinel, follow the *opposite*-direction key — sentinel's `LEFT`/`RIGHT` are anchor pointers, so the opposite key takes you to the appropriate end.
3. **Yield** — yield the chunk you advanced to. Stop when the next pointer is identity.

The advance-then-yield order is what makes the iteration exclusive of `start`.

## Hierarchy: the `CHILDREN` slot

Each carriage's `CHILDREN` 👨‍👩‍👧‍👦 slot can point at the sentinel of another deque (or any other chunk). Attach one at push time via the `children` argument; query it via the `DequeChildren(parent)` selector.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Push a parent carriage whose CHILDREN points at a child deque's sentinel.
storage.mem_set(memory.deque_appender(
    parent_domain,
    memory.with_sparkle(payload_domain, "B"),
    children=memory.deque_carriage(child_domain),
))

# Walk the child deque from the parent.
for chunk in storage.mem_get(
    memory.deque_forward(
        memory.deque_children(
            memory.deque_carriage(parent_domain, parent_carriage_pod)))):
    print(chunk.note)
```
{{#endtab}}
{{#tab name="Go"}}
```go
// Push parent carriage with CHILDREN attached.
p.Memory.Set(ctx, memory.DequeAppender(
    parentDomain, payloadSelector,
    memory.PChildren(memory.DequeCarriage(childDomain, nil)),
))

// Walk the child deque.
for c := range memory.SelectorIter(ctx, view,
    memory.DequeForward(memory.DequeChildren(
        memory.DequeCarriage(parentDomain, &parentCarriagePod)))) {
    fmt.Println(c.Note)
}
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
// Build args with children attached.
let mut args = chunk_producer_proto::Args::default();
args.children = Some(Box::new(deque_carriage(child_domain, None).to_proto()?));
storage.set(producers::deque_appender(parent_domain, payload_sel, args))?;

// Walk the child deque.
let sel = deque_forward(Box::new(deque_children(Box::new(
    deque_carriage(parent_domain, Some(parent_carriage_pod)),
))));
```
{{#endtab}}
{{#endtabs}}

`DequeChildren(parent)` yields zero chunks (no error) when the parent has identity `CHILDREN` or is missing entirely. Hierarchical traversal is the caller's job — walk a parent deque, recurse into `DequeChildren` on each carriage.
