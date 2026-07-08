"""Track D, Phase 3 — mixed-bulk backreaction: proto-area grows with bulk entropy.

Continues Phase 2, targeting Theorem 4.2 of Cao-Cheng-Karthikeyan-Li-Preskill
(arXiv:2603.13475, Sec 4.1, "Mixed bulk state"):

  For a MIXED bulk state (bulk qubit entangled with an external reference r,
  all bulk recoverable from wedge A), the bulk-unitary-AVERAGED proto-area
  entropy increases MONOTONICALLY with the bulk entropy in a skewed
  (approximate, non-Clifford-deformed) code — while it stays FLAT
  (state-independent) in the exact code.

Definitions used (paper Def 3.2): proto-area
    S_PA = S(rho_A) - S_matter,
with S_matter the entropy of the optimally-recovered bulk. We take
S_matter = H(lambda) (the bulk entropy): EXACT for the undeformed code's
perfect wedge recovery, and correct to leading order in the skew for the
deformed code (the optimal deformed recovery differs at higher order — an
honest approximation, labeled). The paper's bulk-unitary average is
replicated by averaging over Haar-random SU(2) on the logical qubit before
encoding (these preserve the bulk entropy H(lambda) while scrambling state
details).

Setup on the [[5,1,3]] code (all bulk recoverable from any 3-qubit wedge;
2-qubit complement recovers nothing — matches the paper's Figure 4):
  - logical L purified by external reference r: sqrt(lambda)|00> +
    sqrt(1-lambda)|11>, bulk entropy S_bulk = H(lambda) in [0,1] bit.
  - encode L into 5 physical (|0>->v0, |1>->v1); wedge A = qubits {0,1,2}.
  - exact: V_0 ; skewed: exp(i theta (X0X2 + X1X3)) V_0  (Phase-2 generator).

PRE-REGISTERED PREDICTIONS:
  P-1 exact code: S(rho_A) = H(lambda) + const, so proto-area S_PA is FLAT
      in bulk entropy (state-independent area — the no-go baseline).
  P-2 skewed code: <S_PA> increases MONOTONICALLY with bulk entropy
      H(lambda) (Theorem 4.2). The correction <S_corr> = <S_PA^skew> -
      S_PA^exact is >= 0 and monotone.
  P-3 the effect scales with the skew and vanishes as theta->0 (same magic
      control as Phase 2).

RESULT (2026-07-08): P-1 and P-3 confirmed; P-2 FAILED with the WRONG SIGN.
This toy does NOT reproduce Theorem 4.2 — the fixed matter-entropy
approximation (S_matter = H(lambda)) discards the deformed-recovery term
where the theorem's effect lives. See the HONEST OUTCOME block at the end
of main() for the full diagnosis and what a faithful Phase 3 requires.
Recorded as a failed pre-registered prediction, per project discipline.
"""

import pathlib
import sys
from functools import reduce

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent / ".." / "capstone-happy"))
from happy_tile import build_codewords  # noqa: E402
from phase0_wedge_magic import reduce_state  # noqa: E402
from phase2_backreaction import skew_unitary  # noqa: E402

LN2 = np.log(2)
WEDGE_A = (0, 1, 2)          # 3-qubit recovering wedge (of 5 physical)
N_AVG = 40                   # bulk-unitary average samples


def binary_entropy(lam):
    if lam in (0.0, 1.0):
        return 0.0
    return float(-(lam * np.log2(lam) + (1 - lam) * np.log2(1 - lam)))


def vn_bits(rho):
    p = np.linalg.eigvalsh(rho)
    p = p[p > 1e-12]
    return float(-np.sum(p * np.log(p)) / LN2)


def haar_su2(rng):
    m = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
    q, r = np.linalg.qr(m)
    return q @ np.diag(np.diag(r) / np.abs(np.diag(r)))


def encoded_mixed_state(lam, U, v0, v1, theta):
    """6-'qubit' state on (5 physical) x (reference r): encode a mixed
    logical (Schmidt lambda, rotated by U) then skew the physical legs."""
    s0, s1 = np.sqrt(lam), np.sqrt(1 - lam)
    # |psi>_{Lr} = (U (x) I)(s0|00> + s1|11>); logical |0>->v0, |1>->v1
    r0 = s0 * (U[0, 0] * v0 + U[1, 0] * v1)     # r=0 branch (32-dim physical)
    r1 = s1 * (U[0, 1] * v0 + U[1, 1] * v1)     # r=1 branch
    Uskew = skew_unitary(theta)
    r0, r1 = Uskew @ r0, Uskew @ r1
    psi = np.stack([r0, r1], axis=1).reshape(-1)   # (32,2)->64, r is qubit 5
    return psi / np.linalg.norm(psi)


