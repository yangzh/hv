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

## Footprint

| | |
|-|-|
| substrate on disk (both languages) | 19 MB |
| pool members per language | 65,536 × 8-bit Learners |
| training | one pass over the corpus, no optimization loop |
