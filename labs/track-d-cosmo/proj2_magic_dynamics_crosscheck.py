"""Project 2 dynamics cross-checks for the dS/SYK horizon-magic claim.

This is Tobin/codex-science's independent check of
proj2_magic_dynamics.py. It does not change the pre-registration. It tests
three possible failure modes in the refined dynamics result:

  1. Small-sample fragility: recompute the late-time plateau gap and rise
     ratio with an independent seed and explicit SEMs.
  2. Spectrum-only contamination: compare each TFD trajectory with a
     same-spectrum diagonal-basis TFD, which keeps the energy weights/phases
     but removes the Hamiltonian eigenbasis.
  3. Overstated timing: quantify the relation between magic saturation and
     the SFF dip instead of relying on a visual "near the dip" statement.

The TFD is pure, so this is not a mixed-state false-positive control. It is a
Hamiltonian-structure control for the dynamics.
"""

from __future__ import annotations

import pathlib
import sys
from dataclasses import dataclass

import numpy as np

THIS_DIR = pathlib.Path(__file__).resolve().parent
MAGIC_DIR = THIS_DIR.parent / "track-d-magic"
sys.path.insert(0, str(THIS_DIR))
sys.path.insert(0, str(MAGIC_DIR))

from phase0_wedge_magic import m2  # noqa: E402
from phase4_syk_magic_baseline import jw_majoranas, mean_sem, syk_hamiltonian, syk_term_ops  # noqa: E402
from proj2_magic_dynamics import sff, tfd_evolved  # noqa: E402


@dataclass(frozen=True)
class CurveSample:
    magic: np.ndarray
    diagonal_twin_magic: np.ndarray
    sff: np.ndarray


def rho(psi: np.ndarray) -> np.ndarray:
    return np.outer(psi, psi.conj())


