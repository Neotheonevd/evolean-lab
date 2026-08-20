import Mathlib.Data.Set.Basic
import Mathlib.Data.Finset.Card
import Mathlib.Data.Int.Interval
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

/-- The pointwise Sidon argument gives an injection on every finite family of
non-anchor points, provided their chosen anchors stay in the Sidon set. -/
theorem anchor_difference_injOn {A : Set ℤ} (R : Finset ℤ) (anchor : ℤ → ℤ)
    (hA : IsSidonSet A)
    (hpoint : ∀ x ∈ R, x ∈ A)
    (hanchor : ∀ x ∈ R, anchor x ∈ A)
    (hne : ∀ x ∈ R, x ≠ anchor x) :
    Set.InjOn (fun x ↦ x - anchor x) (R : Set ℤ) := by
  intro x hx y hy hxy
  exact (anchor_difference_injective hA
    (hpoint x hx) (hanchor x hx) (hpoint y hy) (hanchor y hy)
    (hne x hx) hxy).1

/-- Abstract finite counting step behind the repair estimate.  New points are
partitioned into at most `t` anchors and a remainder injected into a target
set of size at most `K`. -/
theorem repair_cardinality_from_partition
    {α β : Type*} [DecidableEq α] [DecidableEq β]
    (new anchors remainder : Finset α) (targets : Finset β)
    (f : α → β) (t K : ℕ)
    (hpartition : new ⊆ anchors ∪ remainder)
    (hanchors : anchors.card ≤ t)
    (hmaps : Set.MapsTo f (remainder : Set α) (targets : Set β))
    (hinj : Set.InjOn f (remainder : Set α))
    (htargets : targets.card ≤ K) :
    new.card ≤ K + t := by
  have hremainder : remainder.card ≤ targets.card :=
    Finset.card_le_card_of_injOn f hmaps hinj
  calc
    new.card ≤ (anchors ∪ remainder).card := Finset.card_le_card hpartition
    _ ≤ anchors.card + remainder.card := Finset.card_union_le anchors remainder
    _ ≤ t + K := Nat.add_le_add hanchors (hremainder.trans htargets)
    _ = K + t := Nat.add_comm t K

/-- Nonzero multiples `q*k` with coefficient between `-K` and `K`. -/
def nonzeroMultiples (q : ℤ) (K : ℕ) : Finset ℤ :=
  (((Finset.Icc (-(K : ℤ)) (K : ℤ)).erase 0).image fun k ↦ q * k)

/-- There are at most `2K` such nonzero multiples.  The inequality also covers
the degenerate case `q = 0`, where the image collapses. -/
theorem nonzeroMultiples_card_le (q : ℤ) (K : ℕ) :
    (nonzeroMultiples q K).card ≤ 2 * K := by
  unfold nonzeroMultiples
  calc
    (((Finset.Icc (-(K : ℤ)) (K : ℤ)).erase 0).image (fun k ↦ q * k)).card ≤
        ((Finset.Icc (-(K : ℤ)) (K : ℤ)).erase 0).card := Finset.card_image_le
    _ = 2 * K := by simp; omega

/-- Sidon-specialized repair bound.  All geometric work is exposed as explicit
hypotheses: the partition into new anchors and non-anchors, membership of chosen
anchors, and the size of the allowed difference set. -/
theorem sidon_repair_card_bound
    (A : Set ℤ) (new anchors remainder targets : Finset ℤ)
    (anchor : ℤ → ℤ) (t K : ℕ)
    (hA : IsSidonSet A)
    (hpartition : new ⊆ anchors ∪ remainder)
    (hanchors : anchors.card ≤ t)
    (hpoint : ∀ x ∈ remainder, x ∈ A)
    (hanchor : ∀ x ∈ remainder, anchor x ∈ A)
    (hne : ∀ x ∈ remainder, x ≠ anchor x)
    (hmaps : Set.MapsTo (fun x ↦ x - anchor x)
      (remainder : Set ℤ) (targets : Set ℤ))
    (htargets : targets.card ≤ K) :
    new.card ≤ K + t := by
  exact repair_cardinality_from_partition new anchors remainder targets
    (fun x ↦ x - anchor x) t K hpartition hanchors hmaps
    (anchor_difference_injOn remainder anchor hA hpoint hanchor hne) htargets

/-- Concrete finite repair estimate once every non-anchor difference is known
to be a nonzero multiple `q*k` with `|k| ≤ K`. -/
theorem sidon_repair_interval_bound
    (A : Set ℤ) (new anchors remainder : Finset ℤ)
    (anchor : ℤ → ℤ) (q : ℤ) (t K : ℕ)
    (hA : IsSidonSet A)
    (hpartition : new ⊆ anchors ∪ remainder)
    (hanchors : anchors.card ≤ t)
    (hpoint : ∀ x ∈ remainder, x ∈ A)
    (hanchor : ∀ x ∈ remainder, anchor x ∈ A)
    (hne : ∀ x ∈ remainder, x ≠ anchor x)
    (hmaps : Set.MapsTo (fun x ↦ x - anchor x)
      (remainder : Set ℤ) (nonzeroMultiples q K : Set ℤ)) :
    new.card ≤ 2 * K + t := by
  exact sidon_repair_card_bound A new anchors remainder (nonzeroMultiples q K)
    anchor t (2 * K) hA hpartition hanchors hpoint hanchor hne hmaps
    (nonzeroMultiples_card_le q K)

end EvoLeanLab.RuzsaRepair
