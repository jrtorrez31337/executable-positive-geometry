"""Milestone 3, Part 2 — entanglement as proto-geometry.

Same transverse-field Ising chain, exact ground states (N=12, brute force).
Three measurements, three lessons:

  A. Half-chain entanglement entropy vs h, with and without a tiny
     symmetry-breaking field hz. Without it, the ordered phase hides in a
     global cat state (all-up + all-down) whose ln 2 of entropy swamps the
     signal; with the cat collapsed, the genuine quantum-critical PEAK
     near h = J stands alone.

  B. Entropy profile S(l) across every cut, critical vs off-critical:
     off-critical obeys the 1D "area law" (flat — boundary-sized, not
     volume-sized); critical grows logarithmically following the
     Calabrese-Cardy finite-size law S(l) = (c/6) ln[chord(l)] + const,
     chord(l) = (2N/pi) sin(pi l / N), with c = 1/2 the Ising CFT
     central charge — a universal number read straight out of entanglement.

  C. Mutual information I(i,j) between distant spins as an emergent
     RULER: d(i,j) = -ln I(i,j). In the disordered phase d grows
     linearly with separation (a flat geometry with a correlation
     length); at criticality it grows only logarithmically (scale-free,
     "everything is close to everything"). Geometry, read off from
     entanglement — the 1D shadow of the Ryu-Takayanagi idea.

Entropies in nats (natural log). GHZ note: deep in the ordered phase the
half-chain entropy sits at ln 2 = 0.693 — the two symmetry-broken worlds
(all-up / all-down) form a global cat state; that single bit of shared
uncertainty is not critical entanglement, which is why the PEAK, not the
plateau, marks the transition.
"""

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh

N = 12
J = 1.0

I2 = np.eye(2)
SX = np.array([[0, 1], [1, 0]], dtype=float)
SZ = np.array([[1, 0], [0, -1]], dtype=float)


def op_at(op: np.ndarray, site: int) -> sp.csr_matrix:
    full = sp.identity(1, format="csr")
    for s in range(N):
        full = sp.kron(full, sp.csr_matrix(op if s == site else I2), format="csr")
    return full


def hamiltonian(h: float, hz: float = 0.0) -> sp.csr_matrix:
    dim = 2**N
    H = sp.csr_matrix((dim, dim))
    for i in range(N - 1):
        H -= J * (op_at(SZ, i) @ op_at(SZ, i + 1))
    for i in range(N):
        H -= h * op_at(SX, i)
        if hz:
            H -= hz * op_at(SZ, i)
    return H


def ground_state(h: float, hz: float = 0.0) -> np.ndarray:
    if hz == 0.0:
        # Dense eigh: reliably resolves the exponentially split cat doublet.
        vals, vecs = np.linalg.eigh(hamiltonian(h).toarray())
        return vecs[:, 0]
    # Symmetry broken -> unique ground state, Lanczos is safe and fast.
    vals, vecs = eigsh(hamiltonian(h, hz), k=1, which="SA")
    return vecs[:, 0]


def entropy_of_cut(psi: np.ndarray, l: int) -> float:
    """Von Neumann entropy of the first l spins (nats)."""
    lam = np.linalg.svd(psi.reshape(2**l, 2 ** (N - l)), compute_uv=False)
    p = lam**2
    p = p[p > 1e-12]
    return float(-np.sum(p * np.log(p)))


def rho_of_sites(psi: np.ndarray, sites: tuple[int, ...]) -> np.ndarray:
    """Reduced density matrix of the given sites (partial trace of the rest)."""
    tensor = psi.reshape([2] * N)
    keep = list(sites)
    rest = [s for s in range(N) if s not in keep]
    tensor = np.transpose(tensor, keep + rest)
    mat = tensor.reshape(2 ** len(keep), 2 ** len(rest))
    return mat @ mat.conj().T


def vn_entropy(rho: np.ndarray) -> float:
    p = np.linalg.eigvalsh(rho)
    p = p[p > 1e-12]
    return float(-np.sum(p * np.log(p)))


def mutual_information(psi: np.ndarray, i: int, j: int) -> float:
    s_i = vn_entropy(rho_of_sites(psi, (i,)))
    s_j = vn_entropy(rho_of_sites(psi, (j,)))
    s_ij = vn_entropy(rho_of_sites(psi, (i, j)))
    return s_i + s_j - s_ij


def bar(x: float, scale: float = 40) -> str:
    return "#" * max(0, round(x * scale))


def main() -> None:
    print(f"TFIM chain, N={N}, exact ground states\n")

    print("A. Half-chain entanglement entropy vs transverse field h")
    print(f"   {'':14}{'hz=0 (cat state)':>17}   {'hz=1e-3 (cat collapsed)'}")
    hs = (0.2, 0.5, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0, 3.0)
    states = {h: ground_state(h) for h in hs}
    for h in hs:
        s_cat = entropy_of_cut(states[h], N // 2)
        s_true = entropy_of_cut(ground_state(h, hz=1e-3), N // 2)
        print(f"   h={h:4.1f}  S_cat={s_cat:6.4f}   S={s_true:6.4f}  |{bar(s_true)}")
    print("   ln 2 =", f"{np.log(2):.4f}", "— the cat plateau (left column) is")
    print("   one classical bit of global uncertainty, killed by an infinitesimal")
    print("   field; the surviving peak near h=J is genuine critical entanglement.\n")

    print("B. Entropy profile S(l) for every cut position l")
    print(f"   {'l':>3} {'h=1.0 (critical)':>17} {'h=2.0 (off-critical)':>21}")
    crit, off = states[1.0], states[2.0]
    for l in range(1, N):
        print(f"   {l:>3} {entropy_of_cut(crit, l):>17.4f} {entropy_of_cut(off, l):>21.4f}")
    # CFT check with proper finite-size scaling (Calabrese-Cardy):
    #   S(l) = (c/6) ln[ (2N/pi) sin(pi l / N) ] + const
    ls = np.arange(1, N)
    ss = np.array([entropy_of_cut(crit, int(l)) for l in ls])
    chord = (2 * N / np.pi) * np.sin(np.pi * ls / N)
    c_fit = 6 * np.polyfit(np.log(chord), ss, 1)[0]
    print(f"   Calabrese-Cardy fit at h=1.0: c = {c_fit:.2f} "
          f"(Ising CFT predicts c = 0.50)\n")

    print("C. Emergent distance d(i,j) = -ln I(i,j) from spin 0")
    print(f"   {'|i-j|':>6} {'d at h=1.0':>11} {'d at h=2.0':>11}")
    for j in range(1, N):
        d_crit = -np.log(mutual_information(crit, 0, j))
        d_off = -np.log(mutual_information(off, 0, j))
        print(f"   {j:>6} {d_crit:>11.2f} {d_off:>11.2f}")
    print("\n   Off-critical: d grows ~linearly — an ordinary ruler, geometry")
    print("   with a correlation length. Critical: d grows only ~logarithmically")
    print("   — scale-free connectivity, the entanglement pattern a MERA/")
    print("   holographic network mimics. Same chain, two emergent geometries,")
    print("   selected by one coupling constant.")


if __name__ == "__main__":
    main()
