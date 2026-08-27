# Evaluations

> **Note**: the numbers below were measured on the **Go engine** against a held-out corpus. They will be re-measured and confirmed from the Rust engine, along with decode throughput.

**Setup**: combined corpus of 4231 English + 4231 Chinese sentences,
`MODEL_64K_8BIT`, a unified LearnerPool per language. The entire trained model — every transition statistic and open-class inventory for both languages — is a **19 MB** substrate on disk.

## Held-out parse quality

First-100 held-out validation slices, per language:

| metric | English | Chinese |
|--------|---------|---------|
| full-parse | 98% | 99% |
| head attachment | 78.3% | 53.8% |
| upos | 96.3% | 89.6% |
| deprel | 81.1% | 69.0% |
| lemma | 96.9% | 94.7% |
| entity recall | 67.6% | 70.5% |
| entity precision | 78.4% | 84.1% |

On the broader mixed validation sample (both languages, 657 tokens):
head 66.8%, upos 91.3%, deprel 71.5%, with every sentence producing a
full parse.

## The coarse tier's contribution

Ablating the coarse-to-fine backoff (same substrate, tier off → on):

| slice | head, tier off | head, tier on | Δ |
|-------|---------------|---------------|----|
| mixed val | 62.9% | 66.8% | **+3.9** |
| English first-100 | 73.2% | 76.8% | +3.6 |
| Chinese first-100 | 47.5% | 52.1% | **+4.6** |

English entity precision also rises with the tier (74.2% → 78.4%); the
gains come from trained coarse-class evidence rescuing transitions the
fine-grained statistics never saw — not from structural guessing.

## Footprint

| | |
|-|-|
| substrate on disk (both languages) | 19 MB |
| pool members per language | 65,536 × 8-bit Learners |
| training | one pass over the corpus, no optimization loop |
