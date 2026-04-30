# Deque 🚂🚃🚃🚃

A doubly-linked, payload-carrying chunk data structure built on Octopus chunks. The deque is a *train of carriages* — each carriage 🚃 carries one payload chunk, and carriages couple to their neighbors at LEFT ⬅️ / RIGHT ➡️.

## Shape

A deque occupies its own 64-bit `deque_domain`. The structure has two kinds of chunks:

- **Sentinel locomotive 🚂** — the chunk at `(deque_domain, P0)`. Anchors both ends of the train. Its `LEFT` slot points at the leftmost carriage, its `RIGHT` slot at the rightmost. Its `PAYLOAD` slot is identity (no payload).
- **Carriage 🚃** — a chunk at `(deque_domain, carriage_pod)` for some non-zero pod. Each carriage is a specialized Octopus with three slots:
    - `PAYLOAD` 📨 — points at the actual payload chunk in item memory (`Sparkle(payload_domain, payload_pod)`). Always non-identity.
    - `LEFT` ⬅️ — id-Sparkle of the previous carriage, or identity if leftmost.
    - `RIGHT` ➡️ — id-Sparkle of the next carriage, or identity if rightmost.

```text
            sentinel 🚂                       carriages 🚃 🚃 🚃
       (deque_domain, P0)              (deque_domain, *)
       ┌──────────────┐                ┌─────┐  ┌─────┐  ┌─────┐
       │ PAYLOAD = ⊥  │                │ A   │  │ B   │  │ C   │
       │ LEFT  ────────────────────────►│     │  │     │  │     │
       │ RIGHT ──────────────────────►──┴────┴──┴─────┴──┴─────┘
       └──────────────┘
```

## Pushing

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# memory.deque_appender / memory.deque_prepender consume a Selector for the payload.
storage.mem_set(memory.deque_appender(deque_domain, memory.with_sparkle(payload_domain, "A")))
storage.mem_set(memory.deque_prepender(deque_domain, memory.with_sparkle(payload_domain, "Z")))
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

Each push rewrites **three chunks** atomically through one mutable view:

1. The new carriage at `(deque_domain, fresh_pod)`.
2. The previous tail/head carriage, with its tail-side neighbor link updated to the new carriage. (Skipped on the first push, when the deque is empty.)
3. The sentinel, with its tail-side anchor pointer updated to the new carriage. The head-side pointer is updated only when the deque transitions from empty to one element.

The sentinel is auto-created on the first push — no separate "init deque" step is needed.

> ⚠️ **Single-writer per deque.** Concurrent pushes from independent mutable views on the same deque WILL race on the sentinel and on the previous tail/head — last-write wins, with dropped pushes possible. Callers expecting concurrent appenders must synchronize externally (e.g., serialize through a single goroutine/task, or take an external lock keyed on `deque_domain`). Reads through a `View` are always snapshot-consistent per chunk.

## Iterating

`DequeForward` / `DequeBackward` walk the train, yielding each carriage's *payload chunk*. The starting point is itself a Selector — pass `DequeCarriage(domain)` (with no pod) to start from the sentinel for a full-deque iteration, or `DequeCarriage(domain, pod)` to start from a specific carriage.

The starting carriage's payload **is** yielded too (inclusive start), matching C++/Python iterator conventions. The sentinel itself yields no payload (its `PAYLOAD` is identity), so starting from the sentinel produces the natural "iterate the whole deque" semantic.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Whole-deque iteration from the sentinel.
for chunk in storage.mem_get(memory.deque_forward(memory.deque_carriage(deque_domain))):
    print(chunk.note)

# Iterate from a specific carriage onward (inclusive of that carriage).
for chunk in storage.mem_get(memory.deque_backward(memory.deque_carriage(deque_domain, carriage_pod))):
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

// From a specific carriage onward.
for c := range memory.SelectorIter(ctx, view,
    memory.DequeBackward(memory.DequeCarriage(dequeDomain, &carriagePod))) {
    fmt.Println(c.Note)
}
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
// Whole-deque iteration.
let sel = deque_forward(Box::new(deque_carriage(deque_domain.clone(), None)));

// From a specific carriage onward.
let sel = deque_backward(Box::new(deque_carriage(
    deque_domain.clone(),
    Some(carriage_pod),
)));
```
{{#endtab}}
{{#endtabs}}

## Iteration rule

Three rules handle both starting cases (sentinel or carriage) uniformly:

1. **Identity** — the sentinel is identified by `pod == P0`. The sentinel MUST have an identity `PAYLOAD`; a carriage MUST have a non-identity `PAYLOAD`. Either violation returns `FailedPrecondition` (the deque structure is malformed).
2. **Yield** — yield the current chunk's payload only if it's a carriage.
3. **Advance** — for a carriage, follow the matching-direction key (`RIGHT` for forward, `LEFT` for backward) to its next neighbor. For the sentinel, follow the *opposite-direction* key — sentinel's `LEFT`/`RIGHT` are anchor pointers at the leftmost/rightmost, not neighbor pointers, so the opposite key takes you to the appropriate end. Stop when the next pointer is identity.

This unification means starting at the sentinel and starting at a carriage use the same loop — there's no special-case branch in iteration.
