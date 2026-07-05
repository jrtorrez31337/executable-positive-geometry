"""Track B, Lab 4 — the amplituhedron proper.

PART 1 — G+(2,4) and Parke-Taylor.
The MHV gluon amplitude (Parke-Taylor 1986):
    A(1-,2-,3+,4+) = <13>^4 / (<12><23><34><41>)
The cyclic denominator is not an accident of Feynman algebra: it is the
canonical form of the positive Grassmannian G+(2,4). Gauge-fixing columns
1 and 3, positivity of ALL minors reduces to a,b,c,d > 0 — a positive
orthant — whose canonical form is dlog a ^ dlog b ^ dlog c ^ dlog d.
Rewritten in minors, the denominator is EXACTLY p12 p23 p34 p14: the
Parke-Taylor cyclic product. (The <13>^4 numerator carries the helicity
data — supersymmetry bosonizes it; the geometry owns the poles.)

PART 2 — the NMHV amplituhedron A(n=6, k=1, m=4).
In momentum-twistor space the 6-point NMHV amplitude of N=4 super
Yang-Mills is the canonical form of a CYCLIC POLYTOPE: six vertices
Z1..Z6 in P^4 (positive = on a moment curve). Its canonical form is a sum
of simplex forms — the "R-invariants" / five-brackets:

  [abcde] = <abcde>^4 <Y d^4 Y> / (<Yabcd><Ybcde><Ycdea><Ydeab><Yeabc>)

Two different triangulations (BCFW recursions) of the same polytope:

  R1 = [12345] + [12356] + [13456]      (triangulated from vertex 1)
  R2 = [23456] + [12456] + [12346]      (triangulated from vertex 2)

R1 = R2 is the six-term NMHV identity — famously mysterious as an
algebraic fact, self-evident as geometry. We verify it in EXACT rational
arithmetic, watch the spurious poles blow up term-by-term while the sum
stays finite, and confirm that the polytope's true facets (Gale evenness:
<Y i i+1 j j+1>) are exactly the physical poles.
"""

import random
from itertools import combinations

import sympy as sp


# ─── Part 1: G+(2,4) -> Parke-Taylor ─────────────────────────────────────────

def part1() -> None:
    a, b, c, d = sp.symbols("a b c d", positive=True)
    C = sp.Matrix([[1, a, 0, -c], [0, b, 1, d]])

    def minor(i, j):
        return sp.expand(C[:, i].col_join(sp.zeros(0, 1)).T
                         .row_join(C[:, j].T).T.det()
                         if False else
                         C[0, i] * C[1, j] - C[0, j] * C[1, i])

    p = {(i, j): minor(i, j) for i, j in combinations(range(4), 2)}
    print("1. G+(2,4), gauge-fixed:  C = [[1,a,0,-c],[0,b,1,d]]")
    for k, v in p.items():
        print(f"   p{k[0] + 1}{k[1] + 1} = {v}")
    pluck = sp.expand(p[0, 1] * p[2, 3] - p[0, 2] * p[1, 3] + p[0, 3] * p[1, 2])
    print(f"   Plucker relation: {pluck}")
    print(f"   all minors > 0  <=>  a,b,c,d > 0 (p24 = ad+bc comes free):")
    print(f"   G+(2,4) is a positive orthant in disguise.")
    cyc = sp.simplify(p[0, 1] * p[1, 2] * p[2, 3] * p[0, 3])
    print(f"   canonical form of orthant: da db dc dd/(a b c d)")
    print(f"   Parke-Taylor product p12*p23*p34*p14 = {cyc}  ->  SAME THING.")
    print("   The MHV denominator <12><23><34><41> IS the canonical form of")
    print("   the positive Grassmannian. Residue at p12=b->0 (particles 1,2")
    print("   collinear) = canonical form of the boundary: physical")
    print("   singularities = boundaries, at the Grassmannian level.\n")


# ─── Part 2: the NMHV amplituhedron A(6,1,4) ─────────────────────────────────

T_VALUES = (1, 2, 3, 5, 7, 11)          # moment curve parameters, ordered
Z = {i + 1: sp.Matrix([sp.Integer(t) ** k for k in range(5)])
     for i, t in enumerate(T_VALUES)}   # Z_i = (1, t, t^2, t^3, t^4)


def br(Y: sp.Matrix, idxs: tuple[int, ...]) -> sp.Rational:
    """<Y Z_a Z_b Z_c Z_d> with labels in the given order."""
    return sp.Matrix.hstack(Y, *(Z[i] for i in idxs)).det()


