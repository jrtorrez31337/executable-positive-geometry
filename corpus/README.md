# Research Corpus: Quantum Geometry & Spacetime Emergence

Local reference library for the project framework. Every paper was verified against
the arXiv API (title/ID match) before download on 2026-07-04. PDFs are named
`year-authors-topic.pdf`; the arXiv ID for each is listed below.

**Evidence tiers used in this index:**
- 🟢 **Established** — peer-reviewed, heavily cited, mainstream consensus
- 🟡 **Toy model** — rigorous mathematics, but demonstrated in simplified/idealized settings (e.g. planar 𝒩=4 SYM, AdS rather than our universe)
- 🔴 **Recent / speculative** — real research, but new, from a small number of groups, not yet independently confirmed

---

## 1-positive-geometry/ — The "Raw Processor"

Validates: *scattering amplitudes can be computed as geometric properties (canonical
forms) of timeless mathematical shapes, replacing sums over Feynman diagrams.*

| Paper | arXiv | Tier | What it validates |
|---|---|---|---|
| Arkani-Hamed & Trnka, **The Amplituhedron** (2013) | [1312.2007](https://arxiv.org/abs/1312.2007) | 🟡 | The founding paper. Amplitudes in planar 𝒩=4 super Yang-Mills = canonical form of a positive geometry. Locality and unitarity *emerge* from positivity — they are outputs, not inputs. Caveat: toy model, not the Standard Model. |
| Arkani-Hamed, Bai & Lam, **Positive Geometries and Canonical Forms** (2017) | [1703.04541](https://arxiv.org/abs/1703.04541) | 🟢 | The rigorous mathematical definition of "positive geometry" and its unique canonical form. This is the formal backbone — the math itself is proven, independent of any physics application. |
| Arkani-Hamed, Benincasa & Postnikov, **Cosmological Polytopes** (2017) | [1709.02813](https://arxiv.org/abs/1709.02813) | 🟡 | Extends the paradigm from scattering to cosmology: the wavefunction of the universe from a polytope's canonical form. Time evolution recovered from a timeless object. |
| Arkani-Hamed, Bai, He & Yan, **Scattering Forms and the Positive Geometry of Kinematics** (2017) | [1711.09102](https://arxiv.org/abs/1711.09102) | 🟡 | The kinematic associahedron: positive geometry living directly in *kinematic space* (the space of momenta), for ordinary (bi-adjoint scalar) theories — first step beyond 𝒩=4 SYM. |
| Arkani-Hamed & Trnka, **Into the Amplituhedron** (2013) | [1312.7878](https://arxiv.org/abs/1312.7878) | 🟡 | The loop-level amplituhedron: loop momenta as lines in P³, mutual positivity between loops, cuts as boundaries. Foundation for all loop-level positivity. |
| Kojima & Rao, **Triangulation-free Trivialization of 2-loop MHV Amplituhedron** (2020) | [2007.15650](https://arxiv.org/abs/2007.15650) | 🟡 | Source of the one-cell chart and the D⁺/D "maximally positive numerator" structure that labs/track-b/05 verifies symbolically. Positive-infinity trick for multi-loop positivity. |
| Dian, Mazzucchelli & Tellander, **The Two-loop Amplituhedron** (2024) | [2410.11501](https://arxiv.org/abs/2410.11501) | 🔴 | Recent boundary stratification / weighted-positive-geometry analysis of 𝒜₄⁽²⁾; confirms the region definition (each loop one-loop-positive + ⟨ABCD⟩ ≥ 0). Young, single-group. |

## 2-holography-emergence/ — The "Graphics Layer"

Validates: *continuous space and gravity can emerge holographically from entanglement
among boundary degrees of freedom.*

| Paper | arXiv | Tier | What it validates |
|---|---|---|---|
| Maldacena, **The Large N Limit of Superconformal Field Theories** (1997) | [hep-th/9711200](https://arxiv.org/abs/hep-th/9711200) | 🟢 | AdS/CFT — the original holographic duality. A gravitational "bulk" universe is fully encoded on a lower-dimensional boundary. Most-cited paper in high-energy physics. |
| Ryu & Takayanagi, **Holographic Entanglement Entropy** (2006) | [hep-th/0603001](https://arxiv.org/abs/hep-th/0603001) | 🟢 | Entanglement entropy of a boundary region = area of a minimal surface in the bulk. The quantitative dictionary between entanglement and geometry. |
| Swingle, **Entanglement Renormalization and Holography** (2009) | [0905.1317](https://arxiv.org/abs/0905.1317) | 🟢 | Tensor networks (MERA) *are* a discrete emergent spatial geometry. Directly validates the "tensor network → geometric fabric" milestone. |
| Van Raamsdonk, **Building up Spacetime with Quantum Entanglement** (2010) | [1005.3035](https://arxiv.org/abs/1005.3035) | 🟢 | The conceptual thesis: dial entanglement down and spacetime literally disconnects. Entanglement is the glue of space. |
| Almheiri, Dong & Harlow, **Bulk Locality and Quantum Error Correction in AdS/CFT** (2014) | [1411.7041](https://arxiv.org/abs/1411.7041) | 🟢 | Holography works *as* a quantum error-correcting code: bulk operators are logical operators protected by boundary redundancy. |
| Pastawski, Yoshida, Harlow & Preskill, **HaPPY holographic codes** (2015) | [1503.06237](https://arxiv.org/abs/1503.06237) | 🟡 | Explicit buildable toy model where emergent bulk space = the code subspace of a QEC code made of qubits. The strongest single validation of the project's core premise. |
| Czech, Lamprou, McCandlish & Sully, **Integral Geometry and Holography** (2015) | [1505.05515](https://arxiv.org/abs/1505.05515) | 🟡 | Defines *kinematic space* in the holographic sense: an auxiliary geometry where nonlocal boundary data becomes local. Note: this "kinematic space" (space of geodesics) is a **different object** from the kinematic space of momenta in 1711.09102 — the framework document conflates them. |

## 3-qec-topological/ — The "Hardening Layer"

Validates: *topological codes protect quantum information via global/boundary
structure — the same mathematics that appears in holography and TQFT.*

| Paper | arXiv | Tier | What it validates |
|---|---|---|---|
| Kitaev, **Fault-tolerant Quantum Computation by Anyons** (1997) | [quant-ph/9707021](https://arxiv.org/abs/quant-ph/9707021) | 🟢 | The toric code — quantum information stored in *topology*, immune to local errors. Origin of all topological QEC. |
| Fowler, Mariantoni, Martinis & Cleland, **Surface Codes** (2012) | [1208.0928](https://arxiv.org/abs/1208.0928) | 🟢 | The practical engineering guide to surface codes — what real hardware (IBM, Google) actually runs. Milestone 2's textbook. |

## 4-quantum-computing/ — The "Toolchain"

| Paper | arXiv | Tier | What it validates |
|---|---|---|---|
| Peruzzo et al., **A Variational Eigenvalue Solver on a Quantum Processor** (2013) | [1304.3061](https://arxiv.org/abs/1304.3061) | 🟢 | The original VQE paper — the algorithm for Milestone 3 (finding ground states / phase transitions on near-term hardware). |

## 5-tqnn-bridge/ — The Speculative Frontier

| Paper | arXiv | Tier | What it validates |
|---|---|---|---|
| Fields, Glazebrook & Marcianò, **Universal Quantum Computation in TQNNs and Amplituhedron Representation** (2025) | [2509.19772](https://arxiv.org/abs/2509.19772) | 🔴 | The claimed formal correspondence between topological quantum neural networks and amplituhedron-like structures; interprets scattering as computation. Real paper, interesting mathematics, but <1 year old, single research group, not independently confirmed. **Do not load-bear on this.** |

## 6-perception-interface/ — Adjacent: the Hoffman program

Included not as evidence for the framework but as the subject of a test
(Lab 6): Donald Hoffman's claim that conscious-agent Markov dynamics
connect to the amplituhedron via decorated permutations. See
`6-perception-interface/DOSSIER-hoffman.md` for the full assessment.

| Paper | Venue | Tier | What it claims |
|---|---|---|---|
| Hoffman, Singh & Prakash, **The Interface Theory of Perception** (2015) | Psychon. Bull. Rev. | 🟡 | Perception evolves for fitness, not truth; spacetime as species-specific interface. Real math, contested interpretation, legitimate cognitive science. |
| Hoffman & Prakash, **Objects of Consciousness** (2014) | Front. Psychol. | 🔴 | Conscious agents (Markov kernels) as fundamental ontology. Well-defined formalism, no empirical discriminator. |
| Hoffman, Prakash & Prentner, **Fusions of Consciousness** (2023) | Entropy | 🔴 | Agent dynamics → decorated permutations → amplituhedron. Explicitly conjectural in the text; the Def.-2 map uses only communicating-class structure. Lab 6 tests it. |
| Prakash et al., **Fitness Beats Truth in the Evolution of Perception** (2021) | Acta Biotheoretica | 🟡 | The FBT theorem underlying interface theory (previously index-only; now filed). |
| Hoffman, Prakash & Chattopadhyay, **Traces of Consciousness** (2024/2025) | Preprints.org / Trace Institute | 🔴 | The post-Fusions refinement: trace order / trace chains on Markov dynamics, claimed route to empirical tests via scattering data. **Successor map to Def. 2 — the subject of Lab 6b.** |
| **Trace Institute White Paper** (2025) | traceinstitute.org | 🔴 | The program's institutional prospectus (Hoffman's Trace Institute). Context document. |

## 7-magic/ — Track D: magic (non-stabilizerness) and holography

The evidence base for the wedge-resolved magic program — including the
paper whose definitions forced our Phase-1 terminology correction.

| Paper | arXiv | Tier | What it establishes |
|---|---|---|---|
| Leone, Oliviero & Hamma, **Stabilizer Rényi Entropy** (2022) | [2106.12587](https://arxiv.org/abs/2106.12587) | 🟢 | The workhorse computable magic measure (our M₂ engine implements it). Pure-state monotone; mixed-state extension is diagnostic only — the false-positive our twin protocol controls. |
| Cao et al., **Non-trivial Area Operators Require Non-local Magic** (2024) | [2306.14996](https://arxiv.org/abs/2306.14996) | 🟡 | Theory anchor: stabilizer holographic codes cannot host state-dependent area operators / backreaction — magic is structurally required. Motivates magic-injected HaPPY as the minimal backreaction toy. |
| **Gravitational back-reaction is magical** (2024) | [2403.07056](https://arxiv.org/abs/2403.07056) | 🟡 | Companion theory: maps SRE to curvature/area-fluctuation language in holography. |
| **Experimental demonstration of non-local magic in a superconducting quantum processor** (2025) | [2511.15576](https://arxiv.org/abs/2511.15576) | 🟢 | Defines non-local magic = min SRE over local unitaries; closed form −log₂(4P²−6P+3) from reduction purity; 2-qubit hardware measurement. **The definitional source for our Phase-1 correction**: no codes, no wedges, no twin protocol — the boundary of their claims marks our corner. |

---

## What the corpus does NOT validate

For honesty, recorded here permanently:

1. **No paper supports "lateral movement" across a positive geometry to bypass
   physical distance or time.** Positivity *enforces* locality and causality;
   adjacency in kinematic space is descriptive, not traversable.
2. **No paper gives quantum computers privileged ontological access** to
   underlying geometry. They are efficient *simulators* of the relevant math.
3. **The amplituhedron results hold for planar 𝒩=4 SYM** (and cousins), not the
   Standard Model. Extension to realistic theories is open research.

## Reading order (suggested)

1. Van Raamsdonk (2010) — 12 pages, conceptual, the "why"
2. HaPPY (2015) §1–2 — the core toy model
3. Arkani-Hamed & Trnka (2013) — the amplituhedron itself
4. Swingle (2009) — tensor networks as geometry
5. Everything else as the milestones demand it
