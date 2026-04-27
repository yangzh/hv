# Working with Results

## FirstPicked — get the first match

Returns the first chunk matching the selector. Returns an error if nothing is found.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Returns the first matching Chunk (with .id, .code, .note, .extra)
chunk = memory.first_picked(view, selector)
print(chunk.id, chunk.code, chunk.note)
```
{{#endtab}}
{{#endtabs}}

## mem_get — eager batch read (Chunks only)

Returns every match as a `list[Chunk]`. **No extras** — any per-result `SelectorExtra` produced by the selector (e.g. NNS scores) is discarded. Use this when you only need the Chunks.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
chunks = storage.mem_get(selector)        # list[Chunk]
for chunk in chunks:
    print(chunk.id, chunk.note)
```
{{#endtab}}
{{#endtabs}}

## lazy_selector_iter — stream Chunks with extras

Yields `(Chunk, Optional[SelectorExtra])` tuples one at a time. This is the **only** way to access per-result `SelectorExtra` in Python; `mem_get` drops it.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
# Streaming — useful for large result sets or early termination
for chunk, extra in memory.lazy_selector_iter(view, selector):
    print(chunk.id, extra)
    if done():
        break

# Eager with extras — wrap in list()
results = list(memory.lazy_selector_iter(view, selector))
# results: list[tuple[Chunk, Optional[SelectorExtra]]]
```
{{#endtab}}
{{#endtabs}}
