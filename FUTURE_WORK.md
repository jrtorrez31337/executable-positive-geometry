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
