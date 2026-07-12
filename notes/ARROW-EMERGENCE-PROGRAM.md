# Program: igniting a flow for the emergence of the arrow of time

**Opened 2026-07-12 (Jon-directed).** "Build to the point where we can simulate
/ ignite a flow for the emergence of the arrow of time. All the papers are out
there; the missing piece is something you formulate as a team with Tobin, with
extended thinking on both sides." Do tracks (a)/(b)/(c) to completion + the
synthesis capstone, hand-in-hand with codex-science (Tobin), fully documented.

This is the plan + quant-phy's opening formulation of the missing piece. Tobin
posts an independent formulation; we converge here. Two-agent model as with
`corpus/FRONTIER-2026.md` and the S4 sign-off.

---

## 0. Where we are (the honest baseline)

Every arrow this project has produced is the **coarse-graining arrow**: it
appears when an inside observer throws away information — trace out records
(P-B, measured on hardware), condition a Markov chain (S3), or restrict a von
Neumann algebra (S4's arrow half = GSL monotonicity). Tobin and I converged
(commit 27e3214) that these are **one species**: monotonicity of entropy /
relative entropy under restriction. It is real, but it is an *observer's*
arrow — any ignorance manufactures it. It does not explain a **directed
microscopic time**.

`modular_flow.py` made the split exact: from one cyclic-separating state you get
a reversible **clock** (modular flow Δ^{it}), an **arrow** only under
restriction, and an antiunitary **reflection** (J). The clock has no preferred
direction; the arrow is put in by the inside view. **Nothing yet gives a flow
whose direction is intrinsic.**

## 1. The missing piece — quant-phy's formulation (for Tobin to contest)

**Claim.** The intrinsic, non-observer arrow is the **positive generator of a
half-sided modular inclusion (HSMI)**. Its direction is the spectrum condition
P ≥ 0. This is the flow that "ignites," and it is *not* the coarse-graining
arrow — it comes from the algebra's own modular structure, not from tracing out.

**The machinery (all theorems, all in the literature — Jon's intuition is right):**

- **Borchers (1992).** Let U(a) = e^{iPa} be a one-parameter group with
  **P ≥ 0** (positive energy), U(a)Ω = Ω, and half-sided covariance
  U(a) M U(−a) ⊆ M for a ≥ 0. Then the modular data of (M, Ω) is *forced* to
  satisfy
  > Δ^{it} U(a) Δ^{−it} = U(e^{−2πt} a),  J U(a) J = U(−a).
  Positive energy + a half-sided translation rigidly determines the interplay
  with the modular clock.
- **Wiesbrock (1993), converse.** A **half-sided modular inclusion** N ⊂ M
  (Δ_M^{it} N Δ_M^{−it} ⊆ N for t ≤ 0) *generates* exactly such a U(a) with
  P ≥ 0 and N = U(1) M U(−1). **The inclusion IS the flow**, and positivity of
  the generator falls out of it.
- **Ceyhan–Faulkner (`1812.04683`).** Realize the HSMI by null cuts of a QFT
  region; the positive generator P is the **null translation / averaged null
  energy**. QNEC/ANEC positivity *is* P ≥ 0 — a **proven theorem** in
  interacting QFT. So "energy is bounded below" and "time has a direction" are
  the same statement, and it is proven, not assumed.

**Why this is the clean upgrade (Track b) AND the ignition (synthesis).** The
translation semigroup U(a), a ≥ 0, monotonically nests the algebras
N_a = U(a) M U(−a) ⊂ M — a directed flow whose arrow is P ≥ 0, built into the
inclusion. It reduces to none of S1–S4:
- not S3/GSL (no observer, no coarse-graining — the direction is a spectrum
  condition, not a monotone entropy);
- not P-A (Δ^{it} is the *clock*; U(a) is a *different* generator — the
  dilation-translation pair, the ax+b group);
- it is the first candidate for an arrow **from the flow itself**.

**The split, unified:** Δ^{it} = the reversible clock (dilations, P-A);
U(a), P ≥ 0 = the directed arrow (translations, NEW); their commutator
Δ^{it}U(a)Δ^{−it} = U(e^{−2πt}a) is the ax+b algebra [D, P] = iP (modular
normalization 2π). One two-generator structure holds clock and arrow together;
the arrow's direction is the sign of P.

## 2. The formulation questions for Tobin (extended thinking, both sides)

1. **Independence.** Is the P ≥ 0 (HSMI) arrow *genuinely* independent of the
   S3/GSL coarse-graining arrow, or is there a hidden reduction (e.g. via the
   Connes cocycle / relative entropy) that collapses them? My claim is
   independent; find the strongest argument that it is NOT.
2. **Ignition in finite dimensions.** The exact ax+b representation with P ≥ 0
   is infinite-dimensional (tr[D,P] = 0 forbids a strictly positive P with
   exact [D,P] = iP in finite dim — the Type III fingerprint). So "igniting the
   flow" in a simulation means a **regularized/limit** construction. Candidate
   routes — which is most buildable?
   (a) Truncated ax+b: finite matrices with approximate covariance; watch the
       generator's spectrum become positive as the cutoff lifts (the arrow
       "ignites" in the continuum limit).
   (b) Chiral free fermion / light-ray algebra on a lattice: exact HSMI in the
       continuum, approximate on the lattice; measure the emergent P.
   (c) DSSYK Type II₁ chord algebra (`2403.09021`, already filed): does it carry
       a positive-generator translation? A genuinely different, computable arena.
3. **The observable of "ignition."** What number do we plot to *show* an arrow
   emerged? Proposal: the spectrum of the regularized generator crossing into
   P ≥ 0, and/or the monotone nesting N_a ⊂ M measured by a relative-entropy
   that is directional because of P ≥ 0 (not because of coarse-graining).
4. **Falsifier.** State, before building, what result would REFUTE "the arrow
   ignites": e.g. the regularized generator keeps a symmetric spectrum in the
   limit (no positivity emerges), or the directional structure turns out to be
   exactly the S3 monotone after all.

## 3. Tobin independent pass (codex-science) - 2026-07-12

**Precise restatement.** I accept the HSMI target, but with one important
correction: **P >= 0 alone is not the arrow.** An ordinary positive Hamiltonian
also has spectrum bounded below, yet `e^{-iHt}` is still a reversible group.
The arrow is the **one-sided algebraic action** tied to the positive generator:
for `a >= 0`, the translated algebra nests forward,
`N_a = U(a) M U(-a) subset M`, while the reverse translation is not an
inclusion of the same net. The Hilbert-space unitary remains invertible; the
irreversibility is in the ordered family of algebras. That is the right object
to "ignite."

**Independence verdict.** Abstractly, the HSMI theorem is independent of the
S3/GSL entropy species: it is a representation-theoretic statement about a
standard inclusion producing the `ax+b` relation and a positive translation
generator. Operationally, the strongest collapse argument is real: in QFT the
same null-generator positivity is read through ANEC/QNEC, and the known QNEC
route is entangled with relative entropy, strong superadditivity, and modular
Hamiltonian shape derivatives. So the honest status is:

- **formal independence:** yes, as an operator-algebra theorem;
- **physics independence:** qualified, because the cleanest QFT observables
  currently pass through relative-entropy monotonicity;
- **upgrade rule:** count this as a new candidate arrow only if the capstone
  displays the positive semigroup/covariance/nesting witness directly, with
  entropy monotonicity demoted to a check rather than used as the definition.

**Finite-dimensional ignition route.** Exact finite-dimensional HSMI is
forbidden, not just inconvenient: `tr([D,P]) = 0` is incompatible with an exact
nonzero `[D,P] = iP` in finite dimension, and exact Type-III modular structure
has no finite matrix model. The build should therefore be a regulator limit.

Recommended two-stage build:

1. **Stage 1, fastest falsifiable toy:** truncate the positive-energy
   standard-pair / `ax+b` representation on `L^2(R_+)`. Use a cutoff `N`, form
   compressed `D_N`, `P_N`, and `U_N(a)`, then measure convergence of the
   covariance relation and one-sided nesting. This is the fastest way to make
   the obstruction and the continuum limit visible, but it must not pretend
   that finite matrices are the theorem.
2. **Stage 2, physically cleaner lab:** free chiral fermion / null-line
   lattice via correlation-matrix modular Hamiltonians. Extract
   `P_N ~ (K_M - K_N)/(2*pi)` for nested light-ray intervals and test whether
   the positive generator and the forward inclusion emerge under continuum
   extrapolation. This is the best route to an "ignition" claim because the
   generator is inferred from modular data instead of simply chosen positive.
3. **DSSYK status:** keep as watchlist, not first capstone. Xu `2403.09021`
   proves a Type II_1 chord algebra with tracial/cyclic-separating structure
   and a finite maximum entropy, which is excellent for the de Sitter/observer
   front. I do **not** see, in that result, an HSMI or a positive translation
   generator playing the Borchers-Wiesbrock role. A tracial Type II_1 state can
   even make the modular flow trivial, so DSSYK is a poor first place to prove
   a directed modular arrow unless someone identifies the relevant inclusion.

**Observable to plot.** Do not plot "positivity" only after manually projecting
onto a positive cone. The capstone needs regulator-stable numbers:

- `neg_mass(P_N) = sum(max(0, -lambda_i(P_N)))`, or `min eig(P_N)`, tending to
  zero from an unconstrained extraction;
- `cov_defect_N(t,a) =
  ||Delta_N^{it} U_N(a) Delta_N^{-it} - U_N(e^{-2*pi*t}a)|| / ||U_N(a)||`,
  tending to zero;
- `nesting_asymmetry_N(a) = backward_violation_N(a) - forward_violation_N(a)`,
  staying positive while `forward_violation_N(a) -> 0`;
- optional entropy/relative-entropy monotonicity as a downstream sanity check,
  not the defining observable.

**Falsifier.** "The arrow ignites" is refuted if, under increasing cutoff, any
of the following holds: the extracted generator keeps regulator-stable negative
spectral weight; the `ax+b` covariance defect does not improve; forward and
backward nesting become symmetric; the only monotone plot is relative entropy
with no independent semigroup witness; or DSSYK gives only the tracial Type
II_1 entropy story with no HSMI-positive-generator structure.

### Literature check

- **Borchers.** The standard-pair commutation relation used here is the
  Borchers theorem cited in the HSMI literature as Borchers `1992`, with the
  Poincare/HSMI construction sharpened in Borchers, *Half-sided modular
  inclusion and the construction of the Poincare group*, CMP 179 (1996).
  This supports the `Delta^{it} U(a) Delta^{-it} = U(e^{-2*pi*t}a)` backbone,
  but it is not by itself an entropy-arrow theorem.
- **Wiesbrock.** Wiesbrock's 1993 CMP/LMP papers are the converse anchor:
  half-sided modular inclusions generate positive-energy representations.
  Araki-Zsido `math/0412061` is important because it extends the structure
  theorem and explicitly fills a gap in Wiesbrock's proof.
- **QFT null-energy bridge.** Ceyhan-Faulkner `1812.04683` formulates Wall's
  conjecture as a theorem for operator algebras satisfying HSMI properties and
  derives strong superadditivity of relative entropy in the same setting.
  Casini-Teste-Torroba `1703.10656` gives explicit null-plane modular
  Hamiltonians and the Markov/SSA structure. Balakrishnan-Faulkner-Khandker-
  Wang `1706.09432` remains the interacting-QFT QNEC proof. Together these
  are exactly why the independence verdict must stay qualified.
- **Chiral/HSMI construction literature.** Standard HSMIs correspond to
  strongly additive Mobius-covariant nets on `S^1`; this is the structural
  reason the chiral light-ray route is natural. Lechner-Scotford `2111.03172`
  gives explicit deformations of HSMIs and relates them to non-local chiral
  field theories. This is useful as a source of exact continuum examples, not
  a finite-lattice construction.
- **Finite/lattice modular Hamiltonian route.** Eisler-Peschel `1902.04474`
  shows how a free-fermion chain entanglement Hamiltonian approaches the
  conformal one in the continuum limit when longer-range hoppings are retained.
  Chiral-fermion modular Hamiltonian work such as Blanco-Perez-Nadal
  `1905.05210` / Blanco-Garbarz-Perez-Nadal `1906.07057` gives computable
  continuum targets. I found no exact finite-dimensional HSMI result; the
  correct statement is "regularized approximation to a Type-III/null-line
  structure."
- **DSSYK.** Xu `2403.09021` proves the Type II_1 chord algebra and modular
  structure of DSSYK; `2404.02449` studies entropy in that Type II_1 setting.
  Neither source, as checked here, supplies the HSMI positive translation
  generator required for Track (b).

## 4. Formulation lock (joint target after Tobin pass)

**Locked claim, qualified.** The new Track (b) object is not "entropy grows"
and not "modular flow is time." It is:

> A half-sided modular inclusion `(N subset M, Omega)` produces a positive
> translation generator `P >= 0` whose unitary group is reversible on Hilbert
> space but one-sided on the net of algebras. The arrow is the semigroup of
> inclusions, not the modular clock and not entropy monotonicity itself.

This preserves quant-phy's main insight while removing the overclaim
"positive energy = time direction." Positive energy becomes a direction only
when it is coupled to the half-sided inclusion order. The capstone succeeds if
the finite regulator exhibits the continuum emergence of:

1. positive generator with vanishing negative spectral leakage;
2. `ax+b` modular covariance;
3. forward algebra/subspace nesting without backward nesting symmetry.

The capstone fails if those three are absent or if the only arrow visible is
again an S3/GSL relative-entropy monotone.

## 5. The three tracks + the capstone

- **Track (a) — modular clock on hardware.** PREVIEW DONE:
  `labs/track-c-time/modular_arrow_predict.py` (exact three-line prediction:
  arrow rises, modular plateaus flat, control at floor). NEXT: full hardware
  lab, quota-gated, one free-tier window; document the three tomography lines
  as the device-ready S4 stationarity witness. Owner: quant-phy builds; Tobin
  cross-checks. **Needs Jon's explicit go before any QPU submission.**
- **Track (b) — the directed modular arrow.** = §1 refined by §3–§4.
  Buildable core: the finite/regularized ax+b construction with P ≥ 0 emerging
  as a one-sided inclusion witness, not as an entropy definition. This merges
  into the capstone. Owner: joint.
- **Track (c) — write S2 up.** Short original note: closed inside-operations /
  code-holonomy self-transport realize unitary frame rotations but not the
  antiunitary time-reversal twist. Cite the antecedents Tobin found
  (`1801.04364`, `2010.05734`, `2101.04962`); frame as original synthesis +
  hardware-backed finite-code witness (job d958plnu62ks7396rgmg). Owner:
  quant-phy drafts; Tobin reviews.
- **Capstone — ignite the flow.** A toy (`modular_ignition.py`, TBD) that
  exhibits the positive generator emerging from a half-sided modular inclusion —
  the arrow of time appearing from the flow structure, not from conditioning.
  Success = the §3 observable set plus the §4 locked criteria; falsifier = the
  §3 falsifier. Owner: joint, after quant-phy ACKs/extends the lock.

## 6. Collaboration protocol

1. quant-phy posts this formulation to Tobin on the bus with the four §2
   questions.
2. Tobin runs an independent extended-thinking formulation of the missing piece
   + a literature check (Borchers, Wiesbrock, and any finite/lattice HSMI or
   DSSYK-generator work) and posts back.
3. Converge §1–§3 here (the joint "formulation lock" block in §4), the way S4
   was signed off. Only then build the capstone toy.
4. Tracks (a) and (c) proceed in parallel and get checked off here as done.

## 7. Status board

- [x] Track (a) preview simulation — `modular_arrow_predict.py` (this commit)
- [ ] Track (a) hardware run — GATED on Jon's go + quota
- [x] Track (b) Tobin independent pass + formulation-lock target — this note
- [ ] Track (c) S2 note — draft pending
- [ ] Capstone `modular_ignition.py` — build after quant-phy ACKs/extends §4
- [ ] Everything documented + both agents signed off
