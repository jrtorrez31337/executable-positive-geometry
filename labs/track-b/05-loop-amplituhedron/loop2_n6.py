"""Track B, Lab 5d — the boundary-locating experiment: two-loop n=6.

At n=5, postulate P1 (the 2-loop MHV integrand = sum over composite cells
of Kermit x Kermit x D+/D) survived every test, and the quasi-linear
complication that Kojima-Rao built machinery for never appeared. n=6 is
the first place it could. Two structural facts, PROVEN by inspection
before computing (and verified below anyway):

  (i) D = <ABCD> is automatically multilinear in the 8 chart variables
      at every n — each variable enters exactly one column of the det;
  (ii) every monomial coefficient is a SINGLE 4-bracket <Z_a Z_b Z_c Z_d>
      (one term chosen per column), so the sign split defining D+ is
      Z-independent for any positive kinematics.

Therefore P1's preconditions cannot fail at n=6, and the only place the
pattern could break is the ASSEMBLY — testable solely by the
gold-standard comparison: 36-cell sum vs the ABCT double-pentagon
integrand (60 cyclically ordered quadruples at n=6), in exact rational
arithmetic. Ratio 1 extends P1; anything else locates the boundary.
"""

from itertools import product

import sympy as sp

N = 6
T_VALUES = (1, 2, 3, 5, 8, 13)
Z = {i + 1: sp.Matrix([sp.Integer(t) ** p for p in range(4)])
     for i, t in enumerate(T_VALUES)}
CELLS = [(i, j) for i in range(2, N) for j in range(i + 1, N)]   # 6 cells


def cyc(a):
    return (a - 1) % N + 1


def det4(*cols):
    return sp.Matrix.hstack(*cols).det()


def br(A, B, i, j):
    return det4(A, B, Z[i], Z[j])


def kermit(A, B, i, j):
    num = (det4(A, Z[1], Z[i], Z[i + 1]) * det4(B, Z[1], Z[j], Z[j + 1])
           - det4(B, Z[1], Z[i], Z[i + 1]) * det4(A, Z[1], Z[j], Z[j + 1])) ** 2
    den = sp.Integer(1)
    for p, q in ((1, i), (i, i + 1), (1, i + 1), (1, j), (j, j + 1), (1, j + 1)):
        den *= br(A, B, p, q)
    return num / den


V1 = sp.symbols("x1 w1 y1 z1", positive=True)
V2 = sp.symbols("x2 w2 y2 z2", positive=True)


def chart_line(cell, syms):
    i, j = cell
    x, w, y, z = syms
    return Z[1] + x * Z[i] + w * Z[i + 1], -Z[1] + y * Z[j] + z * Z[j + 1]


def part1_one_loop():
    print(f"1. One-loop n=6 regression: {len(CELLS)} sign-flip cells")
    ok = True
    for i, j in CELLS:
        A, B = chart_line((i, j), V1)
        x, w, y, z = V1
        ratio = sp.simplify(sp.cancel(
            kermit(A, B, i, j) * br(A, B, i, i + 1) * br(A, B, j, j + 1)
            * x * w * y * z))
        seq = []
        for m in range(2, N + 1):
            s = {sp.sign(c) for c in
                 sp.expand(br(A, B, 1, m)).as_coefficients_dict().values()}
            seq.append(s.pop() if len(s) == 1 else 0)
        flips = [m for m, (u, v) in enumerate(zip(seq, seq[1:]), start=2)
                 if u * v < 0]
        good = (ratio in (1, -1)) and flips == [i, j]
        ok &= good
        print(f"   cell ({i},{j}): dlog ratio = {ratio}, sign flips at {flips}")
    print(f"   all cells exact dlog orthants with correct flip labels: {ok}\n")


def build_store():
    print("2. The 36 mutual conditions <ABCD>")
    Zalt = {i + 1: sp.Matrix([sp.Integer(t) ** p for p in range(4)])
            for i, t in enumerate((1, 2, 4, 7, 11, 18))}
    store, stable_all = {}, True
    for c1, c2 in product(CELLS, repeat=2):
        A, B = chart_line(c1, V1)
        C, D = chart_line(c2, V2)
        d = sp.expand(det4(A, B, C, D))
        multilin = all(sp.degree(d, v) <= 1 for v in (*V1, *V2))
        pos = sp.expand(sum(c * m for m, c in d.as_coefficients_dict().items()
                            if c > 0))
        # Z-stability check on the alternate moment curve
        A2 = Zalt[1] + V1[0] * Zalt[c1[0]] + V1[1] * Zalt[c1[0] + 1]
        B2 = -Zalt[1] + V1[2] * Zalt[c1[1]] + V1[3] * Zalt[c1[1] + 1]
        C2 = Zalt[1] + V2[0] * Zalt[c2[0]] + V2[1] * Zalt[c2[0] + 1]
        D2 = -Zalt[1] + V2[2] * Zalt[c2[1]] + V2[3] * Zalt[c2[1] + 1]
        dalt = sp.expand(det4(A2, B2, C2, D2))
        pos_alt = {m for m, c in dalt.as_coefficients_dict().items() if c > 0}
        stable = pos_alt == set(
            m for m, c in d.as_coefficients_dict().items() if c > 0)
        stable_all &= multilin and stable
        store[(c1, c2)] = (d, pos)
    n_mono = sorted({len(d.as_coefficients_dict())
                     for d, _ in store.values()})
    print(f"   monomial counts across pairs: {n_mono}")
    print(f"   all 36 multilinear with Z-stable sign splits: {stable_all}\n")
    return store


