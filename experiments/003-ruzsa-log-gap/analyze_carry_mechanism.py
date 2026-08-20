from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

from height_cover_search import residue_triples, singer_set


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or not xs:
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = math.sqrt(
        sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys)
    )
    return None if denominator == 0 else numerator / denominator


def analyze(source: dict[str, object]) -> dict[str, object]:
    p = int(source["p"])
    layers = int(source["layers"])
    heights = tuple(int(value) for value in source["heights"])
    q = p * p + p + 1
    marks = tuple(q if mark == 0 else mark for mark in singer_set(p))
    target = set(range(layers))
    rows = []

    for residue in range(1, q + 1):
        if residue in marks:
            continue
        triples = residue_triples(q, marks, residue)
        height_levels = {
            heights[u] + heights[v] - heights[w]
            for u, v, w, _ in triples
        }
        true_levels = {
            heights[u] + heights[v] - heights[w] + carry
            for u, v, w, carry in triples
        }
        carries = Counter(carry for _, _, _, carry in triples)
        pure_covered = len(height_levels & target)
        true_covered = len(true_levels & target)
        rows.append({
            "residue": residue,
            "pure_unique_levels": len(height_levels),
            "true_unique_levels": len(true_levels),
            "pure_covered": pure_covered,
            "true_covered": true_covered,
            "carry_support": len(carries),
            "carry_histogram": dict(sorted(carries.items())),
            "good": true_covered == layers,
        })

    pure = [row["pure_covered"] for row in rows]
    true = [row["true_covered"] for row in rows]
    carry_support = [row["carry_support"] for row in rows]
    gains = [after - before for before, after in zip(pure, true)]
    return {
        "p": p,
        "q": q,
        "layers": layers,
        "source_method": source.get("method", source.get("family")),
        "source_power": source.get("power"),
        "good_classes": sum(row["good"] for row in rows),
        "bad_classes": sum(not row["good"] for row in rows),
        "average_pure_covered": sum(pure) / len(pure),
        "average_true_covered": sum(true) / len(true),
        "average_carry_gain": sum(gains) / len(gains),
        "carry_gain_histogram": dict(sorted(Counter(gains).items())),
        "carry_support_histogram": dict(sorted(Counter(carry_support).items())),
        "correlation_pure_true": pearson(pure, true),
        "correlation_carry_support_gain": pearson(carry_support, gains),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    result = analyze(source)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
