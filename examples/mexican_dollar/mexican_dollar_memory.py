#!/usr/bin/env python3
"""Mexican Dollar with AnalogicalReasoner and in-memory storage.

Uses near-neighbor search to find analogical matches automatically.
Storage goes through the ChunkProducer API (the Go/Rust idiom): producers
stage chunks against a batched mutable view; nothing is put() by hand.

See docs: https://yangzh.github.io/hv/examples/mexican_dollar/index.html
"""

from kongming import hv, memory

model = hv.MODEL_64K_8BIT
store = memory.InMemory(model)

keys = ["capital", "currency", "country_code"]
FILLER_DOMAIN = 0

countries = {
    "USA": ["dc", "USD", "USA"],
    "MEX": ["mexicoCity", "MXN", "MEX"],
    "SWE": ["stockholm", "SEK", "SWE"],
}

# Terminals for the fillers — NNS needs them as searchable items — then one
# Octopus record per country, its key-aligned values picked by item key.
with store.new_mutable_view() as view:
    for values in countries.values():
        for word in values:
            memory.new_terminal(FILLER_DOMAIN, word).produce(view)
    for name, values in countries.items():
        memory.from_key_values(
            "country",
            name,
            keys,
            memory.joiner(*[memory.by_item_key(FILLER_DOMAIN, w) for w in values]),
            note=name,
        ).produce(view)
    # auto-commits on __exit__

# Feature probes for the queries (same identities the terminals carry).
fillers = {w: hv.Sparkle.from_word(model, FILLER_DOMAIN, w) for values in countries.values() for w in values}

# Retrieve stored records
us_code = store.get("country", "USA").code
mex_code = store.get("country", "MEX").code
swe_code = store.get("country", "SWE").code

with store.new_view() as view:
    # "What is the USD of Mexico?"
    result = memory.first_picked(
        view,
        memory.nns(memory.analogical_reasoner(memory.with_code(mex_code), src=us_code, feature=fillers["USD"])),
    )
    print(f"USD of Mexico: {result.id}")  # → ✨:🌱MXN

    # "What is the Washington DC of Mexico?"
    result = memory.first_picked(
        view,
        memory.nns(memory.analogical_reasoner(memory.with_code(mex_code), src=us_code, feature=fillers["dc"])),
    )
    print(f"DC of Mexico: {result.id}")  # → ✨:🌱mexicoCity

    # "What is the Dollar of Sweden?"
    result = memory.first_picked(
        view,
        memory.nns(memory.analogical_reasoner(memory.with_code(swe_code), src=us_code, feature=fillers["USD"])),
    )
    print(f"USD of Sweden: {result.id}")  # → ✨:🌱SEK
