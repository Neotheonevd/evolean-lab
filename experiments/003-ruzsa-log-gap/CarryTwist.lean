import Mathlib.Data.Int.Basic
import Mathlib.Tactic.Ring

namespace EvoLeanLab.CarryTwist

/-!
# 用线性坐标扭转吸收循环层中的 carry

若 `bu+bv-bw-r=q*carry` 且 `λq=1 (mod M)`，则给每个循环群代表加入
线性高度 `λb` 后，模 `M` 的层关系与原来的含 carry 层关系完全等价。
-/

theorem twisted_difference_sub_original_is_divisible
    (M q lam bu bv bw r du dv dw j carry : ℤ)
    (hcarry : bu + bv - bw - r = q * carry)
    (hinverse : M ∣ lam * q - 1) :
    M ∣ ((du + lam * bu) + (dv + lam * bv) - (dw + lam * bw) - (j + lam * r)) -
      (du + dv - dw + carry - j) := by
  rcases hinverse with ⟨t, ht⟩
  refine ⟨t * carry, ?_⟩
  calc
    (du + lam * bu + (dv + lam * bv) - (dw + lam * bw) - (j + lam * r)) -
        (du + dv - dw + carry - j) =
      lam * (bu + bv - bw - r) - carry := by ring
    _ = lam * (q * carry) - carry := by rw [hcarry]
    _ = (lam * q - 1) * carry := by ring
    _ = M * (t * carry) := by rw [ht]; ring

/-- Cyclic coverage with the original carry is equivalent to a carry-free
coverage equation in the twisted height coordinate. -/
theorem carry_coverage_iff_twisted_coverage
    (M q lam bu bv bw r du dv dw j carry : ℤ)
    (hcarry : bu + bv - bw - r = q * carry)
    (hinverse : M ∣ lam * q - 1) :
    M ∣ (du + dv - dw + carry - j) ↔
      M ∣ ((du + lam * bu) + (dv + lam * bv) - (dw + lam * bw) - (j + lam * r)) := by
  let original := du + dv - dw + carry - j
  let twisted := (du + lam * bu) + (dv + lam * bv) - (dw + lam * bw) - (j + lam * r)
  change M ∣ original ↔ M ∣ twisted
  have hdiff : M ∣ twisted - original := twisted_difference_sub_original_is_divisible
    M q lam bu bv bw r du dv dw j carry hcarry hinverse
  constructor
  · intro horiginal
    rcases hdiff with ⟨a, ha⟩
    rcases horiginal with ⟨b, hb⟩
    refine ⟨a + b, ?_⟩
    calc
      twisted = (twisted - original) + original := by ring
      _ = M * a + M * b := by rw [ha, hb]
      _ = M * (a + b) := by ring
  · intro htwisted
    rcases htwisted with ⟨a, ha⟩
    rcases hdiff with ⟨b, hb⟩
    refine ⟨a - b, ?_⟩
    calc
      original = twisted - (twisted - original) := by ring
      _ = M * a - M * b := by rw [hb, ha]
      _ = M * (a - b) := by ring

/-- For Singer's `q=p²+p+1`, every divisor `M` of `p+1` admits the twist
parameter `λ=1`. -/
theorem singer_modulus_admits_unit_twist (M p : ℤ) (hM : M ∣ p + 1) :
    M ∣ 1 * (p * p + p + 1) - 1 := by
  rcases hM with ⟨t, ht⟩
  refine ⟨p * t, ?_⟩
  calc
    1 * (p * p + p + 1) - 1 = p * (p + 1) := by ring
    _ = p * (M * t) := by rw [ht]
    _ = M * (p * t) := by ring

/-- The carry-removal equivalence specialized to the Singer modulus and `λ=1`. -/
theorem singer_carry_coverage_iff_twisted_coverage
    (M p bu bv bw r du dv dw j carry : ℤ)
    (hcarry : bu + bv - bw - r = (p * p + p + 1) * carry)
    (hM : M ∣ p + 1) :
    M ∣ (du + dv - dw + carry - j) ↔
      M ∣ ((du + bu) + (dv + bv) - (dw + bw) - (j + r)) := by
  simpa using carry_coverage_iff_twisted_coverage
    M (p * p + p + 1) 1 bu bv bw r du dv dw j carry hcarry
      (singer_modulus_admits_unit_twist M p hM)

end EvoLeanLab.CarryTwist
