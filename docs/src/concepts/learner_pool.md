# LearnerPool

**LearnerPool** is an aggregate over member [Learners](../api/hv/learner.md) for improved scalability. Instead of dedicating one Learner to one particular use case, a pool holds a fixed roster of member Learners that can collectively support many learning tasks in parallel.

Each learning task is identified by a particular address, so the conceptual design goal is to have a Learner-like component where an observation can be written into a given address, and with improved capacity.

The solution LearnerPool takes is to return a small access circle of member Learners for each addressed access, which can expand based on actual need.

## Why a pool

A single Learner has a hard capacity ceiling: as more distinct patterns are experienced, each pattern's share of ON bits dilutes, until they become indistinguishable from random noise. This can happen past a few dozen unique patterns for an 8bit Learner, for example.

This capacity limitation (of the classic Learner) bites in various scenarios:
- high fan-out addresses saturate and silently forget everything;
- the long tail of low fan-out addresses wastes almost all of their dedicated capacity.

A pool solves both issues exactly as its name suggests, by pooling many Learners together. Most light addresses still get a nearly-private member, while heavy addresses recruit as many members as their content genuinely needs, up to the whole pool. At the end of the day, an individual member can serve a mixture of low and high fan-out addresses, orchestrated internally by the pool's own scheduling logic. As far as the pool is concerned, the overall storage budget is fixed at construction time, and won't grow unbounded as we have more learning tasks.

The internal "orchestration" (or rewiring) is mathematically sound, stable, and requires no manual intervention. The member Learners organize organically rather than piling up naively: if each Learner were a basic "neuron", a LearnerPool is then akin to an organism that behaves intelligently and coherently toward a common goal.

### Fixed resource consumption

Unlike the naive arrangement of one Learner per learning task which can grow unbounded, a LearnerPool uses a fixed amount of resources: entities of varying fan-out intelligently share the same pool.

The roster size is set at pool creation and won't grow afterwards: there is currently no incremental expansion short of a full retrain. When every member a write could reach is full, the pool refuses the write rather than degrade what it already holds.

So another way to understand LearnerPool: it's an addressable collection of elastically scalable (up to the fixed pool capacity) Learners.

### Recruiting member Learners

The `LearnerPool` recruits a suitable member Learner by ensuring the incoming pattern can be recalled reliably later.

This also implies the pool's scheduler can always find one suitable member, unless the whole pool is out of capacity, in which case the write will fail: all members can be used as reserves as needed.

### Using bigger learners

Using bigger Learners (for example, `10bit`, `12bit`, etc.) is a completely orthogonal direction for expanding capacity. However, adding more members can be straightforward, and most of the time more effective.

Another practical consideration: `8bit` offsets are **byte-aligned** (one byte per segment; `16bit` is two), which unlocks low-level SIMD on all supported platforms and boosts performance significantly. `10bit`/`12bit`/`14bit` offsets are not byte-aligned and do not vectorize this way: so stick with `8bit` if you care about performance.

Jump to the API reference for [LearnerPool](../api/hv/learner_pool.md).
