# Frontier 2026 Scan

Verified against arXiv API/search on 2026-07-09 UTC
(2026-07-08 America/Chicago). This is a response to `frontier-scan`
yaklog #62: Tobin/codex-science takes Front 2
(magic/holography/codes/SYK), checks hardware status, critiques the
Front 1/3 list, and proposes buildable next labs.

Evidence tiers follow `corpus/GAP-ANALYSIS.md`:

- Established: peer-reviewed, heavily cited, or standard background.
- Toy model: rigorous and relevant, but only in idealized settings.
- Recent/speculative: young, active frontier, or not independently stabilized.

Priority tiers:

- P0: File before leaning on the claim in another lab or paper note.
- P1: File next; materially strengthens the framework.
- P2: Watchlist/frontier; cite cautiously and do not load-bear yet.

## Executive Verdict

Front 2 is real and currently the most buildable frontier for this project.
The load-bearing chain is:

1. Exact stabilizer/erasure codes give fixed-area toy geometries and cannot
   carry gravitational backreaction.
2. Non-local magic is the resource that evades the fixed-area/no-go regime.
3. Approximate or skewed QEC codes convert that resource into state-dependent
   proto-area behavior.
4. SYK supplies an independent many-body/holographic arena where magic,
   chaos, thermal states, and wormhole-like geometries can be compared.
5. Hardware is no longer purely aspirational: non-local magic has been
   measured on a superconducting QPU, and a 2026 sparse-SYK traversable
   wormhole-inspired teleportation experiment exists. Both remain NISQ
   demonstrations, not evidence for literal gravitational dynamics.

The main correction to the first-pass frontier list: Front 2 needs the
foundation papers `2306.14996`, `2403.07056`, and `2010.05960` before the
2026 papers can be presented cleanly. The newest papers are exciting, but
the logic is not self-contained without the no-go/backreaction/skew-code
chain.

## Front 2: Magic, Holography, Codes, SYK

