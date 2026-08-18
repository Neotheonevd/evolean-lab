import Mathlib.Data.Finset.Basic
import Lean.Elab.Tactic.Omega

namespace EvoLeanLab.TopicScout

/-- Positive differences between pairs of elements of `A` uniquely identify the pair. -/
def HasUniquePositiveDifferences (A : Finset ℕ) : Prop :=
  ∀ ⦃a b c d : ℕ⦄, a ∈ A → b ∈ A → c ∈ A → d ∈ A →
    a < b → c < d → b - a = d - c → a = c ∧ b = d

/-- Sums of nondecreasing pairs from `A` uniquely identify the pair. -/
def IsSidon (A : Finset ℕ) : Prop :=
  ∀ ⦃a b c d : ℕ⦄, a ∈ A → b ∈ A → c ∈ A → d ∈ A →
    a ≤ b → c ≤ d → a + b = c + d → a = c ∧ b = d

/-- The invariant used by the exact search is sufficient for the Sidon property. -/
theorem uniquePositiveDifferences_implies_isSidon {A : Finset ℕ}
    (h : HasUniquePositiveDifferences A) : IsSidon A := by
  intro a b c d ha hb hc hd hab hcd hsum
  by_cases hac : a = c
  · subst c
    constructor
    · rfl
    · omega
  rcases lt_or_gt_of_ne hac with haltc | hcgta
  · have hdltb : d < b := by omega
    have hdiff : c - a = b - d := by omega
    have hpairs := h ha hc hd hb haltc hdltb hdiff
    omega
  · have hbltd : b < d := by omega
    have hdiff : a - c = d - b := by omega
    have hpairs := h hc ha hb hd hcgta hbltd hdiff
    omega

end EvoLeanLab.TopicScout
