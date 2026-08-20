from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from height_cover_search import coverage, field_mul, field_pow, singer_set
from projective_height_search import primitive_cubic


Vector = tuple[int, int, int]


def field_trace(value: Vector, p: int, relation: Vector) -> int:
    first = field_pow(value, p, p, relation)
    second = field_pow(value, p * p, p, relation)
    result = tuple((value[i] + first[i] + second[i]) % p for i in range(3))
    if result[1:] != (0, 0):
        raise ValueError("trace did not land in the base field")
    return result[0]


def singer_norm_one_points(p: int) -> tuple[Vector, ...]:
    relation = primitive_cubic(p)
    primitive = (0, 1, 0)
    points = tuple(
        field_pow(field_pow(primitive, exponent, p, relation), p - 1, p, relation)
        for exponent in singer_set(p)
    )
    for point in points:
        power = field_pow(point, p + 1, p, relation)
        polynomial = ((power[0] + point[0] + 1) % p,
                      (power[1] + point[1]) % p,
                      (power[2] + point[2]) % p)
        if polynomial != (0, 0, 0):
            raise ValueError("point does not satisfy X^(p+1)+X+1=0")
    return points


def search(p: int, layers: int, mapping: str, power: int):
    relation = primitive_cubic(p)
    points = tuple(field_pow(point, power, p, relation) for point in singer_norm_one_points(p))
    best = None
    tested = 0
    for functional in itertools.product(range(p), repeat=3):
        if functional == (0, 0, 0):
            continue
        values = [
            field_trace(field_mul(functional, point, p, relation), p, relation)
            for point in points
        ]
        for shift in range(p):
            shifted = [((value + shift) % p) for value in values]
            if mapping == "bucket":
                heights = tuple(layers * value // p for value in shifted)
            else:
                heights = tuple(value % layers for value in shifted)
            covered, total, missing = coverage(p, heights, layers, "anchored")
            score = (-len(missing), covered)
            tested += 1
            if best is None or score > best[0]:
                best = score, heights, functional, shift, missing, covered, total
    assert best is not None
    return {
        "family": "finite_field_linear_trace",
        "mapping": mapping,
        "power": power,
        "p": p,
        "q": p * p + p + 1,
        "layers": layers,
        "missing_classes": -best[0][0],
        "covered": best[5],
        "total": best[6],
        "heights": best[1],
        "functional": best[2],
        "shift": best[3],
        "tested": tested,
        "missing": best[4],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--layers", type=int, required=True)
    parser.add_argument("--mapping", choices=("bucket", "mod"), default="bucket")
    parser.add_argument("--power", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = search(args.p, args.layers, args.mapping, args.power)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "missing"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