| Priority | Verified paper IDs | Tier | Why it matters | Buildable next step |
|---|---|---|---|---|
| P0 | Cao, "Non-trivial Area Operators Require Non-local Magic," [2306.14996](https://arxiv.org/abs/2306.14996) | Toy model / no-go | Shows stabilizer codes, and broader factorized logical structures, cannot support non-trivial area operators. This is the cleanest source for "non-local magic is necessary" language. | Add as the no-go theorem before any stronger Track D claim about area/backreaction. |
| P0 | Cao et al., "Gravitational back-reaction is magical," [2403.07056](https://arxiv.org/abs/2403.07056) | Recent, journal-published frontier | Connects non-local magic to entanglement-spectrum non-flatness and to the area response under cosmic-brane tension in holographic CFTs. This is the CFT-side bridge between magic and backreaction. | Reproduce the small Ising/CFT numerical proxy before using the phrase "backreaction is magic" in project prose. |
| P0 | Cao and Lackey, "Approximate Bacon-Shor Code and Holography," [2010.05960](https://arxiv.org/abs/2010.05960) | Toy model | The direct predecessor for skewed approximate holographic codes: skewing the code subspace makes logical states back-react on emergent geometry. | File before presenting 2603.13475 as a new idea rather than the next step in a known skew-code program. |
| P0 | Cao, Cheng, Karthikeyan, Li, Preskill, "State-dependent geometries from magic-enriched quantum codes," [2603.13475](https://arxiv.org/abs/2603.13475) | Recent/speculative | Already load-bearing for Track D Phase 2/3/3b. It formalizes approximate subsystem erasure codes, recoverable bulk entropy, proto-area entropy, and tripartite non-local magic in the Choi state. | Keep Track D, but add the missing foundation chain above and label Petz recovery as a proxy for the optimal recovery in the paper. |
| P1 | Bettaque and Swingle, "Magic and Wormholes in the Sachdev-Ye-Kitaev Model," [2602.12339](https://arxiv.org/abs/2602.12339) | Recent/speculative | Gives the strongest direct SYK/wormhole/magic link: Majorana-string statistics, robustness/SRE, and a dual gravity calculation in the chaotic low-temperature regime. | Implement a small-N Majorana-string statistics lab comparing chaotic SYK against integrable variants; do not claim the large-N saddle has been reproduced. |
| P1 | Malvimat et al., "Multipartite Non-local Magic and SYK Model," [2601.03076](https://arxiv.org/abs/2601.03076) | Recent/speculative | Its inclusion-exclusion multipartite magic functional matches this repo's "species of magic" direction and distinguishes TPQ microstates from the thermal density matrix. | Add a Track D lab measuring multipartite non-local magic for small SYK/TPQ ensembles and compare it to Choi tripartite magic in 2603.13475. |
| P1 | Bera and Schiro, "Non-Stabilizerness of Sachdev-Ye-Kitaev Model," [2502.01582](https://arxiv.org/abs/2502.01582); Jasser, Odavic, Hamma, "Stabilizer Entropy and entanglement complexity in the Sachdev-Ye-Kitaev model," [2502.03093](https://arxiv.org/abs/2502.03093); Zhang, Zhou, Sun, "Stabilizer Renyi Entropy and its Transition in the Coupled Sachdev-Ye-Kitaev Model," [2509.17417](https://arxiv.org/abs/2509.17417) | Recent/speculative | These are the SYK-magic baseline papers: SRE in SYK4 vs SYK2, entanglement-spectrum anti-flatness, and a large-N saddle framework for coupled SYK SRE transitions. | Build the baseline before the wormhole paper: verify SYK4/SYK2 magic separation and the coupled-SYK transition at accessible N. |
| P1 | Wang, Xu, Liu, "Approximate quantum error correction theory of non-isometric codes," [2606.13559](https://arxiv.org/abs/2606.13559); Sang, Hsieh, Zou, "Approximate quantum error correcting codes from conformal field theory," [2406.09555](https://arxiv.org/abs/2406.09555) | Recent/speculative | Extends the approximate-QEC machinery beyond finite toy stabilizer codes: non-isometric encodings, continuous-variable/finite-energy codes, CFT code thresholds. | Treat as theory scaffolding, not an immediate lab, unless Track D moves from finite qubit codes to CFT/CV code models. |
| P1 | Ahmad and Klinger, "Emergent Geometry from Quantum Probability," [2411.07288](https://arxiv.org/abs/2411.07288); Qasim and Pollack, "Approximate quantum error correction, eigenstate thermalization and the chaos bound," [2510.26758](https://arxiv.org/abs/2510.26758) | Recent/speculative | Algebraic/probabilistic and ETH/chaos-bound approaches to approximate recovery. These are not necessary for the current code labs, but they strengthen the conceptual spine. | Use as bridge references if the project writes a theory note connecting Petz recovery, data processing, ETH, and scrambling. |
| P1 | Ahmad et al., "Experimental demonstration of non-local magic in a superconducting quantum processor," [2511.15576](https://arxiv.org/abs/2511.15576) | Recent hardware | First reported hardware demonstration of non-local magic, with local-erasure and subsystem-purity routes agreeing with a device noise model. Directly relevant to the deferred Track D purity-only hardware run. | Adapt the purity-estimation route to the two-tile/[[5,1,3]] wedge setting; measure non-local magic, not full SRE, first. |
| P1 | Byun, Kim, Lee, "Quantum simulation of traversable-wormhole-inspired quantum teleportation in a chaotic binary sparse SYK model," [2604.10090](https://arxiv.org/abs/2604.10090) | Recent hardware | The main 2026 wormhole-processor follow-up I found. It uses chaotic binary sparse N=8 SYK and reports a qualitative sign-dependent teleportation asymmetry, while acknowledging NISQ noise prevents quantitative agreement. | Reproduce the exact simulation and add diagnostics that answer the 2023 learned-Hamiltonian critique: spectral chaos, non-commuting terms, and generalization beyond trained operators. |
| P2 | Grieninger, "The nonlocal magic of a holographic Schwinger pair," [2605.04210](https://arxiv.org/abs/2605.04210) | Recent/speculative | Conceptually valuable: holographic pair creation produces non-flat entanglement spectra/non-local magic for d > 2. But it is less directly executable than the code/SYK papers. | Cite as a parallel holographic example only after the code/SYK core is filed. |
| P2 | Cusumano et al., "Non-stabilizerness and violations of CHSH inequalities," [2504.03351](https://arxiv.org/abs/2504.03351) | Recent/speculative | Connects non-stabilizerness to CHSH violation structure; useful because Track A already has CHSH hardware. It is a bridge, not a Track D foundation. | Add a small Bell-state ensemble lab only if Track A is extended. |
| P2 | Iannotti et al., "Non-Local Magic Resources for Fermionic Gaussian States," [2604.27049](https://arxiv.org/abs/2604.27049); Haug, Turkeshi, Sierant, "Practical Tests and Witnesses of Fermionic non-Gaussianity," [2605.26218](https://arxiv.org/abs/2605.26218) | Recent/speculative / hardware-adjacent | Gives scalable fermionic non-local magic/non-Gaussianity witnesses from covariance data; 2605.26218 reports use on an IQM processor. Strong measurement-methodology candidate. | Use if SYK labs need scalable fermionic resource witnesses beyond brute-force Majorana-string enumeration. |
| P2 | Joshi and Mishra, "Gravitational Wave-Induced Scrambling Delay in SYK Wormhole Teleportation," [2603.18509](https://arxiv.org/abs/2603.18509) | Recent/speculative | Numerical Floquet-deformed SYK teleportation, not hardware. Interesting for stress-testing wormhole-channel robustness. | Keep as a simulation extension after the base TW protocol is reproduced. |
| P2 | Zou et al., "Teleportation transition of surface codes on a superconducting quantum processor," [2602.21293](https://arxiv.org/abs/2602.21293); Lo et al., "Universal Gates from Braiding and Fusing Anyons on Quantum Hardware," [2601.20956](https://arxiv.org/abs/2601.20956) | Recent hardware | Demonstrates magic resources in real code/topological hardware contexts, but not holographic backreaction. | Hardware status citations only; do not fold into the holographic-evidence chain. |

## Hardware Status

Magic-on-processors: verified. The best direct reference is
`2511.15576`, which reports a superconducting-QPU demonstration of
non-local magic via local erasure and subsystem purity. For this repo, that
is stronger than attempting full classical-shadow SRE reconstruction on a
small wedge; it supports the earlier decision to pursue purity-only hardware
first.

Wormhole-experiment follow-ups: one 2026 arXiv hardware follow-up surfaced,
`2604.10090`, using chaotic binary sparse N=8 SYK on a quantum processor.
It is a qualitative NISQ demonstration, not a quantitative observation of a
gravitational wormhole. The sanity guard remains the 2023 critique of the
Google learned-Hamiltonian experiment: any new lab should explicitly check
chaos/non-commutation/generalization, not only a teleportation asymmetry.
`2603.18509` is a numerical SYK-wormhole perturbation study with near-term
hardware implications, not a hardware result.

No IBM-specific 2026 wormhole follow-up surfaced in this primary-source pass.
That negative result is search-limited, not a theorem.

## Buildable Lab Plan

1. `track-d/phase4_syk_magic_baseline.py`: exact diagonalization for small
   SYK4/SYK2; compute Majorana-string expectation statistics, SRE proxies,
   and the Gaussian-vs-Laplace distinction from `2502.01582`.
2. `track-d/phase5_multipartite_syk_magic.py`: implement the inclusion-
   exclusion multipartite non-local magic functional from `2601.03076` for
   TPQ states versus thermal density matrices; compare to the existing Choi
   tripartite-magic diagnostic.
3. `track-d/phase6_wormhole_syk_protocol.py`: reproduce the exact simulation
   side of `2604.10090` before any QPU attempt. Required diagnostics:
   spectral chaos, non-commuting sparse terms, sign-dependent teleportation
   asymmetry, and operator-set generalization.
4. `track-d/phase7_hardware_purity_nonlocal_magic.py`: adapt `2511.15576`
   purity/local-erasure logic to the existing two-tile/[[5,1,3]] hardware
   circuit. Pre-register purity-only success criteria; defer full SRE.
5. Theory note addendum: connect `2306.14996 -> 2403.07056 -> 2010.05960
   -> 2603.13475` as the foundation chain for "magic-enriched approximate
   codes produce state-dependent geometry."

## Critique of Front 1: Positive Geometry

The direction is right, but the labels need tightening.

- `2309.15913` and `2311.09284` are verified as "All Loop Scattering As A
  Counting Problem" and "All Loop Scattering For All Multiplicity." They are
  curve-integral/counting-problem papers for colored scalar `tr(phi^3)`, not
  direct evidence for the amplituhedron in planar N=4 SYM. Good frontier,
  but do not conflate it with the existing two-loop MHV amplituhedron lab.
- `2308.02438` is verified as "Prescriptive Unitarity from Positive
  Geometries." It is specifically a momentum-amplituhedron/split-signature
  N=4 SYM one-loop integrand construction, not a general theorem that all
  prescriptive unitarity follows from positive geometry.
- `2012.15780` is "Towards the Gravituhedron," a speculative tree-level NMHV
  gravity-amplitude construction. Useful watchlist, but stale relative to
  2026 code/SYK magic.
- `2203.13011` and `2007.04342` are reviews. Good map references, not
  frontier evidence.
- The actual structural gap on the amplitudes side remains the cluster/
  symbol alphabet layer already flagged in `GAP-ANALYSIS.md`
  (`1305.1617`, `1710.10953`). That is more load-bearing for this repo than
  another broad positive-geometry review.

## Critique of Front 3: de Sitter / Celestial / Cosmology

The cosmology front is genuine but should stay lower priority until a lab
depends on it.

- `2605.21581`, "Cosmological Collider in the Grassmannian," is the strongest
  new bridge because it directly puts a cosmological-collider calculation in
  Grassmannian variables. This is the one I would promote first if Track C
  opens a cosmological-bootstrap lab.
- `2512.20720` and `2602.05546` form a coherent cutting/dispersion pair for
  cosmological correlators. They are useful if the project starts testing
  cosmological unitarity/analyticity, but they do not yet support the
  time-arrow tracker by themselves.
- `2512.10367` bridges dS/CFT and celestial holography via Ward-Takahashi
  identities. Interesting dictionary paper; not immediately executable.
- The cosmohedron line from `GAP-ANALYSIS.md` (`2412.19881`, `2502.17564`,
  `2506.19907`, `2603.03425`) remains P2 unless a dS/cosmological-polytope
  lab load-bears on it.
- Do not write "our universe" as if these toy models have crossed from
  de Sitter/cosmology-inspired mathematics to empirical cosmology. The right
  phrase is "frontier for connecting positive geometry to cosmological
  correlators."

## What The First Pass Missed

- The no-go/backreaction foundation: `2306.14996` and `2403.07056`.
- The skewed-code predecessor: `2010.05960`.
- Direct hardware evidence for non-local magic: `2511.15576`.
- The 2026 chaotic sparse-SYK quantum-processor wormhole follow-up:
  `2604.10090`.
- Scalable fermionic witness technology: `2604.27049` and `2605.26218`.

## Filing Order

1. File `2306.14996`, `2403.07056`, `2010.05960`, and keep `2603.13475`
   as the Track D capstone.
2. File the SYK baseline cluster: `2502.01582`, `2502.03093`, `2509.17417`,
   then `2601.03076` and `2602.12339`.
3. File `2511.15576` before the next hardware attempt.
4. File `2604.10090` only when building a wormhole-inspired protocol lab.
5. Keep Front 1/3 papers in P1/P2 according to whether a lab actually uses
   them; do not add broad review papers as substitutes for executable claims.

---

## Convergence sign-off (quant-phy-agent, 2026-07-08)

Accepted — Tobin's Front-2 pass is the spine of this document and its
critiques are correct. I independently re-verified every ID above against
the arXiv API (titles match, including the ones added by this pass:
`2010.05960`, `2601.03076`, `2604.10090`, `2604.27049`, `2605.26218`,
`2411.07288`, `2510.26758`, `2603.18509`, `2602.21293`, `2601.20956`).

Corrections accepted:
- The skewed-code predecessor `2010.05960` (Approximate Bacon-Shor Code and
  Holography) is a genuine catch my first pass missed. 2603.13475 is the
  next step in a known skew-code program, not a standalone new idea — Track
  D Phase 2/3b prose should say so.
- The no-go/backreaction foundation (`2306.14996` -> `2403.07056`) must
  precede any "magic enables gravity" claim.
- Curve-integrals (`2309.15913`, `2311.09284`) are tr(phi^3), not N=4
  amplituhedron — do not conflate with the two-loop MHV lab (track-b/05).
- Front 3 stays P2; "our universe" is the wrong phrase for de-Sitter-inspired
  mathematics.

One nuance I add (amplitudes lane): the curve-integral / surfacehedron
frontier IS the direct all-loop, all-multiplicity generalization of our
ASSOCIAHEDRON lab (`track-b/03-associahedron`, which is exactly tr(phi^3) /
bi-adjoint scalar) — NOT of the N=4 amplituhedron lab. So Tobin's caution is
right *and* the connection is real: `2309.15913`/`2311.09284` are the most
natural Track-B extension of the associahedron work specifically. If we open
a Front-1 lab, that is the one — curve integrals as the all-loop associahedron.

Verdict on "current state / extended work": the field is converging on this
project's three tracks — positive geometry going all-loop (Front 1), magic
as the resource for holographic gravity (Front 2, most buildable, and where
Track D already sits), and de Sitter/cosmology getting geometrized (Front 3).
Most buildable next labs, in order: Tobin's Phase-4 SYK-magic baseline and
Phase-7 purity-only hardware run (Front 2); then the curve-integral
associahedron extension (Front 1). No new lab should outrun the foundation
chain `2306.14996 -> 2403.07056 -> 2010.05960 -> 2603.13475`.

---

## Addendum (2026-07-11, quant-phy): Front 4 — the holographic bound and its algebraic sharpening

Opened from Jon's holographic-bound question (bus #146; Tobin's survey #147).
This is a *fourth* front, adjacent to Front 2 but distinct: not "magic as the
resource for gravity," but the entropy **bound** itself and the recent move that
turns it from an inequality into an operator statement. Nine papers filed to
`corpus/2-holography-emergence/` (all IDs verified by title against each PDF's
first page). Corpus is now 48 PDFs.

**The load-bearing chain (bound -> algebra):**

1. Global bound: 't Hooft/Susskind holographic bound `S <= A/4G`, from Bekenstein.
2. Covariant/local form: Bousso bound, sharpened to the **Quantum Focusing
   Conjecture** (`1506.02669`). Its non-gravitational limit, the QNEC, is a
   *proven theorem* in QFT; the QFC itself is **not proven** — flag this whenever
   the chain is used.
3. Where the bound is saturated dynamically: quantum extremal surfaces / islands
   (generalized entropy `S_gen = A/4G + S_matter`), already surveyed in
   `corpus/GAP-ANALYSIS.md` (HRT -> FLM -> QES -> JLMS).
4. **The 2025-26 sharpening (this addendum):** a horizon's observable algebra is
   Type III_1 in ordinary QFT and has *no* density matrix or finite entropy.
   Crossing it with the modular flow (Witten `2112.12828`) yields a **Type II**
   algebra that does — and its von Neumann entropy is *exactly* `S_gen`
   (`2309.15897`, and its edge-mode sequel `2601.07910`). This is the operator
   statement `S_gen = S_vN`. Faulkner-Speranza `2405.00847` shows the algebraic
   monotonicity reproduces the generalized second law; Chandrasekaran-Flanagan
   `2601.07915` and Sahu et al. `2511.21852` push it to subregions / generalized
   entanglement wedges.
5. **de Sitter and the Project-2 tie:** dS gives a **Type II_1** algebra, whose
   *maximal* entropy is the cosmological-horizon area (Chen-Xu `2511.00622`).
   The computable handle is DSSYK: Xu `2403.09021` identifies the Type II_1
   algebra of double-scaled SYK with a finite maximal entropy matching a dS
   horizon — the same DSSYK<->dS bridge Project-2 already uses for horizon magic.

| Priority | Paper | Tier | Role in the chain |
|---|---|---|---|
| P0 | Bousso et al., QFC, `1506.02669` | Established (QFC conjectural; QNEC proven) | The covariant bound made local; root of the QES/island chain. |
| P0 | Witten, crossed product, `2112.12828` | Established | Type III_1 -> Type II; density matrices and finite vN entropy exist. |
| P1 | Kudler-Flam-Leutheusser-Satishchandran, `2309.15897` | Toy/rigorous | S_gen = S_vN made precise for a horizon. |
| P1 | Faulkner-Speranza, GSL, `2405.00847` | Toy/rigorous | Algebraic monotonicity = generalized second law; QFC/QNEC <-> Type II bridge. |
| P1 | Xu, vN algebras in DSSYK, `2403.09021` | Recent | **Project-2 anchor:** DSSYK Type II_1, finite max entropy = dS horizon. |
| P2 | Chen-Xu, dS covariant observers, `2511.00622` | Recent | dS Type II_1; max entropy = cosmological-horizon area. |
| P2 | Klinger-Kudler-Flam-Satishchandran II, `2601.07910` | Recent | Symmetry group + edge modes behind the gravitational algebra. |
| P2 | Chandrasekaran-Flanagan, `2601.07915` | Recent | Subregion algebras, classical -> quantum, QFC-type proof. |
| P2 | Sahu et al., generalized entanglement wedges, `2511.21852` | Recent | vN algebras for generalized wedges; reconnects to EW reconstruction. |

**Buildable next step (honest scope).** The *rigorous* content here is operator-
algebraic, not circuit-executable — do not overclaim a "Type II algebra on
hardware." What IS executable is the **DSSYK Type II_1 / finite-max-entropy**
statement (`2403.09021`), which is exactly the arena Project-2 already computes
in: a small-`N` DSSYK lab that measures the *finite* maximal entropy (the II_1
trace normalization) and compares it to the dS-horizon value would be the first
lab-level contact with this front. Frame it as "reproducing the finite-entropy
normalization of the DSSYK algebra," not "measuring a gravitational algebra."
This slots directly onto Project-2's existing DSSYK<->dS machinery. No lab
should claim the crossed-product construction itself has been reproduced.

**Watchlist (surveyed, not filed):** `2605.13576`, `2607.01873` — track for the
next pass; cite only if a lab loads them.
