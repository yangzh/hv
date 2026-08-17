# LearnerPool

**LearnerPool** is an aggregate over member [Learners](../api/hv/learner.md) for improved scalability. Instead of dedicating one Learner to each address, a pool holds a fixed roster of member Learners that collectively supports learning tasks on-the-fly.

In this sense, an address does not directly lead to a single member, instead, it *addresses* a small access circle of members, which can expand based on actual need. Structurally a classic Learner is the degenerate case where each address trivially maps to a single Learner.

## Why a pool

A single Learner has a hard capacity ceiling: as more distinct patterns are experienced, each one's share of ON bits shrinks, until they become undistinguishable from random noise. This can happen past a few unique dozen patterns.

This limitation of capacity (of individual learner) is unsuitable in various scenarios:
- high fan-out addresses (hubs) saturate and silently forget everything;
- the long tail of low fan-out addresses wastes almost all of its dedicated capacity.

A pool solves both issues exactly as its name suggests, by pooling many member Learners together. Most light addresses still get a nearly-private member, while heavy addresses recruit as many members as their content genuinely needs, up to the whole pool. At the end of the day, individual member can serve a mixture of low and high fan-out addresses, computed internally by its own scheduling logic. 

The internal "load balancing" is mathematically sound, stable, and requires no manual intervention. The member Learners organize organically rather than piling up naively: if each Learner is a basic "neuron", a LearnerPool is an organism which behaves coherently toward a common goal.

### Fixed capacity

Unlike the typical arrangement of one Learner per tracked entity, a LearnerPool uses a fixed amount of resources: entities of varying fan-out share the same pool.

The roster size is set at pool creation and cannot grow afterwards: there is currently no incremental expansion short of a full retrain. When every member a write could reach is full, the pool refuses the write rather than degrade what it already holds. Size pools with headroom for the corpus they are meant to absorb.

### Diversity vs. repetition

The `LeanerPool` can pick the suitable learner by ensuring the member has enough capacity, and the incoming pattern can be recalled reliably later, among other criteria. Note we examine [diversity margin](learner.md#diversity-margin) of each member, so expansion follows diversity (of experiences) rather than crude repetition.

This also implies the scheduler can always find one suitable member, unless the whole pool is out of capacity, in which case the write will fail: all members can be used as reserve as needed.

So another way to understand LearnerPool is an address-able collection of infinitely scalable (up to the fixed capacity) learners.

### Using bigger learners

Using bigger learners (for example, `10bit`, `12bit`, etc) is a complete orthogonal direction for expanding the capacity. However, if you are comfortable with simpler `8bit` learners, adding more members will be quite straightforward to add overall capacity.

Another practical consideration, `8bit` model naturally supports low-level SIMD from all supported platforms, which can boost performance significantly. `10bit`/`12bit`, however, does NOT natively support this level of optimization: so stick with `8bit` if you really care about performance, and fortunately `LearnerPool` can mitigate the capacity limitation.

## API overview

A `LearnerPool` is conceptually determined only by the total count of member learners.

## Persistence

A pool serializes as a small self-describing sentinel — its metadata as a `LearnerPoolProto` — plus one ordinary chunk per trained member; blank members need nothing. Loading is a single call (`memory.load_learner_pool` in Python): the sentinel is read from the substrate, the pool rebuilds itself from its own metadata with no external configuration, and the trained members hydrate in place.
