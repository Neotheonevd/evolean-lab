from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter


@dataclass(frozen=True)
class ExactResult:
    n: int
    maximum_size: int
    witness: list[int]
    explored_nodes: int
    elapsed_seconds: float


def difference_bound(n: int) -> int:
    """Largest m not ruled out by m choose 2 <= n - 1."""
    m = 1
    while (m + 1) * m // 2 <= n - 1:
        m += 1
    return m


def find_sidon_of_size(n: int, target: int) -> tuple[list[int] | None, int]:
    if target == 0:
        return [], 1
    if target == 1:
        return [1], 1
    nodes = 0

    def search(marks: list[int], used_diffs: set[int], start: int) -> list[int] | None:
        nonlocal nodes
        nodes += 1
        need = target - len(marks)
        if need == 0:
            return marks.copy()
        if n - start + 1 < need:
            return None
        for value in range(start, n + 1):
            if n - value + 1 < need - 1:
                break
            new_diffs = [value - old for old in marks]
            if len(set(new_diffs)) != len(new_diffs) or any(diff in used_diffs for diff in new_diffs):
                continue
            result = search(marks + [value], used_diffs | set(new_diffs), value + 1)
            if result is not None:
                return result
        return None

    return search([1], set(), 2), nodes


def exact_maximum(n: int) -> ExactResult:
    started = perf_counter()
    total_nodes = 0
    for target in range(difference_bound(n), 0, -1):
        witness, nodes = find_sidon_of_size(n, target)
        total_nodes += nodes
        if witness is not None:
            return ExactResult(n, target, witness, total_nodes, perf_counter() - started)
    raise AssertionError("singleton witness must exist")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=35)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.max_n < 1:
        raise SystemExit("--max-n must be positive")
    results = [exact_maximum(n) for n in range(1, args.max_n + 1)]
    payload = {
        "definition": "maximum size of a subset of [1,n] with all positive pairwise differences distinct",
        "results": [asdict(result) for result in results],
        "jump_positions": [
            result.n
            for previous, result in zip(results, results[1:])
            if result.maximum_size > previous.maximum_size
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
