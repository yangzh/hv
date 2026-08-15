# LearnerPool

**LearnerPool** is an aggregate over member [Learners](../api/hv/learner.md) for improved scalability. Instead of dedicating one Learner to each address, a pool holds a fixed roster of member Learners shared by *every* address.

In this sense, an address does not own a member, it *addresses* a small access circle of members, which can expand based on actual need. Structurally a classic Learner is the degenerate case where each address simply maps to a single Learner.

## Why a pool

A single Learner has a hard capacity ceiling: as more distinct patterns are bundled in, each one's recoverable signal shrinks, until — past a few dozen patterns — none can be told apart from noise.

This is undesirable in various scenarios:
- high fan-out addresses (hubs) saturate and silently forget;
- the long tail of low fan-out addresses wastes almost all of its dedicated capacity.

A pool solves both issues exactly as its name suggests — by pooling many member Learners together. Most light addresses still get a nearly-private member, while heavy addresses recruit as many members as their content genuinely needs, up to the whole pool. When to recruit is decided by each member's [diversity margin](learner.md#diversity-margin), so growth follows diversity rather than repetition.

The internal "load balancing" is mathematically sound, stable, and requires no manual intervention. The member Learners organize organically rather than piling up at random: if each Learner is a basic "neuron", a LearnerPool is an organism which behaves coherently toward a common goal.

## Persistence

A pool serializes as a small self-describing sentinel — its metadata as a `LearnerPoolProto` — plus one ordinary chunk per trained member; blank members need nothing. Loading is a single call (`memory.load_learner_pool` in Python): the sentinel is read from the substrate, the pool rebuilds itself from its own metadata with no external configuration, and the trained members hydrate in place.

## Capacity is fixed

Unlike the typical arrangement of one Learner per tracked entity, a LearnerPool uses a fixed amount of resources: entities of varying fan-out pool together and share it.

The roster size is set at pool creation and cannot grow afterwards: there is no incremental widening short of a full retrain. When every member a write could reach is full, the pool refuses the write rather than degrade what it already holds. Size pools with headroom for the corpus they are meant to absorb.
