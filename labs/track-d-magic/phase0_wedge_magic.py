"""Track D, Phase 0 — wedge-resolved magic in holographic codes.

THE QUESTION (new: answer unknown to us before running): information in
our holographic codes is wedge-quantized — minority regions know nothing,
majority regions know everything (measured, incl. on hardware). Does
MAGIC (non-stabilizerness, the resource separating quantum computation
from classical simulability) obey the same all-or-nothing wedge law when
a magic bulk state is injected — or does it leak, spread, or concentrate
differently, as its gravitational back-reaction interpretation might
suggest?

PRE-REGISTERED PREDICTION (Ariadne, before running): quantized, mirroring
information — M2 = 0 for minority regions, M2 = log2(4/3) ~ 0.415 for
majority regions — because the wedge reduction inherits the logical
Pauli spectrum intact. Falsifiable by the tables below.

Measure: stabilizer Renyi entropy (alpha=2). For a region's reduced
density matrix rho:
    M2(rho) = -log2 [ sum_P Tr(rho P)^4 / sum_P Tr(rho P)^2 ]
(reduces to the standard pure-state SRE; equals 0 on stabilizer states,
pure or mixed. CAVEAT, stated honestly: for mixed states this quantity
is a computable magic diagnostic, not a proven monotone.)

Engine: all 4^k Pauli expectations of a k-qubit rho at once via
fast Walsh-Hadamard transforms (Tr(rho P_{x,z}) = i^{x.z} WHT_z of the
x-th shifted diagonal), self-tested against direct enumeration.
"""

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent / ".." / "capstone-happy"))
from happy_tile import build_codewords  # noqa: E402
from happy_network import network  # noqa: E402

LN2 = np.log(2)


# ─── Pauli-spectrum engine ───────────────────────────────────────────────────

def fwht(a):
    """Fast Walsh-Hadamard transform of a 1-D array of length 2^k."""
    a = a.copy()
    n = a.size
    h = 1
    while h < n:
        a = a.reshape(-1, 2, h)
        x, y = a[:, 0, :].copy(), a[:, 1, :].copy()
        a[:, 0, :], a[:, 1, :] = x + y, x - y
        a = a.reshape(-1)
        h *= 2
    return a


def pauli_moments(rho):
    """(sum of Tr(rho P)^2, sum of Tr(rho P)^4) over all 4^k Paulis."""
    k = int(np.log2(rho.shape[0]))
    n = 2 ** k
    idx = np.arange(n)
    s2 = s4 = 0.0
    for x in range(n):
        diag = rho[idx ^ x, idx]                      # rho[m^x, m]
        t = fwht(diag)                                # sum_m diag * (-1)^{z.m}
        # phase i^{x.z} makes P Hermitian; |Tr|^2 is phase-free:
        vals2 = np.abs(t) ** 2
        s2 += float(np.sum(vals2))
        s4 += float(np.sum(vals2 ** 2))
    return s2, s4


def m2(rho):
    s2, s4 = pauli_moments(rho)
    return float(-np.log2(s4 / s2))


def reduce_state(psi, keep, nq):
    rest = [q for q in range(nq) if q not in keep]
    m = psi.reshape([2] * nq).transpose(list(keep) + rest).reshape(
        2 ** len(keep), -1)
    return m @ m.conj().T


