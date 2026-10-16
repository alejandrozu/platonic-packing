import PackingCertificates.CubeFast

/-!
# Certified cached coordinate-axis supports

The cache contains exact rational bounds, independently checked against the
actual source-bound cube support formula once per piece and coordinate. An
axis tag in a pair certificate is trusted only after its complete normal is
checked to equal the indicated signed coordinate axis. All other directions
use the general exact support checker. No coordinates or angles are rounded.
-/

namespace PackingCertificates.AxisFast

open PackingCertificates.Rational
open PackingCertificates.Catalogue
open scoped BigOperators

abbrev SignedAxis := Fin 3 × Bool

def axis (k : Fin 3) : QPoint 3 := fun a => if a = k then 1 else 0

def signedAxis (a : SignedAxis) : QPoint 3 := if a.2 then -axis a.1 else axis a.1

structure Cache (n : ℕ) where
  lower : Fin n → QPoint 3
  upper : Fin n → QPoint 3

abbrev Directions (n : ℕ) := Fin n → Fin n → Option SignedAxis

def cachedUpper {n : ℕ} (c : Cache n) (i : Fin n) (a : SignedAxis) : ℚ :=
  if a.2 then -c.lower i a.1 else c.upper i a.1

def cachedLower {n : ℕ} (c : Cache n) (i : Fin n) (a : SignedAxis) : ℚ :=
  if a.2 then -c.upper i a.1 else c.lower i a.1

def cacheRowCheck {n : ℕ} (r : CubeRecord n) (c : Cache n) (i : Fin n) : Bool :=
  allFin 3 (fun k =>
    decide (c.lower i k = CubeFast.lowerSupport (axis k) (r.rotation i) (r.center i)) &&
    decide (c.upper i k = CubeFast.upperSupport (axis k) (r.rotation i) (r.center i)))

theorem qdot_neg_left {d : ℕ} (u v : QPoint d) : qdot (-u) v = -qdot u v := by
  simp [qdot, neg_mul, Finset.sum_neg_distrib]

theorem projection_neg {d : ℕ} (u : QPoint d) (r : Fin d → QPoint d) (b : Fin d) :
    CubeFast.projection (-u) r b = -CubeFast.projection u r b := by
  simp [CubeFast.projection, neg_mul, Finset.sum_neg_distrib]

theorem radius_neg {d : ℕ} (u : QPoint d) (r : Fin d → QPoint d) :
    CubeFast.radius (-u) r = CubeFast.radius u r := by
  simp [CubeFast.radius, projection_neg]

theorem upperSupport_neg {d : ℕ} (u : QPoint d) (r : Fin d → QPoint d) (c : QPoint d) :
    CubeFast.upperSupport (-u) r c = -CubeFast.lowerSupport u r c := by
  simp only [CubeFast.upperSupport, CubeFast.lowerSupport, qdot_neg_left, radius_neg]
  ring

theorem lowerSupport_neg {d : ℕ} (u : QPoint d) (r : Fin d → QPoint d) (c : QPoint d) :
    CubeFast.lowerSupport (-u) r c = -CubeFast.upperSupport u r c := by
  simp only [CubeFast.upperSupport, CubeFast.lowerSupport, qdot_neg_left, radius_neg]
  ring

theorem cachedUpper_eq {n : ℕ} (r : CubeRecord n) (c : Cache n) (i : Fin n)
    (a : SignedAxis) (h : cacheRowCheck r c i = true) :
    cachedUpper c i a = CubeFast.upperSupport (signedAxis a) (r.rotation i) (r.center i) := by
  simp only [cacheRowCheck, allFin_eq_true, Bool.and_eq_true, decide_eq_true_eq] at h
  rcases a with ⟨k, neg⟩
  cases neg <;> simp [cachedUpper, signedAxis, upperSupport_neg, (h k).1, (h k).2]

theorem cachedLower_eq {n : ℕ} (r : CubeRecord n) (c : Cache n) (i : Fin n)
    (a : SignedAxis) (h : cacheRowCheck r c i = true) :
    cachedLower c i a = CubeFast.lowerSupport (signedAxis a) (r.rotation i) (r.center i) := by
  simp only [cacheRowCheck, allFin_eq_true, Bool.and_eq_true, decide_eq_true_eq] at h
  rcases a with ⟨k, neg⟩
  cases neg <;> simp [cachedLower, signedAxis, lowerSupport_neg, (h k).1, (h k).2]

