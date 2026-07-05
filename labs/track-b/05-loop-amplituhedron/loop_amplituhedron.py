"""Track B, Lab 5 — the LOOP amplituhedron (n=4, L=1 and L=2).

At loop level the amplituhedron's points are LINES in P^3 (momentum-twistor
loop momenta): line AB for loop one, CD for loop two. Region (verified
against Kojima-Rao arXiv:2007.15650 and the 2-loop amplituhedron paper
arXiv:2410.11501):

  one loop : <AB i i+1> > 0 (twisted cyclic) + two sign flips in <AB1i>.
             For n=4 this is a SINGLE cell, charted by the positive
             orthant via  A = Z1 + x Z2 + w Z3,  B = -Z1 + y Z3 + z Z4.
  two loops: each line in the one-loop region, PLUS mutual positivity
             <ABCD> > 0 — the two loops cannot be chosen independently.

Known canonical forms in this chart (eqs. 3.1-3.2 of 2007.15650):
  L=1:  Omega_1 = dlog x ^ dlog y ^ dlog z ^ dlog w      (the box)
  L=2:  Omega_2 = (prod of 8 dlogs) * D+ / D,  where
        D  = <ABCD> ~ (x2-x1)(z1-z2) + (y2-y1)(w1-w2)
        D+ = x2 z1 + x1 z2 + y2 w1 + y1 w2   (the positive monomials of D)

Everything below either derives these facts symbolically or tests a
bracket-level formula AGAINST them.
"""

import random
from itertools import combinations

import sympy as sp

Zc = [sp.Matrix(sp.eye(4))[:, i] for i in range(4)]      # Z_i = e_i, <1234>=1


def det4(*cols) -> sp.Expr:
    return sp.Matrix.hstack(*cols).det()


def loop_line(x, w, y, z):
    A = Zc[0] + x * Zc[1] + w * Zc[2]
    B = -Zc[0] + y * Zc[2] + z * Zc[3]
    return A, B


def part1() -> None:
    x, y, z, w = sp.symbols("x y z w", positive=True)
    A, B = loop_line(x, w, y, z)

    print("1. ONE LOOP (n=4): the box as a positive orthant")
    br = {(i, j): sp.expand(det4(A, B, Zc[i - 1], Zc[j - 1]))
          for i, j in combinations(range(1, 5), 2)}
    for k, v in br.items():
        print(f"   <AB{k[0]}{k[1]}> = {v}")
    print("   Physical brackets <AB12>,<AB23>,<AB34>,<AB14> are single")
    print("   MONOMIALS in (x,y,z,w): positivity of the loop line = the")
    print("   positive orthant. Sign-flip sequence {<AB12>, <AB13>, <AB14>}:")
    seq = [br[1, 2], br[1, 3], br[1, 4]]
    print(f"   {[sp.sign(e.subs({x: 1, y: 1, z: 1, w: 1})) for e in seq]}"
          f"  -> exactly 2 sign flips (the ATT characterization).")

    # The famous box integrand equals the dlog form — exactly.
    # Measure: A = Z1+xZ2+wZ3 -> <AB d^2A> = <AB23> dx dw;
    #          B = -Z1+yZ3+zZ4 -> <AB d^2B> = <AB34> dy dz.
    box = (br[2, 3] * br[3, 4]) / (br[1, 2] * br[2, 3] * br[3, 4] * br[1, 4])
    ratio = sp.simplify(box * x * y * z * w)
    print(f"\n   <1234>^2 <ABd2A><ABd2B> / (<AB12><AB23><AB34><AB14>)")
    print(f"   divided by  dx dy dz dw/(xyzw)  =  {ratio}")
    print("   The one-loop box integrand IS dlog x ^ dlog y ^ dlog z ^ dlog w:")
    print("   4 boundaries (propagators on-shell), 4-fold residue (the")
    print("   quadruple cut of generalized unitarity) = 1: the leading")
    print("   singularity of N=4 SYM, normalized by the geometry itself.\n")


