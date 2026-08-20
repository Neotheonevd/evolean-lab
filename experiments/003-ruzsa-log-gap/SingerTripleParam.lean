import Mathlib.Algebra.Field.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

namespace EvoLeanLab.SingerTriple

/-!
# Singer 混合表示公式的代数重构

这里的 `F` 代表文献公式中的 Frobenius 值 `φ(A)`。本文件只验证有理式的
代数恒等式；`U,C` 属于相应 Singer 差集仍使用文献中的差集定理。
-/

/-- The two rational expressions from the explicit mixed representation multiply
back to `A`. -/
theorem mixed_representation_reconstruct
    {𝕂 : Type*} [Field 𝕂] (A F : 𝕂)
    (hF : 1 - F ≠ 0) (hAF : A * F - 1 ≠ 0) :
    ((A * F - 1) / (1 - F)) * ((A - A * F) / (A * F - 1)) = A := by
  field_simp

/-- If `A = R/V`, the mixed representation `A = U*C` gives the required
three-point group relation `U*V*W⁻¹ = R` after setting `W=C⁻¹`. -/
theorem singer_triple_reconstruct
    {𝕂 : Type*} [Field 𝕂] (R V F : 𝕂)
    (hV : V ≠ 0)
    (hF : 1 - F ≠ 0)
    (hAF : (R / V) * F - 1 ≠ 0) :
    let A := R / V
    let U := (A * F - 1) / (1 - F)
    let C := (A - A * F) / (A * F - 1)
    let W := C⁻¹
    U * V / W = R := by
  dsimp
  rw [div_eq_mul_inv, inv_inv]
  calc
    (R / V * F - 1) / (1 - F) * V *
        ((R / V - R / V * F) / (R / V * F - 1)) =
      ((R / V * F - 1) / (1 - F) *
        ((R / V - R / V * F) / (R / V * F - 1))) * V := by ring
    _ = (R / V) * V := by
      rw [mixed_representation_reconstruct (R / V) F hF hAF]
    _ = R := div_mul_cancel₀ R hV

end EvoLeanLab.SingerTriple
