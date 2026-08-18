# EvoLean Lab

EvoLean Lab is an experimental mathematical research system in which conjectures, proof plans, lemmas, counterexamples, and search strategies evolve while Lean controls admission to the verified archive.

Version 0.1 is an offline, model-independent foundation. It provides:

- immutable mathematical statements with explicit derived variants;
- multi-objective candidate fitness;
- diversity-preserving population selection;
- mutation and lineage tracking;
- append-only research events and JSON snapshots;
- a Lean/Mathlib verification adapter;
- a deterministic demo experiment and unit tests.

It does not yet claim autonomous mathematical discovery. LLM generation, literature retrieval, finite model search, and distributed island populations are later adapters.

## Current experiments

- [Experiment 001: topic scouting](experiments/001-topic-scout/README.md) selects finite extremal combinatorics and validates the Sidon/Golomb-ruler search bridge in Lean.
- [Experiment 002: Sidon saturation](experiments/002-sidon-saturation/README.md) studies minimum-size inclusion-maximal Sidon subsets. Its [full Chinese report](experiments/002-sidon-saturation/EXPERIMENT_REPORT.zh-CN.md) records conjecture generation, counterexample search, independent enumeration, literature review, and the Lean-verified upper-bound certificate for `s(43) = 6`.

Evidence labels are intentionally strict: the concrete six-element witness is Lean `VERIFIED`; the exhaustive lower bound is currently `COMPUTATIONALLY_VERIFIED`; literature novelty remains `UNRESOLVED`.

## Quick start

```powershell
python -m evolean_lab.cli init
python -m evolean_lab.cli demo-cycle
python -m evolean_lab.cli status
python -m evolean_lab.cli enqueue-codex --role strategist --objective "Generate three distinct proof plans"
python -m evolean_lab.cli verify --file path\to\Theorem.lean --project path\to\lake-project
```

When running from a source checkout, install the project in a virtual environment, or set `PYTHONPATH=src`:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## Trust boundary

Only Lean exit code 0 without warnings-as-errors violations may produce `VERIFIED`. Numerical checks and finite enumeration are evidence, not general proofs. A counterexample produces `REFUTED` only after every hypothesis has been checked.

See [docs/vision.md](docs/vision.md) and [docs/architecture.md](docs/architecture.md).

## License

No open-source license has been selected yet. Public visibility does not by itself grant permission to reuse the code; a license can be added once the project policy is chosen.
