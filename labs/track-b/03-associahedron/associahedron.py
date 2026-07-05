"""Track B, Lab 3 — the ABHY kinematic associahedron.

The claim (Arkani-Hamed, Bai, He, Yan 2017; corpus 1711.09102): for the
simplest interacting QFT — "bi-adjoint phi^3" scalar theory — the ENTIRE
tree-level amplitude is the canonical form of a polytope, the associahedron,
living directly in the space of momentum invariants (kinematic space).

Kinematic space for n massless particles: Mandelstam invariants
s_ij = (p_i + p_j)^2. The planar variables are

    X_ij = (p_i + p_{i+1} + ... + p_{j-1})^2

— one for each diagonal (i,j) of an n-gon whose edges are the particles.
A planar Feynman diagram of phi^3 = a triangulation of the n-gon; its
propagators are the diagonals used. The ABHY construction intersects the
positive region {all X_ij >= 0} with special constant-shift planes
(s_ij = -c_ij < 0 for non-adjacent i,j < n), and the result is an
(n-3)-dimensional associahedron whose canonical form IS the amplitude:

    n=4: a line segment,  m4 = 1/s + 1/t          (2 diagrams, Catalan(2)=2)
    n=5: a pentagon,      m5 = 5 terms            (5 diagrams, Catalan(3)=5)
    n=6: 3d associahedron, 14 terms               (Catalan(4)=14) ...

Everything below is DERIVED: we impose only masslessness + momentum
conservation + the ABHY constraints, let sympy solve the kinematics, and
then check the geometry/amplitude dictionary by taking residues.
"""

from itertools import combinations

import sympy as sp

x, y = sp.symbols("x y", real=True)
c13, c14, c24 = sp.symbols("c13 c14 c24", positive=True)


def part1_n4() -> None:
    print("1. n=4: the associahedron is a SEGMENT")
    s, c = sp.symbols("s c", positive=True)
    X13, X24 = s, c - s          # ABHY: s + t = c  (u frozen at -c)
    m4 = 1 / X13 + 1 / X24
    print(f"   facets: X13 = s >= 0,  X24 = {X24} >= 0   (segment [0, c])")
    print(f"   m4 = 1/s + 1/t = {sp.together(m4)}")
    print(f"   residues at the two boundaries: "
          f"{sp.residue(m4, s, 0)}, {sp.residue(m4, s, c)}")
    print("   The s-channel and t-channel Feynman diagrams are the two")
    print("   ENDPOINTS of one segment; the amplitude is its canonical form.\n")


def solve_n5_kinematics() -> dict[str, sp.Expr]:
    """Impose masslessness sum rules + ABHY constraints, solve for all s_ij."""
    S = {(i, j): sp.Symbol(f"s{i}{j}") for i, j in combinations(range(1, 6), 2)}
    known = {S[1, 2]: x, S[1, 3]: -c13, S[1, 4]: -c14, S[2, 4]: -c24, S[4, 5]: y}

    # sum_{j != i} s_ij = 0 for each massless particle i (from p_i . P = 0).
    eqs = []
    for i in range(1, 6):
        total = sum(S[tuple(sorted((i, j)))] for j in range(1, 6) if j != i)
        eqs.append(total.subs(known))
    unknowns = [v for v in S.values() if v not in known]
    sol = sp.solve(eqs, unknowns, dict=True)[0]

    def val(i, j):
        sym = S[tuple(sorted((i, j)))]
        return known.get(sym, sol.get(sym, sym))

    X = {
        "X13": sp.expand(val(1, 2)),
        "X14": sp.expand(val(1, 2) + val(1, 3) + val(2, 3)),
        "X24": sp.expand(val(2, 3)),
        "X25": sp.expand(val(2, 3) + val(2, 4) + val(3, 4)),
        "X35": sp.expand(val(3, 4)),
    }
    # Cross-check: X25 = (p2+p3+p4)^2 must equal (p1+p5)^2 = s15.
    assert sp.simplify(X["X25"] - val(1, 5)) == 0, "momentum conservation broken"
    return X


def part2_n5() -> None:
    print("2. n=5: sympy solves the kinematics -> the PENTAGON's five facets")
    X = solve_n5_kinematics()
    for name, expr in X.items():
        print(f"   {name} = {expr} >= 0")
    print("   Two coordinates (x = X13, y = X14), five boundary lines: a")
    print("   pentagon carved out of kinematic space by momentum conservation.\n")

    print("   Vertices at c13 = c14 = c24 = 1  (vertex <-> planar Feynman diagram):")
    numeric = {c13: 1, c14: 1, c24: 1}
    facets = list(X.items())
    cycle = ["X13", "X14", "X24", "X25", "X35"]   # cyclic facet order
    Xn = {k: v.subs(numeric) for k, v in X.items()}
    for a, b in zip(cycle, cycle[1:] + cycle[:1]):
        vert = sp.solve([Xn[a], Xn[b]], [x, y], dict=True)[0]
        print(f"     {a} ∩ {b} -> (x,y) = ({vert[x]}, {vert[y]})"
              f"   diagram with propagators 1/({a}·{b})")
    print()

    print("3. The amplitude: one term per vertex (= per Feynman diagram)")
    terms = [("X13", "X14"), ("X14", "X24"), ("X24", "X25"),
             ("X25", "X35"), ("X35", "X13")]
    m5 = sum(1 / (X[a] * X[b]) for a, b in terms)
    num, den = sp.fraction(sp.cancel(sp.together(m5)))
    print(f"   m5 numerator   : {sp.factor(num)}")
    print(f"   m5 denominator : {sp.factor(den)}")
    print("   The denominator is EXACTLY the product of the five facets: the")
    print("   form has poles on the pentagon's boundary and nowhere else.\n")

    print("4. Residue check: boundary of the form = form of the boundary")
    # Facet X13 (x=0): edge runs in y over [0, c14+c24].
    res13 = sp.simplify(sp.limit(x * m5, x, 0))
    edge13 = sp.together(1 / y - 1 / (y - (c14 + c24)))
    print(f"   Res on X13=0 : {sp.together(res13)}")
    print(f"   edge form    : {edge13}"
          f"   equal? {sp.simplify(res13 - edge13) == 0}")
    # Facet X24 (x = y + c13): slanted edge, y in [0, c14].
    res24 = sp.simplify(sp.limit((y + c13 - x) * m5, x, y + c13))
    edge24 = sp.together(1 / y - 1 / (y - c14))
    match = sp.simplify(res24 - edge24) == 0 or sp.simplify(res24 + edge24) == 0
    print(f"   Res on X24=0 : {sp.together(res24)}")
    print(f"   edge form    : {edge24}   equal (up to orientation)? {match}")
    print("   Residue at a physical pole = amplitude of the factorized")
    print("   sub-process = canonical form of the facet. Locality and")
    print("   unitarity are READ OFF the boundary structure — they were")
    print("   never put in.\n")

    print("5. Feynman diagrams counted by geometry (Catalan numbers):")
    for n in (4, 5, 6, 7, 8):
        print(f"   n={n}: associahedron has {sp.catalan(n - 2)} vertices "
              f"= number of planar phi^3 diagrams")


if __name__ == "__main__":
    part1_n4()
    part2_n5()
