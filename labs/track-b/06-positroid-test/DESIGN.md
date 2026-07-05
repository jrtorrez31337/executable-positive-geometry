# Lab 6 — Load-testing the Hoffman bridge:
# conscious-agent Markov chains → decorated permutations → positroid cells

**Status: COMPLETE at n=4.** Conventions verified against the full text
(Definitions 1–3, pp. 17–21) and the implementation validated by
reproducing the paper's own 9-state worked example exactly, in both its
all-recurrent and transient variants. The map under test is Definition 2
of Hoffman–Prakash–Prentner, *Fusions of Consciousness* (Entropy 2023;
`corpus/6-perception-interface/`): a Markov chain's decorated permutation is
built from its communicating-class structure (transient states become fixed
points; each recurrent state maps to the endpoint of the minimal cyclic
window covering its class). The paper conjectures this connects agent
dynamics to the amplituhedron, whose cells are labeled by decorated
permutations (Postnikov positroid stratification).

**The principle of the test:** a shared labeling set is not a shared
structure. Decorated permutations in the Grassmannian carry geometric
data — the k-statistic (which Gr(k,n)), cell dimension, the boundary
poset, canonical forms. For the bridge to carry any weight, the Def.-2 map
must *inherit* structure, not just borrow names. Each hypothesis below is
something the bridge needs; each is machine-checkable.

## Hypotheses and falsification criteria

**H1 (Coverage).** The image of the Def.-2 map over all chains on n states
covers positroid labels broadly (in particular, cells of every dimension
and several k-sectors). *Falsified if* the image is confined to a
measure-zero / highly degenerate subfamily of the 65 (n=4) decorated
permutations.

**H2 (Statistic meaning).** The Grassmannian k-statistic of the image
permutation tracks some dynamical invariant of the chain (e.g., number of
recurrent classes, transient count). *Note:* even if true, this is weak
evidence — k must then be shown to matter dynamically the way it matters
geometrically (it selects which Grassmannian!).

**H3 (Compositionality).** Hoffman's combination operation (kernel tensor
product) corresponds to a known positroid operation on decorated
permutations (the natural candidate: direct sum). At n1=n2=2 both the
tensor product (2×2) and direct sum (2+2) land in n=4, so they can be
compared head-on. *Falsified if* dp(P1 ⊗ P2) bears no systematic relation
to dp(P1) ⊕ dp(P2).

**H4 (Information retention).** The map retains dynamical information
beyond the communicating-class partition. *This is falsified by
inspection of Definition 2 itself* — the map never reads a transition
probability — but the skeleton demonstrates it explicitly: chains with
identical support and wildly different spectra/mixing times receive
identical labels, and even different supports with the same class
partition collapse together. The lab quantifies the compression: how many
dynamically distinct chains per label.

## Verdict rule

The bridge earns 🟡 only if H1–H3 all pass and H4's compression is shown
to preserve at least the data the amplituhedron actually uses. Any
failure leaves it 🔴 with a precise, citable reason.

## Conventions (verified against the full text)

Definition 2, exactly as published: transient state → σ(a) = a;
**absorbing state (singleton recurrent class) → σ(a) = a + n** (stated
explicitly in the paper); multi-state recurrent class → minimal inclusive
cyclic window rule. The k-statistic counts anti-exceedances
(σ(a) > n). Validation: the paper's 9-state example
(cycles (158)(2)(34)(6)(79) → [8,11,4,12,10,15,9,14,16], and its
transient-2 variant) is reproduced exactly by `def2_affine()`.

**Correction from the first-pass sketch:** the sketch (commit dc36e95)
had the fixed-point decorations inverted (transient counted toward k,
absorbing not). Under the verified conventions the unreachable sector is
**k = 0, not k = 4**: every chain has at least one recurrent class and
each recurrent class contributes ≥ 1 anti-exceedance, so k ≥ 1 always;
meanwhile the identity chain (all states absorbing) reaches the top cell
k = 4. All other findings survived the correction unchanged. We record
this deliberately: reading the primary source flipped a finding.

## Results (exhaustive, n = 4; implementation validated against the paper)

- **H1 partial fail.** Image = 51/65 labels; the k = 0 bottom cell is
  provably unreachable; 5 of 15 k=1 labels and 8 of 33 k=2 labels are
  never attained. Coverage by k: image {1: 10, 2: 25, 3: 15, 4: 1}
  vs census {0: 1, 1: 15, 2: 33, 3: 15, 4: 1}.
- **H2 exact, and exactly class-counting.** In all 50,625 cases,
  k = (#recurrent states) − (#multi-state recurrent classes). The
  statistic that selects the Grassmannian is pure class arithmetic — no
  spectral, metric, or probabilistic content.
- **H3 fail: 1/81.** Kernel tensor products do not correspond to
  positroid direct sums (sole match: the doubly-degenerate absorbing
  pair). Example: two copies of the "everything falls into state 0"
  2-chain compose to upper set {0} where the direct sum requires {0, 2}.
- **H4 fail, quantified.** The 4-cycle label absorbs 25,696 of 50,625
  supports (>50% of all dynamics), each with a continuum of probability
  assignments. Def. 2 reads no transition probability: spectra, mixing
  times, and stationary measures are invisible to the label.

**Verdict: the bridge stays 🔴, now without convention caveats.** The
published map is a coarse invariant of the communicating-class partition
wearing a positroid costume: it borrows the labels and inherits none of
the structure the amplituhedron uses (cell dimensions, boundary poset,
canonical forms, BCFW composition). To upgrade, the program needs a map
that reads the kernel itself — the paper's own Markov-polytope cell
decomposition (its Figure 11) is richer than Def. 2 and would be the
natural place to start — and a demonstrated intertwining of a dynamical
operation with a positroid one.

## Possible extensions

- Cell-dimension refinement of H1 (Le-diagram / alignment count): which
  dimensions does the image see within each k-sector?
- The fusion operation proper (flow to idempotent kernels, rank
  collapse) as a map on labels, distinct from combination.
- The paper's Definition 3 (decorated permutations of arbitrary graphs)
  faces the same H2–H4 objections; a one-page addendum could state this.
- n = 5, 6 scaling of coverage fractions.
