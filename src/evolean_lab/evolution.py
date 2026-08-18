from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import replace
from hashlib import sha256

from .models import Candidate, Fitness, ResearchStatus

Mutator = Callable[[Candidate, int], Candidate]


def behavioral_signature(candidate: Candidate) -> str:
    normalized = "|".join(
        [candidate.kind.value, candidate.method.strip().lower(), candidate.statement.strip().lower()]
    )
    return sha256(normalized.encode("utf-8")).hexdigest()[:16]


def select_diverse_elite(candidates: Iterable[Candidate], limit: int) -> list[Candidate]:
    if limit < 1:
        raise ValueError("limit must be positive")
    ranked = sorted(
        candidates,
        key=lambda item: (item.fitness.scalar_hint(), item.fitness.novelty, item.id),
        reverse=True,
    )
    selected: list[Candidate] = []
    seen: set[str] = set()
    for candidate in ranked:
        signature = behavioral_signature(candidate)
        if signature not in seen:
            selected.append(candidate)
            seen.add(signature)
        if len(selected) == limit:
            return selected
    for candidate in ranked:
        if candidate not in selected:
            selected.append(candidate)
        if len(selected) == limit:
            break
    return selected


def deterministic_plan_mutator(parent: Candidate, variant: int) -> Candidate:
    methods = ["induction", "minimal-counterexample", "double-counting", "invariant"]
    method = methods[variant % len(methods)]
    payload = dict(parent.payload)
    payload["mutation"] = {"operator": "replace_method", "variant": variant}
    fitness = replace(
        parent.fitness,
        novelty=min(1.0, parent.fitness.novelty + 0.1 * (variant + 1)),
        complexity_penalty=parent.fitness.complexity_penalty + 0.02,
    )
    return Candidate(
        problem_id=parent.problem_id,
        kind=parent.kind,
        statement=parent.statement,
        method=method,
        payload=payload,
        fitness=fitness,
        status=ResearchStatus.UNRESOLVED,
        parents=[parent.id],
        generation=parent.generation + 1,
    )


class EvolutionEngine:
    def __init__(self, population_size: int = 8, offspring_per_parent: int = 2) -> None:
        if population_size < 1 or offspring_per_parent < 1:
            raise ValueError("population settings must be positive")
        self.population_size = population_size
        self.offspring_per_parent = offspring_per_parent

    def next_generation(self, population: list[Candidate], mutator: Mutator) -> list[Candidate]:
        if not population:
            return []
        parents = select_diverse_elite(population, min(len(population), self.population_size))
        offspring = [
            mutator(parent, variant)
            for parent in parents
            for variant in range(self.offspring_per_parent)
        ]
        return select_diverse_elite([*parents, *offspring], self.population_size)

