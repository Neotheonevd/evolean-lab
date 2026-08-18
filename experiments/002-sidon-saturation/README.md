# Experiment 002: Sidon saturation

For a positive integer `n`, let `s(n)` be the minimum cardinality of a Sidon
subset of `{1, ..., n}` that is maximal under inclusion.

This experiment asks whether the saturation version has a clean exact sequence,
structural lower bounds, or explicit constructions. It is deliberately separate
from the maximum-cardinality function in Experiment 001.

No novelty is claimed until the definition and any resulting theorem have been
checked against the literature under alternate terminology.

## Result of the first run

The exact values through `n = 35` begin

`1, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, ..., 4, 5, ..., 5`,

with transitions at `n = 2, 5, 11, 23`. A tempting extrapolation predicted the
next transition at `47`; a fixed-order search refuted it.

The finite result obtained is

`s(43) = 6`.

- Upper bound: `{1, 2, 4, 13, 32, 37}` is an inclusion-maximal Sidon subset of
  `[1,43]`. `Saturation43.lean` verifies the executable certificate with Lean.
- Lower bound: `independent_difference_check.py` checks all 1,099,295 subsets
  of `[1,43]` of sizes one through five. Of these, 603,824 are Sidon sets and
  none is inclusion-maximal. This implementation uses positive differences,
  independently of the pair-sum implementation used by Lean and the first scan.

The Lean status of the upper-bound certificate is `VERIFIED`. The complete
equality is currently `COMPUTATIONALLY_VERIFIED`, not yet a fully formal Lean
theorem, because the exhaustive lower-bound computation has not been imported
as a proof-producing Lean certificate.

## Literature status

The general topic is established rather than new: I. Z. Ruzsa's 1998 paper is
titled *A small maximal Sidon set*, and later literature calls these “small
complete Sidon sets.” The exact finite value above remains a candidate data
contribution only; absence from initial searches is not evidence of novelty.
