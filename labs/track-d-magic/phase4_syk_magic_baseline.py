"""Track D, Phase 4 -- SYK magic baseline.

ASSIGNMENT: establish a small-N executable baseline for the claim that
chaotic SYK4 carries more non-stabilizerness than free/integrable SYK2, and
that their connected Majorana/Pauli spectra have different shapes.

PRIMARY SOURCES READ FIRST:
  - Bera and Schiro, arXiv:2502.01582.
    Claim used here: SYK4 ground states have a Gaussian-like connected
    Majorana spectrum and larger SRE; SYK2/free fermions have a Laplace-like
    connected spectrum and lower SRE at larger matched sizes.
  - Jasser, Odavic and Hamma, arXiv:2502.03093.
    Claim used here: in the Majorana SYK4+SYK2 interpolation, SYK4 is the
    chaotic endpoint, SYK2 is the free endpoint, and SRE distinguishes their
    non-stabilizer structure.

CONVENTION USED IN THIS LAB:
  N real Majoranas chi_i mapped to N/2 qubits by Jordan-Wigner,

      H_q = i^(q/2) sum_{i1<...<iq} J_{i1...iq} chi_i1 ... chi_iq,
      Var(J) = (q-1)! / N^(q-1),   J = 1.

This follows the standard real-Majorana SYK convention used in the
Jasser-Odavic-Hamma model section. It is not a literal reproduction of
Bera-Schiro's complex-fermion half-filling numerics; it tests the same
SYK4-vs-SYK2 magic separation in the requested N-Majorana -> N/2-qubit setup.

PRE-REGISTERED PREDICTIONS:
  P1: disorder-averaged M2(SYK4 ground state) > M2(SYK2 ground state) at
      matched N, with the separation clearer at N=10,12 than at N=8.
  P2: the connected Pauli/Majorana spectrum of SYK4 is closer to a Gaussian
      than a Laplace law; SYK2 is closer to a Laplace law than a Gaussian.
      We quantify this by DeltaAIC/string = (AIC_Laplace - AIC_Gaussian)/n:
        positive -> Gaussian better, negative -> Laplace better.
  P3: any finite-size failure is reported as a failure, not hidden.

The SRE engine is intentionally reused from phase0_wedge_magic.m2.
"""

from __future__ import annotations

import argparse
import math
import pathlib
import sys
from dataclasses import dataclass
from itertools import combinations

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from phase0_wedge_magic import fwht, m2  # noqa: E402


PAULI_1Q = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}

DEFAULT_SAMPLE_PLAN = {8: 40, 10: 24, 12: 12}
ZERO_TOL = 1e-10


@dataclass
class SampleResult:
    m2: float
    shape_delta_per_string: float
    excess_kurtosis: float
    connected_count: int
    ground_energy: float


def kron_all(ops: list[np.ndarray]) -> np.ndarray:
    out = ops[0]
    for op in ops[1:]:
        out = np.kron(out, op)
    return out


def jw_majoranas(n_majoranas: int) -> list[np.ndarray]:
    """Jordan-Wigner Majoranas with {chi_i, chi_j}=2 delta_ij."""
    if n_majoranas % 2:
        raise ValueError("N Majoranas must be even for an N/2-qubit JW map")
    n_qubits = n_majoranas // 2
    gammas: list[np.ndarray] = []
    for site in range(n_qubits):
        prefix = ["Z"] * site
        suffix = ["I"] * (n_qubits - site - 1)
        gammas.append(kron_all([PAULI_1Q[p] for p in prefix + ["X"] + suffix]))
        gammas.append(kron_all([PAULI_1Q[p] for p in prefix + ["Y"] + suffix]))

    ident = np.eye(2**n_qubits, dtype=complex)
    for i, gi in enumerate(gammas):
        err = np.linalg.norm(gi @ gi - ident)
        if err > 1e-10:
            raise AssertionError(f"Majorana {i} does not square to I")
    return gammas


