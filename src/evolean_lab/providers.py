from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from .models import utc_now


@dataclass(frozen=True)
class Budget:
    max_requests: int = 1
    max_input_tokens: int | None = None
    max_output_tokens: int | None = None
    max_cost_usd: float | None = None

    def __post_init__(self) -> None:
        if self.max_requests < 1:
            raise ValueError("max_requests must be positive")


@dataclass(frozen=True)
class ProposalRequest:
    role: str
    objective: str
    context: dict[str, Any]
    output_schema: dict[str, Any]
    budget: Budget = field(default_factory=Budget)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)


@dataclass(frozen=True)
class ProposalResponse:
    request_id: str
    provider: str
    proposals: list[dict[str, Any]]
    usage: dict[str, Any] = field(default_factory=dict)


class ProposalProvider(Protocol):
    name: str

    def propose(self, request: ProposalRequest) -> ProposalResponse:
        ...


class CodexWorkspaceProvider:
    """Queue work for an interactive Codex task; this is not an API bridge."""

    name = "codex-workspace"

    def __init__(self, queue_dir: Path) -> None:
        self.queue_dir = queue_dir

    def propose(self, request: ProposalRequest) -> ProposalResponse:
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        path = self.queue_dir / f"{request.id}.json"
        path.write_text(json.dumps(asdict(request), ensure_ascii=False, indent=2), encoding="utf-8")
        return ProposalResponse(
            request_id=request.id,
            provider=self.name,
            proposals=[],
            usage={"state": "QUEUED", "job_file": str(path.resolve())},
        )


class OpenAIAPIProvider:
    """Disabled boundary for a future, separately billed Responses API adapter."""

    name = "openai-api"

    def __init__(self, model: str, project_id: str | None = None) -> None:
        self.model = model
        self.project_id = project_id

    def propose(self, request: ProposalRequest) -> ProposalResponse:
        raise RuntimeError(
            "API transport is disabled. Configure a project, secret management, "
            "cost limits, and representative evals before enabling it."
        )

