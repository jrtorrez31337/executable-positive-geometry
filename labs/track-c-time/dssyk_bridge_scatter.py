"""P3 extension — the quantitative rigidity-arrow scatter (Q-1/Q-2/Q-3).

Pre-registered in notes/PROJECT-3-DSSYK-BRIDGE.md (post-close extension).
S3 gave co-classification (rigid <-> strong arrow); this lab asks whether it is
a RELATION: normalized late Krylov complexity (K_spread_late) vs spectral
number variance Sigma^2(L=4), scattered across ensemble families AND parameter
sweeps.

METHOD LOCK: all measurement code is Tobin's `sample_model` from
dssyk_bridge_falsifiers.py, called verbatim — this file only sweeps parameters
and aggregates. Q-2's falsifier is built in: at matched Sigma^2, family
branches (disagreement beyond combined SEMs) refute the one-curve reading.

Usage: python dssyk_bridge_scatter.py [--dim 64] [--samples 8] (smoke)
       paper-grade: --dim 128 --samples 32 (Tobin's lane)
"""

# SMOKE-RUN RESULTS (quant-phy, dim=64/samples=8, run p3_scatter_20260728T191553Z):
#   Q-1 CONFIRMED: Spearman rho = -0.743 (p=7.6e-5) -- the rigidity-arrow trend
#       is quantitatively real across 22 ensemble points.
#   Q-2 REFUTED at this power: branching fraction 1.00 -- at matched Sigma^2,
#       families disagree far beyond combined SEMs (Anderson W=5 vs RP c=0.35 at
#       Sigma^2~3: K 0.027 vs 0.270, 10x). The pre-registered fallback reading is
#       supported by the recorded IPR: the branch variable is eigenvector
#       localization (Anderson IPR 0.34 vs RP 0.10 at matched rigidity).
#   Q-3 consistent: chord controls at the rigid end (q=0.9 is the MOST rigid,
#       Sigma^2=0.40, with strong K=0.437).
# HONEST STATUS: Q-2's refutation awaits Tobin's paper-grade run (dim=128/s=32;
# note smaller SEMs can only make declared branching easier, so confirmation is
# expected) + agy's reading audit before it hardens into the note.
# Refined bridge statement (candidate for the sixth note): "the arrow tracks
# rigidity as a TREND, not a law; eigenvector delocalization is the missing
# variable that completes it."

import argparse
import json
import pathlib
import sys
from types import SimpleNamespace

import numpy as np
from scipy import stats

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from dssyk_bridge_falsifiers import (sample_model, mean_sem,  # noqa: E402
                                     utc_stamp, write_json, RUN_ROOT)

# Parameter sweep grids. Ensemble families x parameter values.
SWEEP = [
    ("goe",               [("anchor", {})]),
    ("poisson",           [("anchor", {})]),
    ("anderson",          [(f"W={w}", {"anderson_disorder": w})
                           for w in (0.5, 1.0, 2.0, 3.5, 5.0, 8.0)]),
    ("beta-hermite",      [(f"beta={b}", {"beta": b})
                           for b in (0.5, 1.0, 2.0, 4.0)]),
    ("rosenzweig-porter", [(f"c={c}", {"rp_coupling": c})
                           for c in (0.10, 0.20, 0.35, 0.50, 0.75)]),
    ("banded",            [(f"bw={b}", {"bandwidth": b})
                           for b in (2, 3, 5, 8, 14)]),
    ("dssyk-chord",       [(f"q={q}", {"q_deform": q})
                           for q in (0.05, 0.50, 0.90)]),   # deterministic n=1
]
DEFAULTS = dict(anderson_disorder=5.0, beta=1.0, rp_coupling=0.35,
                bandwidth=5, q_deform=0.65)


