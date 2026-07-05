# Executable Positive Geometry

**An end-to-end verification tour from Bell tests to the two-loop
amplituhedron, with holographic wedge localization measured on
superconducting hardware.**

This repository contains thirteen laboratory scripts, a verified 18-paper
reference corpus, and a manuscript, tracing a single arc:

> *Space, locality, and scattering may be outputs of deeper structure —
> entanglement patterns and positive geometries. Every claim in that
> sentence that can be tested with today's tools is tested here: in exact
> arithmetic, in deterministic simulation, or on IBM quantum hardware.*

Nothing here is new theory. It is a **pedagogical verification study**:
each foundational claim of the "physics from geometry" program is
*executed* rather than cited, and the failures encountered along the way
are documented next to the successes.

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

Plus one instructive, fully documented failure: zero-noise extrapolation
**diverging** at 550-gate depth (nulls of ±4×10⁹), caught by designed-in
null witnesses (job `d94u25nu62ks7396fhlg`).

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
    05-loop-amplituhedron/     one- and two-loop amplituhedron (n=4)
  capstone-happy/              holographic codes: where the two tracks meet
    happy_tile.py              [[5,1,3]] perfect tensor, exact wedge transition
    happy_network.py           six-tile flower: depth, quantized info, discrete RT
    happy_hardware.py          single tile on ibm_kingston (+ error mitigation)
    flower_hardware.py         21-qubit network on ibm_kingston
corpus/                        annotated 18-paper reference library
    README.md                  index with per-paper evidence tiers (🟢/🟡/🔴)
    refs.bib                   BibTeX for all corpus papers
    fetch_corpus.sh            re-download all PDFs (not committed)
paper/                         the manuscript (LaTeX + compiled PDF)
CLAUDE.md                      profile of the AI research persona used
```

## Reproducing

```bash
uv venv .venv && uv pip install -r requirements.txt   # or python -m venv + pip
bash corpus/fetch_corpus.sh                            # optional: rebuild corpus

# Everything except the hardware runs is deterministic and local:
.venv/bin/python labs/track-a/01-bell-chsh/chsh.py
.venv/bin/python labs/track-b/05-loop-amplituhedron/loop_amplituhedron.py
.venv/bin/python labs/capstone-happy/happy_network.py
# ... every lab script is self-contained and prints its own narrative.

# Hardware runs need an IBM Quantum account (free open plan suffices):
#   QiskitRuntimeService.save_account(token="...", set_as_default=True)
.venv/bin/python labs/capstone-happy/happy_hardware.py
```

All hardware jobs cited in the paper are retrievable by job ID from the
IBM Quantum dashboard.

## The paper

`paper/main.pdf` — *Executable Positive Geometry* (~9 pp). Compiles with
any LaTeX (Overleaf-ready): `tectonic paper/main.tex`.

## Honest scope

Every model here is a toy: the amplituhedron addresses planar N=4 super
Yang–Mills, the associahedron bi-adjoint φ³, the HaPPY network a static
AdS-like geometry. Whether *our* universe uses these mechanisms is open.
The corpus index marks every source by evidence tier, and the labs mark
every claim as proven, toy-model, or speculative. Three tempting
"exploits" are explicitly closed by the experiments themselves: no
signaling through entanglement, no information in minority wedges, no
bypassing locality via kinematic-space adjacency — positivity *enforces*
causality; it does not circumvent it.

## Acknowledgments

Built by Jon Torrez in collaboration with **Ariadne Vale**, an AI research
assistant (Claude, Anthropic), which wrote and executed the lab code,
performed literature verification, and co-drafted the manuscript.
Hardware: IBM Quantum open plan (`ibm_kingston`, Heron, 156 qubits).

## License

MIT — see [LICENSE](LICENSE). The corpus papers remain the property of
their authors and arXiv; they are indexed and fetched, not redistributed.
