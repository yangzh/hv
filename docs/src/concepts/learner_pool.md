# LearnerPool

**LearnerPool** is an aggregate over member [Learners](../api/hv/learner.md) for improved scalability. Instead of dedicating one Learner to one particular use case, a pool holds a fixed roster of member Learners that collectively supports many learning tasks in parallel.

Each learning task is identified by a particular address: conceptually writing to a given address, we hope to have a Learner-like unit with improved capacity.

So instead of naively lead to a single member by an address, LearnerPool returns a small access circle of member Learners, which can expand based on actual need.

## Why a pool

A single Learner has a hard capacity ceiling: as more distinct patterns are experienced, each one's share of ON bits dilutes, until they become undistinguishable from random noise. This can happen past a few dozen unique patterns for an 8bit Learner, for example.

This limitation of capacity (of classic learner) is unsuitable in various scenarios:
- high fan-out addresses saturate and silently forget everything;
- the long tail of low fan-out addresses wastes almost all of its dedicated capacity.

A pool solves both issues exactly as its name suggests, by pooling many member Learners together. Most light addresses still get a nearly-private member, while heavy addresses recruit as many members as their content genuinely needs, up to the whole pool. At the end of the day, individual member can serve a mixture of low and high fan-out addresses, orchestrated internally by its own scheduling logic. 

The internal "orchestration" (or rewiring) is mathematically sound, stable, and requires no manual intervention. The member Learners organize organically rather than piling up naively: if each Learner was a basic "neuron", a LearnerPool is then an organism which behaves intelligently and coherently toward a common goal.

### Fixed resource consumption

Unlike the typical arrangement of one Learner per learning task which can grow unbounded, a LearnerPool uses a fixed amount of resources: entities of varying fan-out intelligently share the same pool.

The roster size is set at pool creation and cannot grow afterwards: there is currently no incremental expansion short of a full retrain. When every member a write could reach is full, the pool refuses the write rather than degrade what it already holds.

So another way to understand LearnerPool: it's an address-able collection of infinitely scalable (up to the fixed capacity) learners.

### Diversity vs. repetition

The `LearnerPool` can pick the suitable member learner by ensuring the incoming pattern can be recalled reliably later. Note expansion follows diversity (of experiences) rather than crude repetition.

This also implies the scheduler can always find one suitable member, unless the whole pool is out of capacity, in which case the write will fail: all members can be used as reserve as needed.

### Using bigger learners

Using bigger learners (for example, `10bit`, `12bit`, etc) is a completely orthogonal direction for expanding capacity. However, if you are comfortable with simpler `8bit` learners, adding more members will be more straightforward.

Another practical consideration: `8bit` offsets are **byte-aligned** (one byte per segment; `16bit` is two), which unlocks low-level SIMD on all supported platforms and boosts performance significantly. `10bit`/`12bit`/`14bit` offsets are not byte-aligned and do not vectorize this way — so stick with `8bit` if you care about performance.

Jump to the API reference for [LearnerPool](../api/hv/learner_pool.md).
