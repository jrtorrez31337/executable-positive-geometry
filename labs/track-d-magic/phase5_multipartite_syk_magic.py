"""Track D Phase 5 -- multipartite SYK magic.

ASSIGNMENT: implement the multipartite non-local magic diagnostic of
Malvimat, Sarkis, Suk and Yoon, "Multipartite Non-local Magic and SYK Model"
(arXiv:2601.03076), and test the paper's finite-temperature distinction
between SYK4 thermal pure quantum (TPQ) microstates and the thermal density
matrix.

PRIMARY SOURCE READ FIRST:
  - arXiv:2601.03076, verified against the arXiv API and filed in
    corpus/7-magic before this lab was written.

PAPER FUNCTIONAL IMPLEMENTED:
  For n parties, Eq. (2.14) defines

      M_nl^(n)(rho_[n]) = sum_{empty != S subset [n]} (-1)^(n-|S|) M(rho_S),

  where M is the mixed-state proxy M2 = SRE2 - S2. In this repository that is
  exactly phase0_wedge_magic.m2(rho) = -log2(sum_P c_P^4 / sum_P c_P^2).
  The sign is meaningful: positive/zero/negative indicate synergistic,
  factorized, or redundant connected magic. It is not a positive monotone.

MIXED-STATE DISCIPLINE:
  Phase 1 showed that M2 can false-positive on purely classical stabilizer
  mixtures. The paper uses M2 = SRE2 - S2 directly for mixed states. Here we
  report both:

    raw        -- the paper's direct M2 inclusion-exclusion value;
    controlled -- raw M2 minus a same-spectrum computational-basis stabilizer
                  twin for every reduced density matrix before inclusion-
                  exclusion. This preserves each reduced state's eigenvalues
                  and removes the "magic" assigned to diagonal mixedness.

  The controlled value is the safer comparison for thermal rho.

PRE-REGISTERED PREDICTIONS:
  P1: At beta=0, the thermal state is maximally mixed and has zero raw and
      controlled multipartite magic, while a TPQ state is a random pure state
      with nonzero multipartite connected magic.
  P2: TPQ and thermal diagnostics approach each other as beta increases and
      both are projected toward the same low-energy sector; small-N
      nonmonotonicity is possible and must be reported.
  P3: The controlled thermal signal is the one to trust for mixed-state
      comparisons. Any raw-vs-controlled discrepancy is a warning, not a
      nuisance.
  P4: Compared with Phase 2, the same inclusion-exclusion grammar detects a
      different physical carrier: SYK microstate connected magic rather than
      tripartite magic in an encoding Choi state.

CONVENTION:
  Reuses Phase 4's real-Majorana SYK convention and machinery:

      H_q = i^(q/2) sum J_{i1...iq} chi_i1 ... chi_iq,
      Var(J) = (q-1)! / N^(q-1), J=1,
      N Majoranas -> N/2 qubits by Jordan-Wigner.
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
from phase0_wedge_magic import m2, reduce_state  # noqa: E402
from phase4_syk_magic_baseline import (  # noqa: E402
    density,
    jw_majoranas,
    mean_sem,
    self_test_magic_engine,
    syk_hamiltonian,
    syk_term_ops,
)

DEFAULT_SAMPLE_PLAN = {8: 40, 10: 24, 12: 12}
DEFAULT_BETAS = (0.0, 0.5, 1.0, 2.0, 4.0)
ZERO_TOL = 1e-12


@dataclass
class ThermalMagicSample:
    raw_tpq: float
    raw_thermal: float
    controlled_tpq: float
    controlled_thermal: float
    full_raw_tpq: float
    full_raw_thermal: float
    full_controlled_tpq: float
    full_controlled_thermal: float


def reduce_density(rho: np.ndarray, keep: tuple[int, ...], n_qubits: int) -> np.ndarray:
    """Partial trace of an n-qubit density matrix, preserving keep order."""
    keep = tuple(keep)
    traced = tuple(q for q in range(n_qubits) if q not in keep)
    perm = list(keep) + list(traced) + [q + n_qubits for q in keep] + [
        q + n_qubits for q in traced
    ]
    reshaped = rho.reshape([2] * (2 * n_qubits)).transpose(perm)
    dim_keep = 2 ** len(keep)
    dim_trace = 2 ** len(traced)
    return np.trace(
        reshaped.reshape(dim_keep, dim_trace, dim_keep, dim_trace),
        axis1=1,
        axis2=3,
    )


def subsystem_density(
    state_or_rho: np.ndarray, keep: tuple[int, ...], n_qubits: int
) -> np.ndarray:
    if state_or_rho.ndim == 1:
        return reduce_state(state_or_rho, keep, n_qubits)
    return reduce_density(state_or_rho, keep, n_qubits)


def same_spectrum_stabilizer_twin(rho: np.ndarray) -> np.ndarray:
    """Diagonal stabilizer-basis mixture with the same eigenvalues as rho."""
    vals = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    vals = np.clip(vals.real, 0.0, None)
    total = float(np.sum(vals))
    if total <= ZERO_TOL:
        raise ValueError("density matrix eigenvalues sum to zero")
    vals = np.sort(vals / total)[::-1]
    return np.diag(vals).astype(complex)


def magic_value(rho: np.ndarray, controlled: bool) -> float:
    raw = m2(rho)
    if not controlled:
        return raw
    return raw - m2(same_spectrum_stabilizer_twin(rho))


def union_qubits(parties: tuple[tuple[int, ...], ...], subset: tuple[int, ...]) -> tuple[int, ...]:
    out: list[int] = []
    for party_index in subset:
        out.extend(parties[party_index])
    return tuple(out)


def multipartite_nonlocal_magic(
    state_or_rho: np.ndarray,
    parties: tuple[tuple[int, ...], ...],
    n_qubits: int,
    controlled: bool = False,
) -> float:
    """Eq. (2.14) from arXiv:2601.03076 for arbitrary party blocks."""
    n_parties = len(parties)
    total = 0.0
    for size in range(1, n_parties + 1):
        coeff = (-1) ** (n_parties - size)
        for subset in combinations(range(n_parties), size):
            keep = union_qubits(parties, subset)
            rho_sub = subsystem_density(state_or_rho, keep, n_qubits)
            total += coeff * magic_value(rho_sub, controlled=controlled)
    return float(total)


def partition_qubits(n_qubits: int) -> tuple[tuple[int, ...], ...]:
    """Three contiguous parties, balanced as evenly as possible."""
    if n_qubits < 3:
        raise ValueError("Phase 5 needs at least three qubits")
    base, extra = divmod(n_qubits, 3)
    parties = []
    cursor = 0
    for i in range(3):
        width = base + (1 if i < extra else 0)
        parties.append(tuple(range(cursor, cursor + width)))
        cursor += width
    return tuple(parties)


def diagonalize_syk4(
    n_majoranas: int, term_ops: np.ndarray, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    hamiltonian = syk_hamiltonian(term_ops, n_majoranas, 4, rng)
    vals, vecs = np.linalg.eigh(hamiltonian)
    return vals.real, vecs


def thermal_density(vals: np.ndarray, vecs: np.ndarray, beta: float) -> np.ndarray:
    shifted = vals - float(vals[0])
    weights = np.exp(-beta * shifted)
    weights = weights / float(np.sum(weights))
    rho = (vecs * weights) @ vecs.conj().T
    return (rho + rho.conj().T) / 2


def tpq_state(
    vals: np.ndarray, vecs: np.ndarray, beta: float, rng: np.random.Generator
) -> np.ndarray:
    dim = vecs.shape[0]
    ref = rng.normal(size=dim) + 1j * rng.normal(size=dim)
    ref = ref / np.linalg.norm(ref)
    coeffs = vecs.conj().T @ ref
    shifted = vals - float(vals[0])
    filtered = np.exp(-0.5 * beta * shifted) * coeffs
    psi = vecs @ filtered
    return psi / np.linalg.norm(psi)


def one_thermal_magic_sample(
    vals: np.ndarray,
    vecs: np.ndarray,
    beta: float,
    parties: tuple[tuple[int, ...], ...],
    n_qubits: int,
    rng: np.random.Generator,
) -> ThermalMagicSample:
    psi_tpq = tpq_state(vals, vecs, beta, rng)
    rho_tpq = density(psi_tpq)
    rho_thermal = thermal_density(vals, vecs, beta)

    raw_tpq = multipartite_nonlocal_magic(psi_tpq, parties, n_qubits, controlled=False)
    raw_thermal = multipartite_nonlocal_magic(
        rho_thermal, parties, n_qubits, controlled=False
    )
    controlled_tpq = multipartite_nonlocal_magic(
        psi_tpq, parties, n_qubits, controlled=True
    )
    controlled_thermal = multipartite_nonlocal_magic(
        rho_thermal, parties, n_qubits, controlled=True
    )

    full_raw_tpq = magic_value(rho_tpq, controlled=False)
    full_raw_thermal = magic_value(rho_thermal, controlled=False)
    full_controlled_tpq = magic_value(rho_tpq, controlled=True)
    full_controlled_thermal = magic_value(rho_thermal, controlled=True)

    return ThermalMagicSample(
        raw_tpq=raw_tpq,
        raw_thermal=raw_thermal,
        controlled_tpq=controlled_tpq,
        controlled_thermal=controlled_thermal,
        full_raw_tpq=full_raw_tpq,
        full_raw_thermal=full_raw_thermal,
        full_controlled_tpq=full_controlled_tpq,
        full_controlled_thermal=full_controlled_thermal,
    )


def parse_sample_plan(text: str | None) -> dict[int, int]:
    if text is None:
        return dict(DEFAULT_SAMPLE_PLAN)
    plan: dict[int, int] = {}
    for item in text.split(","):
        n_txt, s_txt = item.split(":")
        plan[int(n_txt)] = int(s_txt)
    return plan


def parse_betas(text: str | None) -> tuple[float, ...]:
    if text is None:
        return DEFAULT_BETAS
    return tuple(float(item) for item in text.split(","))


def format_parties(parties: tuple[tuple[int, ...], ...]) -> str:
    return " | ".join("{" + ",".join(str(q) for q in party) + "}" for party in parties)


def run_self_tests() -> None:
    self_test_magic_engine()

    bell = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    rho_bell_a = reduce_state(bell, (0,), 2)
    rho_bell_a_mixed = reduce_density(density(bell), (0,), 2)
    if np.linalg.norm(rho_bell_a - rho_bell_a_mixed) > 1e-10:
        raise AssertionError("reduce_density disagrees with reduce_state")

    ghz = np.zeros(8, dtype=complex)
    ghz[0] = ghz[-1] = 1 / np.sqrt(2)
    ghz_mnl = multipartite_nonlocal_magic(
        ghz, ((0,), (1,), (2,)), 3, controlled=False
    )
    if abs(ghz_mnl) > 1e-9:
        raise AssertionError(f"GHZ stabilizer should have zero Mnl, got {ghz_mnl}")

    t = np.array([1, np.exp(1j * np.pi / 4)], dtype=complex) / np.sqrt(2)
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    zero = np.array([1, 0], dtype=complex)
    product = np.kron(np.kron(t, plus), zero)
    product_mnl = multipartite_nonlocal_magic(
        product, ((0,), (1,), (2,)), 3, controlled=False
    )
    if abs(product_mnl) > 1e-9:
        raise AssertionError(f"product state should have zero Mnl, got {product_mnl}")

    classical_mix = np.diag([0.85, 0.15]).astype(complex)
    if abs(magic_value(classical_mix, controlled=True)) > 1e-9:
        raise AssertionError("same-spectrum twin control failed on diagonal mixture")


def print_source_and_predictions(
    plan: dict[int, int], betas: tuple[float, ...], seed: int
) -> None:
    print("Track D Phase 5 -- multipartite SYK magic")
    print("Primary source verified/read/filed: arXiv:2601.03076")
    print("Functional: Eq. (2.14), inclusion-exclusion over party blocks")
    print("SYK convention: Phase 4 real Majorana SYK4, N Majoranas -> N/2 qubits")
    print(f"Disorder/TPQ plan: {plan}; betas={betas}; RNG seed={seed}")
    print("Mixed-state handling: report paper-raw M2 and same-spectrum")
    print("stabilizer-twin-controlled M2 for every reduced density matrix.\n")
    print("PRE-REGISTERED PREDICTIONS")
    print("  P1: beta=0 thermal Mnl=0, TPQ has nonzero connected magic.")
    print("  P2: TPQ-vs-thermal distinction should generally shrink as beta grows,")
    print("      with small-N nonmonotonicity reported if present.")
    print("  P3: controlled thermal values are the safer mixed-state diagnostic.")
    print("  P4: Phase-2 Choi tripartite magic and SYK Mnl use the same connected")
    print("      inclusion-exclusion grammar but probe different physical carriers.\n")


def summarize_beta(
    n_majoranas: int,
    beta: float,
    samples: list[ThermalMagicSample],
) -> dict[str, float]:
    raw_tpq, raw_tpq_se = mean_sem([s.raw_tpq for s in samples])
    raw_th, raw_th_se = mean_sem([s.raw_thermal for s in samples])
    ctl_tpq, ctl_tpq_se = mean_sem([s.controlled_tpq for s in samples])
    ctl_th, ctl_th_se = mean_sem([s.controlled_thermal for s in samples])
    ctl_gap, ctl_gap_se = mean_sem(
        [s.controlled_tpq - s.controlled_thermal for s in samples]
    )
    ctl_strength_gap, ctl_strength_gap_se = mean_sem(
        [abs(s.controlled_tpq) - abs(s.controlled_thermal) for s in samples]
    )
    full_tpq, full_tpq_se = mean_sem([s.full_controlled_tpq for s in samples])
    full_th, full_th_se = mean_sem([s.full_controlled_thermal for s in samples])

    print(
        f"  beta={beta:>4.1f} raw Mnl: TPQ {raw_tpq:+.4f} +/- {raw_tpq_se:.4f}; "
        f"thermal {raw_th:+.4f} +/- {raw_th_se:.4f}"
    )
    print(
        f"           ctl Mnl: TPQ {ctl_tpq:+.4f} +/- {ctl_tpq_se:.4f}; "
        f"thermal {ctl_th:+.4f} +/- {ctl_th_se:.4f}; "
        f"gap {ctl_gap:+.4f} +/- {ctl_gap_se:.4f}"
    )
    print(
        f"           |ctl| gap {ctl_strength_gap:+.4f} +/- "
        f"{ctl_strength_gap_se:.4f}; full ctl M2 TPQ {full_tpq:.4f} +/- "
        f"{full_tpq_se:.4f}, thermal {full_th:.4f} +/- {full_th_se:.4f}"
    )

    return {
        "raw_tpq": raw_tpq,
        "raw_thermal": raw_th,
        "ctl_tpq": ctl_tpq,
        "ctl_thermal": ctl_th,
        "ctl_gap": ctl_gap,
        "ctl_strength_gap": ctl_strength_gap,
        "full_ctl_tpq": full_tpq,
        "full_ctl_thermal": full_th,
    }


def phase2_choi_comparison() -> tuple[float, float, float]:
    from happy_tile import build_codewords  # noqa: E402
    from phase2_backreaction import skew_unitary  # noqa: E402

    v0, v1 = build_codewords()
    e0, e1 = np.eye(2, dtype=complex)
    choi = (np.kron(e0, v0) + np.kron(e1, v1)) / np.sqrt(2)
    skewed = np.kron(np.eye(2), skew_unitary(np.pi * 0.15)) @ choi
    parties = ((0,), (1, 2), (3, 4, 5))
    raw = multipartite_nonlocal_magic(skewed, parties, 6, controlled=False)
    controlled = multipartite_nonlocal_magic(skewed, parties, 6, controlled=True)
    return m2(density(skewed)), raw, controlled


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", default=None, help="plan like '8:12,10:8,12:4'")
    parser.add_argument("--betas", default=None, help="comma list like '0,0.5,1,2,4'")
    parser.add_argument("--seed", type=int, default=20260709)
    parser.add_argument("--skip-choi", action="store_true")
    args = parser.parse_args()

    sample_plan = parse_sample_plan(args.samples)
    betas = parse_betas(args.betas)

    run_self_tests()
    print_source_and_predictions(sample_plan, betas, args.seed)

    rng = np.random.default_rng(args.seed)
    verdicts: dict[int, dict[float, dict[str, float]]] = {}
    for n_majoranas, n_samples in sorted(sample_plan.items()):
        n_qubits = n_majoranas // 2
        parties = partition_qubits(n_qubits)
        print(
            f"N={n_majoranas} Majoranas ({n_qubits} qubits), samples={n_samples}, "
            f"parties={format_parties(parties)}"
        )
        gammas = jw_majoranas(n_majoranas)
        term_ops = syk_term_ops(gammas, q=4)
        by_beta: dict[float, list[ThermalMagicSample]] = {beta: [] for beta in betas}
        for _ in range(n_samples):
            vals, vecs = diagonalize_syk4(n_majoranas, term_ops, rng)
            for beta in betas:
                by_beta[beta].append(
                    one_thermal_magic_sample(vals, vecs, beta, parties, n_qubits, rng)
                )
        verdicts[n_majoranas] = {}
        for beta in betas:
            verdicts[n_majoranas][beta] = summarize_beta(
                n_majoranas, beta, by_beta[beta]
            )
        print()

    print("PREDICTION CHECK")
    beta0 = min(betas, key=abs)
    beta_hi = max(betas)
    for n_majoranas in sorted(verdicts):
        v0 = verdicts[n_majoranas][beta0]
        vhi = verdicts[n_majoranas][beta_hi]
        p1 = abs(v0["ctl_tpq"]) > abs(v0["ctl_thermal"]) + 1e-9
        shrink = abs(vhi["ctl_strength_gap"]) < abs(v0["ctl_strength_gap"])
        print(
            f"  N={n_majoranas}: P1 beta=0 TPQ distinction={p1} "
            f"(|ctl| gap={v0['ctl_strength_gap']:+.4f}); "
            f"P2 shrink by beta={beta_hi:g}={shrink} "
            f"({v0['ctl_strength_gap']:+.4f}->{vhi['ctl_strength_gap']:+.4f})"
        )

    if not args.skip_choi:
        global_m2, raw_choi, controlled_choi = phase2_choi_comparison()
        print("\nPHASE-2 CHOI COMPARISON")
        print(
            f"  theta=0.15pi skewed Choi global M2={global_m2:.4f}; "
            f"tripartite raw Mnl={raw_choi:+.4f}; "
            f"controlled Mnl={controlled_choi:+.4f}"
        )
        print("  Same inclusion-exclusion grammar; different carrier: encoding-map")
        print("  tripartite resource in Phase 2 vs SYK microstate/ensemble structure here.")

    print("\nVERDICT")
    print("  Phase 5 reproduces the paper's qualitative TPQ-vs-thermal split at")
    print("  beta=0 by construction and quantifies how it survives in small-N SYK4.")
    print("  The controlled columns are the mixed-state-safe values to compare.")


if __name__ == "__main__":
    main()
