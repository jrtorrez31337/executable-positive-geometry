# Executable Positive Geometry

**An end-to-end verification tour from Bell tests to the two-loop
amplituhedron to the magic that lets geometry gravitate — with holographic
wedge localization and an emergent arrow of time measured on
superconducting hardware.**

This repository contains **48 laboratory scripts** across five lines of
work (Tracks A–D plus holographic capstones), a verified **40-paper**
reference corpus (7 pillars), and two manuscripts, tracing a single arc:

> *Space, locality, scattering, time, and even gravitational
> backreaction may be outputs of deeper structure — entanglement patterns,
> positive geometries, and quantum "magic" (non-stabilizerness). Every
> claim in that sentence that can be tested with today's tools is tested
> here: in exact arithmetic, in deterministic simulation, or on IBM
> quantum hardware.*

Mostly this is a **pedagogical verification study**: each foundational
claim of the "physics from geometry" program is *executed* rather than
cited, and the failures encountered along the way are documented next to
the successes. Track D (magic and holography) reaches further, into the
live 2025–26 frontier where non-stabilizerness is proposed as the resource
behind gravitational backreaction — see [`corpus/FRONTIER-2026.md`](corpus/FRONTIER-2026.md).
Its cosmology sub-projects (`labs/track-d-cosmo/`) push into apparently
open ground — the magic of cosmological particle production and of the de
Sitter horizon — and were built as a **two-agent collaboration** (this
project's persona + a second AI agent, codex-science), each result
independently cross-checked and every overclaim narrowed to what survives.

## Headline results

| Result | Where | Value |
|---|---|---|
| CHSH violation on real hardware (with no-signaling check) | `labs/track-a/01-bell-chsh/` | **S = 2.7579** (classical bound 2, job `d94sl25gc6cc73ffgo5g`) |
| Surface-17 code: error strings detected at endpoints, invisible attack = spanning string | `labs/track-a/02-qec-repetition/` | 100% deterministic fingerprints; p_L ∝ p² |
| Ising central charge from entanglement (N=12, Calabrese–Cardy) | `labs/track-a/03-emergence/` | **c ≈ 0.58** (exact: 0.5) |
| ABHY associahedron = bi-adjoint φ³ amplitude | `labs/track-b/03-associahedron/` | exact, symbolic |
| Six-term NMHV identity of the amplituhedron 𝒜(6,1,4) | `labs/track-b/04-amplituhedron/` | **R₁ − R₂ = 0**, exact rationals |
| Two-loop "maximally positive numerator" from double boxes | `labs/track-b/05-loop-amplituhedron/` | **N = D⁺** exactly |
| Single holographic tile: wedge witnesses on hardware (mitigated) | `labs/capstone-happy/` | mean wedge **+0.956**, nulls 0.005 (job `d94ttgtgc6cc73ffi3p0`) |
| 21-qubit six-tile network: bulk-operator localization on hardware | `labs/capstone-happy/` | **+0.552 on the right tile vs +0.004 on the wrong one** (job `d94u424ql68s73c9vtig`) |
| Emergent arrow of time from record-conditioning, on hardware | `labs/track-c-time/` | entropy **0→0.97 bits** monotone (7/7 ticks), recordless control flat (job `d959d86vtlqs73fv5atg`) |
| Magic follows *wedge geometry*, not region size | `labs/track-d-magic/phase0` | 12-qubit majority arc missing the wedge has **zero** magic; T-state wedge = log₂(4/3) |
| Gravitational backreaction *is* magic (state-dependent area) | `labs/track-d-magic/phase2` | exact codes: 0; skewed codes: area + tripartite non-local magic both ∝ θ² |
| Proto-area grows with bulk entropy (Theorem 4.2, Petz recovery) | `labs/track-d-magic/phase3b` | monotone **1.35 → 1.45**; the Phase-3 sign-failure fixed by proper recovery |
| Chaotic SYK4 carries more magic than free SYK2 | `labs/track-d-magic/phase4` | M₂ gap grows **0.07 → 0.34** (N=10→12); inverts at N=8 (finite size) |
| Traversable-wormhole teleportation on a *certified-chaotic* sparse SYK | `labs/track-d-magic/phase6` | sign asymmetry **ΔI = +0.0168 bits** at t₁=2.0; RMT chaos certified at N≥10 |
| Cosmological magic splits by resource theory | `labs/track-d-cosmo/proj1*` | free bosons are Wigner-positive; cubic non-Gaussianity turns CV negativity on; fermion magic is exact qubit magic |
| de Sitter horizon magic appears in the **dynamics, not statically** | `labs/track-d-cosmo/proj2_magic_dynamics` | static null; chaotic TFD magic grows **~2× more** under evolution (2.05/2.30/2.55× at N=6/8/10) |

Plus instructive, fully documented **failures**: zero-noise extrapolation
**diverging** at 550-gate depth (nulls of ±4×10⁹), caught by designed-in
null witnesses (job `d94u25nu62ks7396fhlg`); a Phase-3 backreaction
prediction that came out with the *wrong sign* before proper Petz recovery
fixed it (Phase 3 → 3b); and a Phase-7 hardware run shown *in advance* to be
noise-dominated, so quota is not spent on it. Every refuted prediction is
kept next to the confirmations.

## Repository layout

```
labs/
  track-a/                     Quantum lab (Qiskit)
    01-bell-chsh/              Bell pairs, CHSH, no-signaling; + hardware version
    02-qec-repetition/         repetition code, surface-17, fair-fight Monte Carlo
    03-emergence/              VQE Ising transition; entanglement as proto-geometry
  track-b/                     Geometry lab (SymPy, exact arithmetic)
    01-grassmannian/           Plücker relations, positivity, Parke-Taylor dictionary
    02-canonical-forms/        canonical forms; triangulation independence
    03-associahedron/          ABHY kinematic associahedron (n=4,5)
    04-amplituhedron/          Gr+(2,4) → Parke-Taylor; NMHV A(6,1,4)
    05-loop-amplituhedron/     one- & two-loop amplituhedron (n=4,5,6); leading singularities
    06-positroid-test/         audit of Hoffman's Markov→decorated-permutation bridge
  track-c-time/                Time lab: Page-Wootters emergent time, arrow on hardware
  track-d-magic/               Magic lab: non-stabilizerness in codes & SYK (Phases 0–7)
    phase0..1b                 wedge magic geography; erasable vs irreducible species
    phase2, phase3b            backreaction = magic; proto-area grows with bulk entropy
    phase4, phase5             SYK4-vs-SYK2 magic; multipartite non-local magic (TPQ)
    phase6_*                   traversable-wormhole teleportation + chaos certification
    phase7_*                   purity-only non-local-magic hardware run (prepped)
    species_hardware.py        [[5,1,3]] encoder + two-species single-wedge protocol
  track-d-cosmo/               Cosmological magic (2-agent build): magic of the
    proj1_*                    expanding vacuum (boson/fermion asymmetry, dS->radiation)
    proj2_*                    de Sitter horizon magic (static null -> dynamical signal)
  capstone-happy/              holographic codes: where the tracks meet
    happy_tile / happy_network [[5,1,3]] perfect tensor; six-tile flower (depth, RT)
    happy_hardware / flower_*  single tile & 21-qubit network on ibm_kingston
    self_wedge / holonomy*     self-reference (Klein), code-automorphism holonomy (+ HW)
    spawn_object.py            bulk-object injection via boundary operators (ER=EPR toy)
corpus/                        annotated 50-paper reference library (7 pillars)
    README.md                  index with per-paper evidence tiers (🟢/🟡/🔴)
    GAP-ANALYSIS.md            joint gap analysis (with codex-science agent)
    FRONTIER-2026.md           mid-2026 field survey: positive geometry, magic, cosmology
    refs.bib / fetch_corpus.sh BibTeX + PDF re-download script (PDFs not committed)
notes/                         research notes and scope guards
    TIME-ARROW-TRACKER.md      running log of the "reverse time" theme across labs
    P2-DESITTER-HORIZON-MAGIC.md
                                controls/scope note for the dS/SYK horizon-magic project
paper/                         two manuscripts: main.pdf + note-two-loop.pdf
CLAUDE.md                      profile of the AI research persona used
FUTURE_WORK.md                 open doors: composite LS census, n=6, hardware follow-ups
```

## Reproducing

```bash
uv venv .venv && uv pip install -r requirements.txt   # or python -m venv + pip
bash corpus/fetch_corpus.sh                            # optional: rebuild corpus

# Everything except the hardware runs is deterministic and local:
.venv/bin/python labs/track-a/01-bell-chsh/chsh.py
.venv/bin/python labs/track-b/05-loop-amplituhedron/loop_amplituhedron.py
.venv/bin/python labs/capstone-happy/happy_network.py
.venv/bin/python labs/track-c-time/page_wootters.py
.venv/bin/python labs/track-d-magic/phase2_backreaction.py
# ... every lab script is self-contained and prints its own narrative.

# Hardware runs need an IBM Quantum account (free open plan suffices):
#   QiskitRuntimeService.save_account(token="...", set_as_default=True)
.venv/bin/python labs/capstone-happy/happy_hardware.py
```

All hardware jobs cited in the paper are retrievable by job ID from the
IBM Quantum dashboard.

## The manuscripts

- `paper/main.pdf` — *Executable Positive Geometry* (~9 pp), the full
  verification tour.
- `paper/note-two-loop.pdf` — *Assembly of the two-loop MHV integrand from
  maximally positive mutual numerators at five and six points* (~4 pp),
  the one place the labs push slightly past pure verification into a stated
  (finite-point-checked, not proven) all-n conjecture.

Both compile with any LaTeX (Overleaf-ready): `tectonic paper/main.tex`.

## Honest scope

Every model here is a toy: the amplituhedron addresses planar N=4 super
Yang–Mills, the associahedron bi-adjoint φ³, the HaPPY network a static
AdS-like geometry, and Track D's magic/SYK/wormhole labs are small-N
instantiations of 2025–26 frontier proposals (e.g. magic-enriched codes,
traversable-wormhole teleportation) — reproduced, with their assumptions
labeled, not claims about real gravity. Whether *our* universe uses any of
these mechanisms is open. The corpus index marks every source by evidence
tier, and the labs mark every claim as proven, toy-model, or speculative.
Three tempting "exploits" are explicitly closed by the experiments
themselves: no signaling through entanglement, no information in minority
wedges, no bypassing locality via kinematic-space adjacency — positivity
*enforces* causality; it does not circumvent it.

The project's method is **pre-register a prediction, then execute it, and
keep the refuted ones in the repository.** Track D's Petz-recovery result
(Phase 3b) exists *because* the naive Phase-3 prediction failed with the
wrong sign and the failure was diagnosed rather than hidden; the Phase-6
chaos certification records honestly that it holds at N≥10 but *not* at the
paper's own N=8; the Phase-7 hardware run is shown in advance to be
noise-dominated so quota is not wasted. Failure documentation is a feature.

**On the hardware claims specifically** (per external peer review, codex-science
2026-07-08): the IBM runs are *controlled protocol demonstrations on toy-code
states*, not evidence for real-space emergence. HaPPY "bulk localization" is
HaPPY-language for a code-subspace witness, not a claim about our universe's
spacetime. The surface-code ~7% figure is a *code-capacity pseudo-threshold*,
not an operational fault-tolerant threshold. The two-loop n=5/n=6 "ratio = 1"
results are *finite-point exact checks* at generic rational kinematics, not
symbolic identity proofs over all kinematics — the all-n statement remains a
conjecture. Job IDs are listed per experiment; saved counts/expectation-values
with error bars and retrieval notebooks are a tracked to-do (see FUTURE_WORK),
and hardware scripts pin their backend for reproducibility rather than
selecting least-busy.

## Acknowledgments

Built by Jon Torrez in collaboration with **Ariadne Vale**, an AI research
assistant (Claude, Anthropic), which wrote and executed the lab code,
performed literature verification, and co-drafted the manuscripts. Several
Track D labs (the SYK-magic baselines, multipartite magic, and the
traversable-wormhole protocol, Phases 4–7) were built as a **two-agent
collaboration** with a second AI agent (codex-science), authored by one and
independently verified and reproduced by the other before merging — the
same peer-review and corpus-gap-analysis discipline applied to the code
itself. Hardware: IBM Quantum open plan (`ibm_kingston`, Heron, 156 qubits).

## License

MIT — see [LICENSE](LICENSE). The corpus papers remain the property of
their authors and arXiv; they are indexed and fetched, not redistributed.
