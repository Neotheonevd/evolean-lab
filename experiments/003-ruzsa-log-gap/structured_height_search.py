from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from height_cover_search import coverage, singer_set


def missing_class_count(missing: dict[int, list[int]]) -> int:
    return len(missing)


def circle_bucket_search(p: int, layers: int, degree: int) -> dict[str, object]:
    """Search heights obtained by cutting an affine ordering of Z/qZ into M arcs."""
    q = p * p + p + 1
    marks = singer_set(p)
    best: tuple[int, int, tuple[int, ...], int, int, dict[int, list[int]]] | None = None
    for multiplier in range(1, q):
        if math.gcd(multiplier, q) != 1:
            continue
        for shift in range(q):
            heights = tuple(
                layers * ((multiplier * pow(mark, degree, q) + shift) % q) // q
                for mark in marks
            )
            covered, total, missing = coverage(p, heights, layers, "anchored")
            score = (-missing_class_count(missing), covered)
            if best is None or score > best[:2]:
                best = (score[0], score[1], heights, multiplier, shift, missing)
    assert best is not None
    return {
        "family": "polynomial_circle_bucket",
        "degree": degree,
        "p": p,
        "q": q,
        "layers": layers,
        "missing_classes": -best[0],
        "covered": best[1],
        "total": p * p * layers,
        "heights": best[2],
        "multiplier": best[3],
        "shift": best[4],
        "missing": best[5],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--layers", type=int, required=True)
    parser.add_argument("--degree", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = circle_bucket_search(args.p, args.layers, args.degree)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "missing"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
