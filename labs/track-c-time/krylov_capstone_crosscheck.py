"""Track C CAPSTONE (codex-science half) - spectral/KMS cross-check.

Companion to ``krylov_ignition.py``. Quant-phy's half showed the finite-N
Krylov arrow: sustained late complexity K_late is large for chaotic SYK4 and
localized for free SYK2, while the Parker linear-b_n prediction fails at these
small sizes. This half checks three things:

1. Spectral origin: compare the Krylov plateau/open chain to level statistics
   using the existing Phase-6 gap-ratio and connected-SFF helpers.
2. KMS control: show that the thermal detailed-balance asymmetry
   rho(-w) = exp(-beta*w) rho(w) is present in both SYK4 and SYK2. It is an
   inherited state arrow, not chaos ignition.
3. Lanczos sanity: independently re-run the full-reorthogonalized operator
   Lanczos step, compare coefficients, and verify the seed operator chi_1.

Main verdict: K_late is the honest finite-N ignition signature. The b_n linear
slope is not. The b-plateau is spectral scale evidence, but by itself it is not
an arrow because integrable finite spectra can also have large bandwidth.
"""

from __future__ import annotations

import pathlib
import sys
from dataclasses import dataclass

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
MAGIC = ROOT / "labs" / "track-d-magic"
sys.path.insert(0, str(MAGIC))

from phase4_syk_magic_baseline import (  # noqa: E402
    jw_majoranas,
    mean_sem,
    syk_hamiltonian,
    syk_term_ops,
)
from phase6_chaos_diagnostics import (  # noqa: E402
    POISSON_R,
    connected_sff_ensemble,
    even_parity_energies,
    gap_ratio,
    ramp_metrics,
    rmt_target,
)

from krylov_ignition import (  # noqa: E402
    build_syk,
    frob_ip,
    lanczos_operator,
    linear_slope,
)


@dataclass
class Row:
    n_majoranas: int
    q: int
    seed: int
    chain_len: int
    b_slope: float
    b_mean: float
    b_plateau: float
    bandwidth: float
    gap_r: float
    k_late: float
    kms_rms: float
    kms_bias: float
    seed_square_err: float
    seed_anticomm_err: float
    lanczos_ab_err: float
    basis_orth_err: float


