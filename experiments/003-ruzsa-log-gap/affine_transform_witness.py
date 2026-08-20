from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from height_cover_search import singer_set
from translate_height_witness import canonical, evaluate_marks


def search(source: dict[str, object]):
    p = int(source["p"])
    layers = int(source["layers"])
    q = p * p + p + 1
    base_marks = tuple(
        int(value) for value in source.get("marks", singer_set(p))
    )
    heights = tuple(int(value) for value in source["heights"])
    best = None
    multiplier_rows = []
    tested = 0

    for multiplier in range(1, q):
        if math.gcd(multiplier, q) != 1:
            continue
        best_for_multiplier = None
        for shift in range(q):
            marks = tuple(
                canonical(multiplier * mark + shift, q) for mark in base_marks
            )
            covered, total, missing = evaluate_marks(p, layers, marks, heights)
            score = (-len(missing), covered)
            tested += 1
            candidate = score, multiplier, shift, marks, missing, covered, total
            if best_for_multiplier is None or score > best_for_multiplier[0]:
                best_for_multiplier = candidate
            if best is None or score > best[0]:
                best = candidate
        assert best_for_multiplier is not None
        multiplier_rows.append({
            "multiplier": multiplier,
            "best_shift": best_for_multiplier[2],
            "missing_classes": -best_for_multiplier[0][0],
            "covered": best_for_multiplier[5],
        })

    assert best is not None
    return {
        "method": "affine_equivalent_difference_set_search",
        "source_method": source.get("method", source.get("family")),
        "p": p,
        "q": q,
        "layers": layers,
        "best_multiplier": best[1],
        "best_shift": best[2],
        "missing_classes": -best[0][0],
        "covered": best[5],
        "total": best[6],
        "marks": best[3],
        "heights": heights,
        "missing": best[4],
        "tested": tested,
        "multiplier_summary": multiplier_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    result = search(source)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        key: value for key, value in result.items()
        if key not in ("missing", "multiplier_summary")
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
