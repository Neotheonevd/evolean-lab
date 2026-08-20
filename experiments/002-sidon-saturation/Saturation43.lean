import Mathlib.Data.Finset.Basic

namespace EvoLeanLab.SidonSaturation

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

end EvoLeanLab.SidonSaturation