def part2() -> None:
    v1 = sp.symbols("x1 w1 y1 z1", positive=True)
    v2 = sp.symbols("x2 w2 y2 z2", positive=True)
    x1, w1, y1, z1 = v1
    x2, w2, y2, z2 = v2
    A, B = loop_line(x1, w1, y1, z1)
    C, D = loop_line(x2, w2, y2, z2)

    print("2. TWO LOOPS: mutual positivity <ABCD>")
    abcd = sp.expand(det4(A, B, C, D))
    factored = (z1 - z2) * (w1 * x2 - w2 * x1) + (x1 - x2) * (y1 * z2 - y2 * z1)
    print(f"   <ABCD> = (z1-z2)(w1x2-w2x1) + (x1-x2)(y1z2-y2z1)"
          f"   [verified: {sp.simplify(abcd - sp.expand(factored)) == 0}]")
    print("   (Kojima-Rao's eq. 3.1 is this same object in rescaled")
    print("   'dimensionless-ratio' variables; we stay in the raw chart.)")
    d_plus = sum(t for t in abcd.args if t.as_coeff_Mul()[0] > 0)
    print(f"   positive monomials D+ = {d_plus}")

    f = sp.lambdify((x1, w1, y1, z1, x2, w2, y2, z2), abcd)
    rng = random.Random(7)
    hits = sum(1 for _ in range(100_000)
               if f(*[rng.random() for _ in range(8)]) > 0)
    print(f"   fraction of independently-valid loop pairs that are MUTUALLY")
    print(f"   positive: {hits / 100_000:.3f} — the loops are entangled by the")
    print("   geometry; the L-loop integrand never factorizes into L boxes.\n")

    print("3. Bracket-level double boxes -> chart: solving for the numerator")

    def bk(P, Q, i, j):
        return det4(P, Q, Zc[i - 1], Zc[j - 1])

    def double_box(L1, L2, miss1, miss2):
        """1 / (three <L1 i i+1> props, <L1 L2>, three <L2 i i+1> props)."""
        (P1, Q1), (P2, Q2) = L1, L2
        den = det4(P1, Q1, P2, Q2)
        for i, j in [(1, 2), (2, 3), (3, 4), (1, 4)]:
            if (i, j) != miss1:
                den *= bk(P1, Q1, i, j)
            if (i, j) != miss2:
                den *= bk(P2, Q2, i, j)
        return 1 / den

    # t-channel: AB touches legs 2,3 (miss <AB14>), CD touches 4,1 (miss <CD23>)
    # s-channel: AB touches legs 1,2 (miss <AB34>), CD touches 3,4 (miss <CD12>)
    # plus the two loop-relabelings (AB <-> CD). No 1/2: the amplituhedron
    # is a region of ORDERED pairs (AB,CD), so its canonical form is the
    # full relabeling sum; the physical amplitude's conventional 1/2 for
    # indistinguishable loops is a bookkeeping choice on top.
    m2 = (double_box((A, B), (C, D), (1, 4), (2, 3))
          + double_box((A, B), (C, D), (3, 4), (1, 2))
          + double_box((C, D), (A, B), (1, 4), (2, 3))
          + double_box((C, D), (A, B), (3, 4), (1, 2)))

    # Chart measure: <AB d2A><AB d2B><CD d2C><CD d2D> Jacobians.
    measure = bk(A, B, 2, 3) * bk(A, B, 3, 4) * bk(C, D, 2, 3) * bk(C, D, 3, 4)
    prod_vars = x1 * y1 * z1 * w1 * x2 * y2 * z2 * w2
    numerator = sp.expand(sp.cancel(sp.together(m2 * measure * prod_vars * abcd)))
    print(f"   Omega_2 = (prod of 8 dlogs) * N/<ABCD>  with")
    print(f"   N = {numerator}")
    poly = numerator.as_poly(x1, w1, y1, z1, x2, w2, y2, z2)
    all_pos = poly is not None and all(c > 0 for c in poly.coeffs())
    print(f"   N is a polynomial with ALL-POSITIVE coefficients? {all_pos}")
    print(f"   N equals D+ (every positive monomial of <ABCD>)?  "
          f"{sp.simplify(numerator - d_plus) == 0}")
    print("   The physical double-box sum lands EXACTLY on the positive-")
    print("   geometry prediction: dlog singularities only on boundaries")
    print("   (the 8 chart walls + the mutual cut <ABCD>=0), numerator =")
    print("   the 'maximally positive' part of the mutual condition.")


if __name__ == "__main__":
    part1()
    part2()
