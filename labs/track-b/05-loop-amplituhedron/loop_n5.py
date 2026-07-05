"""Track B, Lab 5b — the n=5 one-loop MHV amplituhedron.

At n=4 the one-loop amplituhedron was a SINGLE cell: one orthant, one box
integrand, no assembly required. n=5 is the first multi-cell loop
geometry: the space of loop lines AB with

    <AB i i+1> > 0 (twisted cyclic)  and  2 sign flips in {<AB 1 i>}

decomposes into (n-2)(n-3)/2 = 3 cells, labeled by WHERE the two sign
flips sit: (i,j) in {(2,3), (2,4), (3,4)}. Each cell has the positive
chart (Kojima-Rao eq. 1.8, verified in corpus/):

    A = Z1 + x Z_i + w Z_{i+1},   B = -Z1 + y Z_j + z Z_{j+1}

and contributes one "Kermit" term (Arkani-Hamed et al.) to the integrand:

  K_ij = <AB (1 i i+1) n (1 j j+1)>^2
         / (<AB1i><AB i i+1><AB 1 i+1> <AB1j><AB j j+1><AB 1 j+1>)

where <AB (abc) n (def)> = <Aabc><Bdef> - <Babc><Adef> is the bracket of
AB with the intersection LINE of two planes. The full integrand is
M5 = K_23 + K_24 + K_34. Tree-level lessons return at loop level:
cells = terms, spurious poles (<AB13>, <AB14>) = seams, and only the
physical poles <AB i i+1> survive the sum.

Everything below is exact (symbolic chart variables over rational Z's).
"""

from itertools import combinations

import sympy as sp

N = 5
T_VALUES = (1, 2, 3, 5, 8)                       # moment curve, ordered
Z = {i + 1: sp.Matrix([sp.Integer(t) ** p for p in range(4)])
     for i, t in enumerate(T_VALUES)}


def det4(*cols) -> sp.Expr:
    return sp.Matrix.hstack(*cols).det()


def br(A, B, i, j) -> sp.Expr:
    return det4(A, B, Z[i], Z[j])


def kermit(A, B, i, j) -> sp.Expr:
    num = (det4(A, Z[1], Z[i], Z[i + 1]) * det4(B, Z[1], Z[j], Z[j + 1])
           - det4(B, Z[1], Z[i], Z[i + 1]) * det4(A, Z[1], Z[j], Z[j + 1])) ** 2
    den = (br(A, B, 1, i) * br(A, B, i, i + 1) * br(A, B, 1, i + 1)
           * br(A, B, 1, j) * br(A, B, j, j + 1) * br(A, B, 1, j + 1))
    return num / den


def chart(i, j):
    x, w, y, z = sp.symbols("x w y z", positive=True)
    A = Z[1] + x * Z[i] + w * Z[i + 1]
    B = -Z[1] + y * Z[j] + z * Z[j + 1]
    return A, B, (x, w, y, z)


def definite_sign(expr) -> int:
    """+1 / -1 if every monomial coefficient shares that sign, else 0."""
    p = sp.expand(expr)
    signs = {sp.sign(c) for c in p.as_coefficients_dict().values()}
    if signs == {1}:
        return 1
    if signs == {-1}:
        return -1
    return 0


def warmup_n4() -> None:
    print("0. Warm-up: Kermit implementation vs the known n=4 identity")
    a = sp.symbols("a0:4")
    b = sp.symbols("b0:4")
    A, B = sp.Matrix(a), sp.Matrix(b)
    lhs = (det4(A, Z[1], Z[2], Z[3]) * det4(B, Z[1], Z[3], Z[4])
           - det4(B, Z[1], Z[2], Z[3]) * det4(A, Z[1], Z[3], Z[4]))
    rhs = br(A, B, 1, 3) * det4(Z[1], Z[2], Z[3], Z[4])
    print(f"   <AB(123)n(134)> == <AB13><1234> for generic A,B: "
          f"{sp.simplify(lhs - rhs) == 0}")
    print("   (so at n=4 the single Kermit term collapses to the box —")
    print("   consistent with Lab 5's result.)\n")


def main() -> None:
    warmup_n4()

    cells = [(2, 3), (2, 4), (3, 4)]
    physical = [(1, 2), (2, 3), (3, 4), (4, 5), (1, 5)]

    print("1. Three cells, each an exact dlog orthant")
    for i, j in cells:
        A, B, (x, w, y, z) = chart(i, j)
        ratio = sp.simplify(sp.cancel(
            kermit(A, B, i, j) * br(A, B, i, i + 1) * br(A, B, j, j + 1)
            * x * w * y * z))
        print(f"   cell ({i},{j}):  K_{i}{j} x <AB {i}{i+1}><AB {j}{j+1}> "
              f"x (xwyz) = {ratio}")
    print("   Each Kermit term IS dlog x ^ dlog w ^ dlog y ^ dlog z on its")
    print("   cell — pure dlog forms, no numerator ambiguity, exactly.\n")

    print("2. Sign-flip dictionary: the cell label IS the flip positions")
    for i, j in cells:
        A, B, _ = chart(i, j)
        phys_signs = [definite_sign(br(A, B, p, q)) for p, q in physical]
        seq = [definite_sign(br(A, B, 1, m)) for m in range(2, 6)]
        flips = sum(1 for u, v in zip(seq, seq[1:]) if u * v < 0)
        flip_pos = [m for m, (u, v) in enumerate(zip(seq, seq[1:]), start=2)
                    if u * v < 0]
        print(f"   cell ({i},{j}): physical brackets {phys_signs}, "
              f"<AB1m> signs {seq} -> {flips} flips at {flip_pos}")
    print("   All five physical brackets have definite sign on every cell;")
    print("   the sequence <AB12>,<AB13>,<AB14>,<AB15> flips exactly at the")
    print("   cell's label (i,j). Distinct sign patterns -> the cells are")
    print("   disjoint: a genuine decomposition, not an overcount.\n")

    print("3. Spurious poles cancel in M5 = K23 + K24 + K34")
    B0 = -Z[1] + 2 * Z[3] + 3 * Z[4] + Z[5]      # generic-ish rational line
    for label, mk_A in (
        ("<AB13> -> 0", lambda e: Z[1] + 2 * Z[3] + e * Z[2]),
        ("<AB14> -> 0", lambda e: Z[1] + 3 * Z[4] + e * Z[2]),
    ):
        print(f"   {label}:")
        print(f"   {'eps':>8} {'K23':>13} {'K24':>13} {'K34':>13} {'sum':>12}")
        for kexp in (2, 4, 6):
            eps = sp.Rational(1, 10 ** kexp)
            A0 = mk_A(eps)
            terms = [kermit(A0, B0, i, j) for i, j in cells]
            print(f"   {f'1e-{kexp}':>8} "
                  + " ".join(f"{sp.Float(t, 5):>13}" for t in terms)
                  + f" {sp.Float(sum(terms), 5):>12}")
    print("   Individual cells diverge on the seams <AB13>, <AB14>; the sum")
    print("   is finite there (exact rational arithmetic). Only the physical")
    print("   poles <AB i i+1> — the unitarity cuts — survive: same seam-")
    print("   cancellation mechanism as the tree amplituhedron (Lab 4), one")
    print("   loop up.")


if __name__ == "__main__":
    main()
