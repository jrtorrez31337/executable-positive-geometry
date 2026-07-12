# Program: igniting a flow for the emergence of the arrow of time

**Opened 2026-07-12 (Jon-directed).** "Build to the point where we can simulate
/ ignite a flow for the emergence of the arrow of time. All the papers are out
there; the missing piece is something you formulate as a team with Tobin, with
extended thinking on both sides." Do tracks (a)/(b)/(c) to completion + the
synthesis capstone, hand-in-hand with codex-science (Tobin), fully documented.

This is the plan + quant-phy's opening formulation of the missing piece. Tobin
posts an independent formulation; we converge here. Two-agent model as with
`corpus/FRONTIER-2026.md` and the S4 sign-off.

**Broadened 2026-07-12.** Jon clarified through quant-phy (#170) that the
half-sided-modular-inclusion bet is one candidate, not the answer. The program
now maps the full spectrum of arrow-start mechanisms, then asks whether the
dynamical-complexity and algebraic-positive-generator families are secretly one
mechanism.

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

## 0.5 Equal-rigor rubric (Jon-directed 2026-07-12): ALL FOUR families, same standard

Jon: "all four deserve equal rigor." No privileged family — the HSMI formulation
in §1 is the *algebraic-family candidate*, not the answer, and it faces the same
test as the rest. The uniform scorecard, one row per family:

| field | what to fill |
|---|---|
| strongest version | the best statement of the mechanism |
| strongest objection | the sharpest published/derivable attack |
| **smuggled direction** | *where does this theory covertly assume the arrow it claims to explain?* |
| tier | 🟢 theorem / 🟡 model-dependent / 🔴 speculative |
| ignition verdict | INHERITED / IGNITED / OBSERVER / ALGEBRAIC — does a flow genuinely START, or is a direction assumed? |

**The unifying test the rubric produces:** a family counts as genuine *ignition*
only if it survives *"where is the direction smuggled in?"*. First-pass answers
(to be pressure-tested, applied to our own bet too):
- INHERITED (Past Hypothesis / Weyl): the special low-entropy start itself.
- IGNITED (Janus / causal-set / complexity): is the Janus/min-complexity point a
  Past Hypothesis in disguise? is causet growth-order physical (Bell causality)?
- OBSERVER (records / GSL): presupposes a background arrow — records form toward
  the future; decoherence needs a low-entropy environment. (Our S3/S4-arrow.)
- ALGEBRAIC (modular / HSMI, §1): the chosen vacuum/KMS state — thermal time is
  state-dependent and P ≥ 0 is a QFT axiom (vacuum = ground state); the direction
  may enter via the state, not be derived. **Our own bet must clear this.**

Deliverable: `notes/ARROW-ORIGINS-SCORECARD.md` — the filled rubric, verified
literature per family (sweep in progress), both agents signed off. No family
gets weighted heavier; the synthesis follows the scorecard, not a prior.

## 1. The algebraic-family candidate — quant-phy's formulation (held to the rubric)

**Claim (algebraic family only — one of four, not the answer).** The intrinsic,
non-observer arrow is the **positive generator of a half-sided modular inclusion
(HSMI)**. Its direction is the spectrum condition P ≥ 0. Candidate for genuine
ignition — but it must clear the smuggled-direction test (does P ≥ 0 / the KMS
state assume the arrow?), exactly as the other three families must.

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

## 4. Algebraic candidate lock (HSMI, not the whole-program answer)

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

## 5. Full-spectrum map after Jon clarification (#170)

The organizing question is no longer "is HSMI the answer?" It is: **what kind
of mechanism can make a flow of time start?** I classify candidates by what is
doing the work.

### 5.1 Mechanism families

| Family | Examples / anchors | What starts the flow? | Verdict |
|---|---|---|---|
| **Inherited boundary** | Boltzmann Past Hypothesis; Penrose Weyl-curvature hypothesis; Carroll-Chen `hep-th/0410270` as a two-headed inflationary variant | A special low-entropy or low-Weyl boundary/neck is selected, then ordinary dynamics carries the arrow away from it | Explains alignment but does not ignite the arrow from the laws alone; the low-order condition is the input |
| **Observer / manufactured** | P-B record tracing; S3 conditioning; decoherence / Quantum Darwinism; S4-GSL entropy under algebra restriction | An inside description discards, conditions on, or restricts information | Real and experimentally accessible, but cheap: it manufactures an arrow from perspective/coarse-graining |
| **Dynamical ignition** | Barbour-Koslowski-Mercati `1310.5167`, `1409.0917`; shape complexity / Janus point | A time-symmetric closed gravitational system generically has a minimum-complexity point; records and complexity grow toward both branches | Best genuine-ignition candidate: the arrow is a branch property of the solution, not an imposed initial macrostate |
| **Sequential growth / causal set** | Rideout-Sorkin `gr-qc/9904062` classical sequential growth | New causal-set elements are born by a stochastic growth law satisfying discrete general covariance and Bell causality | Candidate ignition if birth is physical; if label order is gauge, the physical remnant is causal order, not external becoming |
| **Complexity second law** | Brown-Susskind `1701.01107`; black-hole/interior complexity growth | Less-than-maximal complexity is a resource that overwhelmingly evolves toward higher complexity | Dynamical after uncomplexity exists; not a complete start mechanism unless low initial complexity is typical or derived |
| **Algebraic positive generator** | Connes-Rovelli thermal time; Borchers-Wiesbrock HSMI; Ceyhan-Faulkner `1812.04683` | A standard algebraic inclusion produces a positive generator and one-sided semigroup of algebra inclusions | Rigorous candidate, but conditional: the inclusion/spectrum condition must be derived or tied to a dynamical start |
| **Explicit law-level arrow** | Objective-collapse models; fundamental T/CP-violating dynamics if promoted to macroscopic arrow | The law is time-asymmetric | Not emergence; useful as a control class because it hard-codes what we are trying to explain |
| **Two-boundary / postselected arrows** | Gold-style final conditions; ABL/two-state-vector/postselection families; time-symmetric cosmologies with a special middle or endpoints | Both ends, or a middle neck, constrain admissible histories | Usually inherited rather than ignited; can mimic two-headed arrows and must be kept separate from Janus-style typicality |

### 5.2 Which families genuinely ignite?

**Strongest ignition candidates.**

1. **Janus / shape-complexity gravity** ignites most cleanly at the global
   solution level: a minimum-complexity Janus point is not chosen as a
   low-entropy macrostate but appears generically in the closed unconfined
   model. The caveats are model-dependence, typicality measure, and extension
   from Newtonian shape dynamics to GR/QFT.
2. **Algebraic HSMI** ignites most cleanly at the local/operator level: a
   standard half-sided inclusion gives a positive generator and a forward
   inclusion semigroup. The caveat is that the inclusion/spectrum condition is
   an input unless a dynamics produces it.
3. **Causal-set sequential growth** is genuine if "birth" is ontic. Under
   discrete general covariance, however, label-time is gauge; then it gives a
   causal order, not necessarily a felt flow.

**Borderline.** Complexity second law is powerful once the system has
uncomplexity. It becomes ignition only if the low-complexity resource is
itself derived from typicality, a Janus point, or an algebraic constraint.

**Not ignition.** Past Hypothesis, Weyl-curvature boundary conditions,
ordinary inflationary arrows, observer coarse-graining, GSL-as-entropy
monotonicity, and explicit time-asymmetric laws all either assume the arrow,
manufacture it perspectivally, or write it into the law.

## 6. Stress test: Janus complexity vs algebraic positive generator

**Candidate unification.** The two serious mechanisms may be the same pattern
in different languages:

> A flow starts when a self-contained system has (i) a distinguished
> low-complexity/standard point, (ii) an order on accessible substructures, and
> (iii) a positive generator whose forward semigroup refines that order.

In Janus language, the distinguished point is the minimum of shape complexity;
the order is record formation along a branch; the monotone is complexity. In
HSMI language, the distinguished point is the standard cyclic-separating pair;
the order is algebra inclusion; the monotone generator is `P >= 0`. A real
synthesis would show that branch-wise record growth can be represented as a
net of nested algebras with a positive modular translation, or conversely that
the HSMI semigroup carries a natural complexity that grows along `a >= 0`.

**Strongest case against unification.**

- Janus is global and two-headed; HSMI is local and one-sided. They only match
  if a Janus solution yields two oppositely oriented HSMI branches, related by
  the modular reflection `J`.
- Shape complexity is nonlinear, classical, and coarse; `P` is a linear
  self-adjoint generator in an operator algebra. No theorem currently maps
  `dC/da >= 0` to `P >= 0`.
- Janus produces records dynamically; HSMI assumes a standard inclusion. If
  the inclusion is not generated by the same dynamics that creates records,
  HSMI is a kinematic arrow, not the start of the flow.
- Complexity growth can occur without an algebraic half-sided inclusion, and
  an HSMI can exist without an obvious complexity-growth interpretation. Either
  result would split the mechanisms.

**Bridge conjecture to test.** On each Janus branch, construct a record algebra
`M_a` generated by degrees of freedom accessible up to branch parameter `a`.
If `M_{a+da} subset M_a` or the reverse orientation forms a half-sided modular
net with generator `P_branch >= 0`, then Janus/dynamical ignition and HSMI
positive-generator ignition are the same mechanism at different scales. If no
standard inclusion can be extracted, the two mechanisms stay distinct.

**Observable for the synthesis.**

- Janus side: shape complexity `C(a)` and record count/mutual information grow
  away from the Janus point on both branches.
- Algebra side: `neg_mass(P_N) -> 0`, `cov_defect_N -> 0`, and one-sided
  nesting asymmetry persists.
- Unification side: the same branch parameter orders both `C(a)` and the
  algebra net, with `sign(dC/da)` matching the sign choice of `P_branch`.

**Falsifier for "one mechanism."** The unification fails if Janus branches have
robust complexity/record growth but no extractable positive-inclusion
semigroup, or if the HSMI regulator succeeds while carrying no branch
complexity/record monotone. In that case the program should keep two arrows:
global dynamical ignition and local algebraic orientation.

## 7. Revised program lock

Do **not** lock HSMI as the answer. Lock the search space:

1. **Algebraic deep-dive:** keep §3–§4 as the HSMI candidate and build
   `modular_ignition.py` only as an algebraic-positive-generator capstone.
2. **Dynamical deep-dive:** add a Janus/shape-complexity toy or analysis note
   that makes the two-headed complexity arrow explicit and records its
   falsifiers.
3. **Synthesis test:** only claim "we found how the flow starts" if a common
   positive-order structure links the Janus/complexity branch and the HSMI
   semigroup. Otherwise report two non-equivalent ignition mechanisms.
4. **Controls:** inherited-boundary, observer-manufactured, law-level, and
   two-boundary mechanisms stay in the table as controls, not as the primary
   explanation.

## 8. The three tracks + capstones

- **Track (a) — modular clock on hardware.** PREVIEW DONE:
  `labs/track-c-time/modular_arrow_predict.py` (exact three-line prediction:
  arrow rises, modular plateaus flat, control at floor). NEXT: full hardware
  lab, quota-gated, one free-tier window; document the three tomography lines
  as the device-ready S4 stationarity witness. Owner: quant-phy builds; Tobin
  cross-checks. **Needs Jon's explicit go before any QPU submission.**
- **Track (b) — the directed modular arrow.** = §1 refined by §3–§4.
  Buildable core: the finite/regularized ax+b construction with P ≥ 0 emerging
  as a one-sided inclusion witness, not as an entropy definition. **Post-#172
  correction:** exact finite HSMI is a no-go; finite ax+b is an
  obstruction/regulator exhibit only. The buildable ignition capstone pivots to
  DSSYK/Krylov spectral complexity as the Project-2 arena for testing whether
  dynamical complexity growth and the algebraic positive-generator arrow are
  one mechanism. Owner: joint.
- **Track (c) — write S2 up.** Short original note: closed inside-operations /
  code-holonomy self-transport realize unitary frame rotations but not the
  antiunitary time-reversal twist. Cite the antecedents Tobin found
  (`1801.04364`, `2010.05734`, `2101.04962`); frame as original synthesis +
  hardware-backed finite-code witness (job d958plnu62ks7396rgmg). Owner:
  quant-phy drafts; Tobin reviews.
- **Capstone — ignite the flow.** Pivot from a finite ax+b/HSMI toy to a
  DSSYK/Krylov spectral-complexity lab. The finite ax+b construction may remain
  as a no-go/regulator exhibit, but the honest buildable signal is complexity
  growth/saturation in the DSSYK/de Sitter arena, tested as a bridge to the
  large-N/type-III HSMI story. Success = a common positive-order structure
  linking spectral/Krylov complexity to the algebraic orientation; falsifier =
  complexity growth with no extractable algebraic positive-order structure.
  Owner: joint. **Status 2026-07-12:** quant-phy built
  `labs/track-c-time/krylov_ignition.py`; Tobin added
  `labs/track-c-time/krylov_capstone_crosscheck.py`. Joint verdict: at finite
  N, sustained `K_late` is the honest ignition signature, not the failed
  linear-`b_n` slope. The `b_n` plateau is spectral-scale evidence tied to
  bandwidth/RMT behavior, but it is not an arrow by itself. KMS detailed
  balance is the inherited thermal/modular contrast because it appears in both
  SYK4 and SYK2.
- **Synthesis capstone — compare dynamical and algebraic ignition.** A
  Janus/shape-complexity toy or analysis note should plot branch complexity and
  record formation, then ask whether the same branch parameter can order a
  nested algebra net. Success = common positive-order structure; falsifier =
  §6. Owner: joint, after the algebraic and dynamical deep-dives exist.

## 9. Collaboration protocol

1. quant-phy posts this formulation to Tobin on the bus with the four §2
   questions.
2. Tobin runs an independent extended-thinking formulation of the missing piece
   + a literature check (Borchers, Wiesbrock, and any finite/lattice HSMI or
   DSSYK-generator work) and posts back.
3. Converge §1–§7 here (algebraic lock + full-spectrum map), the way S4 was
   signed off. Only then build capstone toys.
4. Tracks (a) and (c) proceed in parallel and get checked off here as done.
5. Jon clarification #170 broadens the scope: HSMI remains a candidate, while
   Janus/complexity and causal-set/complexity-law families stay live until the
   synthesis test is resolved.

## 10. Status board

- [x] Track (a) preview simulation — `modular_arrow_predict.py` (this commit)
- [ ] Track (a) hardware run — GATED on Jon's go + quota
- [x] Track (b) algebraic candidate pass + HSMI lock target — §3–§4
- [x] Broad-spectrum mechanism map from Jon clarification #170 — §5–§7
- [x] Equal-rigor origins scorecard — `notes/ARROW-ORIGINS-SCORECARD.md`
  (codex-science signed; quant-phy sign-off pending)
- [x] Post-#172 reconciliation — finite-HSMI no-go confirmed; DSSYK/Krylov
  pivot accepted as the buildable bridge test
- [ ] Track (c) S2 note — draft pending
- [x] DSSYK/Krylov ignition capstone — `krylov_ignition.py` +
  `krylov_capstone_crosscheck.py`; finite-N verdict: `K_late` ignites only for
  chaotic SYK4, while KMS detailed balance is inherited and model-generic
- [ ] Dynamical/Janus comparison capstone — pending joint scope
- [ ] Everything documented + both agents signed off
