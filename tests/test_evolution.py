import unittest

from evolean_lab.evolution import EvolutionEngine, deterministic_plan_mutator, select_diverse_elite
from evolean_lab.models import Candidate, CandidateKind, Fitness


def candidate(method: str, score: float) -> Candidate:
    return Candidate(
        problem_id="p",
        kind=CandidateKind.PROOF_PLAN,
        statement="A implies A",
        method=method,
        payload={},
        fitness=Fitness(verified_progress=score),
    )


class EvolutionTests(unittest.TestCase):
    def test_selection_preserves_distinct_methods(self) -> None:
        population = [candidate("direct", 1.0), candidate("direct", 0.9), candidate("induction", 0.8)]
        selected = select_diverse_elite(population, 2)
        self.assertEqual({item.method for item in selected}, {"direct", "induction"})

    def test_generation_tracks_parent_and_generation(self) -> None:
        seed = candidate("direct", 0.1)
        result = EvolutionEngine(population_size=3, offspring_per_parent=3).next_generation(
            [seed], deterministic_plan_mutator
        )
        children = [item for item in result if item.id != seed.id]
        self.assertTrue(children)
        self.assertTrue(all(seed.id in item.parents for item in children))
        self.assertTrue(all(item.generation == 1 for item in children))


if __name__ == "__main__":
    unittest.main()