def chart_coords(P1, P2, cell):
    i, j = cell
    a, b, u, v = sp.symbols("_a _b _u _v")
    solA = sp.solve(a * P1 + b * P2 - Z[1] - u * Z[i] - v * Z[i + 1],
                    [a, b, u, v], dict=True)[0]
    solB = sp.solve(a * P1 + b * P2 + Z[1] - u * Z[j] - v * Z[j + 1],
                    [a, b, u, v], dict=True)[0]
    return solA[u], solA[v], solB[u], solB[v]


def double_pentagon(A, B, C, D, i, j, k, l):
    tri = lambda m: (cyc(m - 1), m, cyc(m + 1))
    def ib(P, Q, t1, t2):
        return (det4(P, *[Z[m] for m in t1]) * det4(Q, *[Z[m] for m in t2])
                - det4(Q, *[Z[m] for m in t1]) * det4(P, *[Z[m] for m in t2]))
    num = (ib(A, B, tri(i), tri(j)) * det4(Z[i], Z[j], Z[k], Z[l])
           * ib(C, D, tri(k), tri(l)))
    den = det4(A, B, C, D)
    for P, Q, m in ((A, B, i), (A, B, j), (C, D, k), (C, D, l)):
        den *= det4(P, Q, Z[cyc(m - 1)], Z[m]) * det4(P, Q, Z[m], Z[cyc(m + 1)])
    return num / den


def cyclic_quadruples():
    quads = []
    for i in range(1, N + 1):
        rest = [cyc(i + s) for s in range(1, N)]
        for a in range(len(rest)):
            for b in range(a + 1, len(rest)):
                for c in range(b + 1, len(rest)):
                    quads.append((i, rest[a], rest[b], rest[c]))
    return quads


def part3_gold(store):
    quads = cyclic_quadruples()
    print(f"3. THE DECISIVE TEST: 36-cell assembly vs {len(quads)} ABCT "
          f"double pentagons")
    points = [
        (Z[1] + Z[2] + 2 * Z[3] + 3 * Z[4],
         -Z[1] + sp.Rational(1, 2) * Z[3] + 2 * Z[5] + Z[6],
         Z[1] + 3 * Z[2] + Z[4] + Z[6],
         -Z[1] + 2 * Z[3] + Z[5]),
        (Z[1] + 2 * Z[2] + Z[5] + sp.Rational(1, 3) * Z[6],
         -Z[1] + Z[3] + 3 * Z[4],
         Z[1] + Z[2] + Z[3] + Z[4] + Z[5],
         -Z[1] + sp.Rational(3, 2) * Z[4] + 2 * Z[6]),
    ]
    print(f"   {'point':>6} {'M2 (ours)':>15} {'sum of DPs':>15} {'ratio':>8}")
    ratios = []
    for idx, (A0, B0, C0, D0) in enumerate(points, 1):
        coordsAB = {c: chart_coords(A0, B0, c) for c in CELLS}
        coordsCD = {c: chart_coords(C0, D0, c) for c in CELLS}
        ours = sp.Integer(0)
        for c1, c2 in product(CELLS, repeat=2):
            d_sym, pos_sym = store[(c1, c2)]
            subs = dict(zip((*V1, *V2), (*coordsAB[c1], *coordsCD[c2])))
            R = pos_sym.subs(subs) / d_sym.subs(subs)
            ours += kermit(A0, B0, *c1) * kermit(C0, D0, *c2) * R
        lit = sum(double_pentagon(A0, B0, C0, D0, *q) for q in quads)
        ratio = sp.nsimplify(sp.cancel(ours / lit))
        ratios.append(ratio)
        print(f"   {idx:>6} {sp.Float(ours, 5):>15} {sp.Float(lit, 5):>15} "
              f"{str(ratio):>8}")
    if len(set(ratios)) == 1 and ratios[0] == 1:
        print("\n   RATIO EXACTLY 1: P1 EXTENDS TO n=6. The maximally positive")
        print("   assembly IS the physical two-loop six-point MHV integrand;")
        print("   the quasi-linear complication does not bite 2-loop MHV in")
        print("   raw sign-flip charts at n=6 either. Combined with the")
        print("   structural facts (i)-(ii) in the docstring, the pattern is")
        print("   now plausibly all-n — the claim for the Door-4 note.")
    else:
        print(f"\n   RATIO NOT 1 ({ratios}): BOUNDARY LOCATED at n=6 —")
        print("   next step: per-pair diagnostics to find which composite")
        print("   cells break the naive maximal-positivity form.")


if __name__ == "__main__":
    part1_one_loop()
    store = build_store()
    part3_gold(store)
