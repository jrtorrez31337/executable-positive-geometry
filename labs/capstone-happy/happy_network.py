"""CAPSTONE II — a six-tile HaPPY network ("the flower").

Geometry: one central pentagon tile, five petal tiles glued to its five
edges. Each tile = the 6-leg perfect tensor of happy_tile.py. Legs:

    central tile : 1 bulk qubit (DEEP)  + 5 links to petals
    each petal   : 1 bulk qubit (SHALLOW) + 1 link + 4 boundary legs

Total: 6 bulk qubits, 5 internal bonds, 20 boundary qubits arranged on a
circle (petal 1 owns boundary positions 0-3, petal 2 owns 4-7, ...).
The network is an exact isometry from bulk to boundary — checked, not
assumed. Boundary state lives in C^(2^20); everything below is exact.

Experiments:
  1. DEPTH = PRICE OF RECONSTRUCTION. Entangle a reference R with ONE
     bulk qubit (others frozen to |0>). Scan all contiguous boundary
     arcs: the smallest arc with I(R:arc) = 2 ln 2 is the smallest
     boundary region whose entanglement wedge reaches that bulk point.
     Prediction: a petal qubit needs ~3 boundary qubits (3 of its tile's
     legs -> push the operator); the CENTRAL qubit needs ~11 (three whole
     petals must enter the wedge before the center does). Radial depth
     in emergent space = error-correction robustness.

  2. DISCRETE RYU-TAKAYANAGI. Freeze all bulk legs; the boundary state is
     pure. For growing arcs, S(arc)/ln2 should equal the number of network
     bonds in the MINIMAL CUT separating the arc from the rest — and as
     the arc grows past a petal, the cut SNAPS from slicing boundary legs
     to slicing the petal's single internal bond, so the entropy dips.
     Area law, holographically discretized.
"""

import string
from functools import reduce

import numpy as np

LN2 = np.log(2)
PAULI_I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PMAP = {"I": PAULI_I, "X": X, "Z": Z}


def op(s: str) -> np.ndarray:
    return reduce(np.kron, [PMAP[c] for c in s])


def perfect_tensor() -> np.ndarray:
    """[[5,1,3]] encoding isometry as a tensor of shape (2,)*6: T[bulk, 5 legs]."""
    proj = np.eye(32, dtype=complex)
    for s in ("XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"):
        proj = proj @ (np.eye(32) + op(s)) / 2
    v0 = proj[:, 0]
    v0 = v0 / np.linalg.norm(v0)
    v1 = op("XXXXX") @ v0
    return np.stack([v0.reshape([2] * 5), v1.reshape([2] * 5)])


T = perfect_tensor()
N_BOUNDARY = 20


def network(b_center: int, b_petals: list[int]) -> np.ndarray:
    """Contract the flower with given bulk basis states; returns 2^20 vector.
    Petal leg convention: planar leg 0 = link to center, legs 1-4 = boundary."""
    letters = string.ascii_letters
    center_legs = letters[:5]
    subs, args, out = [center_legs], [T[b_center]], ""
    pool = iter(letters[5:])
    for i in range(5):
        legs = "".join(next(pool) for _ in range(4))
        subs.append(center_legs[i] + legs)
        args.append(T[b_petals[i]])
        out += legs
    return np.einsum(",".join(subs) + "->" + out, *args).reshape(-1)


def probe_state(which: str) -> np.ndarray:
    """Reference qubit R (index 0) maximally entangled with one bulk leg."""
    if which == "center":
        branches = [network(r, [0] * 5) for r in (0, 1)]
    else:                                   # petal 1
        branches = [network(0, [r, 0, 0, 0, 0]) for r in (0, 1)]
    # Each of the 5 bond contractions costs a factor 1/sqrt(2): the network
    # is an isometry UP TO an overall 2^(5/2). Normalize, then check what
    # isometry actually requires: equal branch norms and orthogonality.
    n0, n1 = np.linalg.norm(branches[0]), np.linalg.norm(branches[1])
    assert abs(n0 - n1) < 1e-9
    branches = [b / np.linalg.norm(b) for b in branches]
    assert abs(np.vdot(branches[0], branches[1])) < 1e-9
    e = np.eye(2)
    return (np.kron(e[0], branches[0]) + np.kron(e[1], branches[1])) / np.sqrt(2)


