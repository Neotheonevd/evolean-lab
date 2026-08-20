import Mathlib.Data.Finset.Card

namespace EvoLeanLab.DefectDecomposition

/-!
# 区间缺陷的循环/绕数不交分解

`exact x` 表示单元有零绕数的真实区间表示，`cyclic x` 表示至少有某个绕数的
循环表示。真实表示必然也是循环表示。
-/

theorem exact_missing_eq_cyclic_missing_add_wrap_only
    {α : Type*} [DecidableEq α]
    (cells : Finset α) (exact cyclic : α → Bool)
    (hsub : ∀ x ∈ cells, exact x = true → cyclic x = true) :
    (cells.filter fun x ↦ exact x = false).card =
      (cells.filter fun x ↦ cyclic x = false).card +
      (cells.filter fun x ↦ cyclic x = true ∧ exact x = false).card := by
  let missing := cells.filter fun x ↦ exact x = false
  let cyclicMissing := cells.filter fun x ↦ cyclic x = false
  let wrapOnly := cells.filter fun x ↦ cyclic x = true ∧ exact x = false
  have hpartition : missing = cyclicMissing ∪ wrapOnly := by
    ext x
    simp only [missing, cyclicMissing, wrapOnly, Finset.mem_filter, Finset.mem_union]
    constructor
    · rintro ⟨hx, hexact⟩
      cases hcyclic : cyclic x
      · exact Or.inl ⟨hx, rfl⟩
      · exact Or.inr ⟨hx, rfl, hexact⟩
    · rintro (⟨hx, hcyclic⟩ | ⟨hx, _, hexact⟩)
      · refine ⟨hx, ?_⟩
        cases hexact : exact x
        · rfl
        · have := hsub x hx hexact
          simp [hcyclic] at this
      · exact ⟨hx, hexact⟩
  have hdisjoint : Disjoint cyclicMissing wrapOnly := by
    apply Finset.disjoint_left.mpr
    intro x hxcyclic hxwrap
    have hfalse := (Finset.mem_filter.mp hxcyclic).2
    have htrue := (Finset.mem_filter.mp hxwrap).2.1
    simp [hfalse] at htrue
  change missing.card = cyclicMissing.card + wrapOnly.card
  rw [hpartition, Finset.card_union_of_disjoint hdisjoint]

end EvoLeanLab.DefectDecomposition
