import Mathlib.Algebra.Order.Chebyshev
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity

/-!
# 缺层导致二次能量间隙

这是 Singer 高度覆盖问题的新归约所需的纯组合核心。`s` 是非空层的集合，
`x i` 是对应层的表示次数。若总共有 `n` 个表示，而至多 `M-1` 个层非空，
则相对完全均匀分布的二次能量至少增加 `n² / (M(M-1))`。
-/

theorem missing_layer_energy_gap
    {ι : Type*} [DecidableEq ι]
    (s : Finset ι) (x : ι → ℝ) (M n : ℝ)
    (hM : 1 < M)
    (hcard : (s.card : ℝ) ≤ M - 1)
    (hsum : ∑ i ∈ s, x i = n) :
    n ^ 2 / M + n ^ 2 / (M * (M - 1)) ≤ ∑ i ∈ s, x i ^ 2 := by
  have hsquares : 0 ≤ ∑ i ∈ s, x i ^ 2 := by positivity
  have hcs := sq_sum_le_card_mul_sum_sq (s := s) (f := x)
  rw [hsum] at hcs
  have hscaled : n ^ 2 ≤ (M - 1) * ∑ i ∈ s, x i ^ 2 := by
    nlinarith
  have hM0 : 0 < M := by linarith
  have hMm10 : 0 < M - 1 := by linarith
  have hprod : 0 < M * (M - 1) := mul_pos hM0 hMm10
  have hid : n ^ 2 / M + n ^ 2 / (M * (M - 1)) = n ^ 2 / (M - 1) := by
    field_simp [ne_of_gt hM0, ne_of_gt hMm10]
    ring
  rw [hid]
  apply (div_le_iff₀ hMm10).2
  simpa [mul_comm] using hscaled
