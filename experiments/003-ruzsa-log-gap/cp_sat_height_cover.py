from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


DEPS = Path(__file__).resolve().parents[2] / ".python-deps"
sys.path.insert(0, str(DEPS))

from ortools.sat.python import cp_model  # noqa: E402

from height_cover_search import residue_triples, singer_set  # noqa: E402


def build_and_solve(p: int, layers: int, seconds: float, workers: int,
                    hint_path: Path | None, max_bad: int | None):
    q = p * p + p + 1
    marks = tuple(q if mark == 0 else mark for mark in singer_set(p))
    model = cp_model.CpModel()
    heights = [model.new_int_var(0, layers - 1, f"d_{i}") for i in range(p + 1)]
    good_classes = []
    layer_covered = []

    for residue in range(1, q + 1):
        if residue in marks:
            continue
        covered_here = []
        triples = residue_triples(q, marks, residue)
        if len(triples) != p + 1:
            raise ValueError(f"residue {residue} has {len(triples)} triples, expected {p + 1}")
        for target in range(layers):
            hits = []
            for triple_index, (u, v, w, carry) in enumerate(triples):
                hit = model.new_bool_var(f"hit_{residue}_{target}_{triple_index}")
                expression = heights[u] + heights[v] - heights[w] + carry
                model.add(expression == target).only_enforce_if(hit)
                model.add(expression != target).only_enforce_if(hit.Not())
                hits.append(hit)
            covered = model.new_bool_var(f"covered_{residue}_{target}")
            model.add_max_equality(covered, hits)
            covered_here.append(covered)
            layer_covered.append(covered)
        good = model.new_bool_var(f"good_{residue}")
        model.add_min_equality(good, covered_here)
        good_classes.append(good)

    # Primary objective: minimize the number of bad residue classes.  A secondary
    # layer-coverage term selects stronger witnesses without changing that optimum.
    layer_weight = len(layer_covered) + 1
    if max_bad is None:
        model.maximize(layer_weight * sum(good_classes) + sum(layer_covered))
    else:
        model.add(sum(good_classes) >= p * p - max_bad)

    if hint_path is not None:
        source = json.loads(hint_path.read_text(encoding="utf-8"))
        for variable, value in zip(heights, source["heights"]):
            model.add_hint(variable, value)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.log_search_progress = False
    status = solver.solve(model)
    status_name = solver.status_name(status)
    result = {
        "method": "cp_sat_exact_model",
        "status": status_name,
        "p": p,
        "q": q,
        "layers": layers,
        "objective": solver.objective_value if max_bad is None else None,
        "best_bound": solver.best_objective_bound if max_bad is None else None,
        "max_bad_decision": max_bad,
        "wall_time_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        good_count = sum(solver.value(variable) for variable in good_classes)
        covered_count = sum(solver.value(variable) for variable in layer_covered)
        result.update({
            "good_classes": good_count,
            "missing_classes": p * p - good_count,
            "covered": covered_count,
            "total": p * p * layers,
            "heights": [solver.value(variable) for variable in heights],
        })
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--layers", type=int, required=True)
    parser.add_argument("--seconds", type=float, default=180)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--hint", type=Path)
    parser.add_argument("--max-bad", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_and_solve(
        args.p, args.layers, args.seconds, args.workers, args.hint, args.max_bad
    )
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