def diagonalize_sample(n_majoranas: int, q: int, term_ops: np.ndarray,
                       rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    h = syk_hamiltonian(term_ops, n_majoranas, q, rng)
    vals, vecs = np.linalg.eigh(h)
    return vals.real, vecs


def sample_curve(n_majoranas: int, q: int, beta: float, times: np.ndarray,
                 term_ops: np.ndarray, rng: np.random.Generator) -> CurveSample:
    vals, vecs = diagonalize_sample(n_majoranas, q, term_ops, rng)
    ident_vecs = np.eye(vecs.shape[0], dtype=complex)

    magic = np.array([
        m2(rho(tfd_evolved(beta, t, vals, vecs))) for t in times
    ])
    diagonal_twin_magic = np.array([
        m2(rho(tfd_evolved(beta, t, vals, ident_vecs))) for t in times
    ])
    return CurveSample(
        magic=magic,
        diagonal_twin_magic=diagonal_twin_magic,
        sff=sff(beta, times, vals),
    )


def first_saturation_time(times: np.ndarray, curve: np.ndarray,
                          plateau: float, frac: float = 0.95) -> float:
    target = curve[0] + frac * (plateau - curve[0])
    if plateau <= curve[0]:
        return float("nan")
    hit = np.flatnonzero(curve >= target)
    return float(times[int(hit[0])]) if hit.size else float("nan")


def local_or_global_sff_dip_time(times: np.ndarray, curve: np.ndarray) -> float:
    """Return the first local SFF dip; fall back to the global minimum."""
    for i in range(1, len(curve) - 1):
        if curve[i] <= curve[i - 1] and curve[i] <= curve[i + 1]:
            return float(times[i])
    return float(times[int(np.argmin(curve))])


def summarize_samples(n_majoranas: int, q4_samples: list[CurveSample],
                      q2_samples: list[CurveSample], times: np.ndarray) -> dict[str, float]:
    m4 = np.asarray([sample.magic for sample in q4_samples])
    m2_ = np.asarray([sample.magic for sample in q2_samples])
    d4 = np.asarray([sample.diagonal_twin_magic for sample in q4_samples])
    d2 = np.asarray([sample.diagonal_twin_magic for sample in q2_samples])
    s4 = np.asarray([sample.sff for sample in q4_samples])
    s2 = np.asarray([sample.sff for sample in q2_samples])

    # Match the published script's plateau definition: mean of the last 3 time
    # points, then compare to t=0.
    init4, init2 = m4[:, 0], m2_[:, 0]
    plat4, plat2 = np.mean(m4[:, -3:], axis=1), np.mean(m2_[:, -3:], axis=1)
    rise4, rise2 = plat4 - init4, plat2 - init2
    gap = plat4 - plat2
    ratio = rise4 / np.clip(rise2, 1e-12, None)

    twin_plat4 = np.mean(d4[:, -3:], axis=1)
    twin_plat2 = np.mean(d2[:, -3:], axis=1)
    basis_ctl_gap = (plat4 - twin_plat4) - (plat2 - twin_plat2)

    mean_m4 = np.mean(m4, axis=0)
    mean_m2 = np.mean(m2_, axis=0)
    mean_s4 = np.mean(s4, axis=0)
    mean_s2 = np.mean(s2, axis=0)
    mean_plat4, mean_plat2 = float(np.mean(mean_m4[-3:])), float(np.mean(mean_m2[-3:]))

    gap_mu, gap_se = mean_sem(gap.tolist())
    ratio_mu, ratio_se = mean_sem(ratio.tolist())
    basis_mu, basis_se = mean_sem(basis_ctl_gap.tolist())

    sat4 = first_saturation_time(times, mean_m4, mean_plat4)
    sat2 = first_saturation_time(times, mean_m2, mean_plat2)
    dip4 = local_or_global_sff_dip_time(times, mean_s4)
    dip2 = local_or_global_sff_dip_time(times, mean_s2)

    print(f"N={n_majoranas} Majoranas, samples={len(q4_samples)} per model")
    print(f"  plateau gap SYK4-SYK2: {gap_mu:+.4f} +/- {gap_se:.4f}")
    print(f"  rise ratio SYK4/SYK2:  {ratio_mu:.2f} +/- {ratio_se:.2f}x")
    print(f"  same-spectrum diagonal-basis controlled plateau gap:")
    print(f"      {basis_mu:+.4f} +/- {basis_se:.4f}")
    print(f"  timing from mean curves:")
    print(f"      SYK4 magic 95% saturation t={sat4:.3g}, first SFF dip t={dip4:.3g}")
    print(f"      SYK2 magic 95% saturation t={sat2:.3g}, first SFF dip t={dip2:.3g}")
    print()

    return {
        "n": float(n_majoranas),
        "gap_mu": gap_mu,
        "gap_se": gap_se,
        "ratio_mu": ratio_mu,
        "ratio_se": ratio_se,
        "basis_mu": basis_mu,
        "basis_se": basis_se,
        "sat4": sat4,
        "dip4": dip4,
    }


def run_crosscheck() -> list[dict[str, float]]:
    print("Project 2 dynamics cross-check -- independent seed + controls\n")
    beta = 1.0
    seed = 20260711
    rng = np.random.default_rng(seed)
    times = np.array([
        0.0, 0.5, 1.0, 1.5, 2.0, 2.67, 3.16, 5.0, 8.0, 12.0, 30.0, 80.0, 126.0
    ])
    plan = {6: 48, 8: 32, 10: 8}
    print(f"beta={beta}, seed={seed}, sample_plan={plan}")
    print(f"time grid={times.tolist()}\n")

    summaries: list[dict[str, float]] = []
    for n_majoranas, n_samples in plan.items():
        ops4 = syk_term_ops(jw_majoranas(n_majoranas), 4)
        ops2 = syk_term_ops(jw_majoranas(n_majoranas), 2)
        q4_samples = [
            sample_curve(n_majoranas, 4, beta, times, ops4, rng)
            for _ in range(n_samples)
        ]
        q2_samples = [
            sample_curve(n_majoranas, 2, beta, times, ops2, rng)
            for _ in range(n_samples)
        ]
        summaries.append(summarize_samples(n_majoranas, q4_samples, q2_samples, times))

    gaps = [item["gap_mu"] for item in summaries]
    basis_gaps = [item["basis_mu"] for item in summaries]
    print("CROSS-CHECK VERDICT")
    print(f"  plateau gap trend: {gaps[0]:+.3f} -> {gaps[1]:+.3f} -> {gaps[2]:+.3f}")
    print(f"  diagonal-basis controlled trend: "
          f"{basis_gaps[0]:+.3f} -> {basis_gaps[1]:+.3f} -> {basis_gaps[2]:+.3f}")
    print("  N=6 is a finite-size failure for the positive plateau-gap claim;")
    print("  the robust plateau evidence is N=8 -> N=10, with SEMs above.")
    print("  The TFD state is pure, so raw M2 is not a mixed-state false positive.")
    print("  The same-spectrum diagonal-basis control is not positive until N=10,")
    print("  so the N=8 raw gap should be read as spectral/dynamical, not as a")
    print("  clean eigenbasis-only discriminator.")
    print("  Timing is only order-of-magnitude: magic saturation precedes or sits")
    print("  near the first SFF dip on this coarse grid, not a precise one-to-one lock.")
    return summaries


if __name__ == "__main__":
    run_crosscheck()
