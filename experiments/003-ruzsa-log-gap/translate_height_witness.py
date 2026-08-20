from __future__ import annotations

import argparse
import json
from pathlib import Path

from height_cover_search import residue_triples, singer_set


def canonical(value: int, q: int) -> int:
    residue = value % q
    return q if residue == 0 else residue


def evaluate_marks(p: int, layers: int, marks: tuple[int, ...], heights: tuple[int, ...]):
    q = p * p + p + 1
    covered = 0
    missing = {}
    for residue in range(1, q + 1):
        if residue in marks:
            continue
        triples = residue_triples(q, marks, residue)
        if len(triples) != p + 1:
            raise ValueError(f"translated residue {residue} has {len(triples)} triples")
        levels = {
            heights[u] + heights[v] - heights[w] + carry
            for u, v, w, carry in triples
        }
        gaps = [target for target in range(layers) if target not in levels]
        covered += layers - len(gaps)
        if gaps:
            missing[residue] = gaps
    return covered, p * p * layers, missing


def search(source: dict[str, object]):
    p = int(source["p"])
    layers = int(source["layers"])
    q = p * p + p + 1
    base_marks = singer_set(p)
    heights = tuple(int(value) for value in source["heights"])
    best = None
    rows = []
    for shift in range(q):
        marks = tuple(canonical(mark + shift, q) for mark in base_marks)
        covered, total, missing = evaluate_marks(p, layers, marks, heights)
        score = (-len(missing), covered)
        rows.append({"shift": shift, "missing_classes": len(missing), "covered": covered})
        if best is None or score > best[0]:
            best = score, shift, marks, missing, covered, total
    assert best is not None
    return {
        "method": "translated_height_witness",
        "source_method": source.get("method", source.get("family")),
        "source_power": source.get("power"),
        "p": p,
        "q": q,
        "layers": layers,
        "best_shift": best[1],
        "missing_classes": -best[0][0],
        "covered": best[4],
        "total": best[5],
        "marks": best[2],
        "heights": heights,
        "missing": best[3],
        "shift_scan": rows,
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
        if key not in ("missing", "shift_scan")
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
