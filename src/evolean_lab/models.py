from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ResearchStatus(StrEnum):
    PROPOSED = "PROPOSED"
    UNRESOLVED = "UNRESOLVED"
    PARTIAL_PROGRESS = "PARTIAL_PROGRESS"
    VERIFIED = "VERIFIED"
    REFUTED = "REFUTED"


class CandidateKind(StrEnum):
    PROOF_PLAN = "PROOF_PLAN"
    LEMMA = "LEMMA"
    COUNTEREXAMPLE = "COUNTEREXAMPLE"
    STRATEGY = "STRATEGY"


@dataclass(frozen=True)
class Problem:
    title: str
    statement: str
    domain: str
    provenance: list[str]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Fitness:
    verified_progress: float = 0.0
    tractability: float = 0.0
    novelty: float = 0.0
    reuse_value: float = 0.0
    counterexample_resilience: float = 0.0
    complexity_penalty: float = 0.0
    assumption_penalty: float = 0.0

    def scalar_hint(self) -> float:
        return (
            3.0 * self.verified_progress
            + self.tractability
            + self.novelty
            + self.reuse_value
            + self.counterexample_resilience
            - self.complexity_penalty
            - 3.0 * self.assumption_penalty
        )


@dataclass
class Candidate:
    problem_id: str
    kind: CandidateKind
    statement: str
    method: str
    payload: dict[str, Any]
    fitness: Fitness = field(default_factory=Fitness)
    status: ResearchStatus = ResearchStatus.PROPOSED
    parents: list[str] = field(default_factory=list)
    generation: int = 0
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["kind"] = self.kind.value
        value["status"] = self.status.value
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Candidate":
        data = dict(value)
        data["kind"] = CandidateKind(data["kind"])
        data["status"] = ResearchStatus(data["status"])
        data["fitness"] = Fitness(**data["fitness"])
        return cls(**data)


@dataclass(frozen=True)
class ResearchEvent:
    event_type: str
    subject_id: str
    data: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VerificationResult:
    status: ResearchStatus
    artifact: str
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["status"] = self.status.value
        return value

