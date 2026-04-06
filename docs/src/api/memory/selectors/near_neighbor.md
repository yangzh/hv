# NNS (Near-Neighbor Search)

Wraps one or more [attractors](attractors.md) to perform [near-neighbor search](../../concepts/near_neighbor_search.md).

{{#tabs global="lang"}}
{{#tab name="Python"}}
```python
result = memory.first_picked(
    view, memory.nns(
    memory.set_members(memory.by_item_key("sets", "my_set")),
))
```
{{#endtab}}
{{#endtabs}}