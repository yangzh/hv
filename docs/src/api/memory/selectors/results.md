# Working with Results

## FirstPicked — get the first match

Returns the first chunk matching the selector. Returns an error if nothing is found.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Returns the code (HyperBinary) of the first match
code = memory.first_picked(view, selector)

# Returns the full Chunk object (with .id, .code, .note, .extra)
chunk = memory.first_picked_chunk(view, selector)
print(chunk.id, chunk.code, chunk.note)
```
{{#endtab}}
{{#endtabs}}

## Iterator — iterate all matches

{{#tabs global="lang"}}
{{#tab name="Python"}}
Not available as iterator in Python. Use `mem_get()` for batch reads.
{{#endtab}}
{{#endtabs}}

## mem_get — high-level batch read

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
results = storage.mem_get(selector)
for hv in results:
    print(hv)
```
{{#endtab}}
{{#endtabs}}

<div class="callout callout-warning">
<div class="callout-title">Python Selector Consumption</div>
Selectors passed to combinators (<code>range_sel</code>, <code>nns</code>, <code>joiner</code>, etc.) are <strong>consumed</strong> — they cannot be reused after being passed. This mirrors Rust's move semantics. Attempting to reuse a consumed selector raises <code>ValueError</code>.
</div>
