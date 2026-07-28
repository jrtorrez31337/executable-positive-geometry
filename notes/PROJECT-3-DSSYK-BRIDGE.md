# Project 3 — The DSSYK spectral bridge (the arrow program's open conjecture)

**Opened 2026-07-27 (Jon-directed; distinct from PROJECT-2-MAGIC-WEDGE.md, same
three-agent step-by-step model).** This is the named open target of the
arrow-of-time program (`ARROW-ORIGINS-SCORECARD.md` §10):

> Does the complexity/Krylov arrow and a modular-positivity diagnostic track the
> **same spectral quantity** in a computable model (DSSYK)?

## Why DSSYK is the arena

- Our Krylov-ignition capstone (`labs/track-c-time/krylov_ignition.py`) showed
  the arrow ignites on the chaotic Krylov chain (K_late discriminator; the
  one-sided chain with n̂ ≥ 0 as the finite shadow of the positive generator).
- DSSYK has an exactly solvable **chord basis** in which the Hamiltonian is
  tridiagonal — i.e. DSSYK *is natively a one-sided chain* (chord number n ≥ 0),
  with hopping b_n from a q-deformed oscillator (Lin `2208.07032`; Berkooz et
  al. `1811.02584`). **S0 VERIFIED (2026-07-27, all IDs checked against abs
  pages + PDF titles; 8 anchors filed, corpus → 58):**
  - **The key identity is established, and exact:** the TFD's Krylov basis
    *coincides with* the chord-number basis (any q), so spread complexity
    = ⟨n̂⟩ — Rabinovici–Sánchez-Garrido–Shir–Sonner `2305.04355`; extended to
    operator K-complexity (= total chord length) in `2412.15318`. The "= bulk
    length" reading is exact only in the triple-scaling/JT limit.
  - **The honest caveat (fold into P3-1):** at finite N the chord basis is an
    *extrapolation* of the true Krylov basis and complexity **saturates** at
    late times (`2412.02038`) — so ideal-chain linear growth is the
    semiclassical statement, saturation the finite-N one.
  - **Our niche is OPEN:** nobody frames chord-number positivity / the
    one-sided chain as an *arrow-of-time* statement. The ingredients exist
    separately — positivity as a thermodynamic constraint (`2404.03535`),
    modular structure of the chord algebra (`2403.09021`, whose zero-chord
    state is cyclic-separating), entropy↔complexity (`2511.03779`) — but no
    one has fused them. Position our P3-3 as that fusion (🔴, conjecture).
  - dS side: `2510.13986` (dS complexity = Krylov, linear rate set by dS
    entropy/temperature) + `2403.13186` support P3-1's dS reading.
- So the bridge question becomes concrete: the chord chain carries BOTH the
  complexity arrow (K(t) = ⟨n̂⟩ growth) and the positivity structure (n̂ ≥ 0,
  boundary at n=0) in one object.

## The tautology guard (the Janus-toy lesson, stated up front)

The Lanczos coefficients b_n determine *both* the spectral density (recursion
method) *and* K(t). So "complexity and spectrum are related" is TRIVIALLY true
and proves nothing. The non-tautological content must be **discriminative**: a
specific feature of the spectral data that controls the arrow on both sides and
**could fail to**. agy-science owns this guard: before we build, it must sign
off that the pre-registered test below is non-circular.

## Pre-registered predictions (draft — converge + tautology-audit before build)

- **P3-1 (chord chain / dS behavior)**: the DSSYK chord chain with
  b_n ∝ √((1−qⁿ)/(1−q)) has b_n → plateau; on the ideal semi-infinite chain
  K(t) grows without saturation — matching the "de Sitter complexity grows
  linearly" statement. Contrast: our finite-N SYK4 chain saturates
  (K_late ≈ dim-limited plateau); SYK2 localizes. Lab readout must state the
  truncation/pre-reflection window explicitly: any finite chord-chain cutoff
  saturates by construction, so the registered signal is ballistic pre-boundary
  growth velocity plus the finite-cutoff saturation caveat, not literal
  infinite-time linear growth in a finite matrix.
- **P3-2 (the non-tautological bridge test)**: the chaotic/integrable
  discriminator lives in the *disorder profile* of the b_n (smooth plateau vs
  fragmented/spiky), and the SAME feature controls (a) independently measured
  spectral rigidity (RMT-like vs Poisson-like) and (b) the arrow (K_late).
  **Tobin caveat:** do not reconstruct rigidity only from the same single
  Jacobi data used to evolve K(t); that collapses back to the recursion-method
  tautology. Rigidity must come from unfolded finite spectra / number variance
  of an independently specified Hamiltonian or Jacobi-matrix ensemble, then be
  compared to separately reported b-profile and wavepacket-localization
  metrics. The falsifier both executors hunt: a model whose chain localizes
  while its spectrum stays RMT-rigid, or vice versa — one clean counterexample
  kills the broad bridge. Candidate controls: Anderson on/off-diagonal disorder
  chains; β-Hermite tridiagonal RMT (disordered coefficients but RMT rigidity);
  Rosenzweig-Porter or power-law banded ensembles; structured-sparse SYK
  variants across K.
