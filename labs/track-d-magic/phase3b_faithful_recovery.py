"""Track D, Phase 3b — faithful mixed-bulk backreaction with PETZ recovery.

Phase 3 failed its monotonic-increase prediction because it fixed the matter
entropy to H(lambda), discarding the deformed-recovery term where Theorem 4.2
(Cao-Cheng-Karthikeyan-Li-Preskill 2603.13475, Sec 4.1) actually lives. This
version computes the matter entropy properly:

    S_matter = S(sigma^{R}_{A1}),   sigma^{R}_{A1} = recovered bulk on A1,

using the PETZ recovery map R (maximally-mixed reference) for the encoding-
to-wedge channel N: L -> A. The Petz map is the canonical near-optimal
recovery in the entanglement-wedge/JLMS literature; it is exact (perfect
recovery) for the undeformed code and degrades smoothly under the skew. This
is a faithful-but-approximate stand-in for the paper's optimal R* (which
maximizes coherent information); labeled as such.

Channel / recovery (all small: dims 2, 8, 32):
  V_eps : L(2) -> phys(32),  columns [skew v0, skew v1]
  A = wedge qubits {0,1,2} (3q, recovers the logical); Abar = {3,4} (2q)
  N(rho) = Tr_Abar(V_eps rho V_eps^t) = sum_j K_j rho K_j^t   (Kraus K_j)
  rho_A0 = N(I/2);   Petz R(X) = sum_j M_j X M_j^t,  M_j = (1/sqrt2) K_j^t rho_A0^{-1/2}
  recovered bulk (still entangled with reference r):
     sigma_{L,r} = (R (x) I_r)(rho_{A,r}),  S_matter = S(Tr_r sigma_{L,r})
  proto-area  S_PA = S(rho_A) - S_matter,  averaged over Haar SU(2) on L.

PRE-REGISTERED PREDICTIONS (unchanged from Phase 3; now with proper recovery):
  P-1 exact code: proto-area FLAT in bulk entropy (Petz = perfect recovery,
      S_matter = H(lambda), S_PA = const area).
  P-2 skewed code: <S_PA> INCREASES monotonically with bulk entropy
      H(lambda) (Theorem 4.2). [the claim Phase 3 could not test]
  P-3 the effect scales with the skew and vanishes as theta -> 0.
Outcome reported honestly regardless of direction.
"""

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent / ".." / "capstone-happy"))
from happy_tile import build_codewords  # noqa: E402
from phase2_backreaction import skew_unitary  # noqa: E402

LN2 = np.log(2)
N_AVG = 40


def binary_entropy(lam):
    return 0.0 if lam in (0.0, 1.0) else float(
        -(lam * np.log2(lam) + (1 - lam) * np.log2(1 - lam)))


def vn_bits(rho):
    p = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    p = p[p > 1e-12]
    return float(-np.sum(p * np.log(p)) / LN2)


def inv_sqrt(rho, tol=1e-10):
    w, U = np.linalg.eigh((rho + rho.conj().T) / 2)
    inv = np.array([1 / np.sqrt(x) if x > tol else 0.0 for x in w])
    return U @ np.diag(inv) @ U.conj().T


def haar_su2(rng):
    m = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
    q, r = np.linalg.qr(m)
    return q @ np.diag(np.diag(r) / np.abs(np.diag(r)))


def petz_kraus(v0, v1, theta):
    """Kraus ops {M_j} of the Petz recovery R: A(8) -> L(2) for the skewed
    encoding-to-wedge channel. A = qubits {0,1,2}, Abar = {3,4}."""
    V = np.stack([v0, v1], axis=1)                 # 32 x 2 isometry
    V = skew_unitary(theta) @ V                    # skewed encoder
    Vr = V.reshape(8, 4, 2)                        # [A, Abar, L]
    K = [Vr[:, j, :] for j in range(4)]            # Kraus of N: K_j is 8x2
    rhoA0 = sum(k @ (0.5 * np.eye(2)) @ k.conj().T for k in K)   # N(I/2), 8x8
    inv = inv_sqrt(rhoA0)
    return [(1 / np.sqrt(2)) * k.conj().T @ inv for k in K]      # M_j: 2x8


def joint_A_r(lam, U, v0, v1, theta):
    """rho_{A,r} (16x16) for a mixed logical (Schmidt lam, rotated by U),
    skew-encoded, wedge A={0,1,2} kept, Abar={3,4} traced, r kept."""
    s0, s1 = np.sqrt(lam), np.sqrt(1 - lam)
    Uskew = skew_unitary(theta)
    r0 = Uskew @ (s0 * (U[0, 0] * v0 + U[1, 0] * v1))   # r=0 physical branch
    r1 = Uskew @ (s1 * (U[0, 1] * v0 + U[1, 1] * v1))   # r=1 branch
    Psi = np.stack([r0, r1], axis=1)               # (32, 2) = (phys, r)
    Psi = Psi.reshape(8, 4, 2)                      # (A, Abar, r)
    # rho_{A,r} = sum_Abar |A,r><A',r'|
    M = Psi.transpose(0, 2, 1).reshape(16, 4)       # (A*r, Abar)
    return M @ M.conj().T                           # 16x16, index (A r)


