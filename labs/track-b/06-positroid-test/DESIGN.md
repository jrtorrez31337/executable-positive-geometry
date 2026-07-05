# Lab 6 (SKETCH) — Load-testing the Hoffman bridge:
# conscious-agent Markov chains → decorated permutations → positroid cells

**Status: design + first-pass skeleton.** The map under test is Definition 2
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

## Interpretive repairs made (to be verified against the full text)

The extracted Definition 2 ("first b > a ...") makes singleton recurrent
classes collide with transient fixed points and can break bijectivity.
The skeleton therefore adopts the natural repair consistent with positroid
conventions: transient state → fixed point decorated as *loop*; singleton
recurrent class → fixed point decorated as *coloop*; multi-state recurrent
class → minimal-cyclic-window rule. The skeleton asserts bijectivity over
the full enumeration and reports any violations. If the full text resolves
the convention differently, only `def2_map()` changes.

## What the skeleton already runs (n = 4)

1. Census: enumerate all 65 decorated permutations of [4]; verify the
   positroid split (1, 15, 33, 15, 1) across k = 0..4 from first
   principles (Gr(0,4) = point; Gr≥0(1,4) cells = 15 nonempty coordinate
   subsets; duality).
2. Exhaustive image: all 50,625 support digraphs with no dead states →
   class partitions → Def.-2 labels. Reports H1 coverage and H2 tables.
3. H3 head-to-head on all 81 pairs of 2-state chains.
4. H4 compression statistics.

## First-pass results (exhaustive, n=4; subject to the convention caveat)

- **H1 partial fail.** Image = 51/65 labels. The entire k=4 sector is
  unreachable — provably: every finite chain has at least one recurrent
  class, and the map forces k = n − R (see H2). The top Grassmannian is
  invisible to conscious agents.
- **H2 trivially true, therefore damning.** k + R = 4 in every one of
  50,625 cases: the "Grassmannian statistic" is exactly (n − number of
  recurrent classes) and nothing more. The label's k carries one integer
  of dynamical content.
- **H3 fail: 1/81.** Kernel tensor products do not correspond to positroid
  direct sums; the single match is the trivial all-fixed-point pair.
- **H4 fail, quantified.** One label (the 4-cycle) absorbs 25,696 of
  50,625 supports — over half of all dynamics — each with a continuum of
  probability assignments. Spectra, mixing times, stationary
  distributions: all invisible.

**Verdict (first pass): the bridge stays 🔴.** As extracted, the Def.-2
map is a coarse invariant of the communicating-class partition wearing a
positroid costume: it borrows the labels and inherits none of the
structure the amplituhedron actually uses (cell dimensions, boundary
poset, canonical forms, BCFW composition). To upgrade, the program would
need a map that reads the kernel itself (not just its support pattern)
and demonstrably intertwines a dynamical operation with a positroid one.

## Not yet done (full lab, if the sketch warrants it)

- Verify Def.-2 conventions against the full paper text (the {1..2n}
  embedding and fusion-simplex construction).
- Dimension refinement of H1: implement cell dimension from the decorated
  permutation (via Le-diagrams or alignment count) and check whether the
  image sees anything beyond a few dimensions.
- The "fusion" (rank-collapse) operation, distinct from combination, and
  its image under the map.
- Write-up as an addendum to the paper if results are crisp either way.
