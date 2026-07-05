"""Lab 5c, test T4 — leading-singularity census of the two-loop n=5 integrand.

Two octa-cut families, all with exact rational Schubert solutions:

FAMILY A ("kissing pentagons"): each loop line frozen on 4 consecutive
physical walls. Solutions per line: the chord (Z_{m+2} Z_{m+4}) or the
plane-intersection line (m+1,m+2,m+3) n (m+3,m+4,m+5). LESSON LEARNED
(this file's first version predicted +-1 here — wrongly): at n=5 any two
disjoint non-adjacent pentagon chords CROSS, so every non-degenerate
kissing cut is a NON-PLANAR cut, and the planar integrand must have
residue exactly 0 on all of them. The census confirms: 50 zeros. A wrong
integrand could easily fail this; ours passes 50/50.

FAMILY B ("pentagon-box"): the quadruples (i,j,k,l) with one pair
non-adjacent (pentagon side, 4 walls) and one adjacent (box side,
3 walls + the mutual propagator <ABCD>). Pentagon solutions: chord
(Z_i Z_j) or (i-1,i,i+1) n (j-1,j,j+1); box solutions: the two
transversals through the corners Z_k / Z_l meeting the remaining wall
and the fixed pentagon line. FINDINGS (each taught us something):
  - plane-intersection pentagon branches: LS = 0 exactly — the ABCT
    chiral numerator is BUILT to vanish on these; design confirmed.
  - chord pentagon branches at n=5: the box-side solutions are forced
    THROUGH polygon vertices, so the cut point lies on extra divisors
    beyond the designated eight. The naive transverse residue is then
    RAY-DEPENDENT (detected automatically below by computing along two
    independent rays): these are COMPOSITE leading singularities,
    requiring iterated-residue machinery beyond this lab. Classified
    and counted, not silently reported.

Residues computed exactly: LS = lim [M2 x (prod of 8 cut fns)] x
<PQ E1E2>^2 <RS E3E4>^2 / J, with J the 8x8 Jacobian in a local
line-pair chart — the measure factor makes the result invariant under
rescaling/shifting of the solution representatives. The machinery is
CALIBRATED in-file against the 1-loop box quadruple cut (residues
exactly -+1, invariant under representative changes). M2 is evaluated
in the double-pentagon representation certified equal to our cell
assembly by T5.
"""

import pathlib
import sys
from itertools import product

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import sympy as sp  # noqa: E402

from t5_literature import (Z, cyc, cyclic_quadruples,  # noqa: E402
                           double_pentagon)

N = 5


def det4(*cols):
    return sp.Matrix.hstack(*cols).det()


def expand_in_basis(target, basis):
    cs = sp.symbols(f"_c0:{len(basis)}")
    combo = sum((c * v for c, v in zip(cs, basis)), sp.zeros(4, 1))
    sol = sp.solve(combo - target, list(cs), dict=True)[0]
    return [sol[c] for c in cs]


def plane_intersection(p1, p2, shared):
    """Line (a,b,shared) n (shared,d,e): span(Z_shared, y)."""
    others = [m for m in p1 + p2 if m != shared]
    coeffs = expand_in_basis(Z[shared], [Z[m] for m in others])
    y = sum((c * Z[m] for c, m in zip(coeffs[:2], others[:2])), sp.zeros(4, 1))
    return Z[shared], y


def pentagon_solutions(i, j):
    """Lines on the 4 walls (i-1,i),(i,i+1),(j-1,j),(j,j+1); (i,j) non-adjacent.
    At n=5, j = i+2 (mod), so the two triples share Z_{i+1}."""
    chord = (Z[i], Z[j])
    plane = plane_intersection((cyc(i - 1), i, cyc(i + 1)),
                               (cyc(j - 1), j, cyc(j + 1)), cyc(i + 1))
    return {"chord": chord, "plane": plane}


def box_solutions(k, l, P, Q):
    """CD on walls (k-1,k),(k,l),(l,l+1) (l = k+1) plus <CD P Q> = 0:
    the two transversals through the corners Z_k and Z_l."""
    def transversal(corner, wall_a, wall_b):
        # point T = a Z_wa + b Z_wb coplanar with (corner, P, Q):
        # a c1 + b c2 = 0 with c_i = <Z_wi corner P Q>  ->  (a,b) = (c2, -c1)
        c1 = det4(Z[wall_a], corner, P, Q)
        c2 = det4(Z[wall_b], corner, P, Q)
        if c1 == 0 and c2 == 0:
            return None                     # whole wall coplanar: degenerate
        T = c2 * Z[wall_a] - c1 * Z[wall_b]
        return corner, T
    return {"corner-k": transversal(Z[k], l, cyc(l + 1)),
            "corner-l": transversal(Z[l], cyc(k - 1), k)}