def planeCheck {n : ℕ} (r : CubeRecord n) (c : Cache n) (directions : Directions n)
    (i j : Fin n) : Bool :=
  match directions i j with
  | none => CubeFast.fastPlaneCheck r i j
  | some a =>
      let p := r.separation i j
      decide (p.normal = signedAxis a) && decide (p.lower < p.upper) &&
        decide (cachedUpper c i a ≤ p.lower) && decide (p.upper ≤ cachedLower c j a)

def pairRowCheck {n : ℕ} (r : CubeRecord n) (c : Cache n) (directions : Directions n)
    (i : Fin n) : Bool :=
  allFin n (fun j => if i < j then planeCheck r c directions i j else true)

theorem planeCheck_implies_fastPlaneCheck {n : ℕ} (r : CubeRecord n) (c : Cache n)
    (directions : Directions n) (i j : Fin n)
    (hi : cacheRowCheck r c i = true) (hj : cacheRowCheck r c j = true)
    (h : planeCheck r c directions i j = true) : CubeFast.fastPlaneCheck r i j = true := by
  cases hd : directions i j with
  | none => simpa only [planeCheck, hd] using h
  | some a =>
    have hp : (r.separation i j).normal = signedAxis a ∧
        (r.separation i j).lower < (r.separation i j).upper ∧
        cachedUpper c i a ≤ (r.separation i j).lower ∧
        (r.separation i j).upper ≤ cachedLower c j a := by
      simpa only [planeCheck, hd, Bool.and_eq_true, decide_eq_true_eq, and_assoc] using h
    have hu : CubeFast.upperSupport (r.separation i j).normal (r.rotation i) (r.center i) =
        cachedUpper c i a := by
      rw [hp.1]
      exact (cachedUpper_eq r c i a hi).symm
    have hl : CubeFast.lowerSupport (r.separation i j).normal (r.rotation j) (r.center j) =
        cachedLower c j a := by
      rw [hp.1]
      exact (cachedLower_eq r c j a hj).symm
    simp only [CubeFast.fastPlaneCheck, Bool.and_eq_true, decide_eq_true_eq, hu, hl]
    exact ⟨⟨hp.2.1, hp.2.2.1⟩, hp.2.2.2⟩

def check {n : ℕ} (r : CubeRecord n) (c : Cache n) (directions : Directions n) : Bool :=
  r.sourceCheck && orthogonalCheck r.toPlacement &&
    allFin n (fun i => cacheRowCheck r c i) &&
    allFin n (fun i => CubeFast.wallRowCheck r i) &&
    allFin n (fun i => pairRowCheck r c directions i)

/-- Assemble separately checked arithmetic fragments, with no monolithic
reevaluation of the source, matrix or pair computations. -/
theorem check_of_rows {n : ℕ} (r : CubeRecord n) (c : Cache n) (directions : Directions n)
    (hs : r.sourceCheck = true) (ho : orthogonalCheck r.toPlacement = true)
    (hc : ∀ i, cacheRowCheck r c i = true)
    (hw : ∀ i, CubeFast.wallRowCheck r i = true)
    (hp : ∀ i, pairRowCheck r c directions i = true) : check r c directions = true := by
  simp only [check, Bool.and_eq_true, allFin_eq_true]
  exact ⟨⟨⟨⟨hs, ho⟩, hc⟩, hw⟩, hp⟩

theorem check_implies_fastCheck {n : ℕ} (r : CubeRecord n) (c : Cache n)
    (directions : Directions n) (h : check r c directions = true) :
    CubeFast.fastCheck r = true := by
  simp only [check, Bool.and_eq_true, allFin_eq_true] at h
  apply CubeFast.fastCheck_of_rows r h.1.1.1.1 h.1.1.1.2 h.1.2
  intro i
  apply allFin_eq_true.mpr
  intro j
  by_cases hij : i < j
  · simp only [hij, if_true]
    apply planeCheck_implies_fastPlaneCheck r c directions i j (h.1.1.2 i) (h.1.1.2 j)
    have hp := allFin_eq_true.mp (h.2 i) j
    simpa only [hij, if_true] using hp
  · simp [hij]

theorem check_sound {n : ℕ} (r : CubeRecord n) (c : Cache n) (directions : Directions n)
    (h : check r c directions = true) : r.Valid :=
  CubeFast.fastCheck_sound r (check_implies_fastCheck r c directions h)

end PackingCertificates.AxisFast
