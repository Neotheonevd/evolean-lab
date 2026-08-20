from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from height_cover_search import (
    coverage,
    field_pow,
    prime_factors,
    singer_set,
)


Vector = tuple[int, int, int]


def primitive_cubic(p: int) -> tuple[int, int, int]:
    order = p ** 3 - 1
    x = (0, 1, 0)
    for relation in itertools.product(range(p), repeat=3):
        if any((r ** 3 + relation[2] * r ** 2 + relation[1] * r + relation[0]) % p == 0
               for r in range(p)):
            continue
        if all(field_pow(x, order // factor, p, relation) != (1, 0, 0)
               for factor in prime_factors(order)):
            return relation
    raise ValueError("primitive cubic not found")


def add_scaled(a: int, u: Vector, b: int, v: Vector, p: int) -> Vector:
    return tuple((a * u[i] + b * v[i]) % p for i in range(3))


def projective_parameters(p: int) -> dict[int, int]:
    """Label Singer trace-zero lines by P^1(F_p), using p for infinity."""
    relation = primitive_cubic(p)
    primitive = (0, 1, 0)
    marks = singer_set(p)
    vectors: dict[int, Vector] = {}
    for exponent in marks:
        value = field_pow(primitive, exponent, p, relation)
        conjugate1 = field_pow(value, p, p, relation)
        conjugate2 = field_pow(value, p * p, p, relation)
        trace = tuple((value[i] + conjugate1[i] + conjugate2[i]) % p for i in range(3))
        if trace != (0, 0, 0):
            raise ValueError("Singer mark is not trace zero")
        vectors[exponent] = value

    basis1 = next(iter(vectors.values()))
    basis2 = next(
        vector for vector in vectors.values()
        if all(add_scaled(a, basis1, 1, vector, p) != (0, 0, 0) for a in range(p))
    )
    result: dict[int, int] = {}
    for exponent, vector in vectors.items():
        coefficients = next(
            (a, b) for a in range(p) for b in range(p)
            if add_scaled(a, basis1, b, basis2, p) == vector
        )
        a, b = coefficients
        result[exponent] = p if b == 0 else (a * pow(b, -1, p)) % p
    if sorted(result.values()) != list(range(p + 1)):
        raise ValueError("projective labels are not a bijection")
    return result


def mobius(t: int, matrix: tuple[int, int, int, int], p: int) -> int:
    a, b, c, d = matrix
    numerator, denominator = (a, c) if t == p else ((a * t + b) % p, (c * t + d) % p)
    return p if denominator == 0 else numerator * pow(denominator, -1, p) % p


def normalized_pgl2(p: int):
    seen = set()
    for matrix in itertools.product(range(p), repeat=4):
        a, b, c, d = matrix
        if (a * d - b * c) % p == 0:
            continue
        first = next(value for value in matrix if value != 0)
        inverse = pow(first, -1, p)
        normalized = tuple(value * inverse % p for value in matrix)
        if normalized not in seen:
            seen.add(normalized)
            yield normalized


def search(p: int, layers: int, mapping: str) -> dict[str, object]:
    marks = singer_set(p)
    parameters = projective_parameters(p)
    best = None
    for matrix in normalized_pgl2(p):
        transformed = [mobius(parameters[mark], matrix, p) for mark in marks]
        if mapping == "mod":
            heights = tuple(value % layers for value in transformed)
        else:
            heights = tuple(layers * value // (p + 1) for value in transformed)
        covered, total, missing = coverage(p, heights, layers, "anchored")
        score = (-len(missing), covered)
        if best is None or score > best[0]:
            best = (score, heights, matrix, missing, covered, total)
    assert best is not None
    return {
        "family": "projective_mobius_bucket",
        "mapping": mapping,
        "p": p,
        "layers": layers,
        "missing_classes": -best[0][0],
        "covered": best[4],
        "total": best[5],
        "heights": best[1],
        "matrix": best[2],
        "parameters": [parameters[mark] for mark in marks],
        "missing": best[3],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--layers", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mapping", choices=("bucket", "mod"), default="bucket")
    args = parser.parse_args()
    result = search(args.p, args.layers, args.mapping)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "missing"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
