"""CAPSTONE VI — code-deformation holonomy: the twist, found or bounded.

Sequel to self_wedge.py, which proved the self-image is route-independent
while the rulebook stays fixed. Here we let the rulebook MOVE: a closed
loop in code space is an operation W = (qubit permutation) x (transversal
single-qubit Clifford U on every qubit) that maps the [[5,1,3]] stabilizer
group exactly back to itself. The code returns home; the logical qubit
need not. The induced logical rotation is the loop's HOLONOMY — the
measurable residue of transporting self-knowledge around a closed path of
self-descriptions.

We enumerate ALL 120 x 24 = 2880 candidate loops, keep the automorphisms,
measure each one's action on the logical Bloch frame, and assemble the
holonomy group. The Klein question is then sharp: does any loop reverse
the frame's orientation (det R = -1)? Quantum mechanics fixes the answer
in advance — unitary conjugation acts on the Bloch sphere by proper
rotations only; orientation reversal is antiunitary (time reversal). So
the census establishes exactly WHICH twists an embedded self-reader can
acquire (a nontrivial rotation group), and why the full mirror twist is
reserved for the one transformation no observer inside can enact.
"""

import pathlib
import sys
from functools import reduce
from itertools import permutations

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from happy_tile import build_codewords  # noqa: E402

PAULI = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
S = np.diag([1, 1j]).astype(complex)


def normalize_phase(m):
    idx = np.argmax(np.abs(m) > 1e-9)
    return m / (m.flat[idx] / abs(m.flat[idx]))


def single_qubit_cliffords():
    seen, frontier = {}, [np.eye(2, dtype=complex)]
    while frontier:
        m = frontier.pop()
        key = tuple(np.round(normalize_phase(m), 8).ravel())
        if key in seen:
            continue
        seen[key] = normalize_phase(m)
        frontier += [g @ m for g in (H, S)]
    return list(seen.values())


def op(chars):
    return reduce(np.kron, [PAULI[c] for c in chars])


STAB_STRINGS = ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"]
GENS = [op(s) for s in STAB_STRINGS]
GROUP = [np.eye(32, dtype=complex)]
for g in GENS:
    GROUP += [g @ h for h in GROUP]        # 16 signed elements


def perm_matrix(pi):
    P = np.zeros((32, 32))
    for idx in range(32):
        bits = [(idx >> (4 - k)) & 1 for k in range(5)]
        jdx = sum(bits[pi[k]] << (4 - k) for k in range(5))
        P[jdx, idx] = 1
    return P


def in_group(m):
    return any(np.allclose(m, g) for g in GROUP)


def main() -> None:
    v0, v1 = build_codewords()
    cliffs = single_qubit_cliffords()
    assert len(cliffs) == 24, len(cliffs)
    print(f"Searching {120 * len(cliffs)} candidate loops "
          f"(permutation x transversal Clifford)...")

    autos = []
    for pi in permutations(range(5)):
        P = perm_matrix(pi)
        for U in cliffs:
            W = P @ reduce(np.kron, [U] * 5)
            if all(in_group(W @ g @ W.conj().T) for g in GENS):
                autos.append((pi, U, W))
    print(f"Automorphisms (closed loops in code space): {len(autos)}\n")

    # logical action of each loop: L = P W P^dag on the code basis
    rotations = {}
    for pi, U, W in autos:
        L = np.array([[np.vdot(v0, W @ v0), np.vdot(v0, W @ v1)],
                      [np.vdot(v1, W @ v0), np.vdot(v1, W @ v1)]])
        assert np.allclose(L @ L.conj().T, np.eye(2)), "code space not preserved"
        R = np.zeros((3, 3))
        for a, sa in enumerate("XYZ"):
            for b, sb in enumerate("XYZ"):
                R[a, b] = np.real(np.trace(
                    PAULI[sa] @ L @ PAULI[sb] @ L.conj().T)) / 2
        rotations[tuple(np.round(R, 6).ravel())] = R

    print(f"Distinct logical holonomies: {len(rotations)}")
    orders, dets = {}, set()
    for R in rotations.values():
        dets.add(round(float(np.linalg.det(R)), 6))
        Rk, k = R.copy(), 1
        while not np.allclose(Rk, np.eye(3)) and k < 13:
            Rk, k = Rk @ R, k + 1
        orders[k] = orders.get(k, 0) + 1
        angle = np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))
        if k > 1 and orders[k] <= 2:        # print a sample of each order
            print(f"   sample holonomy: order {k}, rotation angle "
                  f"{angle:.0f} deg, det {np.linalg.det(R):+.0f}")
    print(f"   holonomy elements by order: {dict(sorted(orders.items()))}")
    print(f"   determinants observed: {sorted(dets)}\n")

    nontrivial = len(rotations) > 1
    mirror = -1.0 in dets
    print(f"VERDICT:")
    print(f"   nontrivial holonomy (self-image twisted by closed loops): "
          f"{nontrivial}")
    print(f"   orientation-reversing (Klein/mirror) holonomy: {mirror}")
    print("   Closed journeys through rulebook-space DO twist the logical")
    print("   frame — the residue self_wedge.py could not find at fixed code")
    print("   exists, and forms a genuine rotation group. But every twist is")
    print("   a PROPER rotation: det +1, always. The full mirror reversal is")
    print("   not forbidden by the code — it is forbidden by unitarity, since")
    print("   orientation reversal of the Bloch frame is antiunitary: time")
    print("   reversal. The one twist an embedded observer cannot acquire by")
    print("   any closed self-transport is the one that runs the film")
    print("   backwards — the Klein blueprint's missing move is TIME, which")
    print("   is where this project's map has said 'here be dragons' from")
    print("   the beginning.")


if __name__ == "__main__":
    main()
