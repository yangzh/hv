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
