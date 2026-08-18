from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Candidate, Problem, ResearchEvent


class ResearchStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.problems_dir = root / "problems"
        self.candidates_dir = root / "candidates"
        self.events_file = root / "events.jsonl"

    def initialize(self) -> None:
        self.problems_dir.mkdir(parents=True, exist_ok=True)
        self.candidates_dir.mkdir(parents=True, exist_ok=True)
        self.events_file.touch(exist_ok=True)

    @staticmethod
    def _write_json(path: Path, value: dict[str, Any]) -> None:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

    def save_problem(self, problem: Problem) -> None:
        self.initialize()
        target = self.problems_dir / f"{problem.id}.json"
        if target.exists():
            existing = json.loads(target.read_text(encoding="utf-8"))
            if existing != problem.to_dict():
                raise ValueError("Original problem records are immutable")
            return
        self._write_json(target, problem.to_dict())
        self.append_event(ResearchEvent("problem.created", problem.id, {}))

    def save_candidate(self, candidate: Candidate) -> None:
        self.initialize()
        self._write_json(self.candidates_dir / f"{candidate.id}.json", candidate.to_dict())
        self.append_event(
            ResearchEvent(
                "candidate.saved",
                candidate.id,
                {"generation": candidate.generation, "status": candidate.status.value},
            )
        )

    def load_candidates(self, problem_id: str | None = None) -> list[Candidate]:
        self.initialize()
        candidates = [
            Candidate.from_dict(json.loads(path.read_text(encoding="utf-8")))
            for path in self.candidates_dir.glob("*.json")
        ]
        if problem_id is not None:
            candidates = [item for item in candidates if item.problem_id == problem_id]
        return sorted(candidates, key=lambda item: (item.generation, item.id))

    def append_event(self, event: ResearchEvent) -> None:
        self.initialize()
        with self.events_file.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

