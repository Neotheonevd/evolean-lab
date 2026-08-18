from __future__ import annotations

import itertools
import json


def differences(a: tuple[int, ...]) -> set[int] | None:
    ds = [y - x for x, y in itertools.combinations(a, 2)]
    return set(ds) if len(ds) == len(set(ds)) else None


def is_maximal_in(a: tuple[int, ...], n: int) -> bool:
    base = differences(a)
    assert base is not None
    for x in range(1, n + 1):
        if x in a:
            continue
        added = tuple(sorted(a + (x,)))
        if differences(added) is not None:
            return False
    return True


def main() -> int:
    n = 43
    total = 0
    sidon = 0
    maximal: list[tuple[int, ...]] = []
    per_order: dict[int, dict[str, int]] = {}
    for order in range(1, 6):
        order_total = 0
        order_sidon = 0
        for a in itertools.combinations(range(1, n + 1), order):
            total += 1
            order_total += 1
            if differences(a) is None:
                continue
            sidon += 1
            order_sidon += 1
            if is_maximal_in(a, n):
                maximal.append(a)
        per_order[order] = {"subsets": order_total, "sidon_subsets": order_sidon}
    witness6 = (1, 2, 4, 13, 32, 37)
    payload = {
        "n": n,
        "orders_checked": [1, 2, 3, 4, 5],
        "all_subsets_checked": total,
        "sidon_subsets_checked": sidon,
        "per_order": per_order,
        "maximal_of_size_at_most_5": maximal,
        "witness6_is_sidon": differences(witness6) is not None,
        "witness6_is_maximal": is_maximal_in(witness6, n),
    }
    print(json.dumps(payload, indent=2))
    return 0 if not maximal and payload["witness6_is_maximal"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
