# Other Selectors

## ByItemKey

Exact lookup by domain + pod.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
sel = memory.by_item_key("animals", "cat")
```
{{#endtab}}
{{#endtabs}}

## ByItemDomain

All chunks in a given domain (prefix scan).

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
sel = memory.by_item_domain("animals")
```
{{#endtab}}
{{#endtabs}}

## WithCode / WithSparkle

Literal selector — returns a hypervector directly, no storage lookup.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
sel = memory.with_code(some_hv)
sel = memory.with_sparkle("animals", "cat")
```
{{#endtab}}
{{#endtabs}}

## Joiner

Union of multiple selectors — returns first result from each.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
sel = memory.joiner(
    memory.by_item_key("animals", "cat"),
    memory.by_item_key("animals", "dog"),
)
```
{{#endtab}}
{{#endtabs}}

## Range

Limits results to `[start, start+limit)`. `limit=0` means no limit.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
sel = memory.range_sel(memory.by_item_domain("animals"), start=0, limit=10)
```
{{#endtab}}
{{#endtabs}}

## OnlyDomain

Filters inner selector results by domain.

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
sel = memory.only_domain("animals", inner_selector)
```
{{#endtab}}
{{#endtabs}}
