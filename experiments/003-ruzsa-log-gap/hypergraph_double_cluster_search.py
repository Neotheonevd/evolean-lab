from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path

from height_cover_search import coverage, residue_triples, singer_set
from hypergraph_cluster_search import coordinate_descent


def evaluate(p: int, layers: int, heights: tuple[int, ...]):
    covered, total, missing = coverage(p, heights, layers, "anchored")
    return (-len(missing), covered), missing, total


def canonical_triples(p: int, residue: int):
    q = p * p + p + 1
    marks = tuple(q if mark == 0 else mark for mark in singer_set(p))
    return residue_triples(q, marks, residue)


def double_forced_candidates(
    p: int,
    layers: int,
    heights: tuple[int, ...],
    first: tuple[int, int],
    second: tuple[int, int],
):
    r1, target1 = first
    r2, target2 = second
    for triple1 in canonical_triples(p, r1):
        u1, v1, w1, carry1 = triple1
        set1 = {u1, v1, w1}
        for triple2 in canonical_triples(p, r2):
            u2, v2, w2, carry2 = triple2
            set2 = {u2, v2, w2}
            # Shared variables are the intended coupled mechanism; two shared
            # variables keep the exhaustive forced neighborhood tractable.
            if len(set1 & set2) < 2:
                continue
            indices = tuple(sorted(set1 | set2))
            for values in itertools.product(range(layers), repeat=len(indices)):
                candidate = list(heights)
                for index, value in zip(indices, values):
                    candidate[index] = value
                if candidate[u1] + candidate[v1] - candidate[w1] + carry1 != target1:
                    continue
                if candidate[u2] + candidate[v2] - candidate[w2] + carry2 != target2:
                    continue
                yield tuple(candidate)


def constraints_are_coupled(p: int, first: tuple[int, int], second: tuple[int, int]) -> bool:
    triples1 = canonical_triples(p, first[0])
    triples2 = canonical_triples(p, second[0])
    return any(
        len({u1, v1, w1} & {u2, v2, w2}) >= 2
        for u1, v1, w1, _ in triples1
        for u2, v2, w2, _ in triples2
    )


def search(p: int, layers: int, start: tuple[int, ...], iterations: int,
           beam: int, raw_pool: int, seed: int):
    rng = random.Random(seed)
    score, heights, missing, total = coordinate_descent(p, layers, start)
    global_score, global_heights, global_missing = score, heights, missing
    frontier = [(score, heights, missing)]

    for iteration in range(iterations):
        parent_score, parent, parent_missing = rng.choice(frontier)
        constraints = [
            (residue, target)
            for residue, targets in parent_missing.items()
            for target in targets
        ]
        if len(constraints) < 2:
            break
        coupled_pairs = [
            (constraints[i], constraints[j])
            for i in range(len(constraints))
            for j in range(i + 1, len(constraints))
            if constraints[i][0] != constraints[j][0]
            and constraints_are_coupled(p, constraints[i], constraints[j])
        ]
        if not coupled_pairs:
            break
        first, second = rng.choice(coupled_pairs)
        raw = set(double_forced_candidates(p, layers, parent, first, second))
        if not raw:
            continue
        # Cheaply rank the forced states before running expensive local descent.
        ranked_raw = []
        for candidate in raw:
            candidate_score, candidate_missing, _ = evaluate(p, layers, candidate)
            ranked_raw.append((candidate_score, candidate, candidate_missing))
        rng.shuffle(ranked_raw)
        ranked_raw.sort(key=lambda item: item[0], reverse=True)
        for _, candidate, _ in ranked_raw[:raw_pool]:
            descended_score, descended, descended_missing, _ = coordinate_descent(
                p, layers, candidate
            )
            frontier.append((descended_score, descended, descended_missing))
            if descended_score > global_score:
                global_score = descended_score
                global_heights = descended
                global_missing = descended_missing
                print(json.dumps({
                    "iteration": iteration,
                    "missing_classes": -descended_score[0],
                    "covered": descended_score[1],
                    "heights": descended,
                    "forced": (first, second),
                }))
        rng.shuffle(frontier)
        unique = {item[1]: item for item in frontier}
        frontier = sorted(unique.values(), key=lambda item: item[0], reverse=True)[:beam]

    return {
        "method": "double_bad_class_cluster_repair",
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
        "raw_pool": raw_pool,
        "seed": seed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--layers", type=int, required=True)
    parser.add_argument("--start", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--beam", type=int, default=20)
    parser.add_argument("--raw-pool", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260820)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.start.read_text(encoding="utf-8"))
    result = search(
        args.p, args.layers, tuple(source["heights"]), args.iterations,
        args.beam, args.raw_pool, args.seed
    )
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "missing"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
