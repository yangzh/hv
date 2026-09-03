# Evaluations

## Setup

> **Note**: the numbers below were measured on the **Rust engine** over the full held-out validation tier (the Go and Rust engines are kept at bit-parity and decode identically).

Combined corpus of 4231 English + 4231 Chinese sentences for training; the statistics live in a unified LearnerPool (`MODEL_64K_8BIT`) per language. 

**Validation tier**: 950 held-out sentences — 484 English (5.8K tokens) and 466 Chinese (5.1K tokens), never seen in training.

## Substrate stats

The entire trained model — every transition statistic and open-class inventory for English and Chinese — is a **17 MB** substrate on disk.

The trained substrate: 336,564 chunks, with Payload types:
- 192,731 SPARKLE;
- 58,129 OCTOPUS;
- 85,704 LEARNER, that made up 2 LearnerPools;

Pool health, per 65,536-member language pool:

| | en | zh |
|-|---------|---------|
| trained members | 46,339 | 39,365 |
| open / closed | 42,643 / 3,696 | 35,036 / 4,329 |
| total load (Σ age) | 401,792 | 457,194 |
| mean member age | 8.7 | 11.6 |
| diversity margin p10 / p50 / p90 | 51 / 128 / 256 | 45 / 128 / 256 |

## Held-out parse quality

Production configuration (coarse tier on), per language and combined
(full-tier run on the pre-redesign substrate; the sampled tables below are
current):

| metric | English | Chinese | mixed |
|--------|---------|---------|-------|
| full-parse | 99.2% | 99.4% | 99.3% |
| head attachment | 74.9% | 57.0% | 66.5% |
| upos | 95.5% | 87.6% | 91.8% |
| deprel | 77.6% | 64.3% | 71.3% |
| lemma | 92.9% | 92.1% | 92.5% |
| entity recall | 56.0% | 63.5% | 59.2% |
| entity precision | 62.5% | 76.2% | 68.1% |

Entity matching is a multiset match on (type, text) between the gold
entities and the surfaced ones, over parsed sentences.

## Training corpus vs held-out

The same sweep per language over sampled tiers (English at 10%, Chinese at
5%), on the consolidated substrate: the training corpus bounds
what the substrate retained; the held-out gap is the generalization cost.

| metric | en training (422) | en val (65) | zh training (215) | zh val (24) |
|--------|-------------------|-------------|-------------------|-------------|
| full-parse | 98.6% | 96.9% | 98.6% | 100% |
| head attachment | 81.9% | 71.1% | 70.1% | 58.5% |
| upos | 97.5% | 93.5% | 91.8% | 85.3% |
| deprel | 89.8% | 77.3% | 78.2% | 63.8% |
| lemma | 96.6% | 91.3% | 97.4% | 91.7% |
| entity recall | 77.3% | 62.9% | 76.6% | 72.7% |
| entity precision | 80.1% | 75.3% | 78.3% | 78.0% |

## The coarse tier's contribution

Ablating the coarse-to-fine backoff on the same substrate and the same
full validation tier (tier off → on), head attachment:

| slice | tier off | tier on | Δ |
|-------|----------|---------|----|
| English (484) | 72.7% | 74.9% | +2.2 |
| Chinese (466) | 54.5% | 57.0% | +2.5 |
| mixed (950) | 64.1% | 66.5% | **+2.4** |

The gains come from trained coarse-class evidence rescuing transitions the
fine-grained statistics never saw — not from structural guessing.

## Decode throughput

Single decoder, sequential decode, on the same MacBook Air that trains the
model in ~12 minutes (sampled tiers, consolidated substrate):

| | combined tokens/s | val tokens/s |
|-|-------------------|--------------|
| English | 21.9 | 20.8 |
| Chinese | 4.1 | 4.7 |

The width-addressed dense posting index (no hashing on the decode-side
Collect/Add) shaved ~10 ms/token off both languages on top of the pool
consolidation: +23% for English; Chinese remains dominated by pool-read
volume from beam churn, not per-probe cost.