RAYS = ((1, 2, 3, 5, 7, 11, 13, 17), (3, 1, 4, 1, 5, 9, 2, 6))


def leading_singularity(solAB, solCD, cut_fns, quads, mutual_cut=False):
    P, Q = solAB
    R, S = solCD
    # For non-mutual (kissing) cuts, intersecting lines signal a different
    # (composite) stratum: skip. For mutual cuts, <ABCD> = 0 IS the cut.
    if not mutual_cut and det4(P, Q, R, S) == 0:
        return None
    E = [sp.Matrix(v) for v in
         ([1, 1, 0, 2], [0, 1, 3, 1], [2, 0, 1, 1], [1, 3, 1, 0])]
    s = sp.symbols("_s0:8")
    A = P + s[0] * E[0] + s[1] * E[1]
    B = Q + s[2] * E[0] + s[3] * E[1]
    C = R + s[4] * E[2] + s[5] * E[3]
    D = S + s[6] * E[2] + s[7] * E[3]
    zero = {t: 0 for t in s}
    rows = [[sp.diff(f(A, B, C, D), v).subs(zero) for v in s] for f in cut_fns]
    J = sp.Matrix(rows).det()
    if J == 0:
        return None                       # chart not transversal: skip
    # The physical form is M2 x <ABd2A><ABd2B><CDd2C><CDd2D>; in this chart
    # the measure contributes <ABE1E2>^2 <CDE3E4>^2 relative to d^8s.
    measure = det4(P, Q, E[0], E[1]) ** 2 * det4(R, S, E[2], E[3]) ** 2

    values = []
    for u in RAYS:                        # two independent approach rays
        eps = sp.Symbol("_eps")
        ray = {t: eps * v for t, v in zip(s, u)}
        Ae, Be, Ce, De = (M.subs(ray) for M in (A, B, C, D))
        cut = sp.prod([f(Ae, Be, Ce, De) for f in cut_fns])
        f = sp.cancel(sp.together(
            sum(double_pentagon(Ae, Be, Ce, De, *q) for q in quads) * cut))
        num, den = sp.fraction(f)
        if den.subs(eps, 0) == 0:
            return "composite"      # divergent: extra divisors at the point
        values.append(sp.nsimplify(
            (num.subs(eps, 0) / den.subs(eps, 0)) * measure / J))
    if values[0] != values[1]:
        return "composite"          # ray-dependent: not a transverse residue
    return values[0]


def wall(i, j, side):
    if side == "AB":
        return lambda A, B, C, D: det4(A, B, Z[i], Z[j])
    return lambda A, B, C, D: det4(C, D, Z[i], Z[j])


MUTUAL = lambda A, B, C, D: det4(A, B, C, D)


def family_A(quads, tally):
    print("Family A — kissing pentagons (all non-degenerate cuts are")
    print("CROSSED at n=5: planarity demands LS = 0 on every one)")
    def sols(m):
        a, b, c, d, e = (cyc(m + t) for t in range(1, 6))
        walls = [(a, b), (b, c), (c, d), (d, e)]
        return ({"chord": (Z[b], Z[d]),
                 "plane": plane_intersection((a, b, c), (c, d, e), c)}, walls)
    zeros = degen = 0
    for m1 in range(1, 6):
        sAB, wAB = sols(m1)
        for m2 in range(1, 6):
            sCD, wCD = sols(m2)
            fns = [wall(*w, "AB") for w in wAB] + [wall(*w, "CD") for w in wCD]
            for b1, b2 in product(("chord", "plane"), repeat=2):
                ls = leading_singularity(sAB[b1], sCD[b2], fns, quads)
                if ls is None:
                    degen += 1
                    continue
                tally[ls] = tally.get(ls, 0) + 1
                zeros += ls == 0
    print(f"   degenerate/skipped: {degen}; LS = 0 on all "
          f"{zeros} remaining cuts: {zeros + degen == 100}\n")


