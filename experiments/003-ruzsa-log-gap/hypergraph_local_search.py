from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from height_cover_search import coverage


def evaluate(p: int, layers: int, heights: tuple[int, ...]):
    covered, total, missing = coverage(p, heights, layers, "anchored")
    return (-len(missing), covered), missing, total


def search(p: int, layers: int, restarts: int, perturbations: int, seed: int,
           pair_rounds: int):
    rng = random.Random(seed)
    width = p + 1
    global_best = None

    for restart in range(restarts):
        current = tuple(rng.randrange(layers) for _ in range(width))
        current_score, current_missing, total = evaluate(p, layers, current)

        for _ in range(perturbations):
            # Steepest coordinate descent: test every value of every height variable.
            while True:
                best_move = None
                for index in range(width):
                    for value in range(layers):
                        if value == current[index]:
                            continue
                        candidate = current[:index] + (value,) + current[index + 1:]
                        score, missing, _ = evaluate(p, layers, candidate)
                        if score > current_score and (best_move is None or score > best_move[0]):
                            best_move = score, candidate, missing
                if best_move is None:
                    break
                current_score, current, current_missing = best_move

            if global_best is None or current_score > global_best[0]:
                global_best = current_score, current, current_missing, restart
                print(json.dumps({
                    "restart": restart,
                    "missing_classes": -current_score[0],
                    "covered": current_score[1],
                    "heights": current,
                }))

            # Escape a local optimum by changing a random pair, then descend again.
            i, j = rng.sample(range(width), 2)
            candidate = list(current)
            candidate[i] = rng.randrange(layers)
            candidate[j] = rng.randrange(layers)
            current = tuple(candidate)
            current_score, current_missing, _ = evaluate(p, layers, current)

    assert global_best is not None
    score, heights, missing, restart = global_best
    for _ in range(pair_rounds):
        best_pair = None
        for i in range(width):
            for j in range(i + 1, width):
                for first in range(layers):
                    for second in range(layers):
                        if first == heights[i] and second == heights[j]:
                            continue
                        candidate = list(heights)
                        candidate[i], candidate[j] = first, second
                        candidate_tuple = tuple(candidate)
                        candidate_score, candidate_missing, _ = evaluate(
                            p, layers, candidate_tuple
                        )
                        if candidate_score > score and (
                            best_pair is None or candidate_score > best_pair[0]
                        ):
                            best_pair = candidate_score, candidate_tuple, candidate_missing
        if best_pair is None:
            break
        score, heights, missing = best_pair
        print(json.dumps({
            "pair_refinement": True,
            "missing_classes": -score[0],
            "covered": score[1],
            "heights": heights,
        }))
    return {
        "method": "hypergraph_coordinate_descent",
        "p": p,
        "q": p * p + p + 1,
        "layers": layers,
        "missing_classes": -score[0],
        "covered": score[1],
        "total": total,
        "heights": heights,
        "missing": missing,
        "best_restart": restart,
        "restarts": restarts,
        "perturbations": perturbations,
        "pair_rounds": pair_rounds,
        "seed": seed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--layers", type=int, required=True)
    parser.add_argument("--restarts", type=int, default=100)
    parser.add_argument("--perturbations", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260820)
    parser.add_argument("--pair-rounds", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = search(
        args.p, args.layers, args.restarts, args.perturbations, args.seed, args.pair_rounds
    )
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "missing"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
