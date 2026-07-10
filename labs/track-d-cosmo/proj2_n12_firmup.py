"""P2 firm-up: extend the TFD magic-dynamics discriminators to N=12 with SEMs.

Loads magic_dynamics from proj2_magic_dynamics. N=12 -> 12-qubit TFD (dim
4096); coarse time grid (t=0 for the initial value, late t for the plateau)
keeps the dense-rho SRE cost bounded. Reports the two discriminators with
error bars over independent seeds: the ~2x scrambling RISE ratio and the
SYK4-SYK2 late PLATEAU gap (the horizon-dof soft spot gating the note).
Tobin's N=8/10 SEMs: rise ratio robust; plateau gap +0.605 -> +1.030.
This adds the N=12 point to firm or bound the extensive-plateau wording.
"""
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from proj2_magic_dynamics import magic_dynamics  # noqa: E402

TIMES = np.array([0.0, 2.0, 8.0, 30.0, 100.0])


def firm(N, n_samples, seeds):
    gaps, ratios = [], []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        m4, _ = magic_dynamics(N, 4, 1.0, TIMES, n_samples, rng)
        m2_, _ = magic_dynamics(N, 2, 1.0, TIMES, n_samples, rng)
        p4, p2 = float(np.mean(m4[-2:])), float(np.mean(m2_[-2:]))
        r4, r2 = p4 - float(m4[0]), p2 - float(m2_[0])
        gaps.append(p4 - p2)
        if r2 > 1e-6:
            ratios.append(r4 / r2)
        print(f"    seed {seed}: plateau gap {p4-p2:+.3f}, rise ratio "
              f"{r4/r2:.2f}x", flush=True)
    def ms(x):
        a = np.array(x)
        return float(a.mean()), float(a.std(ddof=1) / np.sqrt(len(a))) if len(a) > 1 else 0.0
    return ms(gaps), ms(ratios)


def main():
    print("P2 N=12 firm-up (TFD dim 4096, coarse grid, SEMs over seeds)\n")
    for N, ns, seeds in [(12, 3, (101, 202, 303))]:
        print(f"N={N} Majoranas ({N//2}+{N//2} qubit TFD), {ns} samples x {len(seeds)} seeds:")
        (g, gse), (r, rse) = firm(N, ns, seeds)
        print(f"  => plateau gap (SYK4-SYK2): {g:+.3f} +/- {gse:.3f}")
        print(f"  => scrambling rise ratio:   {r:.2f} +/- {rse:.2f}x")
        print(f"\n  TREND with N: rise ratio 2.05(N6)/2.30(N8)/2.55(N10)/{r:.2f}(N12);")
        print(f"  plateau gap +0.605(N8)/+1.030(N10)/{g:+.3f}(N12).")
        if g > 1.030:
            print("  -> plateau gap CONTINUES to grow at N=12: extensive trend firmed.")
        elif g > 0.3:
            print("  -> plateau gap stays clearly positive at N=12 (extensive-consistent).")
        else:
            print("  -> plateau gap does NOT keep growing at N=12: bound the wording honestly.")


if __name__ == "__main__":
    main()
