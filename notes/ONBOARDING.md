# Onboarding a science agent to Executable Positive Geometry (EPG)

**Written 2026-07-23 by quant-phy (Ariadne) + codex-science (Tobin), to onboard
agy-science and any future teammate.** Read this end-to-end before your first
contribution. If anything here is stale, fix it — this doc is part of the work.

---

## 1. What EPG is (the one rule that defines everything)

Executable Positive Geometry is a verification-first research program in quantum
physics and the geometry beneath it (scattering amplitudes, positive geometries,
holographic codes, quantum information, the arrow of time). The core rule:

> **Every claim is EXECUTED — proven exactly, simulated, or measured on real IBM
> quantum hardware — never merely cited. A claim does not stand until a second
> (now third) agent independently reproduces or narrows it.**

We are a small swarm of AI research agents under human direction (Jon), running on
Subnet345's Plexus substrate. The point is not to sound impressive; it is to be
*checkable*. Refuted predictions are kept on the record beside confirmations.

- Public repo: `github.com/jrtorrez31337/executable-positive-geometry` (MIT).
- Canonical checkout: `/home/jon/agents/science` (this is the one that pushes;
  work here or converge here).
- Correspondence / author address: `epg@subnet345.com` (shared team address).

## 2. The conventions (non-negotiable — this is why the work is trusted)

1. **Hand-in-hand adversarial model.** For any substantive step: co-scope, set
   pre-registered predictions *before* running, split the build, cross-check
   tightly, and all involved agents sign the verdict. One agent builds, another
   independently reproduces and *tries to break it*. This has caught real errors
   repeatedly (see §6) — it is the reason claims hold.
2. **Verify-before-add (corpus).** Never add a paper without verifying its arXiv
   ID against the actual title/abstract. Tier every source: 🟢 established /
   🟡 model-dependent-or-toy / 🔴 recent-speculative. Cite load-bearingly only at
   the tier the evidence supports.
3. **Honest scope.** Tag theorem vs conjecture explicitly. State limitations in
   the artifact itself. When a prediction fails, say so and diagnose it; when you
   narrow a claim, record the narrowing. Do not let a plausible-sounding result
   pass as a proven one — our discipline exists to counter exactly that bias.
4. **Commit attribution.** Each agent self-attributes via a `commit-msg` hook that
   rewrites the generic model trailer to `Co-Authored-By: <you>-agent`. You must
   install your own (see §5). **Strip-and-replace, do not append** — the parser
   reads the *last* `Co-Authored-By`, so an appended agent trailer with the model
   trailer still below it silently reverts to `claude-code`.
5. **Coordination is on the plexus bus.** @-mention teammates on a post
   (`POST /api/v1/messages`, channel `handoff`). Keep an armed Monitor so mentions
   surface (see §5). Ack-discipline: substantive content only, silence otherwise.

## 3. Current state (as of 2026-07-23)

- **Corpus:** 50 verified papers across 9 pillars (`corpus/README.md` is the
  annotated index with tiers; `corpus/refs.bib` + `corpus/fetch_corpus.sh`
  reproduce it). PDFs are gitignored; the index/bib/fetch are tracked.
- **Labs:** 55 Python labs across 6 tracks (`labs/`): Track A quantum
  (Bell/CHSH → QEC → VQE/emergence), Track B positive geometry (Plücker →
  associahedron → amplituhedron → loop amplituhedron), Track C time (Page-Wootters,
  arrow-on-hardware, modular flow, Krylov ignition), Track D magic (wedge magic,
  SYK non-stabilizerness, cosmological magic), plus capstones (HaPPY tile/network,
  holonomy, self-wedge, spawn-object).
- **Four research notes** in `paper/` (all compile with tectonic, all
  swarm-authored, all hardware/exact-backed): `note-two-loop` (2-loop MHV
  amplituhedron assembly), `note-cosmo-magic` (magic of cosmological particle
  production + dS horizon), `note-arrow-holonomy` (time reversal = the unreachable
  inside-twist), `note-arrow-origins` (uniform smuggled-direction survey of six
  arrow-origin mechanisms). Blocked only on arXiv endorsement (Jon's lane).
- **The arrow-of-time program is complete** and documented: see
  `notes/ARROW-EMERGENCE-PROGRAM.md`, `notes/ARROW-ORIGINS-SCORECARD.md`,
  `notes/TIME-ARROW-TRACKER.md`. Headline: an arrow can *ignite* from a chaotic
  spectrum (Krylov complexity, `labs/track-c-time/krylov_ignition.py`), cleanly
  separated from the state-inherited thermal arrow. The deep Janus↔algebraic
  unification stays an open conjecture with a named test (DSSYK spectral bridge).
- **Frontier map:** `corpus/FRONTIER-2026.md` (three fronts + a Front-4 holographic-
  bound/gravitational-algebras section) and `corpus/GAP-ANALYSIS.md`.

## 4. Open research directions (pick-one candidates, honestly tiered)

1. **Reproduction / refutation** of a recent NISQ "quantum gravity" claim (e.g.
   sparse-SYK wormhole teleportation) — highest-value *real* contribution, plays
   to our verification strength.
2. **Wedge-geography of magic** — the corner we demonstrably own (Track D).
3. **DSSYK spectral bridge** — the arrow-program's open conjecture; most alive,
   likely lands at "suggestive."
4. **All-n two-loop amplituhedron conjecture** — real but expert-crowded.

## 5. First steps to plug in (your onboarding checklist)

1. Read, in order: `CLAUDE.md` (role + house style), `README.md`,
   `corpus/README.md`, `corpus/FRONTIER-2026.md`, then the four `paper/note-*.pdf`.
2. Reproduce one result end-to-end to confirm your environment (e.g. run
   `labs/track-c-time/modular_flow.py` or `krylov_ignition.py` — exact, no
   hardware needed). Reproduction is the entry ritual here.
3. **Bus + monitor** (see `monitor-howto.md`, `plexus-demo.md`): arm your
   mention-gated Monitor, verify presence (`events_consumer_count >= 1`) and a
   round-trip probe. Coordinate via `@`-mentions on channel `handoff`.
4. **Commit attribution** (see codex-science's setup): install
   `.git/hooks/commit-msg` that reads `git config plexus.agentId`
   (set it to `agy-science-agent`) and STRIP-replaces the generic model trailer
   with your agent trailer. Verify: `git show -s --format='%(trailers:key=Co-Authored-By)' HEAD`.
5. Tell us your model and where your strengths are, so we can decide your role —
   a third *independent* perspective for triangulation, or a specialist lane.

## 6. Why the discipline is not bureaucracy — real errors it caught

- A single-seed plateau overclaim (P2 dynamics) — caught by a teammate's SEMs, a
  sign-flip crossover the excited first pass missed.
- A wrong-sign proto-area prediction (Track D Phase 3) — the failed prediction was
  diagnosed (missing recovered-matter term) and fixed in 3b.
- A resource-theory mislabel (cosmological fermion "magic" vs non-Gaussianity).
- A finite-N linear-`b_n` sub-prediction (Krylov ignition) — failed and stayed
  failed; the honest signature is sustained complexity, not a linear slope.
- A per-qubit-vs-uniform Clifford error in the arrow-holonomy note — caught in
  adversarial review before it went out.

Every one of these was a plausible-sounding claim that a second agent's skeptical
reproduction corrected. That is the job. Welcome to it.
