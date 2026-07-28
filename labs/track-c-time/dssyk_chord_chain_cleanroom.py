"""Track C/P3 S1 -- clean-room DSSYK chord-chain reproduction.

This file intentionally reimplements the S1 chord-chain readout from the
formula posted on yaklog, without importing the authored lab:

    b_n = sqrt((1 - q**n) / (1 - q)),   a_n = 0,   |psi(0)> = |0>.

The finite matrix is only a cutoff.  Reported velocities are fit in a
pre-reflection window, before the ballistic front can reach the final site.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

import numpy as np
from scipy.linalg import eigh_tridiagonal


DEFAULT_QS = (0.05, 0.30, 0.50, 0.70, 0.90)
REFERENCE_E2 = {
    0.05: 1.71,
    0.30: 1.80,
    0.50: 1.86,
    0.70: 1.92,
    0.90: 1.97,
}


@dataclass
class VelocityResult:
    q: float
    b_inf: float
    fit_t_min: float
    fit_t_max: float
    velocity: float
    velocity_over_b_inf: float
    reference_over_b_inf: float | None
    delta_from_reference: float | None


def chord_hops(q_deform: float, dim: int) -> np.ndarray:
    if not 0.0 <= q_deform <= 1.0:
        raise ValueError("q_deform must be in [0, 1] for the DSSYK chord chain")
    n = np.arange(1, dim, dtype=float)
    if abs(1.0 - q_deform) < 1e-12:
        return np.sqrt(n)
    return np.sqrt((1.0 - q_deform ** n) / (1.0 - q_deform))


def complexity_curve(q_deform: float, dim: int,
                     times: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    hops = chord_hops(q_deform, dim)
    evals, vecs = eigh_tridiagonal(np.zeros(dim), hops)
    weights0 = vecs[0, :]
    n_hat = np.arange(dim, dtype=float)
    values = []
    for t in times:
        coeffs = vecs @ (np.exp(-1j * evals * t) * weights0)
        values.append(float(np.sum(n_hat * np.abs(coeffs) ** 2)))
    return np.asarray(values), hops


def b_infinity(q_deform: float) -> float:
    if abs(1.0 - q_deform) < 1e-12:
        return float("inf")
    return float(1.0 / np.sqrt(1.0 - q_deform))


def fit_ballistic_velocity(q_deform: float, *, dim: int, n_times: int,
                           tmax_factor: float, fit_start: float,
                           fit_stop: float) -> VelocityResult:
    b_inf = b_infinity(q_deform)
    # The fastest semi-infinite front is bounded by about 2 b_inf.  Keep the
    # sampled window well before the front can reach the finite cutoff.
    t_reflect = (dim - 1) / (2.0 * b_inf)
    times = np.linspace(0.0, tmax_factor * t_reflect, n_times)
    K, _ = complexity_curve(q_deform, dim, times)
    lo = int(fit_start * n_times)
    hi = int(fit_stop * n_times)
    slope, _ = np.polyfit(times[lo:hi], K[lo:hi], deg=1)
    ratio = float(slope / b_inf)
    ref = REFERENCE_E2.get(round(float(q_deform), 2))
    delta = None if ref is None else ratio - ref
    return VelocityResult(
        q=float(q_deform),
        b_inf=b_inf,
        fit_t_min=float(times[lo]),
        fit_t_max=float(times[hi - 1]),
        velocity=float(slope),
        velocity_over_b_inf=ratio,
        reference_over_b_inf=ref,
        delta_from_reference=delta,
    )


def early_quadratic_check(q_deform: float, dim: int, t_probe: float) -> dict:
    K, hops = complexity_curve(q_deform, dim, np.asarray([t_probe]))
    target = float(hops[0] ** 2 * t_probe ** 2)
    return {
        "q": float(q_deform),
        "t": float(t_probe),
        "K": float(K[0]),
        "b1_squared_t_squared": target,
        "abs_error": float(abs(K[0] - target)),
    }


def oscillator_limit_check(dim: int) -> dict:
    times = np.linspace(0.05, 2.0, 80)
    K, _ = complexity_curve(1.0, dim, times)
    slope, intercept = np.polyfit(np.log(times), np.log(K), deg=1)
    max_rel = float(np.max(np.abs(K - times ** 2) / np.maximum(times ** 2, 1e-15)))
    return {
        "q": 1.0,
        "loglog_slope": float(slope),
        "loglog_intercept": float(intercept),
        "max_relative_error_vs_t_squared": max_rel,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dim", type=int, default=600)
    parser.add_argument("--n-times", type=int, default=500)
    parser.add_argument("--tmax-factor", type=float, default=0.30)
    parser.add_argument("--fit-start", type=float, default=0.35)
    parser.add_argument("--fit-stop", type=float, default=0.75)
    parser.add_argument("--q", type=float, nargs="*", default=list(DEFAULT_QS))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.dim < 16:
        raise SystemExit("--dim must be at least 16")
    if not (0.0 < args.fit_start < args.fit_stop < 1.0):
        raise SystemExit("fit fractions must obey 0 < start < stop < 1")

    quadratic = early_quadratic_check(0.65, args.dim, 0.01)
    velocities = [
        fit_ballistic_velocity(
            q,
            dim=args.dim,
            n_times=args.n_times,
            tmax_factor=args.tmax_factor,
            fit_start=args.fit_start,
            fit_stop=args.fit_stop,
        )
        for q in args.q
    ]
    oscillator = oscillator_limit_check(min(args.dim, 240))
    open_chain = {
        f"{q:.2f}": bool(np.min(chord_hops(q, args.dim)) > 0.0)
        for q in args.q if q > 0.0
    }

    payload = {
        "quadratic_E1": quadratic,
        "ballistic_E2": [asdict(item) for item in velocities],
        "oscillator_E3": oscillator,
        "open_chain_E4": open_chain,
        "method": (
            "clean-room q-oscillator tridiagonal; finite cutoff; K(t)=<n>; "
            "linear fit inside a pre-reflection window"
        ),
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print("Track C/P3 S1 clean-room DSSYK chord chain\n")
    print("E1 early-time check")
    print(
        "  K={K:.8e}, b1^2 t^2={b1_squared_t_squared:.8e}, "
        "|delta|={abs_error:.2e}".format(**quadratic)
    )
    print("\nE2 ballistic pre-reflection velocity")
    print(f"  {'q':>5} {'v/b_inf':>9} {'ref':>8} {'delta':>9} {'fit window':>23}")
    for item in velocities:
        ref = item.reference_over_b_inf
        delta = item.delta_from_reference
        print(
            f"  {item.q:5.2f} {item.velocity_over_b_inf:9.3f} "
            f"{ref if ref is not None else float('nan'):8.3f} "
            f"{delta if delta is not None else float('nan'):9.3f} "
            f"[{item.fit_t_min:.2f}, {item.fit_t_max:.2f}]"
        )
    print("\nE3 q -> 1 oscillator limit")
    print(
        "  log K vs log t slope={loglog_slope:.4f}; "
        "max rel error vs t^2={max_relative_error_vs_t_squared:.2e}".format(
            **oscillator
        )
    )
    print("\nE4 open-chain sanity")
    print("  all sampled q have positive hops:", all(open_chain.values()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
