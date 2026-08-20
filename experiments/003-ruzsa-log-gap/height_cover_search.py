from __future__ import annotations

import argparse
from functools import cache
import itertools
import json
import random
from pathlib import Path


KNOWN_SINGER = {
    2: (0, 1, 3),
    3: (0, 1, 3, 9),
    5: (0, 1, 3, 8, 12, 18),
}


def prime_factors(n: int) -> set[int]:
    factors: set[int] = set()
    divisor = 2
    while divisor * divisor <= n:
        while n % divisor == 0:
            factors.add(divisor)
            n //= divisor
        divisor += 1
    if n > 1:
        factors.add(n)
    return factors


def field_mul(a: tuple[int, int, int], b: tuple[int, int, int], p: int,
              relation: tuple[int, int, int]) -> tuple[int, int, int]:
    """Multiply in F_p[x]/(x^3 + relation[2]x^2 + relation[1]x + relation[0])."""
    raw = [0] * 5
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            raw[i + j] = (raw[i + j] + ai * bj) % p
    for degree in (4, 3):
        coefficient = raw[degree]
        for j in range(3):
            raw[degree - 3 + j] = (raw[degree - 3 + j] - coefficient * relation[j]) % p
    return tuple(raw[:3])


def field_pow(a: tuple[int, int, int], exponent: int, p: int,
              relation: tuple[int, int, int]) -> tuple[int, int, int]:
    result = (1, 0, 0)
    while exponent:
        if exponent & 1:
            result = field_mul(result, a, p, relation)
        a = field_mul(a, a, p, relation)
        exponent //= 2
    return result