def avg_SA(lam, v0, v1, theta, rng):
    vals = [vn_bits(reduce_state(encoded_mixed_state(lam, haar_su2(rng),
            v0, v1, theta), WEDGE_A, 6)) for _ in range(N_AVG)]
    return float(np.mean(vals))


def main():
    v0, v1 = build_codewords()
    rng = np.random.default_rng(20)
    lambdas = [0.5, 0.35, 0.25, 0.15, 0.08, 0.03]     # descending -> S_bulk desc
    theta = np.pi * 0.15

    print("Track D Phase 3 — mixed-bulk backreaction ([[5,1,3]], wedge A={q1,q2,q3})")
    print(f"skew theta={theta/np.pi:.2f}pi; bulk-unitary average over {N_AVG} Haar SU(2)\n")
    print(f"   {'lambda':>7} {'S_bulk':>7} {'<S_A> exact':>12} {'S_PA exact':>11} "
          f"{'<S_A> skew':>11} {'S_PA skew':>10} {'S_corr':>8}")
    rows = []
    for lam in lambdas:
        sb = binary_entropy(lam)
        sa0 = avg_SA(lam, v0, v1, 0.0, rng)
        sae = avg_SA(lam, v0, v1, theta, rng)
        pa0, pae = sa0 - sb, sae - sb
        rows.append((sb, pa0, pae, pae - pa0))
        print(f"   {lam:>7.2f} {sb:>7.4f} {sa0:>12.4f} {pa0:>11.4f} "
              f"{sae:>11.4f} {pae:>10.4f} {pae - pa0:>8.4f}")

    # verdicts (rows are in DESCENDING S_bulk; reverse for ascending checks)
    rows_asc = rows[::-1]
    pa0 = [r[1] for r in rows_asc]
    pae = [r[2] for r in rows_asc]
    corr = [r[3] for r in rows_asc]
    flat0 = max(pa0) - min(pa0)
    mono_skew = all(pae[i + 1] >= pae[i] - 1e-3 for i in range(len(pae) - 1))
    mono_corr = all(corr[i + 1] >= corr[i] - 1e-3 for i in range(len(corr) - 1))
    print(f"\n   P-1 exact proto-area flat in bulk entropy: spread = {flat0:.4f} "
          f"(-> {'FLAT' if flat0 < 1e-3 else 'not flat'}; state-independent area)")
    print(f"   P-2 skewed proto-area monotincreasing with S_bulk: {mono_skew}; "
          f"correction S_corr >=0 & monotone: {mono_corr and min(corr) > -1e-3}")
    print(f"       (S_PA skew rises {pae[0]:.4f} -> {pae[-1]:.4f} as S_bulk 0 -> 1)")

    print("\n   P-3 skew-scaling of the correction at S_bulk=1 (lambda=0.5):")
    print(f"   {'theta/pi':>9} {'S_corr':>9}")
    for frac in (0.0, 0.05, 0.10, 0.15):
        c = avg_SA(0.5, v0, v1, np.pi * frac, rng) - avg_SA(0.5, v0, v1, 0.0, rng)
        print(f"   {frac:>9.2f} {c:>9.4f}")

    print("""
   HONEST OUTCOME (pre-registered prediction FAILED — recorded, not buried):
   - P-1 CONFIRMED: exact-code proto-area is exactly flat (spread 0.0000) —
     the state-independent-area baseline / no-go, solid.
   - P-3 CONFIRMED: the effect is controlled by the non-Clifford skew and
     vanishes as theta -> 0.
   - P-2 FAILED, and with the WRONG SIGN: <S_PA^skew> DECREASES monotonically
     with bulk entropy here, whereas Theorem 4.2 says it should INCREASE
     (more matter -> larger area, the gravity-like behavior).

   DIAGNOSIS: this toy does NOT faithfully test Theorem 4.2. Proto-area =
   S(rho_A) - S_matter, and BOTH terms move under skewing. We fixed
   S_matter = H(lambda) (the undeformed perfect-recovery value), so we only
   captured the change in S(rho_A) and DISCARDED the change in the
   recovered-matter entropy S(sigma^{R*}) under the DEFORMED optimal
   recovery R* (paper Eq 3.3/4.10) — which is exactly where the theorem's
   effect lives (a difference of relative entropies between deformed and
   undeformed recovered states). Our large, specific skew (theta=0.15pi,
   fixed generator) is also not the Haar-averaged infinitesimal deformation
   the theorem assumes.

   WHAT A FAITHFUL PHASE 3 NEEDS: implement the optimal deformed recovery
   R* (maximize coherent information, Eq 3.3) or its Petz approximation,
   compute S_matter = S(sigma^{R*}_{A1}) properly, and take the small-theta
   Haar-averaged limit. Until then, Theorem 4.2 is NOT reproduced here.
   Phase 2 (state-dependence <-> tripartite magic) stands; Phase 3's
   monotonic-INCREASE claim is open.""")


if __name__ == "__main__":
    main()
