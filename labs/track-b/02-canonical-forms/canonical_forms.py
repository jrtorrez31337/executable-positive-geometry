"""Track B, Lab 2 — canonical forms: the geometry IS the calculation.

A positive geometry comes equipped with a unique CANONICAL FORM: a rational
differential form with logarithmic poles exactly on the geometry's
boundaries, defined recursively —

    residue of Omega at a boundary  =  canonical form OF that boundary,
    ending at points (0-dim geometries), whose canonical form is +/-1.

For the amplituhedron, this form's value IS the scattering amplitude.
Here we build the recursion bottom-up on shapes we can draw:

  A. interval  ->  poles at the two endpoints, residues +1 / -1
  B. triangle  ->  residue on an edge = the edge's interval form
  C. THE FLAGSHIP: the unit square, triangulated two different ways.
     Each triangle contributes a term with a SPURIOUS pole (the diagonal —
     a boundary of the triangulation, not of the square). In the sum the
     spurious poles cancel exactly, and both triangulations give the SAME
     total form: the square's.

     Dictionary: triangles <-> individual Feynman/BCFW terms (each with
     unphysical singularities), the square <-> the amplitude (only physical
     poles), triangulation-independence <-> representation-independence of
     the amplitude. "Sum over diagrams" is just ONE way to triangulate.
"""

import sympy as sp

x, y = sp.symbols("x y")


def interval_form(a, b) -> sp.Expr:
    """Canonical form of [a,b] (coefficient of dx): dlog(x-a) - dlog(x-b)."""
    return sp.together(1 / (x - a) - 1 / (x - b))


def edge_residue(omega: sp.Expr, var, at) -> sp.Expr:
    """Residue of a 2-form coefficient along the line var = at."""
    return sp.simplify(sp.limit((var - at) * omega, var, at))


def main() -> None:
    print("A. Interval [0,1]:  Omega =", interval_form(0, 1), "dx")
    for pt in (0, 1):
        print(f"   residue at x={pt}: {sp.residue(interval_form(0, 1), x, pt)}")
    print("   Boundaries of the interval are two points, canonical forms +1, -1.\n")

    # B. Unit triangle, vertices (0,0), (1,0), (0,1); edges x=0, y=0, 1-x-y=0.
    tri = 1 / (x * y * (1 - x - y))
    print("B. Triangle:  Omega =", tri, "dx^dy")
    res_bottom = edge_residue(tri, y, 0)
    print(f"   residue on edge y=0: {res_bottom} dx")
    print(f"   equals the interval [0,1] form? "
          f"{sp.simplify(res_bottom - interval_form(0, 1)) == 0}")
    print("   Boundary of a positive geometry carries the boundary's own")
    print("   canonical form — in physics: residue at a pole = amplitude of")
    print("   the factorized sub-process. Singularities ARE sub-geometries.\n")

    # C. The unit square: only physical poles x=0, x=1, y=0, y=1.
    square = 1 / (x * (1 - x) * y * (1 - y))
    print("C. Square:  Omega =", square, "dx^dy")

    # Triangulation 1: diagonal from (0,0) to (1,1) — spurious pole (x-y).
    t1 = 1 / (y * (1 - x) * (x - y))          # triangle (0,0),(1,0),(1,1)
    t2 = 1 / (x * (1 - y) * (y - x))          # triangle (0,0),(1,1),(0,1)
    sum1 = sp.simplify(t1 + t2)
    print(f"\n   Triangulation 1 (diagonal (0,0)-(1,1), spurious pole x-y):")
    print(f"     term 1: {t1}")
    print(f"     term 2: {t2}")
    print(f"     sum   : {sum1}   -> equals square? {sp.simplify(sum1 - square) == 0}")

    # Triangulation 2: the OTHER diagonal (1,0)-(0,1) — spurious pole (1-x-y).
    u1 = 1 / (x * y * (1 - x - y))            # triangle (0,0),(1,0),(0,1)
    u2 = 1 / ((1 - x) * (1 - y) * (x + y - 1))  # triangle (1,0),(1,1),(0,1)
    sum2 = sp.simplify(u1 + u2)
    print(f"\n   Triangulation 2 (diagonal (1,0)-(0,1), spurious pole 1-x-y):")
    print(f"     term 1: {u1}")
    print(f"     term 2: {u2}")
    print(f"     sum   : {sum2}   -> equals square? {sp.simplify(sum2 - square) == 0}")

    print("""
   Each triangle term has a pole on the diagonal — a boundary of the
   TRIANGULATION, not of the square. In each sum those spurious poles
   cancel EXACTLY, leaving only the square's physical boundaries — and
   both triangulations agree. Feynman diagrams and BCFW terms are exactly
   such triangle-terms: individually they contain unphysical poles that
   cancel in the sum, which mystified people for decades — until the
   amplituhedron reframed it: the terms were never fundamental. They are
   one choice of triangulation of a single geometric object, and the
   AMPLITUDE IS THE CANONICAL FORM OF THE GEOMETRY.""")


if __name__ == "__main__":
    main()
