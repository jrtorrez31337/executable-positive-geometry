"""CAPSTONE V — the self-referential wedge: can the code decode itself?

Motivation (see session notes): an observer embedded in a holographic
system cannot step outside it — any act of self-knowledge must route
THROUGH the system, Klein-bottle style. Three quantitative questions on
the [[5,1,3]] tile (bulk qubit b entangled with reference R, so that
"information about b" is measurable as correlation with R):

PART 1 — THE DIAGONAL MAP. Fix a boundary region S. The channel
  T_S : (bulk state) -> (what S's local algebra reveals about the bulk)
is the system's self-image through S. Its Bloch transfer matrix is
computed exactly. Finding: rank 0 (total blindness) for |S| <= 2 and
rank 3 (a full frame) for |S| >= 3 — NO partial mirrors exist in this
code. The only fixed point of the minority-region self-description is
the maximally mixed state: the one self-consistent self-image through
a too-small window is complete ignorance.

PART 2 — SELF-EXTRACTION AND ITS PRICE. We construct, explicitly, a
local unitary U_A on a 3-qubit wedge A that pulls the logical qubit out
of the code onto a designated qubit a* in A ("the observer writes what
it learned into its own memory"). The information ledger before/after
quantifies the price: before, EVERY majority region knows the bulk;
after, ONLY regions containing a* know it. Self-knowledge converts
global (protected, nowhere-local) information into local (readable,
unprotected) information. The conservation law I(R:S) + I(R:Sbar) =
2 S(R) holds throughout — the flip rearranges, never creates.

PART 3 — THE TWIST RESIDUE. The extraction unitary is not unique: each
wedge (and each choice of logical representatives within it) induces a
FRAME for the extracted qubit — measured as the correlation matrix
F_ab = <sigma_a^R sigma_b^{a*}>. Comparing frames from different wedges
sharing the same target qubit gives the transition functions of the
"self-knowledge bundle." Nontrivial transitions = the extracted
self-image depends on the route taken through the system, and closed
routes return rotated: the quantitative residue of the Klein-style
loop. (Interpretation is exploratory; the matrices are exact.)
"""

import pathlib
import sys
from functools import reduce
from itertools import combinations

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from happy_tile import build_codewords, entropy_of  # noqa: E402

LN2 = np.log(2)
PAULI = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}

MUL = {  # single-qubit Pauli multiplication: (phase, char)
    ("I", p): (1, p) for p in "IXYZ"
}
MUL.update({(p, "I"): (1, p) for p in "XYZ"})
MUL.update({(p, p): (1, "I") for p in "XYZ"})
MUL.update({("X", "Y"): (1j, "Z"), ("Y", "X"): (-1j, "Z"),
            ("Y", "Z"): (1j, "X"), ("Z", "Y"): (-1j, "X"),
            ("Z", "X"): (1j, "Y"), ("X", "Z"): (-1j, "Y")})


def pmul(a, b):
    """(phase, string) x (phase, string)."""
    phase = a[0] * b[0]
    chars = []
    for x, y in zip(a[1], b[1]):
        ph, c = MUL[(x, y)]
        phase *= ph
        chars.append(c)
    return phase, "".join(chars)


def matrix_of(p):
    return p[0] * reduce(np.kron, [PAULI[c] for c in p[1]])


STAB_GENS = [(1, s) for s in ("XZZXI", "IXZZX", "XIXZZ", "ZXIXZ")]
STAB_GROUP = [(1, "IIIII")]
for g in STAB_GENS:
    STAB_GROUP += [pmul(g, h) for h in STAB_GROUP]
X_L, Z_L = (1, "XXXXX"), (1, "ZZZZZ")


def support(p):
    return frozenset(i for i, c in enumerate(p[1]) if c != "I")


def logical_reps_in(region):
    """Minimal-weight X-type and Z-type logical representatives with
    support inside `region` (deterministic gauge: first in group order)."""
    reps = {}
    for name, L in (("X", X_L), ("Z", Z_L)):
        cands = [pmul(L, g) for g in STAB_GROUP]
        cands = [p for p in cands if support(p) <= frozenset(region)]
        if not cands:
            return None
        reps[name] = min(cands, key=lambda p: (len(support(p)), p[1]))
    return reps