def self_test():
    rng = np.random.default_rng(2)
    # direct enumeration on a random 2-qubit pure state
    P1 = {
        "I": np.eye(2, dtype=complex),
        "X": np.array([[0, 1], [1, 0]], dtype=complex),
        "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    }
    v = rng.normal(size=4) + 1j * rng.normal(size=4)
    v /= np.linalg.norm(v)
    rho = np.outer(v, v.conj())
    s2d = s4d = 0.0
    for a in "IXYZ":
        for b in "IXYZ":
            t = float(np.real(np.trace(rho @ np.kron(P1[a], P1[b]))))
            s2d += t ** 2
            s4d += t ** 4
    s2f, s4f = pauli_moments(rho)
    assert abs(s2d - s2f) < 1e-9 and abs(s4d - s4f) < 1e-9, "engine mismatch"
    # canonical values
    T = np.array([1, np.exp(1j * np.pi / 4)]) / np.sqrt(2)
    assert abs(m2(np.outer(T, T.conj())) - np.log2(4 / 3)) < 1e-9
    plus = np.array([1, 1]) / np.sqrt(2)
    assert abs(m2(np.outer(plus, plus.conj()))) < 1e-9
    print("Engine self-test passed: FWHT spectrum = direct enumeration;")
    print(f"M2(|T>) = log2(4/3) = {np.log2(4/3):.4f}; M2(stabilizer) = 0.\n")


# ─── Part 1: the single tile ─────────────────────────────────────────────────

def part1_tile():
    v0, v1 = build_codewords()
    psi_T = (v0 + np.exp(1j * np.pi / 4) * v1) / np.sqrt(2)
    psi_ctrl = (v0 + v1) / np.sqrt(2)                 # |+>_L : stabilizer
    rho_T = np.outer(psi_T, psi_T.conj())

    print("PART 1 — single tile, logical T-state injected (5 qubits)")
    print(f"   global M2 = {m2(rho_T):.4f}   "
          f"(injected magic log2(4/3) = {np.log2(4/3):.4f} — Clifford")
    print("   encoding preserves total magic)")
    print(f"   {'region size':>12} {'M2 (T bulk)':>12} {'M2 (|+> bulk ctrl)':>19}")
    from itertools import combinations
    for k in range(1, 5):
        vals_T, vals_c = [], []
        for sub in combinations(range(5), k):
            vals_T.append(m2(reduce_state(psi_T, sub, 5)))
            vals_c.append(m2(reduce_state(psi_ctrl, sub, 5)))
        print(f"   {k:>12} {min(vals_T):>5.3f}..{max(vals_T):<5.3f} "
              f"{min(vals_c):>8.3f}..{max(vals_c):<5.3f}")
    print()


# ─── Part 2: the flower ──────────────────────────────────────────────────────

def flower_with_bulk(petal_states):
    """petal_states: list of 5 single-qubit vectors for the petal bulks."""
    psi = np.zeros(2 ** 20, dtype=complex)
    from itertools import product
    for bits in product((0, 1), repeat=5):
        amp = np.prod([petal_states[i][b] for i, b in enumerate(bits)])
        if abs(amp) < 1e-14:
            continue
        branch = network(0, list(bits))
        psi = psi + amp * (branch / np.linalg.norm(branch))
    return psi / np.linalg.norm(psi)


def part2_flower():
    T = np.array([1, np.exp(1j * np.pi / 4)]) / np.sqrt(2)
    zero = np.array([1, 0], dtype=complex)
    plus = np.array([1, 1]) / np.sqrt(2)

    psi_T = flower_with_bulk([zero, T, zero, zero, zero])       # T in slot 2
    psi_c = flower_with_bulk([zero, plus, zero, zero, zero])    # control

    blocks = {f"petal {i} block (4q)": tuple(range(4 * (i - 1), 4 * i))
              for i in range(1, 6)}
    regions = dict(blocks)
    regions["slot-2 wedge minus 1q (3q)"] = (4, 5, 6)
    regions["half boundary w/ petal2 (8q)"] = tuple(range(4, 12))
    regions["half boundary w/o petal2 (8q)"] = (0, 1, 2, 3, 12, 13, 14, 15)
    regions["arc: petals 3+4+5 (12q)"] = tuple(range(8, 20))

    print("PART 2 — flower, T-state injected in slot 2 (20 boundary qubits)")
    print(f"   {'region':>28} {'M2 (T)':>8} {'M2 (ctrl)':>10}")
    for name, sub in regions.items():
        vT = m2(reduce_state(psi_T, sub, 20))
        vc = m2(reduce_state(psi_c, sub, 20))
        print(f"   {name:>28} {vT:>8.4f} {vc:>10.4f}")
    print(f"\n   reference values: log2(4/3) = {np.log2(4/3):.4f} "
          f"(the injected magic), 0 = stabilizer")


if __name__ == "__main__":
    self_test()
    part1_tile()
    part2_flower()
