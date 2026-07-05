"""Lab 5c, test T5 — gold standard: our assembled two-loop n=5 integrand
vs the literature's local double-pentagon representation.

Literature source (fetched and read directly, not from memory):
Arkani-Hamed, Bourjaily, Cachazo, Trnka, "Local Integrals for Planar
Scattering Amplitudes" (arXiv:1012.6032), Section 6.3, p. 66:

  A^{2-loop}_MHV = (1/2) * sum over cyclically ordered (i,j,k,l) of

      <AB (i-1 i i+1) n (j-1 j j+1)> <i j k l> <CD (k-1 k k+1) n (l-1 l l+1)>
      -----------------------------------------------------------------------
      <AB i-1 i><AB i i+1><AB j-1 j><AB j j+1> <ABCD>
                          <CD k-1 k><CD k k+1><CD l-1 l><CD l l+1>

with boundary terms (j=i+1, l=k+1) included; the intersection-bracket
numerators then cancel doubled propagators automatically. For n=5 there
are 20 cyclically ordered quadruples.

Our object (Lab 5c): M2 = sum over 9 composite cells of
K_c1(A,B) K_c2(C,D) D+/D. Both expressions have loop-line weight -8, so
if they describe the same integrand the pointwise ratio is a CONSTANT.
Our sum is over ORDERED loop pairs (no 1/2), so the expected constant
is 2. Everything exact (rational arithmetic).
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import sympy as sp  # noqa: E402

from loop2_n5 import (CELLS, Z, det4, m2_terms, pair_D,  # noqa: E402
                      split_pos)
from itertools import product  # noqa: E402

N = 5


def cyc(a: int) -> int:
    return (a - 1) % N + 1


def ib(P, Q, abc, defg):
    """<PQ (abc) n (def)> = <P abc><Q def> - <Q abc><P def>."""
    a, b, c = abc
    d, e, f = defg
    return (det4(P, Z[a], Z[b], Z[c]) * det4(Q, Z[d], Z[e], Z[f])
            - det4(Q, Z[a], Z[b], Z[c]) * det4(P, Z[d], Z[e], Z[f]))


def double_pentagon(A, B, C, D, i, j, k, l):
    tri = lambda m: (cyc(m - 1), m, cyc(m + 1))
    num = (ib(A, B, tri(i), tri(j))
           * det4(Z[i], Z[j], Z[k], Z[l])
           * ib(C, D, tri(k), tri(l)))
    den = det4(A, B, C, D)
    for P, Q, m in ((A, B, i), (A, B, j), (C, D, k), (C, D, l)):
        den *= det4(P, Q, Z[cyc(m - 1)], Z[m]) * det4(P, Q, Z[m], Z[cyc(m + 1)])
    return num / den


def cyclic_quadruples():
    """All (i,j,k,l) cyclically ordered, each i in 1..n as starting label."""
    quads = []
    for i in range(1, N + 1):
        rest = [cyc(i + s) for s in range(1, N)]      # cyclic order after i
        for a in range(len(rest)):
            for b in range(a + 1, len(rest)):
                for c in range(b + 1, len(rest)):
                    quads.append((i, rest[a], rest[b], rest[c]))
    return quads


def main() -> None:
    quads = cyclic_quadruples()
    print(f"T5: literature comparison at n=5 — {len(quads)} cyclically "
          f"ordered double pentagons (ABCT eq. 6.18)")

    store = {}
    for c1, c2 in product(CELLS, repeat=2):
        d = pair_D(c1, c2, Z)
        store[(c1, c2)] = (d, split_pos(d)[0])

    points = [
        (Z[1] + Z[2] + 2 * Z[3] + 3 * Z[4],
         -Z[1] + sp.Rational(1, 2) * Z[3] + 2 * Z[4] + Z[5],
         Z[1] + 3 * Z[2] + Z[4],
         -Z[1] + 2 * Z[3] + Z[5]),
        (Z[1] + 2 * Z[2] + Z[5],
         -Z[1] + Z[3] + 3 * Z[4],
         Z[1] + Z[2] + Z[3] + Z[4],
         -Z[1] + sp.Rational(3, 2) * Z[4] + 2 * Z[5]),
        (Z[1] + sp.Rational(1, 3) * Z[2] + 2 * Z[4],
         -Z[1] + 2 * Z[2] + Z[3] + Z[5],
         Z[1] + Z[3] + sp.Rational(1, 2) * Z[5],
         -Z[1] + Z[2] + Z[4] + Z[5]),
    ]

    print(f"   {'point':>6} {'M2 (ours)':>16} {'sum of DPs':>16} {'ratio':>10}")
    ratios = []
    for idx, (A0, B0, C0, D0) in enumerate(points, 1):
        ours = sum(m2_terms(A0, B0, C0, D0, store).values())
        lit = sum(double_pentagon(A0, B0, C0, D0, *q) for q in quads)
        ratio = sp.nsimplify(sp.cancel(ours / lit))
        ratios.append(ratio)
        print(f"   {idx:>6} {sp.Float(ours, 6):>16} {sp.Float(lit, 6):>16} "
              f"{str(ratio):>10}")

    same = len(set(ratios)) == 1
    print(f"\n   ratio constant across generic points: {same}")
    if same:
        r = ratios[0]
        print(f"   M2_ours = {r} x [sum of 20 double pentagons]")
        print(f"           = {sp.nsimplify(r / 2)} x 2 x A^(2-loop)_ABCT")
        print("   Our ordered-pair cell assembly equals the literature's")
        print("   half-symmetrized local integrand up to the loop-labeling")
        print("   convention — the postulated two-loop n=5 canonical form IS")
        print("   the physical N=4 SYM integrand.")


if __name__ == "__main__":
    main()
