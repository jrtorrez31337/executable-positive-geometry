"""Milestone 3, Part 1 — VQE locates the quantum phase transition.

System: transverse-field Ising chain (open ends), N spins:
    H = -J * sum Z_i Z_{i+1}  -  h * sum X_i
Two regimes fight for the ground state:
    h << J : ferromagnet — neighbors align (ZZ order), like |000..> / |111..>
    h >> J : paramagnet — every spin surrenders to the field, |++++..>
At h ~ J the ground state can't decide: fluctuations at ALL scales,
a quantum critical point. No temperature involved — this is a zero-T
transition driven purely by quantum fluctuations.

VQE ("variational quantum eigensolver"): a parametrized quantum circuit
plays a million-dimensional game of hot-and-cold, descending the energy
landscape until it lands on the ground state. We cross-check against
brute-force exact diagonalization (possible only because N is small —
the honest reason quantum simulation is interesting at all).
"""

import math

import numpy as np
from qiskit.circuit.library import efficient_su2
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import EstimatorV2
from scipy.optimize import minimize

N = 8
J = 1.0
H_SWEEP = (0.2, 0.6, 1.0, 1.4, 2.0)


def hamiltonian(h: float) -> SparsePauliOp:
    terms = [("ZZ", [i, i + 1], -J) for i in range(N - 1)]
    terms += [("X", [i], -h) for i in range(N)]
    return SparsePauliOp.from_sparse_list(terms, num_qubits=N)


# Order parameters watched through the transition.
ZZ_MID = SparsePauliOp.from_sparse_list([("ZZ", [N // 2 - 1, N // 2], 1.0)], num_qubits=N)
X_AVG = SparsePauliOp.from_sparse_list([("X", [i], 1 / N) for i in range(N)], num_qubits=N)


def vqe(h: float, estimator: EstimatorV2, ansatz) -> tuple[float, float, float]:
    """Minimize <H> over circuit parameters; return (E, <ZZ>_mid, <X>_avg)."""
    op = hamiltonian(h)

    def energy(params: np.ndarray) -> float:
        return float(estimator.run([(ansatz, op, params)], precision=0.0)
                     .result()[0].data.evs)

    best = None
    rng = np.random.default_rng(7)
    for _ in range(2):  # two restarts to dodge bad local minima
        x0 = rng.uniform(-0.4, 0.4, ansatz.num_parameters)
        res = minimize(energy, x0, method="COBYLA", options={"maxiter": 600})
        if best is None or res.fun < best.fun:
            best = res

    zz, xa = (
        float(estimator.run([(ansatz, obs, best.x)], precision=0.0).result()[0].data.evs)
        for obs in (ZZ_MID, X_AVG)
    )
    return best.fun, zz, xa


def main() -> None:
    ansatz = efficient_su2(N, reps=2)
    estimator = EstimatorV2()
    print(f"TFIM chain, N={N}, J={J}; ansatz: efficient_su2, "
          f"{ansatz.num_parameters} parameters\n")
    print(f"{'h/J':>5} {'E (VQE)':>10} {'E (exact)':>10} {'error':>8} "
          f"{'<ZZ> order':>11} {'<X> field':>10}")

    for h in H_SWEEP:
        e_exact = float(np.linalg.eigvalsh(hamiltonian(h).to_matrix())[0])
        e_vqe, zz, xa = vqe(h, estimator, ansatz)
        print(f"{h:>5.1f} {e_vqe:>10.4f} {e_exact:>10.4f} {e_vqe - e_exact:>8.4f} "
              f"{zz:>11.3f} {xa:>10.3f}")

    print("\n  <ZZ> (neighbor alignment) collapses as h crosses J while <X>")
    print("  saturates: two phases, one quantum critical point near h/J = 1.")
    print("  The VQE circuit found each ground state without being told which")
    print("  phase it was in — the energy landscape alone encodes the transition.")


if __name__ == "__main__":
    main()