def run_point(model, overrides, dim, samples, max_steps, times, rng):
    ns = SimpleNamespace(**{**DEFAULTS, **overrides})
    rows = []
    n = 1 if model == "dssyk-chord" else samples          # deterministic: n=1
    for _ in range(n):
        rows.append(sample_model(model, dim, rng, max_steps, times, ns))
    out = {}
    for f in ("K_spread_late", "number_variance_L4", "gap_r",
              "chain_eigenvector_ipr"):
        m, s = mean_sem([float(r[f]) for r in rows])
        out[f] = m
        out[f + "_sem"] = s
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dim", type=int, default=64)
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--max-steps", type=int, default=48)
    ap.add_argument("--tmax", type=float, default=25.0)
    args = ap.parse_args()
    rng = np.random.default_rng(20260729)
    times = np.linspace(0.0, args.tmax, 160)

    print(f"P3 quantitative scatter: dim={args.dim} samples={args.samples}\n")
    print(f"{'family':>18} {'param':>8} {'Sigma2(L4)':>11} {'K_late/chain':>13} "
          f"{'gap_r':>6} {'IPR':>6}")
    points = []
    for model, grid in SWEEP:
        for label, overrides in grid:
            p = run_point(model, overrides, args.dim, args.samples,
                          args.max_steps, times, rng)
            p.update(model=model, param=label,
                     deterministic=(model == "dssyk-chord"))
            points.append(p)
            print(f"{model:>18} {label:>8} "
                  f"{p['number_variance_L4']:>7.2f}+/-{p['number_variance_L4_sem']:<4.2f}"
                  f"{p['K_spread_late']:>8.3f}+/-{p['K_spread_late_sem']:<5.3f}"
                  f"{p['gap_r']:>6.2f} {p['chain_eigenvector_ipr']:>6.2f}")

    ens = [p for p in points if not p["deterministic"]]
    x = np.log10([max(p["number_variance_L4"], 1e-3) for p in ens])
    y = [p["K_spread_late"] for p in ens]
    rho, pval = stats.spearmanr(x, y)
    print(f"\nQ-1 Spearman rho (ensemble points, K vs log10 Sigma2): "
          f"{rho:.3f}  (p={pval:.2e})  -> "
          f"{'monotone-decreasing CONFIRMED' if rho < -0.5 and pval < 0.01 else 'NOT confirmed'}")

    # Q-2 universality probe: bin by Sigma2; check cross-family agreement
    print("\nQ-2 universality probe (bins of log10 Sigma2 holding >=2 families):")
    bins = np.linspace(min(x), max(x), 7)
    idx = np.digitize(x, bins)
    verdicts = []
    for b in sorted(set(idx)):
        sel = [p for p, i in zip(ens, idx) if i == b]
        fams = sorted({p["model"] for p in sel})
        if len(fams) < 2:
            continue
        ks = np.array([p["K_spread_late"] for p in sel])
        sems = np.array([max(p["K_spread_late_sem"], 1e-4) for p in sel])
        spread = float(ks.max() - ks.min())
        comb = float(2 * np.sqrt(np.mean(sems ** 2)))
        branch = spread > comb
        verdicts.append(branch)
        print(f"   bin {b}: families={fams} K-spread={spread:.3f} "
              f"2*SEM={comb:.3f} -> {'BRANCHES' if branch else 'consistent'}")
    if verdicts:
        frac = sum(verdicts) / len(verdicts)
        print(f"   branching fraction: {frac:.2f} -> "
              f"{'FAMILY BRANCHES (one-curve REFUTED; categorical + IPR remainder)' if frac > 0.5 else 'consistent with one curve at this power'}")

    chord = [p for p in points if p["deterministic"]]
    print("\nQ-3 chord-chain controls (deterministic, n=1, labeled):")
    for p in chord:
        print(f"   {p['param']}: Sigma2={p['number_variance_L4']:.2f} "
              f"K/chain={p['K_spread_late']:.3f} (rigid-end consistency)")

    out = RUN_ROOT / f"p3_scatter_{utc_stamp()}"
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "scatter.json", {"args": vars(args), "points": points,
                                      "spearman_rho": rho, "spearman_p": pval})
    print(f"\npersisted: {out}/scatter.json")


if __name__ == "__main__":
    main()