def five_bracket(Y: sp.Matrix, s: tuple[int, ...]) -> sp.Rational:
    """Canonical form of the simplex with vertices Z_s (sorted labels)."""
    s = tuple(sorted(s))
    num = sp.Matrix.hstack(*(Z[i] for i in s)).det() ** 4
    den = sp.Integer(1)
    for omit in s:
        den *= br(Y, tuple(i for i in s if i != omit))
    return num / den


def interior_Y(rng: random.Random) -> sp.Matrix:
    lam = [sp.Rational(rng.randint(1, 100), rng.randint(1, 100)) for _ in range(6)]
    return sum((l * Z[i + 1] for i, l in enumerate(lam)), sp.zeros(5, 1))


TRI_1 = [(1, 2, 3, 4, 5), (1, 2, 3, 5, 6), (1, 3, 4, 5, 6)]
TRI_2 = [(2, 3, 4, 5, 6), (1, 2, 4, 5, 6), (1, 2, 3, 4, 6)]


def part2() -> None:
    rng = random.Random(42)

    print("2. A(6,1,4): six-term NMHV identity, exact rational arithmetic")
    for trial in range(3):
        Y = interior_Y(rng)
        r1 = sum(five_bracket(Y, s) for s in TRI_1)
        r2 = sum(five_bracket(Y, s) for s in TRI_2)
        print(f"   random interior Y #{trial + 1}:  R1 - R2 = {sp.nsimplify(r1 - r2)}"
              f"   (R1 = {sp.Float(r1, 6)})")
    print("   Two BCFW triangulations, one canonical form. As algebra this is")
    print("   the 'mysterious' six-term identity; as geometry it is nothing.\n")

    print("3. Spurious pole <Y1235> -> 0: terms diverge, the amplitude doesn't")
    Y0 = Z[1] + Z[2] + Z[3] + Z[5]                     # on the seam <Y1235>=0
    print(f"   {'eps':>8} {'[12345]':>15} {'[12356]':>15} {'[13456]':>12} {'R1 total':>12}")
    for k in (2, 4, 6):
        eps = sp.Rational(1, 10 ** k)
        Y = Y0 + eps * Z[4]
        terms = [five_bracket(Y, s) for s in TRI_1]
        print(f"   {f'1e-{k}':>8} "
              f"{sp.Float(terms[0], 6):>15} {sp.Float(terms[1], 6):>15} "
              f"{sp.Float(terms[2], 6):>12} {sp.Float(sum(terms), 6):>12}")
    print("   The two divergent terms cancel to machine-perfect finiteness")
    print("   (exact rationals — the cancellation is identically true). The")
    print("   seam <Y1235>=0 slices the polytope's INTERIOR: a triangulation")
    print("   artifact, not a boundary. Same mechanism as Lab 2's square,")
    print("   now in P^4 with the real N=4 SYM amplitude.\n")

    print("4. Facets = physical poles (Gale evenness for cyclic polytopes)")
    predicted = set()
    for i in range(1, 7):
        for j in range(1, 7):
            s = frozenset({i, i % 6 + 1, j, j % 6 + 1})
            if len(s) == 4:
                predicted.add(s)
    # Exact test, no sampling: the hyperplane through 4 vertices is a FACET
    # iff the remaining two vertices sit on the SAME side of it.
    facets, seams = set(), set()
    for s in combinations(range(1, 7), 4):
        k1, k2 = (k for k in range(1, 7) if k not in s)
        same_side = sp.sign(br(Z[k1], s)) == sp.sign(br(Z[k2], s))
        (facets if same_side else seams).add(frozenset(s))
    print(f"   facets (remaining 2 vertices on same side) : {len(facets)}")
    print(f"   seams  (hyperplane separates the vertices) : {len(seams)}")
    print(f"   Gale-evenness prediction {{i,i+1,j,j+1}}: {len(predicted)}"
          f"   -> exact match? {facets == predicted}")
    print(f"   {{1,2,3,5}} classified as seam? {frozenset({1, 2, 3, 5}) in seams}")
    print("   Nine facets, all of the form <Y i i+1 j j+1>: precisely the")
    print("   propagator poles ((p_i+...+p_j-1)^2 -> 0) of the physical")
    print("   amplitude. The polytope knows which singularities are real.")


if __name__ == "__main__":
    part1()
    part2()
