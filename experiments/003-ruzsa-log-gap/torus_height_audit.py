from __future__ import annotations

import argparse
import json
from pathlib import Path

from height_cover_search import coverage, residue_triples, singer_set
from projective_height_search import mobius, normalized_pgl2, projective_parameters


def orbit_labels(matrix: tuple[int, int, int, int], p: int) -> dict[int, int] | None:
    """Return exponent labels when the PGL2 element is one (p+1)-cycle."""
    labels: dict[int, int] = {}
    point = p
    for exponent in range(p + 1):
        if point in labels:
            return None
        labels[point] = exponent
        point = mobius(point, matrix, p)
    return labels if point == p and len(labels) == p + 1 else None


def cyclic_missing(p: int, layers: int, heights: tuple[int, ...]) -> int:
    q = p * p + p + 1
    marks = tuple(q if mark == 0 else mark for mark in singer_set(p))
    missing = 0
    for residue in range(1, q + 1):
        if residue in marks:
            continue
        hit = {
            (heights[u] + heights[v] - heights[w] + carry) % layers
            for u, v, w, carry in residue_triples(q, marks, residue)
        }
        missing += layers - len(hit)
    return missing


def audit(p: int, layers: int) -> dict[str, object]:
    if (p + 1) % layers:
        raise ValueError("layers must divide p+1")
    marks = singer_set(p)
    parameters = projective_parameters(p)
    best = None
    cycle_count = 0
    for matrix in normalized_pgl2(p):
        labels = orbit_labels(matrix, p)
        if labels is None:
            continue
        cycle_count += 1
        twisted = tuple(labels[parameters[mark]] % layers for mark in marks)
        # Since q = 1 (mod M), lambda=1 and d = d_tilde-b (mod M).
        heights = tuple((twisted[i] - marks[i]) % layers for i in range(p + 1))
        cyc_missing = cyclic_missing(p, layers, heights)
        covered, total, exact_missing = coverage(p, heights, layers, "anchored")
        score = (cyc_missing, len(exact_missing), total - covered)
        if best is None or score < best[0]:
            best = (score, matrix, twisted, heights)
    if best is None:
        raise ValueError("no nonsplit torus generator found")
    return {
        "family": "nonsplit_torus_quotient_character",
        "p": p,
        "layers": layers,
        "pgl_generators_tested": cycle_count,
        "cyclic_missing_cells": best[0][0],
        "exact_bad_residues": best[0][1],
        "exact_missing_cells": best[0][2],
        "matrix": best[1],
        "twisted_heights": best[2],
        "original_heights": best[3],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--layers", type=int, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.p, args.layers)
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