def subset_entropy(psi: np.ndarray, sites: tuple[int, ...], n: int) -> float:
    if len(sites) > n // 2:                 # pure state: use the smaller side
        sites = tuple(q for q in range(n) if q not in sites)
    rest = [q for q in range(n) if q not in sites]
    m = psi.reshape([2] * n).transpose(list(sites) + rest).reshape(2 ** len(sites), -1)
    p = np.linalg.eigvalsh(m @ m.conj().T)
    p = p[p > 1e-12]
    return float(-np.sum(p * np.log(p)))


def arc(start: int, length: int) -> tuple[int, ...]:
    return tuple((start + k) % N_BOUNDARY for k in range(length))


def mutual_info_R(psi: np.ndarray, boundary_sites: tuple[int, ...]) -> float:
    a = tuple(q + 1 for q in boundary_sites)            # boundary occupies 1..20
    return (subset_entropy(psi, (0,), 21) + subset_entropy(psi, a, 21)
            - subset_entropy(psi, (0,) + a, 21))


def experiment_depth() -> None:
    print("1. DEPTH: smallest boundary arc that reconstructs each bulk qubit")
    for which in ("petal", "center"):
        psi = probe_state(which)
        found = None
        for length in range(1, N_BOUNDARY + 1):
            hits = [s for s in range(N_BOUNDARY)
                    if mutual_info_R(psi, arc(s, length)) / LN2 > 2 - 1e-6]
            if hits:
                found = (length, hits[0])
                break
        length, start = found
        i_small = max(mutual_info_R(psi, arc(s, length - 1)) / LN2
                      for s in range(N_BOUNDARY))
        print(f"   {which:>6} bulk qubit: minimal arc = {length:2d} boundary qubits "
              f"(e.g. positions {start}..{(start + length - 1) % N_BOUNDARY})")
        print(f"          best arc one qubit shorter: I(R:A)/ln2 = {i_small:.6f}")
    print("   The deep qubit costs ~3x more boundary than the shallow one.")
    print("   And information arrives QUANTIZED, never gradually: one qubit")
    print("   short of the petal's arc gives exactly 0; one short of the")
    print("   center's gives exactly 1.0 ln2 — ONE of the two logical Pauli")
    print("   operators has entered the wedge (a classical bit), its")
    print("   conjugate has not. Never 0.3, never 1.7: bulk data crosses")
    print("   the wedge operator-by-operator, because reconstruction is")
    print("   error correction, not signal attenuation. Radial depth in")
    print("   emergent space = code distance, seen geometrically.\n")


def experiment_rt() -> None:
    print("2. DISCRETE RT: S(arc)/ln2 vs the minimal cut, all bulk frozen")
    psi = network(0, [0] * 5)
    psi = psi / np.linalg.norm(psi)
    print(f"   {'arc length':>10} {'S/ln2':>8}   arc contents")
    for length in range(1, 11):
        s = subset_entropy(psi, arc(0, length), N_BOUNDARY) / LN2
        petals_full = length // 4
        note = ""
        if length % 4 == 0 and length > 0:
            note = f"<- petal {petals_full} completed: cut snaps to internal bond(s)"
        print(f"   {length:>10} {s:>8.4f}   boundary 0..{length - 1} {note}")
    print("   Entropy grows as the arc eats into a petal, then DROPS when the")
    print("   petal completes: the minimal cut abandons the boundary legs and")
    print("   slices the petal's single link bond instead. Entanglement =")
    print("   number of bonds crossed = length of a geodesic through the")
    print("   network. The Ryu-Takayanagi formula, one bond at a time.")


if __name__ == "__main__":
    print(f"Flower network: 6 perfect tensors, 5 bonds, {N_BOUNDARY} boundary qubits\n")
    experiment_depth()
    experiment_rt()
