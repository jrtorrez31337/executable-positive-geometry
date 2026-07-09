# Future Work — marked doors

Stored 2026-07-05, after completion of the two-loop n=5 program (T1–T5)
and the self-referential wedge lab.

## Door 1 — Composite leading-singularity census
The 20 chord-branch pentagon-box octa-cuts at n=5 are composite strata
(cut solutions forced through polygon vertices; naive transverse residues
are ray-dependent — auto-detected in `t4_leading_singularities.py`).
Build the iterated-residue machinery (layered single-variable residues in
adapted coordinates) and complete the census; the ±1 unit leading
singularities of N=4 SYM at five points live entirely in these strata.

## Door 2 — n=6 loop amplituhedron  [DONE 2026-07-05, commit 2ccf101]
Two-loop n=6: 36 composite cells; the maximally-positive-numerator
assembly matches the sum of 60 ABCT double pentagons at ratio exactly 1
(finite rational points) — the quasi-linear complication does NOT appear.
See `labs/track-b/05-loop-amplituhedron/loop2_n6.py`. REMAINING (open):
a symbolic identity proof over all kinematics (current evidence is
finite-point exact, not a proof); more independent positive-Z ensembles
beyond moment-curve samples; and the composite iterated-residue census.

## Door 4 — Write up the two-loop five-point result
The postulate P1 (9 product cells glued by maximally positive mutual
numerators), its verification chain (structure, assembly, literature
identity ratio 1, quantized transverse LS census), and the two refuted
predictions (kissing ±1s; wedge-frame holonomy) as an addendum to
`paper/main.tex` or a standalone note.

## Door 5 — Hardware follow-ups
Flower network with hand-optimized qubit layout (reduce the 553-gate
routing cost); the self-extraction ledger of `self_wedge.py` on real
transmons (6 qubits: watch self-knowledge destroy its own protection on
hardware); error-corrected reruns when heavier codes become practical.

## Door 6 — The frame-rate experiment (Page–Wootters emergent time) [OPENED 2026-07-05 — see labs/track-c-time/ and the tracker results]
The one subsystem never built: a clock. Wheeler–DeWitt-style frozen
global state (H|Psi> = 0) with entanglement between a small clock
register and a system register; verify the Page–Wootters mechanism —
the system evolves Schrödinger-correctly relative to clock readings
while the total state is stationary. Time as entanglement structure,
completing the space-from-entanglement labs. Few qubits, exact
statevectors, hardware-portable on the same free tier. Context: the
three independent "arrow of time as the currency of self-containment"
sightings (elliptic dS/Z2 non-time-orientability; det=+1-only holonomy
with the missing mirror = antiunitary time reversal; the conditional-
entropy arrow lemma in Fusions of Consciousness p. 24).

## Door 7 — Track D: magic as the resource for gravity [OPENED 2026-07-08]
The newest and most active line — non-stabilizerness ("magic") in
holographic codes and SYK, the live 2025–26 frontier (see
`corpus/FRONTIER-2026.md`). Executed: Phase 0–1b (wedge magic geography,
erasable vs irreducible species), Phase 2 (backreaction = magic), Phase 3b
(proto-area grows with bulk entropy, Theorem 4.2, via Petz recovery — the
fix for the honestly-recorded Phase-3 sign failure), Phase 4–5 (SYK4-vs-SYK2
and multipartite magic), Phase 6 (traversable-wormhole teleportation on a
chaos-certified sparse SYK). Open doors:

- **Phase 7 hardware, shallower redesign.** The purity-only non-local-magic
  run is fully prepped (`phase7_submit.py` / `phase7_retrieve.py` /
  `phase7_purity_estimator.py`) but shown *in advance* to be noise-dominated
  on free-tier Heron: decoherence mixing of the wedge is indistinguishable
  from the signal's own mixing at ~27 2q-gate depth, so a clean NL readout
  needs a *shallower encoder*, not just error mitigation. Design the shallow
  variant, or fire the run as a Tier-1 device-characterization when quota
  resets (~monthly free-tier reset).
- **Phase 6 N=8 chaos via the full SFF.** The gap ratio and the connected-SFF
  ramp both certify RMT chaos only at N≥10; the paper's own N=8 has too few
  even-parity levels. A larger-statistics / full-spectrum SFF study could
  settle N=8 directly.
- **The foundation-chain theory note.** Write up
  `2306.14996 → 2403.07056 → 2010.05960 → 2603.13475` as the "magic-enriched
  approximate codes produce state-dependent geometry" spine (per the joint
  `corpus/GAP-ANALYSIS.md` / `FRONTIER-2026.md`).
