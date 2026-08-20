from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from fixed_order_scan import blocked_points, is_sidon


def score(a: tuple[int, ...], limit: int) -> int:
    blocked = blocked_points(a, limit)
    n = 0
    while n + 1 in blocked:
        n += 1
    return n


def mutate(a: tuple[int, ...], limit: int, rng: random.Random) -> tuple[int, ...] | None:
    values = list(a)
    index = rng.randrange(len(values))
    if rng.random() < 0.7:
        values[index] += rng.choice((-5, -3, -2, -1, 1, 2, 3, 5))
    else:
        values[index] = rng.randint(1, limit)
    if not 1 <= values[index] <= limit or len(set(values)) != len(values):
        return None
    child = tuple(sorted(values))
    return child if is_sidon(child) else None


def random_sidon(order: int, limit: int, rng: random.Random) -> tuple[int, ...]:
    while True:
        candidate = tuple(sorted(rng.sample(range(1, limit + 1), order)))
        if is_sidon(candidate):
            return candidate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--order", type=int, default=6)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--population", type=int, default=400)
    parser.add_argument("--generations", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260820)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rng = random.Random(args.seed)

    population = {
        random_sidon(args.order, args.limit, rng) for _ in range(args.population)
    }
    history: list[dict[str, object]] = []
    global_best: tuple[int, tuple[int, ...]] = (-1, ())

    for generation in range(args.generations):
        ranked = sorted(((score(a, args.limit), a) for a in population), reverse=True)
        if ranked[0] > global_best:
            global_best = ranked[0]
            history.append({"generation": generation, "score": global_best[0], "witness": global_best[1]})
            print(history[-1])
        elite = [a for _, a in ranked[: max(20, args.population // 5)]]
        next_population = set(elite)
        attempts = 0
        while len(next_population) < args.population and attempts < args.population * 100:
            attempts += 1
            parent = rng.choice(elite)
            child = mutate(parent, args.limit, rng)
            if child is not None:
                next_population.add(child)
        while len(next_population) < args.population:
            next_population.add(random_sidon(args.order, args.limit, rng))
        population = next_population

    payload = {
        "order": args.order,
        "coordinate_limit": args.limit,
        "seed": args.seed,
        "generations": args.generations,
        "population": args.population,
        "best_saturated_prefix": global_best[0],
        "witness": global_best[1],
        "history": history,
        "status": "lower-bound witness only; evolutionary search does not prove optimality",
    }
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
