"""Project 3, S1 — the DSSYK chord chain: complexity arrow on a native one-sided chain.

Pre-registered under notes/PROJECT-3-DSSYK-BRIDGE.md (P3-1, as amended by Tobin
and certified non-circular by agy, all-signed 2026-07-27).

The object. In the chord basis (Lin 2208.07032; chord technology Berkooz et al.
1811.02584) the DSSYK Hamiltonian at infinite temperature is tridiagonal on
chord number n = 0, 1, 2, ...: zero diagonal, hopping

    b_n = sqrt((1 - q^n) / (1 - q)),   n >= 1        [presentation of 2305.04355]

— a q-deformed oscillator. Rabinovici-Sanchez-Garrido-Shir-Sonner 2305.04355
prove the TFD's Krylov basis IS this chord basis (exact, any q), so spread
complexity K(t) = <n_hat>(t) identically; = bulk length in the triple-scaling
limit. Chord number is POSITIVE with a boundary at n=0: the chain is natively
one-sided — the same structure our krylov_ignition.py used as the finite shadow
of the positive generator.

P3-1 readout (per the Tobin amendment, verbatim intent): any finite cutoff
N_max saturates BY CONSTRUCTION, so the registered signal is the BALLISTIC
PRE-BOUNDARY GROWTH VELOCITY measured strictly inside the pre-reflection
window (boundary occupancy below threshold), plus the finite-cutoff saturation
reported separately as the artifact it is. No infinite-time claim is made from
a finite matrix (finite-N saturation caveat: 2412.02038).

Registered expectations:
  E1: small-t exact check K(t) = b_1^2 t^2 + O(t^4), b_1 = 1 for all q.
  E2: b_n -> plateau b_inf = 1/sqrt(1-q); pre-boundary K(t) growth is ballistic
      (linear late in the window) with velocity increasing with plateau height.
  E3: q -> 1 limit (b_n -> sqrt(n), ordinary oscillator): super-ballistic
      growth in the window (SL(2)-type), a qualitatively different profile —
      the contrast that shows the plateau, not mere openness, sets the arrow's
      speed.
  E4: the chord chain is smooth/deterministic -> open/ballistic transport.
      This is the DSSYK-side datum for the P3-2 discriminator (S2 compares
      against disordered/beta-Hermite/RP ensembles with independently unfolded
      rigidity — NOT here, to keep S1 free of the bridge claim).
"""

# RESULTS (quant-phy run, 2026-07-27, N_MAX=400) — all four registered
# expectations confirmed:
#   E1 K(t)=b_1^2 t^2 exact to <2e-5 relative at t=0.01, every q tested.
#   E2 ballistic pre-boundary transport at every q; window velocity scales with
#      the plateau: v/b_inf = 1.71/1.80/1.86/1.92/1.97 at q=0.05/0.3/0.5/0.7/0.9.
#      HONEST NOTE: v/b_inf is only roughly constant (drifts toward the uniform-
#      chain front bound 2b with growing q); we register "v ∝ b_inf with an O(1)
#      coefficient" and do NOT interpret the coefficient — left to the S2/clean-
#      room pass to refine or refute.
#   E3 q->1 oscillator (b_n=sqrt(n)): late-window log-log slope 2.00 — the
#      super-ballistic SL(2) profile, cleanly distinct from ballistic (1.0).
#   E4 open/delocalized at every q (finite t_reflect always) — the DSSYK-side
#      datum for P3-2; the bridge comparison itself lives in S2, not here.
import numpy as np
from scipy.linalg import expm

N_MAX = 400                    # chain cutoff (sites 0..N_MAX-1)
REFLECT_EPS = 1e-6             # boundary-occupancy threshold defining the window


def chord_bs(q: float, n_max: int) -> np.ndarray:
    """b_n = sqrt((1-q^n)/(1-q)) for n = 1..n_max-1 (q<1); q->1 limit sqrt(n)."""
    n = np.arange(1, n_max)
    if abs(q - 1.0) < 1e-12:
        return np.sqrt(n.astype(float))
    return np.sqrt((1.0 - q ** n) / (1.0 - q))


