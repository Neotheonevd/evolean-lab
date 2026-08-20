import Mathlib.Data.Set.Basic
import Lean.Elab.Tactic.Omega

namespace EvoLeanLab.RuzsaRepair

/-- Equal sums in a Sidon set determine the same ordered pair, up to swapping. -/
def IsSidonSet (A : Set ℤ) : Prop :=
  ∀ ⦃a b c d : ℤ⦄, a ∈ A → b ∈ A → c ∈ A → d ∈ A → a + b = c + d →
    (a = c ∧ b = d) ∨ (a = d ∧ b = c)

/--
Core injection behind the repair estimate.  Pair every non-anchor point `x` with an
anchor `ax` in the same residue class.  In a Sidon set two resulting nonzero
differences cannot be equal unless both the points and their anchors agree.
-/
theorem anchor_difference_injective {A : Set ℤ} {x ax y ay : ℤ}
    (hA : IsSidonSet A)
    (hx : x ∈ A) (hax : ax ∈ A) (hy : y ∈ A) (hay : ay ∈ A)
    (hne : x ≠ ax) (hdiff : x - ax = y - ay) :
    x = y ∧ ax = ay := by
  have hsum : x + ay = y + ax := by omega
  rcases hA hx hay hy hax hsum with hsame | hswap
  · exact ⟨hsame.1, hsame.2.symm⟩
  · exact False.elim (hne hswap.1)

end EvoLeanLab.RuzsaRepair
