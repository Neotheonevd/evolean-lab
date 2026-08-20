from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from translate_height_witness import evaluate_marks


def evaluate(p: int, layers: int, marks: tuple[int, ...], heights: tuple[int, ...]):
    covered, total, missing = evaluate_marks(p, layers, marks, heights)
    return (-len(missing), covered), missing, total


def descend(p: int, layers: int, marks: tuple[int, ...], start: tuple[int, ...]):
    current = start
    score, missing, total = evaluate(p, layers, marks, current)
    while True:
        best = None
        for index in range(p + 1):
            for value in range(layers):
                if value == current[index]:
                    continue
                candidate = current[:index] + (value,) + current[index + 1:]
                candidate_score, candidate_missing, _ = evaluate(
                    p, layers, marks, candidate
                )
                if candidate_score > score and (best is None or candidate_score > best[0]):
                    best = candidate_score, candidate, candidate_missing
        if best is None:
            return score, current, missing, total
        score, current, missing = best


def search(source: dict[str, object], perturbations: int, seed: int):
    rng = random.Random(seed)
    p = int(source["p"])
    layers = int(source["layers"])
    marks = tuple(int(value) for value in source["marks"])
    start = tuple(int(value) for value in source["heights"])
    best_score, best_heights, best_missing, total = descend(p, layers, marks, start)
    current = best_heights
    for step in range(perturbations):
        candidate = list(current if rng.random() < 0.7 else best_heights)
        for index in rng.sample(range(p + 1), rng.choice((2, 3))):
            candidate[index] = rng.randrange(layers)
        score, heights, missing, _ = descend(p, layers, marks, tuple(candidate))
        current = heights
        if score > best_score:
            best_score, best_heights, best_missing = score, heights, missing
            print(json.dumps({
                "step": step,
                "missing_classes": -score[0],
                "covered": score[1],
                "heights": heights,
            }))
    return {
        "method": "translated_witness_local_refinement",
        "p": p,
        "q": p * p + p + 1,
        "layers": layers,
        "marks": marks,
        "heights": best_heights,
        "missing_classes": -best_score[0],
        "covered": best_score[1],
        "total": total,
        "missing": best_missing,
        "perturbations": perturbations,
        "seed": seed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--perturbations", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260820)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    result = search(source, args.perturbations, args.seed)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "missing"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
