"""Track C CAPSTONE (quant-phy half) — igniting the arrow on the Krylov chain.

The arrow-origins scorecard (notes/ARROW-ORIGINS-SCORECARD.md) left one buildable
test of "how the flow starts": the two genuine-ignition families (Family 3
dynamical-complexity, Family 6 algebraic positive-generator) meet on a SPECTRAL
quantity, and the finite/computable home of that meeting is the KRYLOV CHAIN.

Lanczos tridiagonalizes the Liouvillian L = [H, .] of a chaotic Hamiltonian into
a hopping model on a SEMI-INFINITE chain (sites n = 0, 1, 2, ...): on-site a_n,
hops b_n. Two readings of the same object:

  Family 5 (complexity / arrow):  K(t) = <n_hat>(t), the mean position on the
      chain, GROWS — the arrow, an operic quantity that increases.
  Family 6 (positive generator):  n_hat >= 0 with a BOUNDARY at n = 0. The chain
      is one-sided; n_hat is a positive generator; the "half-sidedness" is the
      n = 0 wall. This is the finite shadow of the half-sided modular inclusion
      (the exact P >= 0 needs n -> infinity, the type-III_1 / large-N limit —
      hence the finite-HSMI no-go; here the chain just truncates at dim <= d^2).

The IGNITION criterion: the chain "opens" (b_n keep growing, K(t) climbs) iff the
dynamics is chaotic. Parker et al. (universal operator growth, arXiv 1812.08657):
b_n ~ alpha*n (linear) is the maximal-chaos signature and is set by the spectrum
(level repulsion). So the arrow (K grows), the positive-generator structure (the
one-sided chain), and the spectral origin (linear b_n <-> RMT) are ONE fact in
the chaotic case, and fail together in the integrable case.

This file is the quant-phy half: the Krylov engine + complexity + b_n growth,
SYK4 (chaotic) vs SYK2 (free). Tobin's half ties b_n growth to the level
statistics / SFF ramp (phase6) and runs the KMS control (the thermal arrow is
state-inherited, present in BOTH — the honest INHERITED-vs-IGNITED contrast).
Hand-in-hand; both sign the verdict.
"""

# RESULTS (quant-phy half, seeds 11/22/33, N=8/10/12) — 2026-07-12
# THE ARROW IGNITES on the chaotic Krylov chain, robustly:
#   sustained complexity K_late   SYK4: 28.7 / 42.2 / 62.7  (grows with N)
#                                 SYK2:  3.1 /  3.3 /  4.0  (flat, localized)
#   Krylov bandwidth b_mean       SYK4: 1.02 / 1.54 / 1.98  (grows with N)
# The one-sided positive generator n_hat>=0 climbs (arrow) iff chaotic; the free
# chain localizes. K_late is the robust discriminator (SYK4 ~13x SYK2 at N=12).
# HONEST SUB-PREDICTION FAILURE: b_n do NOT grow linearly (P1, from Parker's
# thermodynamic-limit b_n ~ alpha*n). At finite N they RISE-TO-PLATEAU (SYK4
# N=12: 1.43 -> ~2.4 plateau), so the linear slope ~ 0. Parker linearity is a
# large-N statement; the finite-N ignition signature is PLATEAU + open chain +
# sustained K, not a linear b-slope. Robust discriminator = K_late, not b_slope.
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "track-d-magic"))
from phase4_syk_magic_baseline import (  # reuse, don't reinvent
    jw_majoranas, syk_term_ops, syk_hamiltonian,
)


def build_syk(n_majoranas, q, rng):
    gammas = jw_majoranas(n_majoranas)
    term_ops = syk_term_ops(gammas, q)
    H = syk_hamiltonian(term_ops, n_majoranas, q, rng)
    return H, gammas


def frob_ip(a, b, d):
    """Normalized Frobenius inner product <A|B> = Tr(A^dag B)/d."""
    return np.trace(a.conj().T @ b) / d


def lanczos_operator(H, O0, max_steps):
    """Matrix-free operator Lanczos for the Liouvillian L = [H, .].
    Returns (a_n, b_n): on-site energies and hops of the Krylov chain.
    Full reorthogonalization keeps the chain clean at small dimension."""
    d = H.shape[0]
    O0 = O0 / np.sqrt(np.real(frob_ip(O0, O0, d)))
    basis = [O0]
    a_list, b_list = [], []
    prev = np.zeros_like(O0)
    b_prev = 0.0
    cur = O0
    for _ in range(max_steps):
        Lcur = H @ cur - cur @ H                       # [H, O_n]
        a_n = np.real(frob_ip(cur, Lcur, d))
        w = Lcur - a_n * cur - b_prev * prev
        for Ok in basis:                               # full reorthogonalization
            w = w - frob_ip(Ok, w, d) * Ok
        b_n = np.sqrt(np.real(frob_ip(w, w, d)))
        a_list.append(a_n)
        if b_n < 1e-9:                                  # chain terminates
            break
        w = w / b_n
        basis.append(w)
        prev, cur, b_prev = cur, w, b_n
        b_list.append(b_n)
    return np.array(a_list), np.array(b_list)


