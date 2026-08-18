from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .models import ResearchStatus, VerificationResult


class LeanVerifier:
    def __init__(self, checker: Path | None = None) -> None:
        default = Path.home() / ".codex" / "skills" / "lean-proof-checker" / "scripts" / "check-lean.ps1"
        self.checker = checker or Path(os.environ.get("EVOLEAN_LEAN_CHECKER", default))

    def verify(self, lean_file: Path, project: Path | None = None) -> VerificationResult:
        if not lean_file.is_file():
            raise FileNotFoundError(lean_file)
        if not self.checker.is_file():
            raise FileNotFoundError(f"Lean checker not found: {self.checker}")
        command = ["pwsh", "-NoProfile", "-File", str(self.checker), "-File", str(lean_file.resolve())]
        if project is not None:
            command.extend(["-Project", str(project.resolve())])
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        status = ResearchStatus.VERIFIED if completed.returncode == 0 else ResearchStatus.UNRESOLVED
        return VerificationResult(
            status=status,
            artifact=str(lean_file.resolve()),
            command=command,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

