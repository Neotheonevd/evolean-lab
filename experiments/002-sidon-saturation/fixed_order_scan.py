from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def is_sidon(a: tuple[int, ...]) -> bool:
    sums = [x + y for i, x in enumerate(a) for y in a[i:]]
    return len(sums) == len(set(sums))


def blocked_points(a: tuple[int, ...], limit: int) -> set[int]:
    old_sums = {x + y for i, x in enumerate(a) for y in a[i:]}
    blocked = set(a)
    for x in range(1, limit + 1):
        if x in blocked:
            continue
        new_sums = [x + y for y in a] + [2 * x]
        if len(new_sums) != len(set(new_sums)) or any(s in old_sums for s in new_sums):
            blocked.add(x)
    return blocked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--order", type=int, required=True)
    parser.add_argument("--coordinate-limit", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    best_prefix = 0
    witnesses: list[list[int]] = []
    sidon_count = 0
    for a in itertools.combinations(range(1, args.coordinate_limit + 1), args.order):
        if not is_sidon(a):
            continue
        sidon_count += 1
        blocked = blocked_points(a, args.coordinate_limit)
        prefix = 0
        while prefix + 1 in blocked:
            prefix += 1
        if prefix > best_prefix:
            best_prefix, witnesses = prefix, [list(a)]
        elif prefix == best_prefix:
            witnesses.append(list(a))
    payload = {
        "order": args.order,
        "coordinate_limit": args.coordinate_limit,
        "largest_saturated_prefix": best_prefix,
        "witnesses": witnesses,
        "sidon_sets_checked": sidon_count,
        "conditional": "The result only ranges over sets whose elements do not exceed coordinate_limit.",
    }
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({**payload, "witnesses": witnesses[:10]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
