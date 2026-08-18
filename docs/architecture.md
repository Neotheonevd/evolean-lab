# Architecture

## Research loop

```text
problem pool -> feasibility ranking -> frozen statement
       -> proof-plan and lemma populations
       <-> counterexample population
       -> selection, mutation, migration, archive
       -> Lean gate
       -> VERIFIED / REFUTED / PARTIAL_PROGRESS / UNRESOLVED
```

## Core records

- `Problem`: immutable original statement plus provenance.
- `Candidate`: an evolving proof plan, lemma, counterexample, or strategy.
- `Fitness`: a vector; it is never mathematical evidence.
- `ResearchEvent`: append-only audit record.
- `VerificationResult`: exact command, output, artifact, and status.

## Planned adapters

- LLM proposal and mutation providers;
- literature and Mathlib premise retrieval;
- finite enumeration, SAT, SMT, and computer algebra;
- island-model orchestration;
- novelty and benchmark evaluation.

The core package remains independent of these adapters so experiments can compare them under the same state model.

## Model backends and billing boundaries

`ProposalProvider` is the common interface.

- `CodexWorkspaceProvider` writes bounded jobs for an interactive Codex task. It consumes Codex usage only when Codex actually processes a job; it is not a hidden API bridge.
- `OpenAIAPIProvider` is a disabled transport boundary for separately billed API execution. It must use managed secrets, project budgets, and evals before activation.

Never assume Codex credits are API credits. Record provider identity and usage metadata with every generated candidate.
