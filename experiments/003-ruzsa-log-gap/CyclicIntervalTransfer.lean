import Mathlib.Data.Int.Basic
import Mathlib.Tactic.Linarith
import Lean.Elab.Tactic.Omega

namespace EvoLeanLab.CyclicTransfer

/-!
# 循环层到整数区间层的三提升分解

在 Singer 提升中，真实层值落在 `[-M,2M-1]`。若它与目标层 `j∈[0,M-1]`
模 `M` 同余，则绕数只能为 `-1,0,1`。
-/

theorem cyclic_hit_has_three_lifts
    (M j L : ℤ)
    (hM : 0 < M) (hj0 : 0 ≤ j) (hjM : j < M)
    (hL0 : -M ≤ L) (hL1 : L ≤ 2 * M - 1)
    (hcongr : ∃ k : ℤ, L = j + k * M) :
    L = j - M ∨ L = j ∨ L = j + M := by
  rcases hcongr with ⟨k, rfl⟩
  have hklo : -1 ≤ k := by
    by_contra h
    have hk : k ≤ -2 := by omega
    nlinarith
  have hkhi : k ≤ 1 := by
    by_contra h
    have hk : 2 ≤ k := by omega
    nlinarith
  have hkcases : k = -1 ∨ k = 0 ∨ k = 1 := by omega
  rcases hkcases with rfl | rfl | rfl
  · left
    omega
  · right
    left
    omega
  · right
    right
    omega

/-- Cyclic coverage alone cannot imply interval coverage: the upper-wrap lift
`L=j+M` is always in the allowed global range and is congruent to `j`, but is
never the exact integer target. -/
theorem upper_wrap_is_abstract_counterexample
    (M j : ℤ) (hM : 0 < M) (hj0 : 0 ≤ j) (hjM : j < M) :
    let L := j + M
    (-M ≤ L ∧ L ≤ 2 * M - 1 ∧
      (∃ k : ℤ, L = j + k * M) ∧ L ≠ j) := by
  dsimp
  constructor
  · omega
  constructor
  · omega
  constructor
  · exact ⟨1, by simp⟩
  · omega

end EvoLeanLab.CyclicTransfer