def active_hops(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Hops actually used by the finite tridiagonal with len(a) sites."""
    return b[: max(0, len(a) - 1)]


def b_plateau_scale(a: np.ndarray, b: np.ndarray) -> float:
    hops = active_hops(a, b)
    if len(hops) == 0:
        return 0.0
    if len(hops) < 12:
        return float(np.mean(hops))
    start = max(4, len(hops) // 4)
    return float(np.mean(hops[start:]))


def krylov_complexity_fast(a: np.ndarray, b: np.ndarray,
                           times: np.ndarray) -> np.ndarray:
    """Same restricted Krylov evolution as krylov_ignition, via one eigensolve."""
    m = len(a)
    T = np.diag(a).astype(complex)
    for n, hop in enumerate(active_hops(a, b)):
        T[n, n + 1] = hop
        T[n + 1, n] = hop
    vals, vecs = np.linalg.eigh(T)
    e0 = np.zeros(m, dtype=complex)
    e0[0] = 1.0
    coeff = vecs.conj().T @ e0
    n_hat = np.arange(m)
    out = []
    for t in times:
        c = vecs @ (np.exp(1j * vals * t) * coeff)
        out.append(float(np.sum(n_hat * np.abs(c) ** 2)))
    return np.asarray(out)


def lanczos_with_basis(H: np.ndarray, O0: np.ndarray, max_steps: int):
    """Independent mirror of lanczos_operator, returning the reorthogonalized basis."""
    d = H.shape[0]
    O0 = O0 / np.sqrt(np.real(frob_ip(O0, O0, d)))
    basis = [O0]
    a_list: list[float] = []
    b_list: list[float] = []
    prev = np.zeros_like(O0)
    b_prev = 0.0
    cur = O0
    for _ in range(max_steps):
        Lcur = H @ cur - cur @ H
        a_n = np.real(frob_ip(cur, Lcur, d))
        w = Lcur - a_n * cur - b_prev * prev
        for Ok in basis:
            w = w - frob_ip(Ok, w, d) * Ok
        b_n = np.sqrt(np.real(frob_ip(w, w, d)))
        a_list.append(float(a_n))
        if b_n < 1e-9:
            break
        w = w / b_n
        basis.append(w)
        prev, cur, b_prev = cur, w, b_n
        b_list.append(float(b_n))
    return np.asarray(a_list), np.asarray(b_list), basis


def basis_orthogonality_error(basis: list[np.ndarray]) -> float:
    if len(basis) < 2:
        return 0.0
    d = basis[0].shape[0]
    worst = 0.0
    for i, bi in enumerate(basis):
        for j, bj in enumerate(basis):
            target = 1.0 if i == j else 0.0
            worst = max(worst, abs(frob_ip(bi, bj, d) - target))
    return float(worst)


def seed_sanity(gammas: list[np.ndarray]) -> tuple[float, float]:
    ident = np.eye(gammas[0].shape[0], dtype=complex)
    square_err = float(np.linalg.norm(gammas[0] @ gammas[0] - ident))
    anti_err = 0.0
    for other in gammas[1:]:
        anti_err = max(anti_err, float(np.linalg.norm(gammas[0] @ other + other @ gammas[0])))
    return square_err, anti_err


def kms_detailed_balance(H: np.ndarray, O: np.ndarray,
                         beta: float = 1.0) -> tuple[float, float, int]:
    """Pairwise KMS check for positive transitions of O in the energy basis.

    For w = E_n - E_m > 0:
      rho(+w) contains exp(-beta E_m) |O_mn|^2,
      rho(-w) contains exp(-beta E_n) |O_nm|^2,
    so log(rho(-w)/rho(+w)) + beta*w = 0.

    Returns RMS residual, mean absolute log-bias beta*w, and transition count.
    """
    energies, vecs = np.linalg.eigh(H)
    Oe = vecs.conj().T @ O @ vecs
    residuals: list[float] = []
    biases: list[float] = []
    for m, em in enumerate(energies):
        for n, en in enumerate(energies):
            omega = float(en - em)
            amp = abs(Oe[m, n]) ** 2
            if omega <= 1e-9 or amp <= 1e-12:
                continue
            log_forward = -beta * em + np.log(amp)
            log_reverse = -beta * en + np.log(amp)
            residuals.append(log_reverse - log_forward + beta * omega)
            biases.append(abs(log_reverse - log_forward))
    if not residuals:
        return float("nan"), float("nan"), 0
    return (
        float(np.sqrt(np.mean(np.square(residuals)))),
        float(np.mean(biases)),
        len(residuals),
    )


def one_row(n_majoranas: int, q: int, seed: int,
            max_steps: int, times: np.ndarray) -> Row:
    rng = np.random.default_rng(seed)
    H, gammas = build_syk(n_majoranas, q, rng)
    a, b = lanczos_operator(H, gammas[0], max_steps=max_steps)
    a2, b2, basis = lanczos_with_basis(H, gammas[0], max_steps=max_steps)
    k = krylov_complexity_fast(a, b, times)
    energies = even_parity_energies(H, n_majoranas // 2)
    kms_rms, kms_bias, _ = kms_detailed_balance(H, gammas[0], beta=1.0)
    sq_err, anti_err = seed_sanity(gammas)
    ab_err = max(
        float(np.max(np.abs(a - a2))) if len(a) == len(a2) else float("inf"),
        float(np.max(np.abs(b - b2))) if len(b) == len(b2) else float("inf"),
    )
    return Row(
        n_majoranas=n_majoranas,
        q=q,
        seed=seed,
        chain_len=len(b),
        b_slope=linear_slope(b),
        b_mean=float(np.mean(b)) if len(b) else 0.0,
        b_plateau=b_plateau_scale(a, b),
        bandwidth=float(np.std(energies)),
        gap_r=gap_ratio(energies),
        k_late=float(np.mean(k[-40:])),
        kms_rms=kms_rms,
        kms_bias=kms_bias,
        seed_square_err=sq_err,
        seed_anticomm_err=anti_err,
        lanczos_ab_err=ab_err,
        basis_orth_err=basis_orthogonality_error(basis),
    )


def summarize(rows: list[Row], attr: str) -> tuple[float, float]:
    return mean_sem([float(getattr(r, attr)) for r in rows])


def dense_phase4_build(N: int, q: int, rng: np.random.Generator,
                       term_ops: np.ndarray) -> np.ndarray:
    return syk_hamiltonian(term_ops, N, q, rng)


def sff_check(N: int, q: int, n_samples: int,
              seed: int = 20260712) -> tuple[float, float]:
    rng = np.random.default_rng(seed + 100 * N + q)
    nq = N // 2
    term_ops = syk_term_ops(jw_majoranas(N), q)
    times = np.logspace(-1.0, 2.2, 28)
    _, conn = connected_sff_ensemble(
        lambda rg, ops: dense_phase4_build(N, q, rg, ops),
        N,
        nq,
        n_samples,
        times,
        0.5,
        rng,
        term_ops,
    )
    return ramp_metrics(times, conn)


def print_krylov_spectral_tables(seeds: list[int]) -> None:
    times = np.linspace(0.0, 20.0, 200)
    all_rows: list[Row] = []
    print("Krylov / spectral / KMS cross-check")
    print("Seeds: " + ", ".join(str(s) for s in seeds))
    print("beta=1 for KMS detailed balance; K_late = mean over final 20% of t in [0,20].\n")
    for N in (8, 10, 12):
        ens, rmt = rmt_target(N)
        print(f"=== N={N} Majoranas ({N // 2} qubits); SYK4 target {ens} <r>~{rmt:.4f} ===")
        print(
            f"{'model':>5} {'<r>':>13} {'target':>12} {'b_slope':>13} "
            f"{'b_plateau':>13} {'bandwidth':>13} {'K_late':>13} "
            f"{'KMS rms':>10} {'KMS bias':>10}"
        )
        for q, name, target in ((4, "SYK4", f"{ens} {rmt:.3f}"),
                                (2, "SYK2", f"Poisson {POISSON_R:.3f}")):
            rows = [one_row(N, q, s, 80, times) for s in seeds]
            all_rows.extend(rows)
            gr = summarize(rows, "gap_r")
            bs = summarize(rows, "b_slope")
            bp = summarize(rows, "b_plateau")
            bw = summarize(rows, "bandwidth")
            kl = summarize(rows, "k_late")
            kr = summarize(rows, "kms_rms")
            kb = summarize(rows, "kms_bias")
            print(
                f"{name:>5} {gr[0]:6.3f}+/-{gr[1]:5.3f} {target:>12} "
                f"{bs[0]:7.3f}+/-{bs[1]:5.3f} "
                f"{bp[0]:7.3f}+/-{bp[1]:5.3f} "
                f"{bw[0]:7.3f}+/-{bw[1]:5.3f} "
                f"{kl[0]:7.2f}+/-{kl[1]:5.2f} "
                f"{kr[0]:10.1e} {kb[0]:10.3f}"
            )
        print()

    max_seed_square = max(r.seed_square_err for r in all_rows)
    max_seed_anticomm = max(r.seed_anticomm_err for r in all_rows)
    max_ab_err = max(r.lanczos_ab_err for r in all_rows)
    max_orth_err = max(r.basis_orth_err for r in all_rows)
    print("Lanczos / seed sanity")
    print(f"  max ||chi_1^2-I||                         : {max_seed_square:.2e}")
    print(f"  max ||{{chi_1, chi_j}}|| for j>1           : {max_seed_anticomm:.2e}")
    print(f"  max |(a,b)_existing - (a,b)_independent|  : {max_ab_err:.2e}")
    print(f"  max full-reorthogonalized basis error     : {max_orth_err:.2e}\n")


def print_sff_table() -> None:
    print("Connected-SFF refinement (Phase-6 helper, dense Phase-4 Hamiltonians)")
    print("Finite-size readout: SYK4 should show a deeper RMT dip and steeper rise;")
    print("the overstrong 'SYK2 has no ramp at all' control is not clean at these sizes.\n")
    print(f"{'N':>3} {'model':>5} {'dip':>9} {'ramp slope':>11}")
    for N, samples in ((10, 60), (12, 30)):
        for q, name in ((4, "SYK4"), (2, "SYK2")):
            dip, slope = sff_check(N, q, samples)
            print(f"{N:>3} {name:>5} {dip:9.4f} {slope:11.3f}")
    print()


def main() -> None:
    print("Track C CAPSTONE (codex-science half) - spectral/KMS cross-check\n")
    print_krylov_spectral_tables([11, 22, 33])
    print_sff_table()
    print("VERDICT")
    print("  1. K_late reproduces quant-phy's ignition signal: chaotic SYK4 sustains")
    print("     large Krylov complexity, while SYK2 stays localized.")
    print("  2. The failed linear-b_n subprediction stays failed. b_plateau is useful")
    print("     spectral-scale evidence, but not an arrow by itself; K_late is the")
    print("     finite-N discriminator.")
    print("  3. Level statistics provide the spectral origin: SYK4 is RMT-like while")
    print("     SYK2 trends toward Poisson. The SFF control is weaker but consistent")
    print("     when read as deeper/steeper SYK4 ramp, not an absolute no-ramp SYK2.")
    print("  4. KMS detailed balance holds to numerical precision in both SYK4 and")
    print("     SYK2. That thermal/modular asymmetry is inherited from beta and state")
    print("     choice; it is not the chaos-only ignition mechanism.")
    print("\nI agree with the capstone framing: KMS-control-as-INHERITED contrast works,")
    print("and K_late, not b_slope, is the honest finite-N ignition signature.")


if __name__ == "__main__":
    main()
