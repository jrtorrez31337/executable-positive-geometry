"""Track B, Lab 1 — the positive Grassmannian Gr+(2,4).

The Grassmannian Gr(k,n) is the space of k-dimensional planes inside
n-dimensional space. A point of Gr(2,4) is a 2x4 matrix (two spanning row
vectors), up to row operations. Its intrinsic coordinates are the PLUCKER
COORDINATES: the six 2x2 minors p_ij. They are not independent — they obey
one quadratic constraint, the Plucker relation:

    p12 p34 - p13 p24 + p14 p23 = 0

The POSITIVE part Gr+(2,4) is where every ordered minor p_ij > 0 (i<j).
This tiny region is the k=2, n=4 seed of the amplituhedron story.

The physics dictionary (planar N=4 super Yang-Mills, 4 gluons):
    columns of the matrix  <->  the 4 particles' spinors lambda_i
    minor p_ij             <->  spinor bracket <ij>  (angle bracket)
    Plucker relation       <->  the Schouten identity
    cyclic minors p12 p23 p34 p14  <->  the Parke-Taylor denominator:
        A_MHV(1234) ~ <13>^4 / (<12><23><34><41>)
An entire 4-gluon amplitude is a rational function OF PLUCKER COORDINATES —
the calculation lives on the Grassmannian, not in spacetime.
"""

import numpy as np
import sympy as sp

rng = np.random.default_rng(11)


def pluckers(M: sp.Matrix) -> dict[tuple[int, int], sp.Expr]:
    return {
        (i, j): sp.expand(M[0, i] * M[1, j] - M[0, j] * M[1, i])
        for i in range(4)
        for j in range(i + 1, 4)
    }


def main() -> None:
    # 1. The Plucker relation, proven symbolically for a GENERAL matrix.
    a = sp.symbols("a0:4")
    b = sp.symbols("b0:4")
    M = sp.Matrix([list(a), list(b)])
    p = pluckers(M)
    rel = sp.expand(p[0, 1] * p[2, 3] - p[0, 2] * p[1, 3] + p[0, 3] * p[1, 2])
    print("1. Plucker relation p12*p34 - p13*p24 + p14*p23 for a generic matrix:")
    print(f"   simplifies to: {rel}")
    print("   Six minors, one identity -> Gr(2,4) is 4-dimensional, and any")
    print("   'amplitude' built from brackets inherits this identity (Schouten).\n")

    # 2. Positivity is rare: random planes are almost never positive.
    n_trials, n_positive = 100_000, 0
    for _ in range(n_trials):
        m = rng.normal(size=(2, 4))
        minors = [np.linalg.det(m[:, [i, j]]) for i in range(4) for j in range(i + 1, 4)]
        n_positive += all(v > 0 for v in minors)
    print(f"2. Random 2-planes with ALL six minors positive: "
          f"{n_positive}/{n_trials} = {n_positive / n_trials:.2%}")
    print("   Positivity carves out a tiny, special chamber of the Grassmannian.\n")

    # 3. The moment curve makes positivity automatic — and PROVABLY so.
    t = sp.symbols("t0:4", positive=True)
    V = sp.Matrix([[1, 1, 1, 1], list(t)])   # column i is (1, t_i)
    pv = pluckers(V)
    print("3. Columns on the moment curve (1, t_i) with t0 < t1 < t2 < t3:")
    for (i, j), val in pv.items():
        print(f"   p{i + 1}{j + 1} = {sp.factor(val)}")
    print("   Every minor is t_j - t_i > 0 whenever the t's are ORDERED:")
    print("   positivity of the geometry = an ordering of the particles.")
    print("   This is why the amplituhedron knows about planar (cyclically")
    print("   ordered) amplitudes: convexity <-> ordering <-> positivity.\n")

    # 4. The Parke-Taylor denominator: adjacent minors, cyclically.
    subs = dict(zip(t, (1, 2, 4, 8)))
    cyc = [pv[0, 1], pv[1, 2], pv[2, 3], pv[0, 3]]
    denom = sp.prod(cyc)
    print("4. Parke-Taylor denominator <12><23><34><41> on the moment curve:")
    print(f"   = {sp.factor(denom)}")
    print(f"   at (t0,t1,t2,t3)=(1,2,4,8): {denom.subs(subs)} > 0 — the amplitude's")
    print("   poles all sit on the BOUNDARY of the positive region (some t_j -> t_i),")
    print("   i.e. where two particles' data collide: physical singularities =")
    print("   boundaries of the positive geometry. That is the whole thesis.")


if __name__ == "__main__":
    main()
