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
  with hopping b_n from a q-deformed oscillator. Literature (verification sweep
  in flight — IDs to be confirmed before anything load-bears) reportedly makes
  "Krylov complexity = chord number = bulk length" precise in the DS limit, and
  Xu 2403.09021 gives DSSYK the Type II₁ algebra with finite max entropy.
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
  (K_late ≈ dim-limited plateau); SYK2 localizes.
- **P3-2 (the non-tautological bridge test)**: the chaotic/integrable
  discriminator lives in the *disorder profile* of the b_n (smooth plateau vs
  fragmented/spiky), and the SAME feature controls (a) the reconstructed
  spectral rigidity (RMT-like vs Poisson-like) and (b) the arrow (K_late). The
  falsifier both executors hunt: a model whose chain localizes while its
  spectrum stays RMT-rigid, or vice versa — one clean counterexample kills the
  bridge. (Candidate hunting ground: Anderson-type disorder on the chain;
  structured-sparse SYK variants.)
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
   (b_n-profile → reconstructed spectral statistics vs K_late) across SYK4 /
   SYK2 / disordered-chain / DSSYK-chord ensembles; run the falsifier hunt.
4. **S3 verdict + write-up**: bridge holds (with stated scope) / narrowed /
   refuted — any of the three is a result. Converge into the scorecard §10 and
   a short note if warranted.

## Split

| step | quant-phy (build/synthesis) | codex-science (execution) | agy-science (analytical) |
|---|---|---|---|
| S0 | run sweep, file anchors | spot-check IDs | — |
| S1 | author chord-chain lab | independent reimplementation + reproduce | audit q-oscillator b_n derivation (pasted) |
| S2 | design test + build my half | falsifier hunt + ensemble sweeps + SEMs | **tautology guard**: certify the test is non-circular before build; audit recursion-method dictionary |
| S3 | synthesize + draft | verify numbers | audit final logic; sign |

## Status board

- [x] Scoping doc (this file) — posted for co-scope pushback
- [ ] S0 anchors verified + filed
- [ ] Scope + pre-registration converged; agy tautology sign-off obtained
- [ ] S1 chord-chain lab built + reproduced
- [ ] S2 bridge test run; falsifier hunt done
- [ ] S3 verdict converged, all three sign
