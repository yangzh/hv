# LearnerPool 🎱

A **LearnerPool** is an aggregate over member [Learners](learner.md) for
improved scalability: a fixed roster of members that collectively serves
many address-keyed learning tasks in parallel. Writes to an address land on
a small **access circle** of members; heavy addresses recruit more members
as needed while light addresses keep a nearly-private one. See
[the concepts chapter](../../concepts/learner_pool.md) for why and how.

## Constructors

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# model, member domain, roster size
pool = hv.LearnerPool(hv.MODEL_64K_8BIT, "pool", 65536)
pool.init()          # fill the still-empty roster with fresh Learners
```
{{#endtab}}
{{#tab name="Go"}}
```go
model := api.Model_MODEL_64K_8BIT
pool := hv.NewLearnerPool(model, domainPool, hv.GetGlobalEnv().RngHint, 65536)
pool.Init()
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let model = Model::Model64k8bit;
let mut pool = LearnerPool::new(model, domain_pool, flag_rng(), 65536);
pool.init();
```
{{#endtab}}
{{#endtabs}}

## Writing

`bundle` stores `data` under `addr`. Omitting the address stores the pattern
auto-associatively.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
pool.bundle(data, addr=addr)            # hetero-associative write
pool.bundle(data, addr=addr, multiple=3)  # with weight
```
{{#endtab}}
{{#tab name="Go"}}
```go
pool.Bundle(addr, data, 1)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
pool.bundle(Some(&addr.core()), &data.core(), 1)?;
```
{{#endtab}}
{{#endtabs}}

When reaching the collective capacity of the pool, it refuses future write.

## Reading

We support wwo read scenarios:

- **`support`** — evidence that `probe` was stored under `addr` (a scalar,
  noise-subtracted). This is the discriminative read: "how strongly does
  the pool associate addr → probe?"
- **`read_members`** — the content/experiences of the circle's members, one hypervector each. This is the generative read: use them as attractors for near-neighbor search when you don't know the `probe` in advance.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
s = pool.support(addr, probe)      # scalar evidence

for attractor in pool.read_members(addr):
    ...                            # feed into NNS / overlap checks
```
{{#endtab}}
{{#tab name="Go"}}
```go
s := pool.Read(addr).Support(probe)

// selector form, composing with the memory query machinery:
memory.AccessCircleRead(pool, addr, nil)
```
{{#endtab}}
{{#tab name="Rust"}}
```rust
let s = pool.read(&addr).support(probe);
```
{{#endtab}}
{{#endtabs}}

## Introspection

```python
pool.total()             # fixed member count
pool.load()              # total write mass W = Σ member ages
pool.unique_estimated()  # ≈ distinct items held in this pool
pool.member_domain()     # the members' domain
```

## Persistence

A pool serializes as a small self-describing sentinel — its metadata as a `LearnerPoolProto` — plus one ordinary chunk per trained member.

The pool serializes as metadata plus per-member contents. Round-trip via
the memory layer: the pool sentinel is self-describing, so loading needs no
config.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# load from a substrate view in one call.
pool = memory.load_learner_pool(view, member_domain)

# or manually: metadata first, members via a loader callback
pool = hv.LearnerPool.from_proto_bytes(raw)
pool.hydrate(lambda domain, pod: ...)   # return Learner or None (blank)
```
{{#endtab}}
{{#endtabs}}

## See also

- [LearnerPool concepts](../../concepts/learner_pool.md) — why a pool,
  access circles, diversity vs. repetition.
- [Learner](learner.md) — the member primitive.