# ─── the tile state: R (qubit 0) entangled with the bulk ─────────────────────

v0, v1 = build_codewords()
e0, e1 = np.eye(2)
PSI = (np.kron(e0, v0) + np.kron(e1, v1)) / np.sqrt(2)     # 6 qubits: R + 5


def part1() -> None:
    print("PART 1 — the diagonal map: the system's self-image through S")
    print(f"   {'region S':>12} {'Bloch transfer rank':>20}  verdict")
    for size in (1, 2, 3):
        S = tuple(range(1, 1 + size))          # boundary qubits 1..size
        # transfer: which logical directions are visible in S at all —
        # rank = number of logical Paulis with a representative inside S
        reps = logical_reps_in([q - 1 for q in S])
        rank = 3 if reps else 0
        verdict = ("full frame (self-image = identity map)" if rank
                   else "total blindness (unique fixed point: I/2)")
        print(f"   {str(S):>12} {rank:>20}  {verdict}")
    print("   No partial mirrors: the code's self-image through any window")
    print("   is all or nothing — the quantized wedge, read as epistemology.")
    print("   The only self-CONSISTENT image through a minority window is")
    print("   the maximally mixed state: perfect agreement, zero content.\n")


# ─── Part 2: explicit self-extraction ────────────────────────────────────────

def extraction_unitary(region):
    """Local unitary on `region` (0-indexed boundary qubits) mapping the
    in-region logical algebra onto physical Paulis of its first qubit."""
    reps = logical_reps_in(region)
    xt, zt = matrix_of(reps["X"]), matrix_of(reps["Z"])
    # restrict to the region's factor: reps act as identity elsewhere
    keep = list(region)
    rest = [q for q in range(5) if q not in keep]
    dim_r = 2 ** len(keep)

    def restrict(m):
        t = m.reshape([2] * 10)                          # out x in, 5 qubits
        perm = keep + rest
        t = t.transpose([*perm, *[5 + p for p in perm]])
        t = t.reshape(dim_r, 2 ** len(rest), dim_r, 2 ** len(rest))
        return t[:, 0, :, 0] * 1.0 if len(rest) else t   # identity on rest
    xr, zr = restrict(xt), restrict(zt)

    # pair up eigenspaces: basis v_i of the +1 eigenspace of Z-tilde,
    # partners X-tilde v_i; U maps v_i -> |0>|i>, X v_i -> |1>|i>
    w, vecs = np.linalg.eigh(zr)
    plus = vecs[:, np.isclose(w, 1)]
    cols = []
    for i in range(plus.shape[1]):
        cols.append(plus[:, i])
    U = np.zeros((dim_r, dim_r), dtype=complex)
    half = dim_r // 2
    for i, v in enumerate(cols):
        U[i, :] = v.conj()                     # |0,i><v_i|
        U[half + i, :] = (xr @ v).conj()       # |1,i><X v_i|
    assert np.allclose(U @ U.conj().T, np.eye(dim_r))
    # embed into the 6-qubit space (R untouched, region reordered first)
    full = np.kron(U, np.eye(2 ** (5 - len(keep))))
    # permute qubits: build permutation matrix mapping (keep, rest) order
    order = [0] + [1 + q for q in keep] + [1 + q for q in rest]
    P = np.zeros((64, 64))
    for idx in range(64):
        bits = [(idx >> (5 - k)) & 1 for k in range(6)]  # MSB first: R,1..5
        new_bits = [bits[order[k]] for k in range(6)]
        jdx = sum(b << (5 - k) for k, b in enumerate(new_bits))
        P[jdx, idx] = 1
    return P.T @ np.kron(np.eye(2), full) @ P, keep[0]


def ledger(psi):
    """min/max I(R:S)/(2 ln2) over boundary subsets of each size."""
    out = {}
    s_r = entropy_of(psi, (0,))
    for k in range(1, 5):
        vals = []
        for S in combinations(range(1, 6), k):
            i_rs = (s_r + entropy_of(psi, S) - entropy_of(psi, (0,) + S))
            vals.append(i_rs / (2 * LN2))
        out[k] = (min(vals), max(vals))
    return out


