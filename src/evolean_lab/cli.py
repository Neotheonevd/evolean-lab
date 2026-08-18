from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evolution import EvolutionEngine, deterministic_plan_mutator
from .lean import LeanVerifier
from .models import Candidate, CandidateKind, Fitness, Problem
from .providers import Budget, CodexWorkspaceProvider, ProposalRequest
from .store import ResearchStore


def default_store() -> Path:
    return Path.cwd() / ".evolean"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="evolean")
    parser.add_argument("--store", type=Path, default=default_store())
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    commands.add_parser("status")
    commands.add_parser("demo-cycle")
    verify = commands.add_parser("verify")
    verify.add_argument("--file", type=Path, required=True)
    verify.add_argument("--project", type=Path)
    enqueue = commands.add_parser("enqueue-codex")
    enqueue.add_argument("--role", required=True)
    enqueue.add_argument("--objective", required=True)
    return parser


def run_demo(store: ResearchStore) -> dict[str, object]:
    problem = Problem(
        title="Demo finite-set plan search",
        statement="For every finite set A, A is a subset of A.",
        domain="finite combinatorics",
        provenance=["internal deterministic smoke test"],
    )
    store.save_problem(problem)
    seed = Candidate(
        problem_id=problem.id,
        kind=CandidateKind.PROOF_PLAN,
        statement=problem.statement,
        method="direct",
        payload={"steps": ["unfold subset", "introduce element", "close by assumption"]},
        fitness=Fitness(tractability=0.8, novelty=0.1, reuse_value=0.2),
    )
    engine = EvolutionEngine(population_size=4, offspring_per_parent=4)
    population = engine.next_generation([seed], deterministic_plan_mutator)
    store.save_candidate(seed)
    for candidate in population:
        store.save_candidate(candidate)
    return {"problem_id": problem.id, "population": [item.to_dict() for item in population]}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = ResearchStore(args.store)
    if args.command == "init":
        store.initialize()
        print(f"Initialized research store at {store.root.resolve()}")
        return 0
    if args.command == "status":
        candidates = store.load_candidates()
        print(json.dumps({"store": str(store.root.resolve()), "candidates": len(candidates)}, indent=2))
        return 0
    if args.command == "demo-cycle":
        print(json.dumps(run_demo(store), ensure_ascii=False, indent=2))
        return 0
    if args.command == "verify":
        result = LeanVerifier().verify(args.file, args.project)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.exit_code == 0 else 1
    if args.command == "enqueue-codex":
        request = ProposalRequest(
            role=args.role,
            objective=args.objective,
            context={},
            output_schema={"proposals": "array"},
            budget=Budget(max_requests=1),
        )
        response = CodexWorkspaceProvider(store.root / "jobs" / "pending").propose(request)
        print(json.dumps(response.usage, ensure_ascii=False, indent=2))
        return 0
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
