#!/usr/bin/env python3
"""Mexican Dollar with AnalogicalReasoner and in-memory storage.

Uses near-neighbor search to find analogical matches automatically.

See docs: https://yangzh.github.io/hv/examples/mexican_dollar/index.html
"""

from kongming import hv, memory

model = hv.MODEL_64K_8BIT
store = memory.InMemory(model)

keys = ["capital", "currency", "country_code"]

# Store individual fillers — NNS needs them as searchable items
fillers = {}
for word in ["dc", "USD", "USA", "mexicoCity", "MXN", "MEX", "stockholm", "SEK", "SWE"]:
    s = hv.Sparkle.from_word(model, 0, word)
    store.put(s)
    fillers[word] = s

# Store country records as Octopus composites
store.put(hv.Octopus(hv.Seed128("country", "USA"), keys, fillers["dc"], fillers["USD"], fillers["USA"]))
store.put(hv.Octopus(hv.Seed128("country", "MEX"), keys, fillers["mexicoCity"], fillers["MXN"], fillers["MEX"]))
store.put(hv.Octopus(hv.Seed128("country", "SWE"), keys, fillers["stockholm"], fillers["SEK"], fillers["SWE"]))

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
