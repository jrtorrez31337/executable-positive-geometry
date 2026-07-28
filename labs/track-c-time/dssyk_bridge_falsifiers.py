"""Track C/P3 -- DSSYK spectral-bridge falsifier ensembles.

The P3-2 bridge is non-tautological only if spectral rigidity is measured from
finite spectra independently of the Jacobi data used to evolve K(t). This lab
therefore reports three separately computed columns for each ensemble:

  1. b-profile disorder from a Krylov/Jacobi chain,
  2. the complexity arrow K(t)=<n> on that chain,
  3. unfolded spectral rigidity from finite Hamiltonian spectra.

A clean bridge-killer is either
  - RMT-rigid spectrum with localized/weak K(t), or
  - Poisson-like spectrum with delocalized/strong K(t).

The defaults are small enough for a fast local falsifier hunt; increase
--dim/--samples for paper-grade SEMs.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from typing import Callable

import numpy as np


RUN_ROOT = pathlib.Path(__file__).with_name("dssyk_bridge_runs")
POISSON_R = 0.3863
GOE_R = 0.5307


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def write_json(path: pathlib.Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def mean_sem(values: list[float]) -> tuple[float, float]:
    arr = np.asarray(values, dtype=float)
    mean = float(np.nanmean(arr))
    good = arr[np.isfinite(arr)]
    if good.size < 2:
        return mean, 0.0
    return mean, float(np.nanstd(good, ddof=1) / np.sqrt(good.size))


def tridiag(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    h = np.diag(a.astype(float))
    for i, bi in enumerate(b):
        h[i, i + 1] = h[i + 1, i] = float(bi)
    return h


def gap_ratio(energies: np.ndarray, trim_fraction: float = 0.12) -> float:
    e = np.sort(np.asarray(energies, dtype=float))
    trim = int(trim_fraction * len(e))
    if len(e) > 2 * trim + 4:
        e = e[trim:-trim]
    spacings = np.diff(e)
    spacings = spacings[spacings > 1e-12]
    if spacings.size < 2:
        return float("nan")
    ratios = np.minimum(spacings[:-1] / spacings[1:], spacings[1:] / spacings[:-1])
    return float(np.mean(ratios))


def unfolded_levels(energies: np.ndarray, degree: int = 3) -> np.ndarray:
    e = np.sort(np.asarray(energies, dtype=float))
    n = len(e)
    ranks = np.arange(n, dtype=float)
    lo, hi = int(0.12 * n), int(0.88 * n)
    if hi - lo < degree + 2:
        lo, hi = 0, n
    deg = min(degree, max(1, hi - lo - 2))
    coeff = np.polyfit(e[lo:hi], ranks[lo:hi], deg=deg)
    unfolded = np.polyval(coeff, e)
    unfolded = np.sort(unfolded)
    span = unfolded[-1] - unfolded[0]
    if span <= 0:
        return ranks
    return (unfolded - unfolded[0]) * ((n - 1) / span)


def number_variance(unfolded: np.ndarray, window: float = 4.0,
                    n_windows: int = 64) -> float:
    x = np.sort(np.asarray(unfolded, dtype=float))
    if x[-1] - x[0] <= window:
        return float("nan")
    starts = np.linspace(x[0], x[-1] - window, n_windows)
    counts = [
        int(np.searchsorted(x, start + window, side="right")
            - np.searchsorted(x, start, side="left"))
        for start in starts
    ]
    return float(np.var(counts, ddof=1)) if len(counts) > 1 else 0.0


def goe_matrix(dim: int, rng: np.random.Generator) -> np.ndarray:
    a = rng.normal(size=(dim, dim))
    h = (a + a.T) / np.sqrt(4.0 * dim)
    return (h + h.T) / 2


def poisson_matrix(dim: int, rng: np.random.Generator) -> np.ndarray:
    return np.diag(np.sort(rng.normal(size=dim)))


def anderson_chain(dim: int, rng: np.random.Generator, disorder: float = 5.0) -> np.ndarray:
    onsite = rng.uniform(-disorder / 2, disorder / 2, size=dim)
    hops = 1.0 + 0.20 * rng.normal(size=dim - 1)
    hops = np.clip(hops, 0.05, None)
    return tridiag(onsite, hops)


def beta_hermite_tridiag(dim: int, rng: np.random.Generator,
                         beta: float = 1.0) -> np.ndarray:
    # Dumitriu-Edelman beta-Hermite tridiagonal. The scale is irrelevant for
    # gap ratios, but the sqrt(dim) normalization keeps K(t) times comparable.
    a = rng.normal(0.0, np.sqrt(2.0), size=dim) / np.sqrt(dim)
    dfs = beta * np.arange(dim - 1, 0, -1)
    b = np.sqrt(rng.chisquare(dfs)) / np.sqrt(beta * dim)
    return tridiag(a, b)


def rosenzweig_porter(dim: int, rng: np.random.Generator,
                      coupling: float = 0.35) -> np.ndarray:
    diag = np.diag(rng.normal(size=dim))
    return diag + coupling * goe_matrix(dim, rng)


def banded_matrix(dim: int, rng: np.random.Generator, bandwidth: int = 5) -> np.ndarray:
    h = np.zeros((dim, dim), dtype=float)
    for offset in range(bandwidth + 1):
        vals = rng.normal(size=dim - offset)
        scale = np.sqrt(max(1, 2 * bandwidth + 1))
        vals = vals / scale
        i = np.arange(dim - offset)
        h[i, i + offset] = vals
        h[i + offset, i] = vals
    return (h + h.T) / 2


def dssyk_chord_chain(dim: int, q_deform: float = 0.65) -> np.ndarray:
    a = np.zeros(dim)
    if abs(1.0 - q_deform) < 1e-9:
        b = np.sqrt(np.arange(1, dim))
    else:
        n = np.arange(1, dim)
        b = np.sqrt((1.0 - q_deform ** n) / (1.0 - q_deform))
    return tridiag(a, b)


def lanczos_vector(H: np.ndarray, max_steps: int) -> tuple[np.ndarray, np.ndarray]:
    dim = H.shape[0]
    steps = min(max_steps, dim)
    v = np.zeros(dim)
    v[0] = 1.0
    v_prev = np.zeros(dim)
    basis = [v.copy()]
    a_vals: list[float] = []
    b_vals: list[float] = []
    b_prev = 0.0
    for _ in range(steps):
        w = H @ v
        a = float(v @ w)
        w = w - a * v - b_prev * v_prev
        for old in basis:
            w = w - float(old @ w) * old
        b = float(np.linalg.norm(w))
        a_vals.append(a)
        if b < 1e-10 or len(a_vals) >= steps:
            break
        b_vals.append(b)
        v_prev, v, b_prev = v, w / b, b
        basis.append(v.copy())
    return np.asarray(a_vals), np.asarray(b_vals)


def krylov_complexity(a: np.ndarray, b: np.ndarray,
                      times: np.ndarray) -> tuple[np.ndarray, float]:
    T = tridiag(a, b)
    evals, vecs = np.linalg.eigh(T)
    weights0 = vecs.T @ np.eye(len(a))[0]
    n_hat = np.arange(len(a), dtype=float)
    K = []
    for t in times:
        coeffs = vecs @ (np.exp(-1j * evals * t) * weights0)
        K.append(float(np.sum(n_hat * np.abs(coeffs) ** 2)))
    ipr = float(np.mean(np.sum(np.abs(vecs) ** 4, axis=0)))
    return np.asarray(K), ipr


def sample_model(name: str, dim: int, rng: np.random.Generator,
                 max_steps: int, times: np.ndarray,
                 args: argparse.Namespace) -> dict:
    builders: dict[str, Callable[[], np.ndarray]] = {
        "goe": lambda: goe_matrix(dim, rng),
        "poisson": lambda: poisson_matrix(dim, rng),
        "anderson": lambda: anderson_chain(dim, rng, args.anderson_disorder),
        "beta-hermite": lambda: beta_hermite_tridiag(dim, rng, args.beta),
        "rosenzweig-porter": lambda: rosenzweig_porter(dim, rng, args.rp_coupling),
        "banded": lambda: banded_matrix(dim, rng, args.bandwidth),
        "dssyk-chord": lambda: dssyk_chord_chain(dim, args.q_deform),
    }
    if name not in builders:
        raise ValueError(f"unknown model {name!r}")
    H = builders[name]()
    H = (H + H.T) / 2
    evals = np.linalg.eigvalsh(H)
    scale = float(np.std(evals))
    if scale <= 1e-12:
        scale = 1.0
    a, b = lanczos_vector(H / scale, max_steps=max_steps)
    K, ipr = krylov_complexity(a, b, times)
    b_mean = float(np.mean(b)) if b.size else 0.0
    b_cv = float(np.std(b) / b_mean) if b_mean > 0 else 0.0
    b_spike = float(np.max(b) / np.median(b)) if b.size and np.median(b) > 0 else 0.0
    unfolded = unfolded_levels(evals)
    return {
        "model": name,
        "gap_r": gap_ratio(evals),
        "number_variance_L4": number_variance(unfolded, window=4.0),
        "b_mean": b_mean,
        "b_cv": b_cv,
        "b_spike": b_spike,
        "chain_len": int(len(a)),
        "K_late": float(np.mean(K[int(0.75 * len(K)):])),
        "K_peak": float(np.max(K)),
        "K_spread_late": float(np.mean(K[int(0.75 * len(K)):]) / max(1, len(a) - 1)),
        "chain_eigenvector_ipr": ipr,
    }


def summarize_model(model: str, rows: list[dict]) -> dict:
    fields = [
        "gap_r",
        "number_variance_L4",
        "b_mean",
        "b_cv",
        "b_spike",
        "K_late",
        "K_peak",
        "K_spread_late",
        "chain_eigenvector_ipr",
        "chain_len",
    ]
    out: dict[str, float | str | bool] = {"model": model}
    for field in fields:
        mean, sem = mean_sem([float(row[field]) for row in rows])
        out[f"{field}_mean"] = mean
        out[f"{field}_sem"] = sem

    rigid = (
        float(out["gap_r_mean"]) > 0.49
        and float(out["number_variance_L4_mean"]) < 3.0
    )
    poisson_like = float(out["gap_r_mean"]) < 0.43
    localized = (
        float(out["K_spread_late_mean"]) < 0.22
        or float(out["chain_eigenvector_ipr_mean"]) > 0.18
    )
    delocalized = float(out["K_spread_late_mean"]) > 0.35
    out["spectral_rigidity_class"] = (
        "rigid/RMT-like" if rigid else "Poisson-like" if poisson_like else "intermediate"
    )
    out["krylov_arrow_class"] = (
        "localized/weak" if localized else "delocalized/strong" if delocalized else "intermediate"
    )
    out["candidate_bridge_killer"] = bool((rigid and localized) or (poisson_like and delocalized))
    if rigid and localized:
        out["bridge_killer_reason"] = "rigid/RMT-like finite spectrum but localized/weak K(t)"
    elif poisson_like and delocalized:
        out["bridge_killer_reason"] = "Poisson-like finite spectrum but delocalized/strong K(t)"
    else:
        out["bridge_killer_reason"] = "no clean contradiction at these thresholds"
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dim", type=int, default=64)
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument("--max-steps", type=int, default=48)
    parser.add_argument("--tmax", type=float, default=25.0)
    parser.add_argument("--times", type=int, default=160)
    parser.add_argument("--seed", type=int, default=20260728)
    parser.add_argument("--models", default=(
        "goe,poisson,anderson,beta-hermite,rosenzweig-porter,banded,dssyk-chord"
    ))
    parser.add_argument("--out", type=pathlib.Path, default=None)
    parser.add_argument("--anderson-disorder", type=float, default=5.0)
    parser.add_argument("--beta", type=float, default=1.0)
    parser.add_argument("--rp-coupling", type=float, default=0.35)
    parser.add_argument("--bandwidth", type=int, default=5)
    parser.add_argument("--q-deform", type=float, default=0.65)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.dim < 8 or args.samples < 1 or args.max_steps < 4:
        raise SystemExit("dim>=8, samples>=1, max-steps>=4 required")
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    times = np.linspace(0.0, args.tmax, args.times)
    run_dir = args.out or RUN_ROOT / f"p3_falsifiers_{utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=False)

    rng = np.random.default_rng(args.seed)
    samples: list[dict] = []
    summaries: list[dict] = []
    print("P3 DSSYK bridge falsifier sweep")
    print(f"dim={args.dim}, samples={args.samples}, max_steps={args.max_steps}")
    print("rigidity is measured from finite spectra; K(t) from the Krylov/Jacobi chain\n")

    for model in models:
        rows = []
        for _ in range(args.samples):
            row = sample_model(model, args.dim, rng, args.max_steps, times, args)
            rows.append(row)
            samples.append(row)
        summary = summarize_model(model, rows)
        summaries.append(summary)
        print(
            f"{model:>18}: r={summary['gap_r_mean']:.3f} "
            f"+/- {summary['gap_r_sem']:.3f}; "
            f"Sigma2(L=4)={summary['number_variance_L4_mean']:.2f}; "
            f"b_cv={summary['b_cv_mean']:.2f}; "
            f"Klate/chain={summary['K_spread_late_mean']:.2f}; "
            f"{summary['spectral_rigidity_class']} / "
            f"{summary['krylov_arrow_class']}; "
            f"killer={summary['candidate_bridge_killer']}"
        )

    payload = {
        "project": "PROJECT-3-DSSYK-BRIDGE P3-2 falsifier hunt",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "dim": args.dim,
            "samples": args.samples,
            "max_steps": args.max_steps,
            "tmax": args.tmax,
            "times": args.times,
            "seed": args.seed,
            "models": models,
            "anderson_disorder": args.anderson_disorder,
            "beta": args.beta,
            "rp_coupling": args.rp_coupling,
            "bandwidth": args.bandwidth,
            "q_deform": args.q_deform,
        },
        "classification_thresholds": {
            "rmt_like": "gap_r > 0.49 and number_variance_L4 < 3.0",
            "poisson_like": "gap_r < 0.43",
            "localized_weak": "K_spread_late < 0.22 or chain_eigenvector_ipr > 0.18",
            "delocalized_strong": "K_spread_late > 0.35",
        },
        "summaries": summaries,
        "samples": samples,
    }
    write_json(run_dir / "summary.json", payload)
    killers = [s for s in summaries if s["candidate_bridge_killer"]]
    print(f"\nsummary written: {run_dir / 'summary.json'}")
    if killers:
        print("candidate bridge-killers:")
        for item in killers:
            print(f"  {item['model']}: {item['bridge_killer_reason']}")
    else:
        print("no clean bridge-killer at this sweep size/threshold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
