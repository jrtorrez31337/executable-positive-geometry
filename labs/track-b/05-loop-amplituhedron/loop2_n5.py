"""Track B, Lab 5c — POSTULATE TEST: the two-loop n=5 MHV integrand.

Postulate P1 ("maximal positivity assembles"): the 2-loop n=5 MHV
amplituhedron decomposes into 9 composite cells — ordered pairs of the
three 1-loop sign-flip cells (Lab 5b) — and its integrand is

    M2 = sum over 9 pairs of  K_c1(A,B) * K_c2(C,D) * D+_pair / D_pair

where K_c are the (bracket-native, Lab 5b-verified) Kermit factors,
D_pair = <ABCD> expressed in the pair's positive chart, and D+_pair is
the sum of its positive monomials (the n=4 "maximally positive
numerator" pattern, which we verified exactly in Lab 5).

Tests:
  T1  structure: compute D_pair symbolically for all 9 pairs; classify
      (multilinearity, sign-split), check the sign pattern is
      independent of the choice of positive Z's, and regress the n=4
      single-pair case against Lab 5's known polynomial.
  T3  assembly: exact-rational seam tables. P1 requires the 9-term sum
      to stay finite on the spurious seams <AB13>, <AB14> while
      individual terms diverge — and to DIVERGE on the physical mutual
      pole <ABCD> -> 0.
Falsification: any non-sign-stable D, any seam where the sum diverges,
or finiteness at the physical pole kills or modifies P1 (DESIGN notes
the anticipated failure mode: quasi-linearity on mixed pairs).
"""

from itertools import product

import sympy as sp

N = 5
CELLS = [(2, 3), (2, 4), (3, 4)]


def make_Z(ts):
    return {i + 1: sp.Matrix([sp.Integer(t) ** p for p in range(4)])
            for i, t in enumerate(ts)}


Z = make_Z((1, 2, 3, 5, 8))


def det4(*cols):
    return sp.Matrix.hstack(*cols).det()


def kermit(A, B, i, j, Zs):
    num = (det4(A, Zs[1], Zs[i], Zs[i + 1]) * det4(B, Zs[1], Zs[j], Zs[j + 1])
           - det4(B, Zs[1], Zs[i], Zs[i + 1]) * det4(A, Zs[1], Zs[j], Zs[j + 1])) ** 2
    den = sp.Integer(1)
    for p, q in ((1, i), (i, i + 1), (1, i + 1), (1, j), (j, j + 1), (1, j + 1)):
        den *= det4(A, B, Zs[p], Zs[q])
    return num / den


def chart_line(cell, syms, Zs):
    i, j = cell
    x, w, y, z = syms
    return Zs[1] + x * Zs[i] + w * Zs[i + 1], -Zs[1] + y * Zs[j] + z * Zs[j + 1]


def split_pos(poly):
    """(positive part, negative part) by monomial coefficient sign."""
    pos = sum(c * m for m, c in poly.as_coefficients_dict().items() if c > 0)
    neg = sum(-c * m for m, c in poly.as_coefficients_dict().items() if c < 0)
    return sp.expand(pos), sp.expand(neg)


V1 = sp.symbols("x1 w1 y1 z1", positive=True)
V2 = sp.symbols("x2 w2 y2 z2", positive=True)


def pair_D(c1, c2, Zs):
    A, B = chart_line(c1, V1, Zs)
    C, D = chart_line(c2, V2, Zs)
    return sp.expand(det4(A, B, C, D))


def t1_structure():
    print("T1. Structure of D = <ABCD> in all 9 composite-cell charts")
    # n=4 regression against Lab 5 (Z = identity, single cell (2,3)):
    Z4 = {i + 1: sp.Matrix(sp.eye(4))[:, i] for i in range(4)}
    A, B = (Z4[1] + V1[0] * Z4[2] + V1[1] * Z4[3],
            -Z4[1] + V1[2] * Z4[3] + V1[3] * Z4[4 - 0] if False else None)
    x1, w1, y1, z1 = V1
    x2, w2, y2, z2 = V2
    A = Z4[1] + x1 * Z4[2] + w1 * Z4[3]
    B = -Z4[1] + y1 * Z4[3] + z1 * Z4[4]
    C = Z4[1] + x2 * Z4[2] + w2 * Z4[3]
    D = -Z4[1] + y2 * Z4[3] + z2 * Z4[4]
    d4 = sp.expand(det4(A, B, C, D))
    lab5 = sp.expand((z1 - z2) * (w1 * x2 - w2 * x1)
                     + (x1 - x2) * (y1 * z2 - y2 * z1))
    print(f"   n=4 regression vs Lab 5 polynomial: "
          f"{sp.simplify(d4 - lab5) == 0}")

    Zalt = make_Z((2, 3, 7, 11, 20))
    results = {}
    all_ok = True
    for c1, c2 in product(CELLS, repeat=2):
        d = pair_D(c1, c2, Z)
        dalt = pair_D(c1, c2, Zalt)
        multilin = all(sp.degree(d, v) <= 1 for v in (*V1, *V2))
        pos, neg = split_pos(d)
        pos_a, _ = split_pos(dalt)
        stable = set(pos.as_coefficients_dict().keys()) == \
            set(pos_a.as_coefficients_dict().keys())
        n_pos = len(pos.as_coefficients_dict())
        n_neg = len(neg.as_coefficients_dict())
        results[(c1, c2)] = (d, pos)
        all_ok &= multilin and stable
        print(f"   pair {c1}x{c2}: {n_pos + n_neg} monomials "
              f"({n_pos} pos / {n_neg} neg), multilinear={multilin}, "
              f"sign-pattern Z-independent={stable}")
    print(f"   T1 verdict: all pairs multilinear with Z-stable sign split: "
          f"{all_ok}\n")
    return results


