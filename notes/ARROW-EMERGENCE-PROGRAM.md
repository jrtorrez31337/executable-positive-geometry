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

## 3. The three tracks + the capstone

- **Track (a) — modular clock on hardware.** PREVIEW DONE:
  `labs/track-c-time/modular_arrow_predict.py` (exact three-line prediction:
  arrow rises, modular plateaus flat, control at floor). NEXT: full hardware
  lab, quota-gated, one free-tier window; document the three tomography lines
  as the device-ready S4 stationarity witness. Owner: quant-phy builds; Tobin
  cross-checks. **Needs Jon's explicit go before any QPU submission.**
- **Track (b) — the directed modular arrow.** = §1 above. Buildable core: the
  finite/regularized ax+b construction with P ≥ 0 emerging (§2.2). This merges
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
  Success = §2.3 observable; falsifier = §2.4. Owner: joint, after (b)'s
  formulation converges.

## 4. Collaboration protocol

1. quant-phy posts this formulation to Tobin on the bus with the four §2
   questions.
2. Tobin runs an independent extended-thinking formulation of the missing piece
   + a literature check (Borchers, Wiesbrock, and any finite/lattice HSMI or
   DSSYK-generator work) and posts back.
3. Converge §1–§2 here (a joint "formulation lock" block), the way S4 was
   signed off. Only then build the capstone toy.
4. Tracks (a) and (c) proceed in parallel and get checked off here as done.

## 5. Status board

- [x] Track (a) preview simulation — `modular_arrow_predict.py` (this commit)
- [ ] Track (a) hardware run — GATED on Jon's go + quota
- [ ] Track (b) formulation lock — awaiting Tobin's independent pass
- [ ] Track (c) S2 note — draft pending
- [ ] Capstone `modular_ignition.py` — after (b) locks
- [ ] Everything documented + both agents signed off
