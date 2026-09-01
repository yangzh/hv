# Evaluations

> **Note**: the numbers below were measured on the **Rust engine** over the full held-out validation tier (the Go and Rust engines are kept at bit-parity and decode identically).

**Setup**: combined corpus of 4231 English + 4231 Chinese sentences,
`MODEL_64K_8BIT`, a unified LearnerPool per language. The entire trained model — every transition statistic and open-class inventory for both languages — is a **19 MB** substrate on disk.

**Validation tier**: 950 held-out sentences — 484 English (5.8K tokens) and 466 Chinese (5.1K tokens), never seen in training.

## Held-out parse quality

Production configuration (coarse tier on), per language and combined:

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
5%): the combined (training) corpus bounds what the substrate retained; the
held-out gap is the generalization cost.

| metric | en combined (422) | en val (65) | zh combined (215) | zh val (24) |
|--------|-------------------|-------------|-------------------|-------------|
| full-parse | 99.1% | 100% | 96.7% | 100% |
| head attachment | 81.5% | 76.5% | 64.6% | 55.8% |
| upos | 97.1% | 93.3% | 90.2% | 87.2% |
| deprel | 88.2% | 78.2% | 74.9% | 62.6% |
| lemma | 96.6% | 91.3% | 97.0% | 92.1% |
| entity recall | 75.4% | 59.5% | 64.6% | 72.7% |
| entity precision | 76.3% | 67.0% | 71.9% | 80.0% |

The 24-sentence Chinese validation slice is small — its entity numbers
(above the training tier's) are sampling noise, not signal. The pattern
that holds across slices: English retains and generalizes several points
above Chinese on structure (head/deprel), while lemma recovery is
language-neutral.

## Sampling stability

Held-out metrics at three scales — 2.5% and 10% per-language samples
against the full tier (the full run predates the expectation-based pool
reads; the sampled columns include them):

| metric | 2.5% (30) | 10% (108) | full (950) |
|--------|-----------|-----------|------------|
| head attachment | 67.8% | 69.5% | 66.5% |
| upos | 90.3% | 91.0% | 91.8% |
| deprel | 72.0% | 72.1% | 71.3% |
| lemma | 89.4% | 91.4% | 92.5% |
| entity recall | 62.3% | 61.5% | 59.2% |
| entity precision | 66.7% | 69.7% | 68.1% |

The 30-sentence sample wobbles a couple of points; the 10% sample tracks
the full tier within ~1–3, with the head and entity gains carried by the
newer per-entry pool reads.

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
model in under ten minutes:

| | tokens/s |
|-|----------|
| English | 19.1 |
| Chinese | 5.2 |

The coarse backoff buys its accuracy with extra pool reads: with the tier
off, throughput rises to 24.8 (en) / 7.3 (zh) tokens/s.

## Substrate stats

The trained substrate: 343,772 chunks in a 19.0 MB archive, with Payload types:
- 192,731 SPARKLE;
- 58,129 OCTOPUS;
- 92,912 LEARNER, that made up 2 LearnerPools;

Pool health, per 65,536-member language pool:

| | en | zh |
|-|---------|---------|
| trained members | 49,087 | 43,825 |
| open / closed | 40,816 / 8,271 | 32,894 / 10,931 |
| total load (Σ age) | 401,792 | 457,194 |
| mean member age | 8.2 | 10.4 |
| diversity margin p10 / p50 / p90 | 11 / 128 / 256 | 10 / 128 / 256 |

