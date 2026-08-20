import Mathlib.Data.Set.Basic
import Mathlib.Data.Finset.Card
import Mathlib.Data.Int.Interval
import Lean.Elab.Tactic.Omega

namespace EvoLeanLab.RuzsaRepair

/-- Equal sums in a Sidon set determine the same ordered pair, up to swapping. -/
def IsSidonSet (A : Set ℤ) : Prop :=
  ∀ ⦃a b c d : ℤ⦄, a ∈ A → b ∈ A → c ∈ A → d ∈ A → a + b = c + d →
    (a = c ∧ b = d) ∨ (a = d ∧ b = c)

/-- An old set blocks `x` if adjoining it would create one of the two possible
sum collisions involving the new point. -/
def IsBlockedBy (A₀ : Set ℤ) (x : ℤ) : Prop :=
  ∃ a ∈ A₀, ∃ b ∈ A₀, ∃ c ∈ A₀, x + a = b + c ∨ x + x = b + c

/-- A point lying in a Sidon superset but outside the old set was not already
blocked by the old set. -/
theorem new_point_not_blocked_by_old {A A₀ : Set ℤ} {x : ℤ}
    (hA : IsSidonSet A) (hsub : A₀ ⊆ A) (hx : x ∈ A) (hxold : x ∉ A₀) :
    ¬ IsBlockedBy A₀ x := by
  rintro ⟨a, ha, b, hb, c, hc, htranslate | hmidpoint⟩
  · rcases hA hx (hsub ha) (hsub hb) (hsub hc) htranslate with hsame | hswap
    · exact hxold (hsame.1 ▸ hb)
    · exact hxold (hswap.1 ▸ hc)
  · rcases hA hx hx (hsub hb) (hsub hc) hmidpoint with hsame | hswap
    · exact hxold (hsame.1 ▸ hb)
    · exact hxold (hswap.1 ▸ hc)

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

/-- End-to-end residue-class interface for the repair count.  Old residue
classes choose their anchor in `A₀`; every genuinely new class lies in the
exceptional set `E`; and equal residues use the same anchor.  These hypotheses
automatically make the new-anchor-to-residue map injective. -/
theorem sidon_repair_from_exceptional_residues
    {β : Type*} [DecidableEq β]
    (A A₀ : Finset ℤ) (E : Finset β)
    (ρ : ℤ → β) (anchor : ℤ → ℤ) (q : ℤ) (K : ℕ)
    (hA : IsSidonSet (A : Set ℤ))
    (hA₀ : A₀ ⊆ A)
    (hanchor_mem : ∀ x ∈ A, anchor x ∈ A)
    (hcanonical : ∀ x ∈ A, ∀ y ∈ A, ρ x = ρ y → anchor x = anchor y)
    (hbase : ∀ x ∈ A, (∃ a ∈ A₀, ρ a = ρ x) → anchor x ∈ A₀)
    (hunblocked_location : ∀ x ∈ A, x ∉ A₀ →
      ¬ IsBlockedBy (A₀ : Set ℤ) x →
        (∃ a ∈ A₀, ρ a = ρ x) ∨ ρ x ∈ E)
    (hdifference : ∀ x ∈ A, x ≠ anchor x →
      x - anchor x ∈ nonzeroMultiples q K) :
    (A \ A₀).card ≤ 2 * K + E.card := by
  let new : Finset ℤ := A \ A₀
  let anchors : Finset ℤ := new.filter fun x ↦ x = anchor x
  let remainder : Finset ℤ := new \ anchors
  have hpartition : new ⊆ anchors ∪ remainder := by
    intro x hx
    by_cases hxa : x ∈ anchors
    · exact Finset.mem_union_left remainder hxa
    · exact Finset.mem_union_right anchors (Finset.mem_sdiff.mpr ⟨hx, hxa⟩)
  have hanchors_map : Set.MapsTo ρ (anchors : Set ℤ) (E : Set β) := by
    intro x hx
    have hxfilter := Finset.mem_filter.mp hx
    have hxnew := Finset.mem_sdiff.mp hxfilter.1
    have hxA : x ∈ A := hxnew.1
    rcases hunblocked_location x hxA hxnew.2
      (new_point_not_blocked_by_old hA (fun _ ha ↦ hA₀ ha) hxA hxnew.2) with hold | hE
    · have hanchor_old := hbase x hxA hold
      rw [← hxfilter.2] at hanchor_old
      exact False.elim (hxnew.2 hanchor_old)
    · exact hE
  have hanchors_inj : Set.InjOn ρ (anchors : Set ℤ) := by
    intro x hx y hy hrho
    have hxfilter := Finset.mem_filter.mp hx
    have hyfilter := Finset.mem_filter.mp hy
    have hxA : x ∈ A := (Finset.mem_sdiff.mp hxfilter.1).1
    have hyA : y ∈ A := (Finset.mem_sdiff.mp hyfilter.1).1
    exact hxfilter.2.trans ((hcanonical x hxA y hyA hrho).trans hyfilter.2.symm)
  have hanchors_card : anchors.card ≤ E.card :=
    Finset.card_le_card_of_injOn ρ hanchors_map hanchors_inj
  have hpoint : ∀ x ∈ remainder, x ∈ (A : Set ℤ) := by
    intro x hx
    exact (Finset.mem_sdiff.mp (Finset.mem_sdiff.mp hx).1).1
  have hchosen : ∀ x ∈ remainder, anchor x ∈ (A : Set ℤ) := by
    intro x hx
    exact hanchor_mem x (hpoint x hx)
  have hnonanchor : ∀ x ∈ remainder, x ≠ anchor x := by
    intro x hx hxeq
    have hxparts := Finset.mem_sdiff.mp hx
    apply hxparts.2
    exact Finset.mem_filter.mpr ⟨hxparts.1, hxeq⟩
  have hdiff_map : Set.MapsTo (fun x ↦ x - anchor x)
      (remainder : Set ℤ) (nonzeroMultiples q K : Set ℤ) := by
    intro x hx
    exact hdifference x (hpoint x hx) (hnonanchor x hx)
  have hbound := sidon_repair_interval_bound (A : Set ℤ) new anchors remainder
    anchor q E.card K hA hpartition hanchors_card hpoint hchosen hnonanchor hdiff_map
  simpa [new] using hbound

end EvoLeanLab.RuzsaRepair