@cache
def generated_singer(p: int) -> tuple[int, ...]:
    """Generate a Singer difference set via trace zero in F_(p^3)."""
    order = p ** 3 - 1
    factors = prime_factors(order)
    primitive: tuple[int, int, int] | None = None
    relation: tuple[int, int, int] | None = None
    x = (0, 1, 0)
    for candidate in itertools.product(range(p), repeat=3):
        # A reducible cubic has a root in F_p.
        if any((r ** 3 + candidate[2] * r ** 2 + candidate[1] * r + candidate[0]) % p == 0
               for r in range(p)):
            continue
        if all(field_pow(x, order // factor, p, candidate) != (1, 0, 0)
               for factor in factors):
            primitive = x
            relation = candidate
            break
    if primitive is None or relation is None:
        raise ValueError(f"could not find primitive cubic for p={p}")
    q = p * p + p + 1
    marks = []
    for exponent in range(q):
        value = field_pow(primitive, exponent, p, relation)
        trace = tuple(
            (value[i]
             + field_pow(value, p, p, relation)[i]
             + field_pow(value, p * p, p, relation)[i]) % p
            for i in range(3)
        )
        if trace == (0, 0, 0):
            marks.append(exponent)
    result = tuple(marks)
    if not verify_perfect_difference_set(p, result):
        raise ValueError(f"generated set failed verification for p={p}: {result}")
    return result


@cache
def singer_set(p: int) -> tuple[int, ...]:
    return KNOWN_SINGER.get(p) or generated_singer(p)


def verify_perfect_difference_set(p: int, marks: tuple[int, ...]) -> bool:
    q = p * p + p + 1
    differences = [(a - b) % q for a in marks for b in marks if a != b]
    return len(marks) == p + 1 and sorted(differences) == list(range(1, q))


@cache
def residue_triples(q: int, marks: tuple[int, ...], residue: int) -> tuple[tuple[int, int, int, int], ...]:
    triples = []
    for u, bu in enumerate(marks):
        for v, bv in enumerate(marks):
            for w, bw in enumerate(marks):
                raw = bu + bv - bw
                if raw % q == residue:
                    triples.append((u, v, w, (raw - residue) // q))
    return tuple(triples)


def coverage(p: int, heights: tuple[int, ...], layers: int,
             model: str = "anchored") -> tuple[int, int, dict[int, list[int]]]:
    q = p * p + p + 1
    # Ruzsa takes representatives in {1,...,q}; using 0 for the zero residue
    # shifts the boundary layer when N=qM.
    marks = tuple(q if mark == 0 else mark for mark in singer_set(p))
    covered = 0
    total = 0
    missing: dict[int, list[int]] = {}
    for residue in range(1, q + 1):
        if residue in marks:
            continue
        if model == "paper":
            levels = {
                heights[u] + heights[v] - heights[w]
                for u, v, w, _ in residue_triples(q, marks, residue)
            }
            targets = range(-1, layers + 2)
        else:
            levels = {
                heights[u] + heights[v] - heights[w] + carry
                for u, v, w, carry in residue_triples(q, marks, residue)
            }
            targets = range(layers)
        gaps = [level for level in targets if level not in levels]
        total += len(targets)
        covered += len(targets) - len(gaps)
        if gaps:
            missing[residue] = gaps
    return covered, total, missing


def score_result(covered: int, missing: dict[int, list[int]], objective: str) -> tuple[int, int]:
    if objective == "residues":
        return (-len(missing), covered)
    return (covered, -len(missing))


def exact_search(p: int, layers: int, objective: str, model: str) -> dict[str, object]:
    width = p + 1
    best: tuple[tuple[int, int], int, tuple[int, ...], dict[int, list[int]]] | None = None
    for heights in itertools.product(range(layers), repeat=width):
        covered, total, missing = coverage(p, heights, layers, model)
        score = score_result(covered, missing, objective)
        if best is None or score > best[0]:
            best = score, covered, heights, missing
        if covered == total:
            break
    assert best is not None
    return {
        "p": p,
        "q": p * p + p + 1,
        "layers": layers,
        "covered": best[1],
        "total": p * p * (layers + 3 if model == "paper" else layers),
        "perfect": best[1] == p * p * (layers + 3 if model == "paper" else layers),
        "heights": best[2],
        "missing": best[3],
        "method": "exact",
        "objective": objective,
        "model": model,
    }


def evolutionary_search(p: int, layers: int, generations: int, seed: int,
                        objective: str, model: str) -> dict[str, object]:
    rng = random.Random(seed)
    width = p + 1
    population = {tuple(rng.randrange(layers) for _ in range(width)) for _ in range(1000)}
    best: tuple[tuple[int, int], int, tuple[int, ...], dict[int, list[int]]] | None = None
    for _ in range(generations):
        ranked = []
        for heights in population:
            covered, total, missing = coverage(p, heights, layers, model)
            score = score_result(covered, missing, objective)
            ranked.append((score, covered, heights, missing))
            if best is None or score > best[0]:
                best = score, covered, heights, missing
        assert best is not None
        target_total = p * p * (layers + 3 if model == "paper" else layers)
        if best[1] == target_total:
            break
        elite = [heights for _, _, heights, _ in sorted(ranked, reverse=True)[:100]]
        population = set(elite)
        while len(population) < 1000:
            child = list(rng.choice(elite))
            child[rng.randrange(width)] = rng.randrange(layers)
            population.add(tuple(child))
    return {
        "p": p,
        "q": p * p + p + 1,
        "layers": layers,
        "covered": best[1],
        "total": p * p * (layers + 3 if model == "paper" else layers),
        "perfect": best[1] == p * p * (layers + 3 if model == "paper" else layers),
        "heights": best[2],
        "missing": best[3],
        "method": "evolutionary",
        "seed": seed,
        "generations": generations,
        "objective": objective,
        "model": model,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--layers", type=int, required=True)
    parser.add_argument("--generations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260820)
    parser.add_argument("--objective", choices=("cells", "residues"), default="cells")
    parser.add_argument("--model", choices=("anchored", "paper"), default="anchored")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    marks = singer_set(args.p)
    if not verify_perfect_difference_set(args.p, marks):
        raise SystemExit("invalid Singer difference set")
    search_space = args.layers ** (args.p + 1)
    if search_space <= 2_000_000:
        result = exact_search(args.p, args.layers, args.objective, args.model)
    else:
        result = evolutionary_search(
            args.p, args.layers, args.generations, args.seed, args.objective, args.model
        )
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "missing"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