def krylov_complexity(a, b, times):
    """K(t) = sum_n n |c_n(t)|^2, c(t) = exp(i T t) e_0, T the Krylov tridiagonal.
    The Krylov subspace is L-invariant, so this restricted evolution is exact."""
    from scipy.linalg import expm
    m = len(a)
    T = np.diag(a).astype(complex)
    for n in range(min(len(b), m - 1)):               # m sites -> m-1 hops
        T[n, n + 1] = b[n]
        T[n + 1, n] = b[n]
    e0 = np.zeros(m, dtype=complex)
    e0[0] = 1.0
    n_hat = np.arange(m)
    K = []
    for t in times:
        c = expm(1j * T * t) @ e0
        K.append(float(np.sum(n_hat * np.abs(c) ** 2)))
    return np.array(K)


def linear_slope(b):
    """Fit b_n ~ alpha * n over the growing region (Parker slope alpha)."""
    n = np.arange(1, len(b) + 1)
    keep = slice(1, max(2, len(b) - 1))               # drop n=1 edge, tail
    if len(b) < 4:
        return float("nan")
    alpha, _ = np.polyfit(n[keep], b[keep], 1)
    return float(alpha)


def run_one(n_majoranas, q, seed, max_steps=80):
    rng = np.random.default_rng(seed)
    H, gammas = build_syk(n_majoranas, q, rng)
    d = H.shape[0]
    O0 = gammas[0]                                     # seed operator = chi_1
    a, b = lanczos_operator(H, O0, max_steps)
    times = np.linspace(0, 20, 200)
    K = krylov_complexity(a, b, times)
    return {
        "N": n_majoranas, "q": q, "d": d,
        "chain_len": len(b), "b": b, "a": a,
        "b_slope": linear_slope(b),
        "b_mean": float(np.mean(b)) if len(b) else 0.0,
        "K": K, "times": times,
        "K_max": float(np.max(K)), "K_late": float(np.mean(K[-40:])),
    }


def main():
    print("Track C CAPSTONE (quant-phy half) — Krylov-chain ignition\n")
    print("SYK4 = chaotic (should ignite: b_n grow, chain opens, K climbs)")
    print("SYK2 = free/integrable (should NOT: b_n bounded, K localizes)\n")
    seeds = [11, 22, 33]
    for N in (8, 10, 12):
        print(f"=== N = {N} Majoranas ({N // 2} qubits) ===")
        print(f"   {'model':>6} {'chain':>6} {'b_slope':>8} {'b_mean':>7} "
              f"{'K_max':>7} {'K_late':>7}")
        for q, name in ((4, "SYK4"), (2, "SYK2")):
            rows = [run_one(N, q, s) for s in seeds]
            cl = np.mean([r["chain_len"] for r in rows])
            sl = np.nanmean([r["b_slope"] for r in rows])
            bm = np.mean([r["b_mean"] for r in rows])
            km = np.mean([r["K_max"] for r in rows])
            kl = np.mean([r["K_late"] for r in rows])
            print(f"   {name:>6} {cl:>6.0f} {sl:>8.3f} {bm:>7.3f} "
                  f"{km:>7.2f} {kl:>7.2f}")
        # discriminators
        r4 = run_one(N, 4, seeds[0])
        r2 = run_one(N, 2, seeds[0])
        print(f"   -> b_n growth (slope) chaotic/free : "
              f"{r4['b_slope']:.3f} vs {r2['b_slope']:.3f}")
        print(f"   -> late complexity K chaotic/free  : "
              f"{r4['K_late']:.2f} vs {r2['K_late']:.2f}")
        print(f"   -> first 8 b_n SYK4: "
              f"{np.round(r4['b'][:8], 2)}")
        print(f"   -> first 8 b_n SYK2: "
              f"{np.round(r2['b'][:8], 2)}\n")
    print("Reading: if SYK4 shows growing b_n + climbing K and SYK2 does not,")
    print("the arrow IGNITES on the chaotic Krylov chain — the one-sided positive")
    print("generator (n_hat>=0) whose growth is the arrow, driven by the spectrum.")
    print("Tobin's half: tie b_slope to level repulsion (phase6 <r>/SFF ramp) and")
    print("run the KMS control (thermal arrow present in BOTH = state-inherited).")


if __name__ == "__main__":
    main()
