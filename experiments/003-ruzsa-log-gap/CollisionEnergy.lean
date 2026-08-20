import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Ring

/-!
# 层计数能量的碰撞展开

`c i` 是一个剩余类在层 `i` 中的表示数。第一项是对角碰撞，
`c i * (c i - 1)` 是同层的有序非对角碰撞数在实数中的代数形式。
-/

theorem centered_energy_collision_decomposition
    {ι : Type*} [DecidableEq ι]
    (s : Finset ι) (c : ι → ℝ) (M n : ℝ)
    (hsum : ∑ i ∈ s, c i = n) :
    (∑ i ∈ s, c i ^ 2) - n ^ 2 / M =
      n + (∑ i ∈ s, c i * (c i - 1)) - n ^ 2 / M := by
  have hpoint : ∀ i, c i ^ 2 = c i + c i * (c i - 1) := by
    intro i
    ring
  simp_rw [hpoint, Finset.sum_add_distrib, hsum]
