# Project 2 — Wedge geography of magic (the corner we own)

**Opened 2026-07-27 (Jon-directed: run #2 and #3 as distinct projects, all three
agents hand-in-hand, step-by-step).** Companion: `PROJECT-3-DSSYK-BRIDGE.md`.
Status board at bottom; nothing builds until scope + pre-registration converge.

## Goal

Turn our verified unclaimed corner — **magic resolved across explicit
holographic-code wedges** — into (A) an outward note and (B) a real hardware
measurement (or an honest noise-bound), extending the only hardware
demonstration to date (arXiv 2511.15576, two bare qubits, no codes/wedges).

## What we already have (all exact, cross-checked, on record)

- **Phase 0/1/1b** (`labs/track-d-magic/`): magic follows wedge geometry, not
  region size; twin-control protocol isolating phase-injected magic; the
  **erasable/irreducible decomposition** with the closed form
  `NL = −log₂(4P²−6P+3)` and the complementary-geography result — *"what local
  operations can remove, single wedges cannot see; what they cannot remove,
  single wedges cannot miss."* Junk-corrected boundary-purity protocol (factors
  0.5 / 0.25) reads irreducible magic from ONE wedge.
- **Phases 2/3/3b**: magic-enriched codes (2603.13475) — state-dependent
  proto-area, Petz-recovery fix, "more matter → larger area" in a toy.
- **`species_hardware.py`**: true 2-tile [[5,1,3]] encoder (GF(2) symplectic
  completion), noiseless extraction EXACT (NL = 0.29956).
- **Phase 7 harness** (Tobin): quota-gated submit/retrieve with the two-tier
  criterion. **Phase 7 rehearsal finding (quant-phy)**: the purity route is
  noise-dominated at current depth — NL 0.2996 → ~0.01 on a Heron noise model;
  root cause is fundamental (decoherence mixes the wedge exactly like the
  signal does). Tier 2 (NL > 0.10) requires a **shallower encoder**, not more
  mitigation.

## The work (three streams)

**W1 — the note** (viable since Phase 1b, never written): *"Wedge geography of
erasable and irreducible magic in holographic codes."* Phases 0+1+1b + the
junk-corrected one-wedge purity protocol as a hardware-ready proposal + honest
methods (twin control; mixed-SRE false-positive trap).

**W2 — shallower-encoder redesign + rehearsal**: redesign the 2-tile encoder to
cut routed 2q depth (targets: better Clifford synthesis of the stabilizer group;
layout-aware synthesis for heavy-hex; possibly a single-tile irreducible-magic
variant first, but only as a separate pilot unless it preserves P2-A's same-code
claim). Gate: noise-model rehearsal must show the Tier-2 signal clears the
rehearsal noise floor with margin before any real shots: use the lower
confidence bound `NL_rehearsal - 2σ_total > 0.10`, where `σ_total` combines the
purity-estimator shot error and rehearsal ensemble SEM. With the current Phase 7
reference (`400x1024` gives `σ(NL) ≈ 0.046`), this means the redesigned circuit
needs roughly `NL_rehearsal > 0.192`; the naive Phase 7 circuit (`~0.01`,
optimistic bracket `~0.09`) is decisively below gate.

**W3 — hardware shot** (free-tier quota resets ~Aug 1): fire Tobin's harness
with the redesigned circuit if W2's gate passes; else fire Tier-1
(device-characterization: P_wedge − 2σ > 0.125 + noise-model consistency) and
publish the redesign + honest bound in the note.

## Pre-registered predictions (draft — converge before any run)

- **P2-A**: the redesigned encoder reproduces the exact noiseless NL = 0.29956
  (same code, same state — synthesis must not change the physics).
- **P2-B**: rehearsal NL should improve as the *routed* 2q count and idle depth
  drop under the same backend/noise/mitigation model, but monotonicity is a
  trend sanity check, not the pass criterion. The Tier-2 gate passes only if
  `NL_rehearsal - 2σ_total > 0.10`; otherwise the result is Tier 1 /
  honest-null even if the point estimate exceeds 0.10.
- **P2-C** (hardware, if fired): measured irreducible magic from ONE wedge via
  junk-corrected purity agrees with the noise-model prediction within 2σ; the
  no-magic control wedge reads consistent with zero.
- **Falsifier / honest-null**: if no synthesis reaches the rehearsal gate, the
  deliverable is the note + a quantified noise-bound ("wedge magic below the
  Heron floor at depth d"), not a forced signal.

## Split (each agent in its proven lane)

| stream | quant-phy (build/synthesis) | codex-science (execution) | agy-science (analytical) |
|---|---|---|---|
| W1 note | draft | verify every number vs reruns | audit the closed-form + junk-factor derivations (pasted) |
| W2 redesign | synthesis attempts | noise-model rehearsals + SEMs; persist per-candidate routed metrics, circuit hashes, and lower-bound gate verdicts | audit: does the pasted stabilizer set generate the same code? tautology/logic check on Tier gates |
| W3 hardware | pre-reg + convergence | submit/retrieve + raw data | audit criterion logic before firing |

## Status board

- [x] Scoping doc (this file) — posted for co-scope pushback
- [x] Scope + pre-registration converged 2026-07-27 (Tobin amendments 8332df3 accepted; agy audit #338/#340: closed-form corrected (my paste error -- labs were right), RDM reasoning sound, note scoped to PURE logical states; all three signed)
- [x] W1 note CLOSED three-signed 2026-07-27: Tobin verified all numbers + gate (#347, additive sigma redline applied b16ebb6); agy audits: closed-form (#340), pure-state scope, junk-factor soundness via state-independent factorization (#350). paper/note-wedge-magic.pdf is the fifth research note.
- [ ] W2 redesign meets rehearsal gate (or honest-null recorded)
- [ ] W3 fired when quota resets (~Aug 1) → results converged
- [ ] Project closed: note final, both/all signed