def recovered_matter_entropy(rho_Ar, Ms):
    """(R (x) I_r) rho_{A,r} -> recovered (L,r); S_matter = S(Tr_r)."""
    I2 = np.eye(2)
    sig = np.zeros((4, 4), dtype=complex)           # (L, r)
    for M in Ms:
        MI = np.kron(M, I2)                         # 4 x 16
        sig += MI @ rho_Ar @ MI.conj().T
    sig /= np.trace(sig)
    rhoL = sig.reshape(2, 2, 2, 2).trace(axis1=1, axis2=3)   # trace r
    return vn_bits(rhoL)


def SA(rho_Ar):
    rhoA = rho_Ar.reshape(8, 2, 8, 2).trace(axis1=1, axis2=3)   # trace r
    return vn_bits(rhoA)


def proto_area_avg(lam, v0, v1, theta, rng):
    Ms = petz_kraus(v0, v1, theta)
    spa = []
    for _ in range(N_AVG):
        U = haar_su2(rng)
        rho_Ar = joint_A_r(lam, U, v0, v1, theta)
        spa.append(SA(rho_Ar) - recovered_matter_entropy(rho_Ar, Ms))
    return float(np.mean(spa))


def main():
    v0, v1 = build_codewords()
    rng = np.random.default_rng(20)
    lambdas = [0.03, 0.08, 0.15, 0.25, 0.35, 0.5]   # ascending bulk entropy
    theta = np.pi * 0.15

    # sanity: exact-code Petz recovery is perfect (S_matter == H(lambda))
    Ms0 = petz_kraus(v0, v1, 0.0)
    U = haar_su2(rng)
    chk = recovered_matter_entropy(joint_A_r(0.25, U, v0, v1, 0.0), Ms0)
    print(f"Phase 3b — Petz recovery. Sanity: exact-code S_matter(lam=.25) = "
          f"{chk:.4f} vs H(.25) = {binary_entropy(0.25):.4f}\n")

    # paper convention (Eq 4.9): S_PA = S(chi) - S_corr, with S(chi) = the
    # exact-code proto-area (the fixed geometric entropy). Thm 4.2: S_corr>=0
    # and DECREASES monotonically with bulk entropy.
    print(f"   {'S_bulk':>7} {'S_PA exact=S(chi)':>17} {'S_PA skew':>10} "
          f"{'S_corr(paper)':>14}")
    pae, pao = [], []
    for lam in lambdas:
        sb = binary_entropy(lam)
        p0 = proto_area_avg(lam, v0, v1, 0.0, rng)
        pe = proto_area_avg(lam, v0, v1, theta, rng)
        pao.append(p0); pae.append(pe)
        print(f"   {sb:>7.4f} {p0:>17.4f} {pe:>10.4f} {p0 - pe:>14.4f}")

    flat0 = max(pao) - min(pao)
    mono_pa = all(pae[i + 1] >= pae[i] - 3e-3 for i in range(len(pae) - 1))
    scorr = [pao[i] - pae[i] for i in range(len(pae))]         # paper's S_corr
    scorr_ok = min(scorr) > -3e-3 and all(
        scorr[i + 1] <= scorr[i] + 3e-3 for i in range(len(scorr) - 1))
    print(f"\n   P-1 exact proto-area flat: spread = {flat0:.4f} "
          f"({'FLAT' if flat0 < 3e-3 else 'NOT flat'})")
    print(f"   P-2 skewed proto-area monotonically INCREASING with S_bulk: {mono_pa}"
          f"  (rises {pae[0]:.4f} -> {pae[-1]:.4f})")
    print(f"       paper's S_corr = S(chi)-S_PA >=0 and DECREASING (Thm 4.2): "
          f"{scorr_ok}  ({scorr[0]:.4f} -> {scorr[-1]:.4f})")

    print("\n   P-3 skew scaling of the correction at S_bulk=1 (lam=0.5):")
    print(f"   {'theta/pi':>9} {'S_corr':>9}")
    for frac in (0.0, 0.05, 0.10, 0.15):
        c = (proto_area_avg(0.5, v0, v1, np.pi * frac, rng)
             - proto_area_avg(0.5, v0, v1, 0.0, rng))
        print(f"   {frac:>9.2f} {c:>9.4f}")

    print("\n   VERDICT reported honestly above. If P-2 now holds (increase),")
    print("   the Petz-recovery proto-area reproduces Theorem 4.2 qualitatively")
    print("   in a toy; if not, the discrepancy is diagnosed against the")
    print("   optimal-R* / small-theta assumptions the theorem actually makes.")


if __name__ == "__main__":
    main()