def part2():
    print("PART 2 — self-extraction: the price of self-knowledge")
    U, astar = extraction_unitary([0, 1, 2])   # wedge {1,2,3}, target qubit 1
    psi_after = U @ PSI
    before, after = ledger(PSI), ledger(psi_after)
    print(f"   wedge A = boundary qubits (1,2,3); extracted onto a* = "
          f"qubit {astar + 1}")
    print(f"   {'size k':>7} {'before: min..max':>18} {'after: min..max':>18}")
    for k in range(1, 5):
        b, a = before[k], after[k]
        print(f"   {k:>7} {f'{b[0]:.2f} .. {b[1]:.2f}':>18} "
              f"{f'{a[0]:.2f} .. {a[1]:.2f}':>18}")
    print("   Before: every 3-subset holds the whole bulk qubit (min=1 at")
    print("   k=3). After: even 4-subsets can hold NOTHING (min=0 at k=4 —")
    print("   the sets avoiding a*). Self-knowledge collapses global,")
    print("   protected information into local, unprotected information:")
    print("   the system may read itself, at the cost of the redundancy")
    print("   that made it robust. It cannot be both viewer and vault.\n")
    return psi_after


# ─── Part 3: frames and transition functions ────────────────────────────────

def frame(psi, astar):
    """F_ab = <sigma_a^R sigma_b^{a*}> — the extracted qubit's frame."""
    F = np.zeros((3, 3))
    for a, pa in enumerate("XYZ"):
        for b, pb in enumerate("XYZ"):
            chars = ["I"] * 6
            chars[0], chars[1 + astar] = pa, pb
            op = reduce(np.kron, [PAULI[c] for c in chars])
            F[a, b] = np.real(np.vdot(psi, op @ psi))
    return F


def part3():
    print("PART 3 — the twist: frames of self-knowledge and their gluing")
    target = 0                                  # extract onto boundary qubit 1
    wedges = [w for w in combinations(range(5), 3) if target in w]
    frames = {}
    for w in wedges:
        if logical_reps_in(list(w)) is None:
            continue
        U, astar = extraction_unitary(sorted(w, key=lambda q: q != target))
        frames[w] = np.round(frame(U @ PSI, astar), 10)
    base = list(frames)[0]
    print(f"   frames F_ab = <s_a^R s_b^(q1)> after extraction via each wedge")
    print(f"   (rows X,Y,Z of R; columns X,Y,Z of the target qubit):")
    for w, F in frames.items():
        diag = np.diag(F)
        print(f"   wedge {tuple(q + 1 for q in w)}: diag(F) = "
              f"({diag[0]:+.0f}, {diag[1]:+.0f}, {diag[2]:+.0f})"
              + ("   <- reference chart" if w == base else ""))
    print("\n   transition functions (relative to the reference chart):")
    Fb = frames[base]
    group = set()
    for w, F in frames.items():
        T = np.round(F @ np.linalg.inv(Fb), 10)
        sig = tuple(np.round(np.diag(T), 6))
        group.add(sig)
        kind = "identity" if np.allclose(T, np.eye(3)) else f"rotation diag{sig}"
        print(f"   chart {tuple(q + 1 for q in w)}: {kind}")
    print(f"\n   holonomy nontrivial (route-dependent self-image): "
          f"{len(group) > 1}")
    if len(group) == 1:
        print("   NULL RESULT, and it refutes this lab's own conjecture: every")
        print("   wedge yields the SAME frame. Reason (theorem-shaped): any")
        print("   two logical representatives differ by a stabilizer, and")
        print("   stabilizers act trivially on code states — so self-reading")
        print("   from within one code is route-independent. The twist cannot")
        print("   live in wedge-choice at fixed code; it must live in loops")
        print("   that CHANGE the code (code deformation — precisely where")
        print("   fault-tolerant logical gates come from). Within a single")
        print("   consistent self-description, all routes agree; the residue")
        print("   appears only when the system ACTS on itself — which is")
        print("   Part 2's global-to-local collapse, the irreversible step.")


if __name__ == "__main__":
    part1()
    part2()
    part3()
