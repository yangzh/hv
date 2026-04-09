#!/usr/bin/env python3
"""Mexican Dollar: analogical reasoning with hypervectors.

"What's the Dollar of Mexico?" → Peso
"What's the Washington DC of Mexico?" → Mexico City

See docs: https://yangzh.github.io/hv/examples/mexican_dollar/index.html
"""

from kongming import hv

model = hv.MODEL_64K_8BIT
so = hv.SparseOperation(model, "knowledge", 0)

# Create role markers
country_code = hv.Sparkle.from_word(model, "role", "country_code")
capital = hv.Sparkle.from_word(model, "role", "capital")
currency = hv.Sparkle.from_word(model, "role", "currency")

# Create fillers
usa = hv.Sparkle.from_word(model, "country", "usa")
mex = hv.Sparkle.from_word(model, "country", "mex")
swe = hv.Sparkle.from_word(model, "country", "swe")
dc = hv.Sparkle.from_word(model, "capital", "dc")
mexico_city = hv.Sparkle.from_word(model, "capital", "mexico_city")
stockholm = hv.Sparkle.from_word(model, "capital", "stockholm")
dollar = hv.Sparkle.from_word(model, "currency", "dollar")
peso = hv.Sparkle.from_word(model, "currency", "peso")
krona = hv.Sparkle.from_word(model, "currency", "krona")

# Encode each country as role-filler bundles
us_record = hv.bundle(
    hv.Seed128.random(so),
    hv.bind(country_code, usa),
    hv.bind(capital, dc),
    hv.bind(currency, dollar),
)
mexico_record = hv.bundle(
    hv.Seed128.random(so),
    hv.bind(country_code, mex),
    hv.bind(capital, mexico_city),
    hv.bind(currency, peso),
)
sweden_record = hv.bundle(
    hv.Seed128.random(so),
    hv.bind(country_code, swe),
    hv.bind(capital, stockholm),
    hv.bind(currency, krona),
)

# Transfer vector: Mexico / US
transfer_to_mexico = hv.release(mexico_record, us_record)

# "What's the Dollar of Mexico?"
mexican_dollar = hv.bind(dollar, transfer_to_mexico)
print(f"peso overlap:  {hv.overlap(mexican_dollar, peso)}")  # high!
print(f"dollar overlap: {hv.overlap(mexican_dollar, dollar)}")  # ~1 (noise)
print(f"krona overlap:  {hv.overlap(mexican_dollar, krona)}")  # ~1 (noise)

# "What's the Washington DC of Mexico?"
mexican_dc = hv.bind(dc, transfer_to_mexico)
print(f"mexico_city overlap: {hv.overlap(mexican_dc, mexico_city)}")  # high!

# Transfer to Sweden works the same way
transfer_to_sweden = hv.release(sweden_record, us_record)
swedish_dollar = hv.bind(dollar, transfer_to_sweden)
print(f"krona overlap: {hv.overlap(swedish_dollar, krona)}")  # high!
