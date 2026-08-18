from __future__ import annotations

import argparse
import itertools

from fixed_order_scan import blocked_points, is_sidon


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--order", type=int, required=True)
    parser.add_argument("--n", type=int, required=True)
    args = parser.parse_args()
    checked = 0
    for a in itertools.combinations(range(1, args.n + 1), args.order):
        if not is_sidon(a):
            continue
        checked += 1
        if len(blocked_points(a, args.n)) == args.n:
            print({"n": args.n, "order": args.order, "witness": a, "sidon_checked": checked})
            return 0
    print({"n": args.n, "order": args.order, "witness": None, "sidon_checked": checked})
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
