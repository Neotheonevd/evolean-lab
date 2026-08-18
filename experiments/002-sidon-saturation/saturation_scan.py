from __future__ import annotations

import argparse
import json
from pathlib import Path


def can_add(chosen: tuple[int, ...], sums: frozenset[int], x: int) -> bool:
    new_sums = [x + a for a in chosen] + [2 * x]
    return len(new_sums) == len(set(new_sums)) and not any(s in sums for s in new_sums)


def minimum_maximal_sidon(n: int) -> dict[str, object]:
    best = n + 1
    witnesses: list[list[int]] = []
    sidon_nodes = 0

    def visit(next_x: int, chosen: tuple[int, ...], sums: frozenset[int]) -> None:
        nonlocal best, witnesses, sidon_nodes
        sidon_nodes += 1
        if len(chosen) > best:
            return
        if next_x > n:
            if all(x in chosen or not can_add(chosen, sums, x) for x in range(1, n + 1)):
                if len(chosen) < best:
                    best = len(chosen)
                    witnesses = [list(chosen)]
                elif len(chosen) == best:
                    witnesses.append(list(chosen))
            return

        # Include first: early saturated witnesses quickly improve the size bound.
        if can_add(chosen, sums, next_x):
            additions = {next_x + a for a in chosen}
            additions.add(2 * next_x)
            visit(next_x + 1, chosen + (next_x,), sums | additions)
        visit(next_x + 1, chosen, sums)

    visit(1, (), frozenset())
    return {
        "n": n,
        "minimum_size": best,
        "witness_count": len(witnesses),
        "witnesses": witnesses,
        "sidon_nodes": sidon_nodes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = [minimum_maximal_sidon(n) for n in range(1, args.max_n + 1)]
    payload = {
        "definition": "minimum size of an inclusion-maximal Sidon subset of [1,n]",
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
