"""Track D Phase 6 -- traversable-wormhole protocol exact simulation.

This is the codex-science half of the Phase 6 split.  It implements the
state-vector side of Byun, Kim and Lee, "Quantum simulation of
traversable-wormhole-inspired quantum teleportation in a chaotic binary sparse
SYK model" (arXiv:2604.10090).

PRIMARY SOURCE READ FIRST:
  - arXiv:2604.10090, especially Eqs. (1)-(5), Eq. (10), Eq. (11), and
    Supplemental Sec. S1.  The paper fixes N=8, q=4, beta=3 and |mu|=12.

PROTOCOL IMPLEMENTED:
  |in> = |Bell>_PQ x |TFD>_LR x |0>_T
  |out> = SWAP_RT U(t1) exp(i mu V) U(t0) SWAP_QL U(-t0) |in>,
  U(t) = exp[-i(H_L + H_R)t], V = H_int/(q N),
  H_int = i sum_j psi_L^j psi_R^j.

The one-sided Hamiltonian is imported from phase6_chaos_diagnostics when that
file is available:

    binary_sparse_syk_hamiltonian(N=8, q=4, K=10, rng)

That chaos-diagnostics half certifies whether the sparse model is in the
appropriate Bott-periodic RMT regime.  This module only tests the
information-transfer signal.

PRE-REGISTERED PREDICTIONS:
  P1: near the teleportation-time window at t0=1.8, the sign asymmetry
      Delta I_PT = I_PT(mu<0) - I_PT(mu>0) should be positive.
  P2: the signal is meaningful only for a Hamiltonian independently certified
      as chaotic by phase6_chaos_diagnostics.  The paper's N=8 circuit is the
      TW target, but N=8 gap-ratio statistics are too small-sector to certify
      chaos by themselves; use the N>=10/12 backing or an N=8 SFF refinement.
  P3: finite-size or random-instance failures are reported explicitly.

CONVENTION:
  Reuses Phase 4's Jordan-Wigner Majoranas with {gamma_i, gamma_j}=2 delta_ij.
  The paper's normalized psi_i satisfy psi_i = gamma_i / sqrt(2).  The Dirac
  injection/readout mode (psi_1 +/- i psi_2)/sqrt(2) is therefore the first
  qubit in the one-sided JW register, so the SWAP gates are implemented as
  ordinary qubit swaps against that first mode.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from dataclasses import dataclass
from itertools import combinations

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from phase4_syk_magic_baseline import (  # noqa: E402
    PAULI_1Q,
    jw_majoranas,
    kron_all,
    syk_term_ops,
)

try:  # noqa: SIM105 - the fallback keeps this half runnable before the peer push.
    from phase6_chaos_diagnostics import (  # type: ignore  # noqa: E402
        J_COUPLING,
        binary_sparse_syk_hamiltonian,
        parity_operator,
    )
except ImportError:  # pragma: no cover - exercised only before the peer file lands.
    J_COUPLING = np.sqrt(2.0)

    def parity_operator(n_qubits: int) -> np.ndarray:
        return kron_all([PAULI_1Q["Z"] for _ in range(n_qubits)])

    def binary_sparse_syk_hamiltonian(
        N: int,
        q: int,
        K: int,
        rng: np.random.Generator,
        term_ops: np.ndarray | None = None,
    ) -> np.ndarray:
        """Local compatibility fallback for the Phase 6 chaos-half API."""
        if term_ops is None:
            term_ops = syk_term_ops(jw_majoranas(N), q)
        n_terms = term_ops.shape[0]
        K = min(K, n_terms)
        keep = rng.choice(n_terms, size=K, replace=False)
        eta = rng.choice([-1.0, 1.0], size=K)
        coeff = eta * (J_COUPLING / np.sqrt(K))
        hamiltonian = np.tensordot(coeff, term_ops[keep], axes=(0, 0))
        return (hamiltonian + hamiltonian.conj().T) / 2


N_MAJORANAS = 8
Q_LOCALITY = 4
DEFAULT_K = 10
DEFAULT_BETA = 3.0
DEFAULT_T0 = 1.8
DEFAULT_MU = 12.0
DEFAULT_T1_GRID = tuple(0.5 * k for k in range(1, 13))


@dataclass(frozen=True)
class ProtocolPoint:
    t1: float
    i_negative: float
    i_positive: float

    @property
    def delta(self) -> float:
        return self.i_negative - self.i_positive


@dataclass(frozen=True)
class ProtocolSummary:
    points: tuple[ProtocolPoint, ...]
    peak_t1: float
    peak_delta: float
    peak_i_negative: float
    peak_i_positive: float


@dataclass(frozen=True)
class HermitianEvolution:
    vals: np.ndarray
    vecs: np.ndarray

    def unitary(self, time: float, sign: int = -1) -> np.ndarray:
        phases = np.exp(sign * 1j * self.vals * time)
        return (self.vecs * phases) @ self.vecs.conj().T


@dataclass
class ProtocolEngine:
    initial: np.ndarray
    h_evolution: HermitianEvolution
    u_backward_t0: np.ndarray
    u_forward_t0: np.ndarray
    kick_negative: np.ndarray
    kick_positive: np.ndarray

    def evolve(self, t1: float, negative_mu: bool) -> np.ndarray:
        state = np.array(self.initial, copy=True)
        state = apply_two_sided_time(state, self.u_backward_t0)
        state = swap_message_into_left(state)
        state = apply_two_sided_time(state, self.u_forward_t0)
        state = apply_lr_matrix(state, self.kick_negative if negative_mu else self.kick_positive)
        state = apply_two_sided_time(state, self.h_evolution.unitary(t1, sign=-1))
        state = swap_right_into_target(state)
        return state / np.linalg.norm(state)


def hermitianize(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2


def evolution_from_hermitian(matrix: np.ndarray) -> HermitianEvolution:
    vals, vecs = np.linalg.eigh(hermitianize(matrix))
    return HermitianEvolution(vals=vals.real, vecs=vecs)


def unitary_from_hermitian(hamiltonian: np.ndarray, time: float) -> np.ndarray:
    return evolution_from_hermitian(hamiltonian).unitary(time, sign=-1)


def kick_from_generator(generator: np.ndarray, mu: float) -> np.ndarray:
    return evolution_from_hermitian(generator).unitary(mu, sign=+1)


def tfd_state(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    vals, vecs = np.linalg.eigh(hermitianize(hamiltonian))
    shifted = vals.real - float(vals[0].real)
    weights = np.exp(-0.5 * beta * shifted)
    weights /= np.linalg.norm(weights)
    state = np.einsum("in,jn,n->ij", vecs, vecs, weights, optimize=True)
    state = state.reshape(-1)
    return state / np.linalg.norm(state)


def selected_paper_hamiltonian(term_ops: np.ndarray) -> np.ndarray:
    """Byun-Kim-Lee Eq. (11) support/sign pattern in the Phase 6 convention."""
    signs_and_terms = (
        (-1.0, (1, 2, 4, 7)),
        (+1.0, (1, 2, 6, 8)),
        (-1.0, (1, 3, 4, 5)),
        (+1.0, (1, 3, 7, 8)),
        (-1.0, (1, 4, 5, 6)),
        (+1.0, (1, 5, 6, 7)),
        (-1.0, (2, 3, 4, 8)),
        (+1.0, (2, 3, 5, 7)),
        (-1.0, (2, 4, 6, 7)),
        (+1.0, (3, 5, 6, 8)),
    )
    combo_to_index = {
        combo: i for i, combo in enumerate(combinations(range(N_MAJORANAS), Q_LOCALITY))
    }
    coeffs = np.zeros(term_ops.shape[0], dtype=float)
    coupling = J_COUPLING / np.sqrt(DEFAULT_K)  # sqrt(2)/sqrt(10) = 1/sqrt(5)
    for sign, one_based in signs_and_terms:
        combo = tuple(i - 1 for i in one_based)
        coeffs[combo_to_index[combo]] = sign * coupling
    hamiltonian = np.tensordot(coeffs, term_ops, axes=(0, 0))
    return hermitianize(hamiltonian)


def build_one_sided_hamiltonian(
    instance: str,
    rng: np.random.Generator,
    term_ops: np.ndarray,
    k_terms: int,
) -> tuple[np.ndarray, str]:
    if instance == "paper":
        return selected_paper_hamiltonian(term_ops), "paper Eq. (11) selected K=10 instance"
    if instance == "random":
        hamiltonian = binary_sparse_syk_hamiltonian(
            N_MAJORANAS, Q_LOCALITY, k_terms, rng, term_ops
        )
        return hamiltonian, f"binary sparse random K={k_terms} instance"
    raise ValueError(f"unknown instance: {instance}")


def interaction_generator(gammas: list[np.ndarray], q: int, n_majoranas: int) -> np.ndarray:
    """Return V = H_int/(qN) using a fermionic tensor-product convention.

    Left Majoranas are represented as gamma_j x parity_R and right Majoranas as
    I_L x gamma_j, so left/right Majoranas anticommute.  With psi=gamma/sqrt(2),
    H_int = i/2 sum_j gamma_j x parity_R gamma_j.
    """
    dim = gammas[0].shape[0]
    parity = parity_operator(n_majoranas // 2)
    h_int = np.zeros((dim * dim, dim * dim), dtype=complex)
    for gamma in gammas:
        h_int += 0.5j * np.kron(gamma, parity @ gamma)
    h_int = hermitianize(h_int)
    return h_int / (q * n_majoranas)


def initial_state(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    bell_pq = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    tfd_lr = tfd_state(hamiltonian, beta)
    zero_t = np.array([1, 0], dtype=complex)
    state = np.kron(np.kron(bell_pq, tfd_lr), zero_t)
    state = state.reshape(2, 2, 16, 16, 2)
    return state / np.linalg.norm(state)


def apply_to_axis(state: np.ndarray, matrix: np.ndarray, axis: int) -> np.ndarray:
    moved = np.moveaxis(state, axis, 0)
    flat = moved.reshape(matrix.shape[1], -1)
    updated = (matrix @ flat).reshape(moved.shape)
    return np.moveaxis(updated, 0, axis)


def apply_lr_matrix(state: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    moved = np.moveaxis(state, (2, 3), (0, 1))
    flat = moved.reshape(matrix.shape[1], -1)
    updated = (matrix @ flat).reshape(moved.shape)
    return np.moveaxis(updated, (0, 1), (2, 3))


def apply_two_sided_time(state: np.ndarray, u_side: np.ndarray) -> np.ndarray:
    state = apply_to_axis(state, u_side, axis=2)
    state = apply_to_axis(state, u_side, axis=3)
    return state


def swap_qubit_axes(state: np.ndarray, axis_a: int, axis_b: int) -> np.ndarray:
    qubit_shape = (2, 2) + (2,) * 4 + (2,) * 4 + (2,)
    expanded = state.reshape(qubit_shape)
    expanded = np.swapaxes(expanded, axis_a, axis_b)
    return expanded.reshape(2, 2, 16, 16, 2)


def swap_message_into_left(state: np.ndarray) -> np.ndarray:
    # Expanded axes: P, Q, L0, L1, L2, L3, R0, R1, R2, R3, T.
    return swap_qubit_axes(state, axis_a=1, axis_b=2)


def swap_right_into_target(state: np.ndarray) -> np.ndarray:
    # The first right Dirac mode is R0.
    return swap_qubit_axes(state, axis_a=6, axis_b=10)


def rho_pt_from_state(state: np.ndarray) -> np.ndarray:
    grouped = state.transpose(0, 4, 1, 2, 3).reshape(4, -1)
    rho = grouped @ grouped.conj().T
    return hermitianize(rho) / np.trace(rho).real


def entropy_base2(rho: np.ndarray) -> float:
    vals = np.linalg.eigvalsh(hermitianize(rho)).real
    vals = np.clip(vals, 0.0, None)
    vals = vals[vals > 1e-14]
    return float(-np.sum(vals * np.log2(vals)))


def partial_trace_one_qubit(rho_2q: np.ndarray, keep: int) -> np.ndarray:
    tensor = rho_2q.reshape(2, 2, 2, 2)
    if keep == 0:
        return np.trace(tensor, axis1=1, axis2=3)
    if keep == 1:
        return np.trace(tensor, axis1=0, axis2=2)
    raise ValueError("keep must be 0 or 1")


def mutual_information_pt(state: np.ndarray) -> float:
    rho_pt = rho_pt_from_state(state)
    rho_p = partial_trace_one_qubit(rho_pt, keep=0)
    rho_t = partial_trace_one_qubit(rho_pt, keep=1)
    return entropy_base2(rho_p) + entropy_base2(rho_t) - entropy_base2(rho_pt)


def evolve_protocol(
    hamiltonian: np.ndarray,
    v_generator: np.ndarray,
    beta: float,
    t0: float,
    t1: float,
    mu: float,
) -> np.ndarray:
    state = initial_state(hamiltonian, beta)
    state = apply_two_sided_time(state, unitary_from_hermitian(hamiltonian, -t0))
    state = swap_message_into_left(state)
    state = apply_two_sided_time(state, unitary_from_hermitian(hamiltonian, t0))
    state = apply_lr_matrix(state, kick_from_generator(v_generator, mu))
    state = apply_two_sided_time(state, unitary_from_hermitian(hamiltonian, t1))
    state = swap_right_into_target(state)
    return state / np.linalg.norm(state)


def make_protocol_engine(
    hamiltonian: np.ndarray,
    v_generator: np.ndarray,
    beta: float,
    t0: float,
    mu_abs: float,
) -> ProtocolEngine:
    h_evolution = evolution_from_hermitian(hamiltonian)
    v_evolution = evolution_from_hermitian(v_generator)
    return ProtocolEngine(
        initial=initial_state(hamiltonian, beta),
        h_evolution=h_evolution,
        u_backward_t0=h_evolution.unitary(-t0, sign=-1),
        u_forward_t0=h_evolution.unitary(t0, sign=-1),
        kick_negative=v_evolution.unitary(-abs(mu_abs), sign=+1),
        kick_positive=v_evolution.unitary(+abs(mu_abs), sign=+1),
    )


def scan_fixed_injection(
    hamiltonian: np.ndarray,
    v_generator: np.ndarray,
    beta: float,
    t0: float,
    t1_values: tuple[float, ...],
    mu_abs: float,
) -> ProtocolSummary:
    engine = make_protocol_engine(hamiltonian, v_generator, beta, t0, mu_abs)
    points: list[ProtocolPoint] = []
    for t1 in t1_values:
        state_negative = engine.evolve(t1, negative_mu=True)
        state_positive = engine.evolve(t1, negative_mu=False)
        points.append(
            ProtocolPoint(
                t1=t1,
                i_negative=mutual_information_pt(state_negative),
                i_positive=mutual_information_pt(state_positive),
            )
        )
    peak = max(points, key=lambda point: point.delta)
    return ProtocolSummary(
        points=tuple(points),
        peak_t1=peak.t1,
        peak_delta=peak.delta,
        peak_i_negative=peak.i_negative,
        peak_i_positive=peak.i_positive,
    )


def run_self_tests() -> None:
    product = np.zeros((2, 2, 16, 16, 2), dtype=complex)
    product[0, 0, 0, 0, 0] = 1.0
    if abs(mutual_information_pt(product)) > 1e-12:
        raise AssertionError("product PT mutual information should vanish")

    bell_pt = np.zeros((2, 2, 16, 16, 2), dtype=complex)
    bell_pt[0, 0, 0, 0, 0] = 1 / np.sqrt(2)
    bell_pt[1, 0, 0, 0, 1] = 1 / np.sqrt(2)
    if abs(mutual_information_pt(bell_pt) - 2.0) > 1e-12:
        raise AssertionError("Bell PT mutual information should be 2 bits")

    marker = np.zeros((2, 2, 16, 16, 2), dtype=complex)
    marker[0, 1, 0, 0, 0] = 1.0
    swapped = swap_message_into_left(marker)
    if abs(swapped[0, 0, 8, 0, 0] - 1.0) > 1e-12:
        raise AssertionError("Q/L0 swap failed")


def parse_t1_grid(text: str | None) -> tuple[float, ...]:
    if text is None:
        return DEFAULT_T1_GRID
    return tuple(float(item) for item in text.split(",") if item.strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", choices=("paper", "random"), default="paper")
    parser.add_argument("--seed", type=int, default=20260709)
    parser.add_argument("--k", type=int, default=DEFAULT_K)
    parser.add_argument("--beta", type=float, default=DEFAULT_BETA)
    parser.add_argument("--t0", type=float, default=DEFAULT_T0)
    parser.add_argument("--mu", type=float, default=DEFAULT_MU)
    parser.add_argument(
        "--t1-grid",
        default=None,
        help="comma-separated readout times; default is 0.5,1.0,...,6.0",
    )
    args = parser.parse_args()

    run_self_tests()
    rng = np.random.default_rng(args.seed)
    gammas = jw_majoranas(N_MAJORANAS)
    term_ops = syk_term_ops(gammas, Q_LOCALITY)
    hamiltonian, source = build_one_sided_hamiltonian(args.instance, rng, term_ops, args.k)
    v_generator = interaction_generator(gammas, Q_LOCALITY, N_MAJORANAS)
    if np.linalg.norm(v_generator - v_generator.conj().T) > 1e-10:
        raise AssertionError("interaction generator is not Hermitian")
    t1_values = parse_t1_grid(args.t1_grid)

    print("Track D Phase 6 -- TW protocol exact simulation")
    print("Primary source: arXiv:2604.10090; exact state-vector protocol")
    print(f"Model: {source}")
    print(
        f"Parameters: N={N_MAJORANAS}, q={Q_LOCALITY}, beta={args.beta}, "
        f"t0={args.t0}, |mu|={args.mu}, seed={args.seed}"
    )
    print("\nPRE-REGISTERED PREDICTIONS")
    print("  P1: Delta I_PT = I_PT(mu<0) - I_PT(mu>0) > 0 near teleportation time.")
    print("  P2: interpret P1 only with independent chaos backing; N=8 gap ratio")
    print("      alone is inconclusive, so use N>=10/12 diagnostics or N=8 SFF.")
    print("  P3: finite-size/random-instance failures are reported explicitly.\n")

    summary = scan_fixed_injection(
        hamiltonian,
        v_generator,
        beta=args.beta,
        t0=args.t0,
        t1_values=t1_values,
        mu_abs=abs(args.mu),
    )

    print("Fixed-injection scan")
    print("  t1      I_PT(mu=-|mu|)   I_PT(mu=+|mu|)   Delta I_PT")
    for point in summary.points:
        print(
            f"  {point.t1:>4.1f}    {point.i_negative:>12.6f}    "
            f"{point.i_positive:>12.6f}    {point.delta:>+12.6f}"
        )

    print("\nPREDICTION CHECK")
    print(
        f"  peak Delta I_PT = {summary.peak_delta:+.6f} bits at t1={summary.peak_t1:.1f} "
        f"(I-={summary.peak_i_negative:.6f}, I+={summary.peak_i_positive:.6f})"
    )
    if summary.peak_delta > 0:
        print("  P1 satisfied for this exact finite-size run.")
    else:
        print("  P1 NOT satisfied for this exact finite-size run; do not claim a TW signal.")
    print("  P2 delegated to phase6_chaos_diagnostics.py: N=8 is the TW circuit")
    print("  target, while the robust gap-ratio chaos backing is N>=10/12 unless")
    print("  an ensemble-averaged N=8 SFF refinement is added.")


if __name__ == "__main__":
    main()