def chart_coords(P1, P2, cell):
    """Canonical chart coordinates of the plane span(P1,P2) in a cell:
    A = Z1 + x Zi + w Zi+1 and B = -Z1 + y Zj + z Zj+1 on the plane."""
    i, j = cell
    a, b, u, v = sp.symbols("_a _b _u _v")
    solA = sp.solve(a * P1 + b * P2 - Z[1] - u * Z[i] - v * Z[i + 1],
                    [a, b, u, v], dict=True)[0]
    solB = sp.solve(a * P1 + b * P2 + Z[1] - u * Z[j] - v * Z[j + 1],
                    [a, b, u, v], dict=True)[0]
    return solA[u], solA[v], solB[u], solB[v]


def m2_terms(A0, B0, C0, D0, Dstore):
    """The 9 assembled contributions at common representatives."""
    terms = {}
    coordsAB = {c: chart_coords(A0, B0, c) for c in CELLS}
    coordsCD = {c: chart_coords(C0, D0, c) for c in CELLS}
    for c1, c2 in product(CELLS, repeat=2):
        d_sym, dpos_sym = Dstore[(c1, c2)]
        subs = dict(zip((*V1, *V2), (*coordsAB[c1], *coordsCD[c2])))
        R = dpos_sym.subs(subs) / d_sym.subs(subs)
        K1 = kermit(A0, B0, *c1, Z)
        K2 = kermit(C0, D0, *c2, Z)
        terms[(c1, c2)] = sp.nsimplify(K1 * K2 * R)
    return terms


def t3_assembly(Dstore):
    print("T3. Assembly: exact-rational seam and pole tables")
    B0 = -Z[1] + sp.Rational(1, 2) * Z[3] + 2 * Z[4] + Z[5]
    C0 = Z[1] + 3 * Z[2] + Z[4]
    D0 = -Z[1] + 2 * Z[3] + Z[5]

    scenarios = [
        ("seam <AB13> -> 0 (must stay finite)",
         lambda e: (Z[1] + 2 * Z[3] + e * Z[2], B0, C0, D0)),
        ("seam <AB14> -> 0 (must stay finite)",
         lambda e: (Z[1] + 3 * Z[4] + e * Z[2], B0, C0, D0)),
    ]
    A0g = Z[1] + Z[2] + 2 * Z[3] + 3 * Z[4]
    Dstar = A0g + B0 + C0                       # <A0 B0 C0 Dstar> = 0
    scenarios.append(
        ("physical pole <ABCD> -> 0 (must DIVERGE)",
         lambda e: (A0g, B0, C0, Dstar + e * Z[5])))

    for label, mk in scenarios:
        print(f"   {label}:")
        print(f"   {'eps':>8} {'max |term|':>14} {'sum':>16}")
        for kexp in (2, 4, 6):
            eps = sp.Rational(1, 10 ** kexp)
            A0, B_, C_, D_ = mk(eps)
            terms = m2_terms(A0, B_, C_, D_, Dstore)
            vals = list(terms.values())
            total = sum(vals)
            biggest = max(abs(sp.Float(t, 30)) for t in vals)
            print(f"   {f'1e-{kexp}':>8} {sp.Float(biggest, 5):>14} "
                  f"{sp.Float(total, 6):>16}")
        print()


if __name__ == "__main__":
    store = t1_structure()
    t3_assembly(store)
    print("Verdict key: P1 survives iff seams finite, physical pole")
    print("divergent, and T1 all-multilinear/sign-stable.")
