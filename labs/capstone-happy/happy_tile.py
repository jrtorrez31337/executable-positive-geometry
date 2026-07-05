"""CAPSTONE — one tile of the HaPPY holographic code.

(Pastawski-Yoshida-Harlow-Preskill, corpus/2-holography-emergence/1503.06237)

The HaPPY model tiles the hyperbolic plane with pentagons; on each sits a
6-legged PERFECT TENSOR: the encoding isometry of the [[5,1,3]] quantum
code. One leg points into the bulk (a logical qubit = a point of emergent
space); five legs are the boundary. Gluing tiles grows a discrete AdS
geometry. Here we build ONE tile exactly (64-dim state vector, no
approximations) and verify the three claims that make holography work:

  1. PERFECT TENSOR: across EVERY 3|3 split of the six qubits, the state
     is maximally entangled. Entanglement is spread perfectly evenly —
     the "isotropy" that lets geometry emerge without preferred directions.

  2. THE INFORMATION PHASE TRANSITION (baby Ryu-Takayanagi): entangle the
     bulk leg with an external reference R. Then for ANY boundary region A,
         |A| <= 2  =>  I(R:A) = 0        (A knows NOTHING about the bulk)
         |A| >= 3  =>  I(R:A) = 2 ln 2   (A knows EVERYTHING)
     The bulk point sits in the entanglement wedge of any majority region;
     minority regions are blind. Information jumps — it is never partial.

  3. OPERATOR PUSHING (baby bulk reconstruction): the logical X on the
     bulk qubit has DIFFERENT representations supported on different
     3-qubit boundary regions — multiply by stabilizers, which act
     trivially on the code space. One bulk operator, many boundary
     avatars: this is AdS-Rindler wedge reconstruction in miniature, and
     the mechanism (Almheiri-Dong-Harlow) is quantum error correction.

The [[5,1,3]] code: stabilizers = cyclic shifts of XZZXI;
logical X = XXXXX, logical Z = ZZZZZ; distance 3.
"""

from functools import reduce
from itertools import combinations

import numpy as np

PAULI = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}
LN2 = np.log(2)


def op(pauli_string: str) -> np.ndarray:
    return reduce(np.kron, [PAULI[c] for c in pauli_string])


STABILIZERS = ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"]


def build_codewords() -> tuple[np.ndarray, np.ndarray]:
    """|0_L> by projecting |00000> onto the +1 eigenspace of all stabilizers;
    |1_L> = X_L |0_L>."""
    proj = np.eye(32, dtype=complex)
    for s in STABILIZERS:
        proj = proj @ (np.eye(32) + op(s)) / 2
    v0 = proj[:, 0]                      # projector applied to |00000>
    v0 = v0 / np.linalg.norm(v0)
    v1 = op("XXXXX") @ v0
    return v0, v1


def entropy_of(psi: np.ndarray, sites: tuple[int, ...], n: int = 6) -> float:
    """Von Neumann entropy (nats) of a subset of qubits. Qubit 0 = reference R,
    qubits 1..5 = the boundary."""
    keep = list(sites)
    rest = [q for q in range(n) if q not in keep]
    m = psi.reshape([2] * n).transpose(keep + rest).reshape(2 ** len(keep), -1)
    p = np.linalg.eigvalsh(m @ m.conj().T)
    p = p[p > 1e-12]
    return float(-np.sum(p * np.log(p)))


def main() -> None:
    v0, v1 = build_codewords()

    # Sanity: orthonormal codewords, correct stabilizer/logical action.
    assert abs(np.vdot(v0, v0) - 1) < 1e-10 and abs(np.vdot(v0, v1)) < 1e-10
    for s in STABILIZERS:
        assert np.allclose(op(s) @ v0, v0) and np.allclose(op(s) @ v1, v1)
    assert np.allclose(op("ZZZZZ") @ v0, v0) and np.allclose(op("ZZZZZ") @ v1, -v1)
    print("[[5,1,3]] code built: stabilizers verified, codewords orthonormal.\n")

    # The tile state: bulk leg maximally entangled with reference R.
    e0, e1 = np.eye(2)[0], np.eye(2)[1]
    psi = (np.kron(e0, v0) + np.kron(e1, v1)) / np.sqrt(2)

    print("1. PERFECT TENSOR: entropy of every 3-qubit subset of the 6 legs")
    entropies = {sub: entropy_of(psi, sub) / LN2 for sub in combinations(range(6), 3)}
    lo, hi = min(entropies.values()), max(entropies.values())
    print(f"   all {len(entropies)} subsets: S/ln2 in [{lo:.10f}, {hi:.10f}]")
    print("   Every 3|3 cut is maximally entangled (3 bits): entanglement is")
    print("   perfectly isotropic — no leg, no direction is special.\n")

    print("2. BABY RYU-TAKAYANAGI: bulk-boundary mutual information I(R:A)")
    s_r = entropy_of(psi, (0,))
    print(f"   {'|A|':>4} {'I(R:A)/ln2 across ALL regions A':>35}")
    for k in range(1, 6):
        vals = []
        for a in combinations(range(1, 6), k):
            i_ra = s_r + entropy_of(psi, a) - entropy_of(psi, (0,) + a)
            vals.append(i_ra / LN2)
        print(f"   {k:>4} {f'min={min(vals):.10f}  max={max(vals):.10f}':>35}")
    print("   Minority regions (1 or 2 qubits): EXACTLY zero — the bulk point")
    print("   is outside their entanglement wedge. Majority regions (3+): the")
    print("   full 2 bits — complete recovery. Nothing in between, ever: the")
    print("   RT surface jumps across the bulk point discontinuously.\n")

    print("3. OPERATOR PUSHING: one bulk operator, many boundary homes")
    # Multiplying X_L by a stabilizer changes nothing on the code space
    # but relocates the operator's support.
    o1 = op("XXXXX") @ op(STABILIZERS[0])
    o2 = op("XXXXX") @ op(STABILIZERS[1])
    assert np.allclose(o1, -op("IYYIX")) and np.allclose(o2, -op("XIYYI"))
    x_on_r = np.kron(PAULI["X"], np.eye(32))
    for o, label, support in ((o1, "-(I Y Y I X)", "{2,3,5}"),
                              (o2, "-(X I Y Y I)", "{1,3,4}")):
        same = np.allclose(np.kron(PAULI["I"], o) @ psi, x_on_r @ psi)
        print(f"   X_L == {label}  on boundary qubits {support}: "
              f"acts as bulk-X? {same}")
    print("   Two DIFFERENT 3-qubit boundary regions each carry a complete")
    print("   copy of the bulk operator (and by part 2, no 2-qubit region")
    print("   carries any). A bulk point is not 'at' a boundary location —")
    print("   it is redundantly encoded across all majority regions. That")
    print("   redundancy pattern IS its location in emergent space.\n")

    print("Scaling out (what the full HaPPY tiling adds): glue tiles so five")
    print("pentagons meet at each vertex — negative curvature, a discrete")
    print("hyperbolic disk. Deep bulk qubits need ever-larger boundary regions")
    print("to reconstruct: radial depth = error-correction robustness. Minimal")
    print("cuts through the network compute entanglement entropies (RT), and")
    print("erasing boundary chunks removes exactly the bulk region whose wedge")
    print("was lost. Geometry = the code's protection structure, at scale.")


if __name__ == "__main__":
    main()
