from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path

from height_cover_search import coverage, residue_triples, singer_set


def evaluate(p: int, layers: int, heights: tuple[int, ...]):
    covered, total, missing = coverage(p, heights, layers, "anchored")
    return (-len(missing), covered), missing, total


def coordinate_descent(p: int, layers: int, start: tuple[int, ...]):
    current = start
    current_score, current_missing, total = evaluate(p, layers, current)
    while True:
        best = None
        for index in range(p + 1):
            for value in range(layers):
                if value == current[index]:
                    continue
                candidate = current[:index] + (value,) + current[index + 1:]
                score, missing, _ = evaluate(p, layers, candidate)
                if score > current_score and (best is None or score > best[0]):
                    best = score, candidate, missing
        if best is None:
            return current_score, current, current_missing, total
        current_score, current, current_missing = best


def forced_cluster_candidates(
    p: int,
    layers: int,
    heights: tuple[int, ...],
    residue: int,
    target: int,
):
    q = p * p + p + 1
    marks = tuple(q if mark == 0 else mark for mark in singer_set(p))
    for u, v, w, carry in residue_triples(q, marks, residue):
        indices = tuple(dict.fromkeys((u, v, w)))
        for values in itertools.product(range(layers), repeat=len(indices)):
            candidate = list(heights)
            for index, value in zip(indices, values):
                candidate[index] = value
            if candidate[u] + candidate[v] - candidate[w] + carry == target:
                yield tuple(candidate)


def search(
    p: int,
    layers: int,
    start: tuple[int, ...],
    iterations: int,
    beam: int,
    seed: int,
):
    rng = random.Random(seed)
    initial = coordinate_descent(p, layers, start)
    global_score, global_heights, global_missing, total = initial
    frontier = [(global_score, global_heights, global_missing)]

    for iteration in range(iterations):
        parent_score, parent, parent_missing = rng.choice(frontier)
        if not parent_missing:
            break
        residue = rng.choice(tuple(parent_missing))
        target = rng.choice(parent_missing[residue])
        raw_candidates = list(forced_cluster_candidates(
            p, layers, parent, residue, target
        ))
        rng.shuffle(raw_candidates)
        # Keep diverse forced repairs; every candidate already closes the selected gap.
        for candidate in raw_candidates[: max(beam * 3, 30)]:
            score, descended, missing, _ = coordinate_descent(p, layers, candidate)
            frontier.append((score, descended, missing))
            if score > global_score:
                global_score, global_heights, global_missing = score, descended, missing
                print(json.dumps({
                    "iteration": iteration,
                    "missing_classes": -score[0],
                    "covered": score[1],
                    "heights": descended,
                    "forced_residue": residue,
                    "forced_target": target,
                }))
        # Deduplicate states and retain the best beam, with random tie order.
        rng.shuffle(frontier)
        unique = {}
        for item in frontier:
            unique[item[1]] = item
        frontier = sorted(unique.values(), key=lambda item: item[0], reverse=True)[:beam]

    return {
        "method": "bad_class_cluster_repair",
        "p": p,
        "q": p * p + p + 1,
        "layers": layers,
        "missing_classes": -global_score[0],
        "covered": global_score[1],
        "total": total,
        "heights": global_heights,
        "missing": global_missing,
        "iterations": iterations,
        "beam": beam,
        "seed": seed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--layers", type=int, required=True)
    parser.add_argument("--start", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=200)
    parser.add_argument("--beam", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260820)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.start.read_text(encoding="utf-8"))
    start = tuple(source["heights"])
    if len(start) != args.p + 1:
        raise SystemExit("start vector has the wrong width")
    result = search(args.p, args.layers, start, args.iterations, args.beam, args.seed)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "missing"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
