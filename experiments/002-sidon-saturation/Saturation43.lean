import Mathlib.Data.Finset.Basic

namespace EvoLeanLab.SidonSaturation

/-- Mathematical Sidon predicate: equal ordered-pair sums have the same unordered pair. -/
def IsSidonSet (A : Set ℕ) : Prop :=
  ∀ ⦃a b c d : ℕ⦄, a ∈ A → b ∈ A → c ∈ A → d ∈ A → a + b = c + d →
    (a = c ∧ b = d) ∨ (a = d ∧ b = c)

/-- A point is blocked when adding it creates a sum collision with old elements. -/
def IsBlockedBy (A : Set ℕ) (x : ℕ) : Prop :=
  ∃ a ∈ A, ∃ b ∈ A, ∃ c ∈ A, x + a = b + c ∨ x + x = b + c

/-- A blocking equation is a genuine certificate that `x` cannot be adjoined. -/
theorem blocked_prevents_sidon_extension {A : Set ℕ} {x : ℕ}
    (hx : x ∉ A) (hblock : IsBlockedBy A x) : ¬ IsSidonSet (insert x A) := by
  rintro hsidon
  rcases hblock with ⟨a, ha, b, hb, c, hc, htranslate | hmidpoint⟩
  · have hcollision := hsidon (show x ∈ insert x A by simp)
        (show a ∈ insert x A by simp [ha])
        (show b ∈ insert x A by simp [hb])
        (show c ∈ insert x A by simp [hc]) htranslate
    rcases hcollision with hsame | hswap
    · exact hx (hsame.1 ▸ hb)
    · exact hx (hswap.1 ▸ hc)
  · have hcollision := hsidon (show x ∈ insert x A by simp)
        (show x ∈ insert x A by simp)
        (show b ∈ insert x A by simp [hb])
        (show c ∈ insert x A by simp [hc]) hmidpoint
    rcases hcollision with hsame | hswap
    · exact hx (hsame.1 ▸ hb)
    · exact hx (hswap.1 ▸ hc)

def pairSums (A : List ℕ) : List ℕ :=
  A.flatMap fun a => (A.filter fun b => a ≤ b).map fun b => a + b

def isSidonB (A : List ℕ) : Bool :=
  decide (pairSums A).Nodup

def maximalSidonInB (n : ℕ) (A : List ℕ) : Bool :=
  isSidonB A &&
    A.all (fun x => 1 ≤ x && x ≤ n) &&
    (List.range n).all
      (fun y => let x := y + 1; A.contains x || !(isSidonB (x :: A)))

def witness43 : List ℕ := [1, 2, 4, 13, 32, 37]

/-- A six-element inclusion-maximal Sidon subset of `[1, 43]`. -/
theorem witness43_is_maximal : maximalSidonInB 43 witness43 = true := by
  native_decide

theorem witness43_card : witness43.length = 6 := by
  native_decide

def witness61 : List ℕ := [22, 30, 31, 33, 43, 58]

/-- Evolutionary search certificate: six marks already saturate `[1, 61]`. -/
theorem witness61_is_maximal : maximalSidonInB 61 witness61 = true := by
  native_decide

theorem witness61_card : witness61.length = 6 := by
  native_decide

def witness63 : List ℕ := [7, 23, 24, 30, 38, 43]

/-- A later evolutionary run improves the certified lower bound to `M(6) ≥ 63`. -/
theorem witness63_is_maximal : maximalSidonInB 63 witness63 = true := by
  native_decide

theorem witness63_card : witness63.length = 6 := by
  native_decide

end EvoLeanLab.SidonSaturation
