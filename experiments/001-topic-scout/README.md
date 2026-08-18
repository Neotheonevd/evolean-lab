# Experiment 001: topic scouting

## Frozen domain

Finite extremal combinatorics, initially focused on additive combinatorics and finite set systems.

## Objective

Select a first research topic with a precise open parent problem, a finite computational entry point, plausible intermediate lemmas, and a manageable Lean formalization path.

This is a scouting experiment, not a novelty claim. Open status must be independently rechecked before serious work.

## Primary candidate

Erdős Problem #155. Let `F(N)` be the largest cardinality of a Sidon subset of `{1, ..., N}`. For every fixed `k`, is `F(N+k) <= F(N)+1` for all sufficiently large `N`?

Source: https://www.erdosproblems.com/155

## Experiment

`sidon_scan.py` performs an exact branch-and-bound search using the equivalent distinct-positive-differences characterization. It fixes the minimum mark at `1`, which is valid because every finite integer Sidon set can be translated left without changing its differences.

The finite computation is evidence and a source of sub-conjectures. It cannot resolve the asymptotic open problem.

## First run

The exact scan through `N = 35` found jumps at `2, 4, 7, 12, 18, 26, 35`; at
`N = 35` it produced the size-eight witness `{1, 2, 5, 10, 16, 23, 33, 35}`.
These values agree with the known optimal-Golomb-ruler sequence, so this is a
pipeline validation rather than a novelty claim.

`SidonBridge.lean` mechanically verifies the structural implication used by the
search: unique positive differences imply uniqueness of nondecreasing pair sums.
Lean exits successfully with no `sorry`, `admit`, or added axioms.

Current research status: `PARTIAL_PROGRESS`. The finite maximality certificates
remain Python computations rather than Lean proofs, and no new theorem about the
asymptotic parent problem has been established.
