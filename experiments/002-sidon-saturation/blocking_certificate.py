from __future__ import annotations

import argparse
import json
from pathlib import Path

from fixed_order_scan import is_sidon


def first_blocker(a: tuple[int, ...], x: int) -> dict[str, object] | None:
    if x in a:
        return {"x": x, "kind": "member"}
    old_pairs = [(u, v) for i, u in enumerate(a) for v in a[i:]]
    old_by_sum = {u + v: (u, v) for u, v in old_pairs}
    if 2 * x in old_by_sum:
        u, v = old_by_sum[2 * x]
        return {"x": x, "kind": "midpoint", "equation": f"2*{x}={u}+{v}"}
    for y in a:
        if x + y in old_by_sum:
            u, v = old_by_sum[x + y]
            return {"x": x, "kind": "translate", "equation": f"{x}+{y}={u}+{v}"}
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", dest="marks", nargs="+", type=int, required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    a = tuple(sorted(args.marks))
    if len(set(a)) != len(a) or not is_sidon(a):
        raise SystemExit("the supplied marks are not a Sidon set")
    certificates = [first_blocker(a, x) for x in range(1, args.n + 1)]
    uncovered = [x for x, certificate in enumerate(certificates, 1) if certificate is None]
    kinds: dict[str, int] = {}
    for certificate in certificates:
        if certificate is not None:
            kind = str(certificate["kind"])
            kinds[kind] = kinds.get(kind, 0) + 1
    payload = {
        "set": a,
        "n": args.n,
        "is_sidon": True,
        "is_maximal": not uncovered,
        "uncovered": uncovered,
        "blocking_kind_counts": kinds,
        "certificates": certificates,
    }
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in payload.items() if key != "certificates"}, indent=2))
    return 0 if not uncovered else 1


if __name__ == "__main__":
    raise SystemExit(main())