def syk_term_ops(gammas: list[np.ndarray], q: int) -> np.ndarray:
    """Hermitian q-Majorana operators i^(q/2) chi_i1...chi_iq."""
    phase = (1j) ** (q // 2)
    ops = []
    for combo in combinations(range(len(gammas)), q):
        op = np.eye(gammas[0].shape[0], dtype=complex)
        for idx in combo:
            op = op @ gammas[idx]
        op = phase * op
        # Numerical guard; the algebra makes this Hermitian for even q.
        op = (op + op.conj().T) / 2
        ops.append(op)
    return np.asarray(ops)


def syk_hamiltonian(term_ops: np.ndarray, n_majoranas: int, q: int,
                    rng: np.random.Generator) -> np.ndarray:
    sigma = math.sqrt(math.factorial(q - 1) / (n_majoranas ** (q - 1)))
    couplings = rng.normal(loc=0.0, scale=sigma, size=term_ops.shape[0])
    h = np.tensordot(couplings, term_ops, axes=(0, 0))
    return (h + h.conj().T) / 2


def ground_state(hamiltonian: np.ndarray) -> tuple[float, np.ndarray]:
    vals, vecs = np.linalg.eigh(hamiltonian)
    return float(vals[0]), vecs[:, 0]


def density(psi: np.ndarray) -> np.ndarray:
    return np.outer(psi, psi.conj())


def pauli_expectations(rho: np.ndarray) -> np.ndarray:
    """All signed Tr(rho P) for Hermitian Paulis P = i^(x.z) X^x Z^z."""
    dim = rho.shape[0]
    idx = np.arange(dim)
    vals = []
    for x in range(dim):
        shifted_diag = rho[idx ^ x, idx]
        transformed = fwht(shifted_diag)
        phases = np.array([(1j) ** ((x & z).bit_count()) for z in range(dim)])
        signed = phases * transformed
        vals.extend(np.real_if_close(signed, tol=1000).real)
    return np.asarray(vals, dtype=float)


def connected_spectrum_values(rho: np.ndarray) -> np.ndarray:
    vals = pauli_expectations(rho)
    nonzero = np.abs(vals) > ZERO_TOL
    nontrivial = np.abs(np.abs(vals) - 1.0) > ZERO_TOL
    return vals[nonzero & nontrivial]


def shape_metrics(values: np.ndarray) -> tuple[float, float]:
    """Return (DeltaAIC per datum, excess kurtosis).

    DeltaAIC = AIC_Laplace - AIC_Gaussian, so positive means Gaussian better.
    Both fits have two parameters: location and scale.
    """
    n = values.size
    if n < 8:
        return float("nan"), float("nan")

    mu = float(np.mean(values))
    centered = values - mu
    sigma = float(np.sqrt(np.mean(centered**2)))
    sigma = max(sigma, 1e-300)
    ll_gauss = float(-n * np.log(sigma * np.sqrt(2 * np.pi))
                     - np.sum(centered**2) / (2 * sigma**2))

    med = float(np.median(values))
    b = float(np.mean(np.abs(values - med)))
    b = max(b, 1e-300)
    ll_laplace = float(-n * np.log(2 * b) - np.sum(np.abs(values - med)) / b)

    aic_gauss = 2 * 2 - 2 * ll_gauss
    aic_laplace = 2 * 2 - 2 * ll_laplace
    variance = float(np.mean(centered**2))
    fourth = float(np.mean(centered**4))
    kurtosis = fourth / (variance**2) - 3.0 if variance > 0 else float("nan")
    return (aic_laplace - aic_gauss) / n, kurtosis


def one_sample(n_majoranas: int, q: int, term_ops: np.ndarray,
               rng: np.random.Generator) -> SampleResult:
    h = syk_hamiltonian(term_ops, n_majoranas, q, rng)
    energy, psi = ground_state(h)
    rho = density(psi)
    values = connected_spectrum_values(rho)
    delta, kurtosis = shape_metrics(values)
    return SampleResult(
        m2=m2(rho),
        shape_delta_per_string=delta,
        excess_kurtosis=kurtosis,
        connected_count=int(values.size),
        ground_energy=energy,
    )


def mean_sem(xs: list[float]) -> tuple[float, float]:
    arr = np.asarray(xs, dtype=float)
    mean = float(np.mean(arr))
    if arr.size < 2:
        return mean, float("nan")
    return mean, float(np.std(arr, ddof=1) / np.sqrt(arr.size))


def parse_sample_plan(text: str | None) -> dict[int, int]:
    if text is None:
        return dict(DEFAULT_SAMPLE_PLAN)
    plan: dict[int, int] = {}
    for item in text.split(","):
        n_txt, s_txt = item.split(":")
        plan[int(n_txt)] = int(s_txt)
    return plan


def self_test_magic_engine() -> None:
    t = np.array([1, np.exp(1j * np.pi / 4)]) / np.sqrt(2)
    plus = np.array([1, 1]) / np.sqrt(2)
    mt = m2(density(t))
    mp = m2(density(plus))
    if abs(mt - np.log2(4 / 3)) > 1e-9 or abs(mp) > 1e-9:
        raise AssertionError("phase0 m2 engine failed the |T>/|+> self-test")


def print_source_and_predictions(plan: dict[int, int], seed: int) -> None:
    print("Track D Phase 4 -- SYK magic baseline")
    print("Primary sources verified/read: arXiv:2502.01582 and arXiv:2502.03093")
    print("Convention: N real Majoranas -> N/2 qubits, "
          "Var(J)=(q-1)!/N^(q-1), J=1")
    print(f"Disorder plan: {plan}; RNG seed={seed}")
    print("\nPRE-REGISTERED PREDICTIONS")
    print("  P1: mean M2(SYK4) > mean M2(SYK2), clearer at N=10,12.")
    print("  P2: DeltaAIC/string = AIC_Laplace - AIC_Gaussian is")
    print("      positive for SYK4 and negative for SYK2.")
    print("  P3: finite-size failures are reported explicitly.\n")


def summarize_by_n(n_majoranas: int, samples2: list[SampleResult],
                   samples4: list[SampleResult]) -> dict[str, float | bool]:
    m2_2, se_2 = mean_sem([s.m2 for s in samples2])
    m2_4, se_4 = mean_sem([s.m2 for s in samples4])
    gaps = [b.m2 - a.m2 for a, b in zip(samples2, samples4)]
    gap, gap_se = mean_sem(gaps)

    d2, d2_se = mean_sem([s.shape_delta_per_string for s in samples2])
    d4, d4_se = mean_sem([s.shape_delta_per_string for s in samples4])
    k2, k2_se = mean_sem([s.excess_kurtosis for s in samples2])
    k4, k4_se = mean_sem([s.excess_kurtosis for s in samples4])
    c2, _ = mean_sem([s.connected_count for s in samples2])
    c4, _ = mean_sem([s.connected_count for s in samples4])

    print(f"N={n_majoranas} Majoranas ({n_majoranas // 2} qubits), "
          f"samples={len(samples2)}")
    print(f"  M2: SYK2 {m2_2:.4f} +/- {se_2:.4f}; "
          f"SYK4 {m2_4:.4f} +/- {se_4:.4f}; "
          f"gap {gap:.4f} +/- {gap_se:.4f}")
    print(f"  shape DeltaAIC/string (>0 Gaussian, <0 Laplace): "
          f"SYK2 {d2:+.4f} +/- {d2_se:.4f}; "
          f"SYK4 {d4:+.4f} +/- {d4_se:.4f}")
    print(f"  excess kurtosis (Gaussian 0, Laplace 3): "
          f"SYK2 {k2:.2f} +/- {k2_se:.2f}; "
          f"SYK4 {k4:.2f} +/- {k4_se:.2f}")
    print(f"  connected nontrivial strings kept: "
          f"SYK2 mean {c2:.0f}; SYK4 mean {c4:.0f}\n")

    return {
        "gap_positive": gap > 0,
        "syk2_laplace": d2 < 0,
        "syk4_gaussian": d4 > 0,
        "gap": gap,
        "d2": d2,
        "d4": d4,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", default=None,
                        help="comma plan such as '8:40,10:24,12:12'")
    parser.add_argument("--seed", type=int, default=20260709)
    args = parser.parse_args()

    sample_plan = parse_sample_plan(args.samples)
    self_test_magic_engine()
    print_source_and_predictions(sample_plan, args.seed)

    rng = np.random.default_rng(args.seed)
    verdicts = {}
    for n_majoranas, n_samples in sorted(sample_plan.items()):
        gammas = jw_majoranas(n_majoranas)
        ops2 = syk_term_ops(gammas, q=2)
        ops4 = syk_term_ops(gammas, q=4)
        samples2: list[SampleResult] = []
        samples4: list[SampleResult] = []
        for _ in range(n_samples):
            samples2.append(one_sample(n_majoranas, 2, ops2, rng))
            samples4.append(one_sample(n_majoranas, 4, ops4, rng))
        verdicts[n_majoranas] = summarize_by_n(n_majoranas, samples2, samples4)

    print("PREDICTION CHECK")
    for n, v in verdicts.items():
        print(f"  N={n}: P1 gap positive={v['gap_positive']} "
              f"(gap={v['gap']:.4f}); P2 SYK2 Laplace={v['syk2_laplace']} "
              f"(Delta={v['d2']:+.4f}); P2 SYK4 Gaussian={v['syk4_gaussian']} "
              f"(Delta={v['d4']:+.4f})")

    robust_gap = all(verdicts[n]["gap_positive"] for n in verdicts if n >= 10)
    robust_shape = all(v["syk2_laplace"] and v["syk4_gaussian"]
                       for v in verdicts.values())
    print("\nVERDICT")
    if robust_gap and robust_shape:
        print("  Confirmed in this small-N Majorana baseline: SYK4 has larger")
        print("  disorder-averaged M2 than SYK2 at N>=10, while the spectrum")
        print("  shape cleanly separates chaotic/Gaussian from free/Laplace.")
    else:
        print("  Not fully confirmed. The failed finite-size checks above are")
        print("  part of the result and should be investigated before using")
        print("  Phase 4 as a strong scaling claim.")


if __name__ == "__main__":
    main()
