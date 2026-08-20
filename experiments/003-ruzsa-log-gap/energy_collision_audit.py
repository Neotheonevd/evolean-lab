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

    rows = []
    total_energy = Fraction(0)
    total_diagonal = 0
    total_ordered_collisions = 0
    total_off_diagonal = 0
    bad_weight = 0
    bad_count = 0
    nondivisible = 0

    for residue in range(1, q + 1):
        if residue in marks:
            continue
        counts = Counter()
        for u, v, w, carry in residue_triples(q, marks, residue):
            level = heights[u] + heights[v] - heights[w] + carry
            if 0 <= level < layers:
                counts[level] += 1
        in_range = sum(counts.values())
        sum_squares = sum(value * value for value in counts.values())
        energy = Fraction(sum_squares) - Fraction(in_range * in_range, layers)
        missing = [level for level in range(layers) if counts[level] == 0]
        total_energy += energy
        total_diagonal += in_range
        total_ordered_collisions += sum_squares
        total_off_diagonal += sum(value * (value - 1) for value in counts.values())
        nondivisible += in_range % layers != 0
        if missing:
            bad_count += 1
            bad_weight += in_range * in_range
        rows.append({
            "residue": residue,
            "in_range": in_range,
            "counts": [counts[level] for level in range(layers)],
            "missing": missing,
            "energy": str(energy),
        })

    return {
        "method": "energy_collision_audit",
        "p": p,
        "q": q,
        "layers": layers,
        "residue_classes": len(rows),
        "bad_classes": bad_count,
        "classes_with_in_range_count_not_divisible_by_M": nondivisible,
        "total_in_range_diagonal": total_diagonal,
        "total_ordered_collisions": total_ordered_collisions,
        "total_off_diagonal_collisions": total_off_diagonal,
        "total_baseline": str(Fraction(sum(row["in_range"] ** 2 for row in rows), layers)),
        "total_centered_energy": str(total_energy),
        "energy_per_residue": float(total_energy / len(rows)),
        "bad_weight_sum_n_squared": bad_weight,
        "energy_inequality_rhs": str(layers * (layers - 1) * total_energy),
        "weighted_inequality_holds": Fraction(bad_weight) <= layers * (layers - 1) * total_energy,
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
