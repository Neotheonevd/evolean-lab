from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from height_cover_search import residue_triples, singer_set


def canonical_marks(p: int, source: dict[str, object]) -> tuple[int, ...]:
    q = p * p + p + 1
    raw = source.get("marks")
    if raw is None:
        raw = singer_set(p)
    return tuple(q if int(mark) % q == 0 else int(mark) % q for mark in raw)


def audit(source: dict[str, object]) -> dict[str, object]:
    p = int(source["p"])
    q = p * p + p + 1
    layers = int(source["layers"])
    heights = tuple(int(value) for value in source["heights"])
    marks = canonical_marks(p, source)

    cells = []
    category_counts: Counter[str] = Counter()
    winding_histogram: Counter[int] = Counter()
    exact_covered = 0
    cyclic_covered = 0

    for residue in range(1, q + 1):
        if residue in marks:
            continue
        levels = [
            heights[u] + heights[v] - heights[w] + carry
            for u, v, w, carry in residue_triples(q, marks, residue)
        ]
        for target in range(layers):
            windings = sorted((level - target) // layers for level in levels
                              if (level - target) % layers == 0)
            winding_histogram.update(windings)
            exact = 0 in windings
            cyclic = bool(windings)
            exact_covered += exact
            cyclic_covered += cyclic
            if exact:
                category = "exact"
            elif cyclic:
                category = "wrap_only"
            else:
                category = "cyclic_uncovered"
            category_counts[category] += 1
            cells.append({
                "residue": residue,
                "target": target,
                "category": category,
                "windings": windings,
            })

    total = len(cells)
    missing = total - exact_covered
    return {
        "method": "winding_defect_audit",
        "p": p,
        "q": q,
        "layers": layers,
        "total_cells": total,
        "exact_covered": exact_covered,
        "cyclic_covered": cyclic_covered,
        "missing_cells": missing,
        "category_counts": dict(category_counts),
        "winding_histogram": {str(key): value for key, value in sorted(winding_histogram.items())},
        "fraction_of_missing_that_is_wrap_only": (
            category_counts["wrap_only"] / missing if missing else 0.0
        ),
        "cells": cells,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    result = audit(source)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "cells"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
