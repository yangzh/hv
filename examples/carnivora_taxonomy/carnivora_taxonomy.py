"""Hierarchical Carnivora taxonomy showcase — per-rank deques edition.

Builds a 5-rank taxonomic tree (Order → Family → [Subfamily →] Genus →
species) of ~99 Carnivora species (cats, dogs, bears, otters/weasels)
on top of the chunk-level deque API.

This version uses **one deque per taxonomic rank** instead of one
deque per parent. Each parent's children form a contiguous slice of
the next-rank deque, addressed via [CHILDREN_BEGIN, CHILDREN_END).

Run from anywhere::

    python examples/carnivora_taxonomy/carnivora_taxonomy.py

Demonstrates:
  * **Per-rank deques** — one deque per taxonomic level (Order, Family,
    Subfamily, Genus, species). Felidae's children land in the
    Subfamily deque; Canidae / Ursidae / Mustelidae skip Subfamily and
    land their children directly in the Genus deque.
  * **Slice navigation** — each parent carriage's
    `[CHILDREN_BEGIN, CHILDREN_END)` slice points into the
    immediately-next-rank deque. `DequeChildren(parent)` walks it.
  * **Two-pass build** — pass 1 plans the random pods + per-rank order;
    pass 2 writes carriages deepest-rank-first (children must exist
    before parents reference them via CHILDREN_BEGIN/END).
  * **Reference-mode payloads** — each taxon also has a Sparkle Terminal
    in the `cats` payload domain at the same pod as its carriage. The
    polymorphic deque_appender API also accepts an inline protobuf
    message directly (see the notebook's bonus cell for a demo).
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass, field

import yaml
from kongming import hv, memory

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "carnivora.yaml")

# Taxonomic ranks, root → leaf. The deque-per-rank layout writes them
# in *reverse* order (deepest first) since carriages must exist before
# parents can reference them via CHILDREN_BEGIN/END.
RANKS = ["Order", "Family", "Subfamily", "Genus", "species"]


# ── Phase 0: helpers ────────────────────────────────────────────────


def get_random_pod() -> hv.Pod:
    """Returns a 64-bit random pod."""
    return hv.Pod.from_seed(random.getrandbits(64))


def load_taxonomy(path: str = DATA_FILE) -> dict:
    """Load the taxonomy literal from YAML.

    Lists are leaves (species, named by their 2-part Latin binomial);
    dicts are internal nodes (Order / Family / Subfamily / Genus).
    """
    with open(path) as f:
        return yaml.safe_load(f)


def rank_of(name: str, has_children: bool) -> str:
    """Infer a taxon's rank from its name + structural position.

    Suffix conventions: ``-idae`` = Family, ``-inae`` = Subfamily,
    "Carnivora" = Order. Anything else with children is a Genus;
    anything without is a species.
    """
    if not has_children:
        return "species"
    if name == "Carnivora":
        return "Order"
    if name.endswith("idae"):
        return "Family"
    if name.endswith("inae"):
        return "Subfamily"
    return "Genus"


# ── Phase 1: build (two-pass, per-rank deques) ──────────────────────


@dataclass
class Node:
    """In-process index. One per taxon.

    `pod` is shared by:
      - the cat's identity Sparkle in the `cats` payload domain
        (embedded inline on the carriage chunk's payload field)
      - the carriage chunk's pod in this taxon's rank deque
    """

    name: str
    rank: str
    pod: hv.Pod
    children: list["Node"] = field(default_factory=list)
    # Populated during pass 2; the index of the *first* carriage in
    # this taxon's child rank deque that falls AFTER our last child.
    # Used to compute CHILDREN_END. None if we're the rightmost
    # contributor to that rank's deque.
    end_pod: hv.Pod | None = None


def plan(taxonomy: dict) -> tuple[Node, dict[str, list[Node]]]:
    """Pass 1 — DFS over the YAML, allocating pods and bucketing nodes
    by rank in DFS order. Returns (root_node, by_rank).

    `by_rank[r]` is the list of carriages that will be pushed into
    rank r's deque, in the exact order they'll appear there.
    """
    by_rank: dict[str, list[Node]] = {r: [] for r in RANKS}

    def go(name: str, sub) -> Node:
        rank = rank_of(name, bool(sub))
        node = Node(name=name, rank=rank, pod=get_random_pod())
        by_rank[rank].append(node)
        if sub:
            items = sub if isinstance(sub, list) else list(sub.items())
            for entry in items:
                cname, csub = (entry, None) if isinstance(sub, list) else entry
                node.children.append(go(cname, csub))
        return node

    ((root_name, root_sub),) = taxonomy.items()
    root = go(root_name, root_sub)

    # Compute end_pod for each non-leaf parent: the carriage right
    # after my last child in the child rank's deque (or None if none).
    for rank, nodes in by_rank.items():
        # For each parent at this rank, look up its children's positions
        # in the child rank's deque. The "end" is the first carriage in
        # that deque that comes AFTER the parent's last child.
        for parent in nodes:
            if not parent.children:
                continue
            child_rank = parent.children[0].rank
            child_list = by_rank[child_rank]
            last_child_idx = child_list.index(parent.children[-1])
            after_idx = last_child_idx + 1
            if after_idx < len(child_list):
                parent.end_pod = child_list[after_idx].pod

    return root, by_rank


def write(storage: memory.InMemory, by_rank: dict[str, list[Node]], model: int) -> dict[str, hv.Domain]:
    """Pass 2 — push each rank's carriages, deepest first.

    For each carriage:
      - reference-mode payload = a Sparkle Terminal in `cats` at the
        same pod as the carriage (deque API reuses payload_pod as
        carriage_pod, so plan()'s random pods address both)
      - CHILDREN_BEGIN = first child's deque_carriage in child rank's deque
      - CHILDREN_END   = parent.end_pod's deque_carriage (or identity)
    """
    cats_domain = hv.Domain("cats")
    rank_deques = {r: hv.Domain(f"taxonomy/{r.lower()}") for r in RANKS}

    for rank in reversed(RANKS):  # species → Genus → Subfamily → Family → Order
        for node in by_rank[rank]:
            # Materialize the cat's identity Sparkle in `cats`.
            storage.mem_set(memory.new_terminal(cats_domain, node.pod, note=node.name))
            payload_sel = memory.with_sparkle(cats_domain, node.pod)

            kwargs = {}
            if node.children:
                child_rank = node.children[0].rank
                child_deque = rank_deques[child_rank]
                kwargs["children_begin"] = memory.deque_carriage(child_deque, node.children[0].pod)
                if node.end_pod is not None:
                    kwargs["children_end"] = memory.deque_carriage(child_deque, node.end_pod)

            storage.mem_set(memory.deque_appender(rank_deques[rank], payload_sel, **kwargs))

    return rank_deques


def build(storage: memory.InMemory, taxonomy: dict, model: int) -> tuple[Node, dict[str, hv.Domain]]:
    """Build the substrate-backed tree and return (root, rank_deques)."""
    root, by_rank = plan(taxonomy)
    rank_deques = write(storage, by_rank, model)
    return root, rank_deques


# ── Phase 2: walk via substrate ─────────────────────────────────────


def walk(storage: memory.InMemory, node: Node, rank_deques: dict[str, hv.Domain], indent: int = 0) -> int:
    """Walk top-down. Reads payloads via DequeChildren on the parent's
    carriage, decodes each child's inline Sparkle from chunk.payload,
    and recurses via the parallel index. Returns total leaves visited.
    """
    print("  " * indent + node.name)
    if not node.children:
        return 1

    parent_sel = memory.deque_carriage(rank_deques[node.rank], node.pod)
    payloads = list(storage.mem_get(memory.deque_children(parent_sel)))
    leaves = 0
    for payload, child in zip(payloads, node.children):
        # In inline mode the carriage chunk IS the yielded payload;
        # its note is the taxon name and chunk.payload carries the
        # embedded Sparkle. (Sanity-check the round-trip.)
        assert payload.note == child.name, f"mismatch: {payload.note} != {child.name}"
        leaves += walk(storage, child, rank_deques, indent + 1)
    return leaves


# ── Phase 3: lookup-by-name ─────────────────────────────────────────


def find_paths(root: Node, query: str) -> list[list[Node]]:
    """Return every breadcrumb path to a Node whose name contains `query`."""
    out: list[list[Node]] = []

    def dfs(node: Node, path: list[Node]):
        new_path = path + [node]
        if query in node.name:
            out.append(new_path)
        for c in node.children:
            dfs(c, new_path)

    dfs(root, [])
    return out


# ── Main ────────────────────────────────────────────────────────────


def main():
    random.seed(42)  # reproducible pods
    model = hv.MODEL_64K_8BIT
    storage = memory.InMemory(model)

    print("Building Carnivora taxonomy in substrate...")
    root, rank_deques = build(storage, load_taxonomy(), model)
    print("  Per-rank deques:")
    for r in RANKS:
        print(f"    {r:9} → {rank_deques[r].name()}")
    print()

    print("Full hierarchy (read back from substrate):")
    print("─" * 60)
    leaves = walk(storage, root, rank_deques)
    print(f"\n... {leaves} leaves visited.")
    print()

    # Lookup demo: shared species epithet "bengalensis" appears in two
    # families — a leopard cat (Felidae) and a Bengal fox (Canidae).
    query = "bengalensis"
    print(f'Substring lookup "{query}" — every match shows its full breadcrumb:')
    print("─" * 60)
    matches = find_paths(root, query)
    for path in matches:
        breadcrumb = " › ".join(n.name for n in path)
        leaf = path[-1]
        print(f"  {breadcrumb}")
        print(f"    pod = 0x{leaf.pod.seed():016x}")
    print(f"\n... {len(matches)} match(es). Distinct pods prove they're separate carriages, not collapsed by epithet.")


if __name__ == "__main__":
    main()
