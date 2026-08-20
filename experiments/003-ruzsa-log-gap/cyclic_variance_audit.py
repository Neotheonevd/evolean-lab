from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
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
    representation_count = p + 1

    total_energy = Fraction(0)
    empty_cells = 0
    rows = []
    for residue in range(1, q + 1):
        if residue in marks:
            continue
        counts = Counter(
            (heights[u] + heights[v] - heights[w] + carry) % layers
            for u, v, w, carry in residue_triples(q, marks, residue)
        )
        sum_squares = sum(counts[layer] ** 2 for layer in range(layers))
        energy = Fraction(sum_squares) - Fraction(representation_count ** 2, layers)
        zeros = sum(counts[layer] == 0 for layer in range(layers))
        total_energy += energy
        empty_cells += zeros
        rows.append({
            "residue": residue,
            "counts": [counts[layer] for layer in range(layers)],
            "empty_cells": zeros,
            "centered_energy": str(energy),
        })

    local_gap = Fraction(representation_count ** 2, layers * (layers - 1))
    moment_upper_bound = total_energy / local_gap
    return {
        "method": "cyclic_variance_audit",
        "p": p,
        "q": q,
        "layers": layers,
        "residue_classes": len(rows),
        "representations_per_residue": representation_count,
        "cyclic_empty_cells": empty_cells,
        "total_centered_energy": str(total_energy),
        "energy_per_residue": float(total_energy / len(rows)),
        "missing_layer_energy_gap": str(local_gap),
        "second_moment_upper_bound_on_empty_cells": str(moment_upper_bound),
        "bound_to_actual_ratio": float(moment_upper_bound / empty_cells) if empty_cells else 0.0,
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    result = audit(source)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
