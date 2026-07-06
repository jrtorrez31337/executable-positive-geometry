# Dossier: Donald D. Hoffman and the Interface/Conscious-Agents Program

*Compiled 2026-07-05. Facts verified against his UCI page, the papers in this
directory, and a PMC full-text extraction of the key construction. Tier labels
follow the corpus convention (🟢 established / 🟡 serious-but-contested /
🔴 speculative).*

## Who

Donald David Hoffman — professor emeritus, Department of Cognitive Sciences,
University of California, Irvine. Cognitive psychologist (MIT PhD, 1983,
computational psychology under Whitman Richards); career work on visual
perception, object recognition, and the evolution of perceptual systems.
Public profile via the book *The Case Against Reality* (2019) and extensive
podcast circuit appearances. Note: frequently misspelled "Huffman" (that's
the coding-theory David Huffman, unrelated).

## The program, in three layers

**Layer 1 — Interface Theory of Perception (🟡).**
Claim: natural selection optimizes perception for *fitness payoffs*, not
veridicality; perceptual categories are a species-specific user interface
("desktop icons"), not approximations of objective structure. Supported by
evolutionary-game-theory simulations and the "Fitness-Beats-Truth" (FBT)
theorem. This layer is real, published cognitive science
(`2015-...interface-theory-of-perception.pdf`) with legitimate mathematical
content and legitimate critics (the standard objection: fitness functions
are themselves defined over world states, so "truth goes extinct" depends
on how veridicality is formalized). Serious, contested, respectable.

**Layer 2 — Conscious Realism / Conscious Agents (🔴).**
Claim: consciousness is fundamental; "conscious agents" (Markovian kernels
on experience spaces) are the ontology, and physical objects — including
brains and spacetime — are interface artifacts of agent interactions
(`2014-...objects-of-consciousness.pdf`). This is metaphysics with a
mathematical skin: the Markov formalism is well-defined, but nothing
currently distinguishes it empirically from ordinary physicalism.

**Layer 3 — The Amplituhedron Bridge (🔴, explicitly conjectural).**
Claim (`2023-...fusions-of-consciousness.pdf`): the asymptotic dynamics of
conscious-agent Markov chains are summarized by *decorated permutations*,
the same combinatorial objects that label positroid cells of the positive
Grassmannian and the amplituhedron; hence agent dynamics may "project" to
the structures from which physicists recover spacetime and scattering.
The paper itself frames this as incomplete and invited-for-development;
Hoffman's public talks present it with more confidence than the text does.

## The load-bearing construction (extracted verbatim from Fusions of Consciousness, Def. 2)

> "If a is transient, set σ(a)=a. If a is recurrent, let σ(a) be the first
> element b>a of {1,…,2n}, such that the sequence (a,a+1…,b) between a and
> b contains the communicating class of a."

I.e. the decorated permutation assigned to a Markov chain depends **only on
the partition of states into communicating classes and their
transient/recurrent status** — all transition probabilities, spectral data,
and mixing behavior are discarded. Fusion of agents is kernel tensor
product; stationarity (Q² = Q) collapses rank and "fuses" qualia.

## Relationship to this repository

Convergences: the interface metaphor is essentially this project's
"emergent screen output" framing; both programs cite the same physics
(spacetime non-fundamentality, the amplituhedron); the combinatorial claim
about decorated permutations labeling positroid cells is *correct
mathematics* (Postnikov), and those are precisely the objects of our
Track B labs.

Divergence: direction of inference. This project verified physics-side
claims by execution and never inferred ontology; Hoffman posits ontology
and gestures at the physics. The bridge's weak link is precise: **a shared
labeling set is not a shared structure.** Decorated permutations in the
Grassmannian carry geometric freight (positivity, cell dimension, boundary
poset, canonical forms); Definition 2 produces label-compatible objects
with no demonstrated inheritance of any of that freight.

## What would change the assessment

Lab 6 (`labs/track-b/06-positroid-test/`) operationalizes this: if the
Def.-2 map hit positroid cells in a structure-respecting way (image
covering cells of all dimensions with the k-statistic tracking a dynamical
invariant), if agent fusion corresponded to a known positroid operation,
and if the map retained dynamical information beyond the class partition,
the bridge would earn 🟡. Current expectation, stated before running the
full tests: the map is highly lossy and structurally degenerate (it cannot
see probabilities at all), so the bridge as published cannot carry physics.
That expectation is falsifiable by the lab itself.

## Papers in this directory

| File | Venue | Tier |
|---|---|---|
| `2015-hoffman-singh-prakash-interface-theory-of-perception.pdf` | Psychon. Bull. Rev. 22:1480 | 🟡 |
| `2014-hoffman-prakash-objects-of-consciousness.pdf` | Front. Psychol. 5:577 | 🔴 |
| `2023-hoffman-prakash-prentner-fusions-of-consciousness.pdf` | Entropy 25(1):129 | 🔴 |

Index-only (paywalled/book, not downloaded): *The Case Against Reality*
(Norton, 2019); Prakash et al., "Fitness Beats Truth in the Evolution of
Perception," Acta Biotheoretica 69:319 (2021).

---

## Update 2026-07-06: the program moved — Traces of Consciousness

After Lab 6 audited the Fusions Definition 2 (2023), we discovered the
program's successor paper: **Traces of Consciousness** (Hoffman, Prakash
& Chattopadhyay, Preprints.org Oct 2024; revised 2025), introducing a
"trace order" / "trace chain" construction on Markov dynamics — the
refined observation machinery Fusions promised. Notable shifts: the
third author is now an accelerator physicist (Chattopadhyay); the paper
claims a route to EMPIRICAL TESTS via scattering data; and the program
has institutionalized as the Trace Institute (traceinstitute.org, white
paper filed here). Lab 6's verdict stands for the 2023 map; the 2024/25
map requires its own audit (Lab 6b) before any claim about the current
program. Standing structural headwind, sharpened by our Track D work:
"non-trivial area operators require non-local magic" (JHEP 11(2024)105)
— classical Markov substrates sit even further from the required
non-stabilizerness than stabilizer QM does; any map from trace chains to
physics-bearing geometry must manufacture magic from classical
stochastic dynamics, an unaddressed resource-theoretic gap.