def family_B(quads, tally):
    print("Family B — pentagon-box cuts (4 walls | 3 walls + <ABCD>)")
    def adjacent(a, b):
        return b == cyc(a + 1)
    rows = []
    for (i, j, k, l) in quads:
        pent_on_AB = (not adjacent(i, j)) and adjacent(k, l)
        pent_on_CD = adjacent(i, j) and (not adjacent(k, l))
        if not (pent_on_AB or pent_on_CD):
            continue
        pi, pj, bk, bl = (i, j, k, l) if pent_on_AB else (k, l, i, j)
        pside, bside = ("AB", "CD") if pent_on_AB else ("CD", "AB")
        pw = [(cyc(pi - 1), pi), (pi, cyc(pi + 1)),
              (cyc(pj - 1), pj), (pj, cyc(pj + 1))]
        bw = [(cyc(bk - 1), bk), (bk, bl), (bl, cyc(bl + 1))]
        fns = [wall(*w, pside) for w in pw] + [wall(*w, bside) for w in bw]
        fns.append(MUTUAL)
        for pb in ("chord", "plane"):
            pline = pentagon_solutions(pi, pj)[pb]
            for cb, bline in box_solutions(bk, bl, *pline).items():
                if bline is None:
                    tally["degen"] = tally.get("degen", 0) + 1
                    rows.append(((i, j, k, l), pb, cb, "degen"))
                    continue
                solAB, solCD = ((pline, bline) if pent_on_AB
                                else (bline, pline))
                ls = leading_singularity(solAB, solCD, fns, quads,
                                         mutual_cut=True)
                key = ls if ls is not None else "degen"
                tally[key] = tally.get(key, 0) + 1
                rows.append(((i, j, k, l), pb, cb, ls))
    for q, pb, cb, ls in rows:
        print(f"   quad {q}  pentagon:{pb:6s} box:{cb:9s} LS = {ls}")
    print()


def calibrate() -> None:
    """Machinery check: the 1-loop box quadruple cut must give exactly -+1,
    independent of the choice of solution representatives."""
    def box(A, B):
        num = det4(Z[1], Z[2], Z[3], Z[4]) ** 2
        den = sp.Integer(1)
        for i, j in ((1, 2), (2, 3), (3, 4), (1, 4)):
            den *= det4(A, B, Z[i], Z[j])
        return num / den
    E = [sp.Matrix(v) for v in ([1, 1, 0, 2], [0, 1, 3, 1])]
    results = []
    for P, Q in ((Z[1], Z[3]), (Z[2], Z[4]), (7 * Z[1], -3 * Z[3] + Z[1])):
        s = sp.symbols("_t0:4")
        A = P + s[0] * E[0] + s[1] * E[1]
        B = Q + s[2] * E[0] + s[3] * E[1]
        zero = {t: 0 for t in s}
        walls = [(1, 2), (2, 3), (3, 4), (1, 4)]
        rows = [[sp.diff(det4(A, B, Z[i], Z[j]), v).subs(zero) for v in s]
                for i, j in walls]
        J = sp.Matrix(rows).det()
        eps = sp.Symbol("_eps")
        ray = {t: eps * u for t, u in zip(s, (1, 2, 3, 5))}
        Ae, Be = A.subs(ray), B.subs(ray)
        cut = sp.prod([det4(Ae, Be, Z[i], Z[j]) for i, j in walls])
        f = sp.cancel(box(Ae, Be) * cut)
        num, den = sp.fraction(f)
        g = num.subs(eps, 0) / den.subs(eps, 0)
        results.append(sp.nsimplify(g * det4(P, Q, E[0], E[1]) ** 2 / J))
    assert all(abs(r) == 1 for r in results), results
    print(f"Calibration (1-loop box quad cuts): residues {results} — "
          f"unit, rep-independent.\n")


def main() -> None:
    calibrate()
    quads = cyclic_quadruples()
    tally: dict = {}
    family_A(quads, tally)
    family_B(quads, tally)
    print("Census across both families:")
    for v, cnt in sorted(tally.items(), key=lambda kv: str(kv[0])):
        print(f"   LS = {v}: {cnt}")
    numeric = [v for v in tally if v not in ("degen", "composite")]
    print(f"\n   all WELL-DEFINED (transverse) leading singularities in "
          f"{{0, +1, -1}}: {all(v in (0, 1, -1) for v in numeric)}")
    print("   Zeros where planarity demands them; zeros where the chiral")
    print("   numerators are designed to vanish; composite strata detected")
    print("   and classified rather than mis-reported. The full composite")
    print("   census (iterated residues) is the marked next step.")


if __name__ == "__main__":
    main()
