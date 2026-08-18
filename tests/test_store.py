import tempfile
import unittest
from pathlib import Path

from evolean_lab.models import Candidate, CandidateKind, Problem
from evolean_lab.store import ResearchStore


class StoreTests(unittest.TestCase):
    def test_round_trip_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = ResearchStore(Path(directory))
            problem = Problem("title", "statement", "domain", ["source"])
            store.save_problem(problem)
            item = Candidate(problem.id, CandidateKind.LEMMA, "lemma", "direct", {})
            store.save_candidate(item)
            loaded = store.load_candidates(problem.id)
            self.assertEqual([candidate.id for candidate in loaded], [item.id])

    def test_problem_is_immutable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = ResearchStore(Path(directory))
            original = Problem("title", "statement", "domain", ["source"], id="same")
            changed = Problem("title", "different", "domain", ["source"], id="same")
            store.save_problem(original)
            with self.assertRaises(ValueError):
                store.save_problem(changed)


if __name__ == "__main__":
    unittest.main()