- **P3-3 (positivity framing — statement only, no proof claim)**: the chord
  chain's n̂ ≥ 0-with-boundary is definitionally the same one-sided structure as
  the Krylov chain; the DS limit is where it should become an algebra statement
  (Type II₁). Deliverable is the precise conjecture + what a proof would
  require, tiered honestly (🔴), not a claimed theorem.

## The work (steps, strictly ordered)

1. **S0 lit-verification** (in flight): confirm the chord-basis tridiagonal +
   Krylov=chord-number sources with real IDs; file anchors to corpus
   (verify-before-add). Nothing cites until verified.
2. **S1 chord-chain lab** (`labs/track-c-time/dssyk_chord_chain.py`): build the
   DSSYK tridiagonal from the q-oscillator b_n; compute K(t) across q; verify
   P3-1 against our krylov_ignition results.
3. **S2 bridge test**: implement the P3-2 discriminative test on both sides
   (b_n-profile + Krylov localization metrics vs independently unfolded
   spectral rigidity) across SYK4 / SYK2 / disordered-chain / β-Hermite /
   Rosenzweig-Porter or banded / DSSYK-chord ensembles; run the falsifier hunt
   with SEMs.
4. **S3 verdict + write-up**: bridge holds (with stated scope) / narrowed /
   refuted — any of the three is a result. Converge into the scorecard §10 and
   a short note if warranted.

## Split

| step | quant-phy (build/synthesis) | codex-science (execution) | agy-science (analytical) |
|---|---|---|---|
| S0 | run sweep, file anchors | spot-check IDs | — |
| S1 | author chord-chain lab | independent reimplementation from the formula only + reproduce; no imports from the authored lab except shared test fixtures | audit q-oscillator b_n derivation (pasted) |
| S2 | design test + build my half | falsifier hunt + ensemble sweeps + SEMs; include β-Hermite and Rosenzweig-Porter/banded controls | **tautology guard**: certify the test is non-circular before build; audit recursion-method dictionary |
| S3 | synthesize + draft | verify numbers | audit final logic; sign |

## Status board

- [x] Scoping doc (this file) — posted for co-scope pushback
- [x] S0 anchors verified + filed (2026-07-27: 8 papers, corpus -> 58; key identity established exact; finite-N saturation caveat folded into P3-1; positivity-as-arrow niche confirmed OPEN)
- [x] Scope + pre-registration converged; agy tautology sign-off obtained 2026-07-27 (#340: P3-2 as amended is NON-CIRCULAR -- independent-rigidity requirement + beta-Hermite falsifier controls certify it falsifiable; Tobin amendments accepted)
- [x] S1 CLOSED: authored (dssyk_chord_chain.py) + Tobin clean-room reproduction (dssyk_chord_chain_cleanroom.py, from formula only) matches to 3 decimals across q. agy b_n audit still pending (folds into S2/S3 sign-off).
  - Codex clean-room reproduction artifact added:
    `labs/track-c-time/dssyk_chord_chain_cleanroom.py` builds only from
    `b_n = sqrt((1-q^n)/(1-q))`, zero diagonal, and `|n=0>`; it reproduces the
    registered E2 velocity table and E3 oscillator slope without importing the
    authored S1 lab.
- [x] S2 falsifier hunt RUN + converged between executors (2026-07-28):
  quant-phy run (dim64/s12) + Tobin reruns (dim128/s32; RP transition probes
  c=0.20/0.35/0.50 at dim128/s64): NO BRIDGE-KILLER in any of 7 ensembles.
  beta-Hermite (the designed killer) survives; RP stays intermediate/consistent.
  KEY REFINEMENT (both executors concur): the DSSYK chord chain reads
  r=0.968 + low Sigma2 = PICKET-FENCE (integrable-type) rigidity, not RMT,
  yet carries the strongest arrow (Klate/chain=0.57) -> the bridge narrows to
  "the arrow co-varies with spectral RIGIDITY (low number variance), not chaos
  per se; chaos is one route to rigidity." Classifier patched in `dssyk_bridge_falsifiers.py`:
  picket-fence (r>0.85 + low Sigma2) now distinct from RMT (0.49<r<0.75).
  Chord chain stays in the comparison as a structured control, flagged n=1.
  GATES OPEN for S3: agy audits (A) b_n derivation (#343), (B) soundness of
  the picket-fence reading + the chaos->rigidity narrowing (#358).
  - Codex execution artifact added:
    `labs/track-c-time/dssyk_bridge_falsifiers.py` sweeps Anderson,
    beta-Hermite tridiagonal RMT, Rosenzweig-Porter, banded, GOE/Poisson, and
    DSSYK-chord controls with SEMs; rigidity is measured from independently
    unfolded finite spectra before comparison to b-profile and K(t) metrics.
- [ ] S3 verdict converged, all three sign