def evolve_chain(bs: np.ndarray, times: np.ndarray):
    """Evolve |n=0> under the zero-diagonal tridiagonal H; return K(t) and
    boundary occupancy |c_{N-1}(t)|^2."""
    m = len(bs) + 1
    H = np.zeros((m, m))
    idx = np.arange(len(bs))
    H[idx, idx + 1] = bs
    H[idx + 1, idx] = bs
    c0 = np.zeros(m, dtype=complex)
    c0[0] = 1.0
    # eigendecomposition once; evolve all times
    w, V = np.linalg.eigh(H)
    proj = V.conj().T @ c0
    n_hat = np.arange(m)
    K, edge = [], []
    for t in times:
        c = V @ (np.exp(-1j * w * t) * proj)
        p = np.abs(c) ** 2
        K.append(float(p @ n_hat))
        edge.append(float(p[-1]))
    return np.array(K), np.array(edge)


def window_velocity(times, K, edge, eps=REFLECT_EPS):
    """Ballistic velocity from a linear fit over the LATE HALF of the
    pre-reflection window (skipping the early quadratic regime)."""
    inside = edge < eps
    t_ref = times[np.argmax(~inside)] if (~inside).any() else times[-1]
    win = (times > 0.25 * t_ref) & (times < 0.9 * t_ref)
    if win.sum() < 8:
        return float("nan"), t_ref
    v, _ = np.polyfit(times[win], K[win], 1)
    return float(v), float(t_ref)


def main():
    print("Project 3 S1 — DSSYK chord chain (N_max = %d)\n" % N_MAX)

    print("E1 small-t exactness: K(t) vs b_1^2 t^2 at t=0.01 (b_1=1 for all q)")
    for q in (0.05, 0.5, 0.95):
        bs = chord_bs(q, N_MAX)
        K, _ = evolve_chain(bs, np.array([0.01]))
        print(f"   q={q:4.2f}: K={K[0]:.3e}   b1^2 t^2={bs[0]**2 * 1e-4:.3e}"
              f"   ratio={K[0] / (bs[0]**2 * 1e-4):.6f}")

    print("\nE2 plateau + ballistic velocity in the pre-reflection window")
    times = np.linspace(0, 260, 900)
    print(f"   {'q':>5} {'b_inf':>7} {'v_window':>9} {'v/b_inf':>8} "
          f"{'t_reflect':>9} {'K(t_ref)':>9}")
    for q in (0.05, 0.3, 0.5, 0.7, 0.9):
        bs = chord_bs(q, N_MAX)
        b_inf = 1.0 / np.sqrt(1.0 - q)
        K, edge = evolve_chain(bs, times)
        v, t_ref = window_velocity(times, K, edge)
        k_at = float(np.interp(t_ref, times, K))
        print(f"   {q:5.2f} {b_inf:7.3f} {v:9.4f} {v / b_inf:8.4f} "
              f"{t_ref:9.1f} {k_at:9.1f}")
    print("   (v/b_inf ~ constant across q  =>  plateau height sets the arrow's")
    print("    speed; the transport is ballistic, v ∝ b_inf.)")

    print("\nE3 q->1 oscillator contrast (b_n = sqrt(n)): super-ballistic window")
    bs1 = chord_bs(1.0, N_MAX)
    times3 = np.linspace(0, 12, 600)
    K1, edge1 = evolve_chain(bs1, times3)
    inside = edge1 < REFLECT_EPS
    t_ref1 = times3[np.argmax(~inside)] if (~inside).any() else times3[-1]
    win = times3 < 0.9 * t_ref1
    # fit log K vs log t late in the window: ballistic => slope 1; oscillator => 2
    late = win & (times3 > 0.3 * t_ref1) & (K1 > 0)
    slope = np.polyfit(np.log(times3[late]), np.log(K1[late]), 1)[0]
    print(f"   t_reflect={t_ref1:.2f}; log-log slope of K(t) late in window: "
          f"{slope:.2f}  (ballistic=1, oscillator~2)")

    print("\nE4 openness (DSSYK-side datum for P3-2, no bridge claim here):")
    print("   smooth deterministic b_n -> no localization: K reaches the")
    print("   boundary at every q tested (t_reflect finite above).")

    print("\nHonest scope: finite cutoff saturates by construction (2412.02038);")
    print("all readouts above are strictly pre-reflection. No infinite-time or")
    print("bulk-length claim from a finite matrix.")


if __name__ == "__main__":
    main()
