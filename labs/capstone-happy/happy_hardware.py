"""CAPSTONE III — the HaPPY tile on real quantum hardware.

We prepare the perfect-tensor state |Psi> = (|0>_R |0_L> + |1>_R |1_L>)/sqrt(2)
— reference qubit R maximally entangled with the BULK qubit of one holographic
tile — on a physical superconducting processor, and measure Pauli witnesses:

  encoding checks : the four [[5,1,3]] stabilizers            (ideal +1)
  bulk-boundary   : X_R X_L and Z_R Z_L (weight-6 logicals)   (ideal +1)
  WEDGE tests     : the same bulk-X pushed onto two DIFFERENT
                    3-qubit boundary regions, -(IYYIX) on {2,3,5}
                    and -(XIYYI) on {1,3,4}; and bulk-Z pushed
                    to -(YIIYZ) on {1,4,5}                     (ideal +1)
  NULL tests      : correlators between R and 2-qubit regions  (ideal  0)

If holography-as-error-correction survives contact with hardware noise, the
wedge correlators stay far above the null tests: majority regions carry the
bulk qubit, minority regions measure pure noise.

|Psi> is a stabilizer state: it is the unique +1 eigenstate of
  S1..S4 (code stabilizers on qubits 1-5),  X_R X_L,  Z_R Z_L
so a Clifford preparation circuit can be synthesized directly.
"""

import numpy as np
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.synthesis import synth_circuit_from_stabilizers
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2, QiskitRuntimeService

CODE_STABS = ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"]   # char k -> code qubit k+1


def label(mapping: dict[int, str]) -> str:
    """Qiskit Pauli label for 6 qubits (qubit 0 = R; leftmost char = qubit 5)."""
    return "".join(mapping.get(q, "I") for q in reversed(range(6)))


def code_qubit_map(s: str) -> dict[int, str]:
    return {k + 1: c for k, c in enumerate(s) if c != "I"}


def build_prep_circuit():
    gens = [label(code_qubit_map(s)) for s in CODE_STABS]
    gens.append("X" * 6)   # X_R X_L
    gens.append("Z" * 6)   # Z_R Z_L
    return synth_circuit_from_stabilizers(gens)


def observables() -> list[tuple[str, SparsePauliOp, float]]:
    obs: list[tuple[str, SparsePauliOp, float]] = []
    for i, s in enumerate(CODE_STABS, 1):
        obs.append((f"stabilizer S{i}", SparsePauliOp(label(code_qubit_map(s))), 1.0))
    obs.append(("X_R * X_L (weight 6)", SparsePauliOp("X" * 6), 1.0))
    obs.append(("Z_R * Z_L (weight 6)", SparsePauliOp("Z" * 6), 1.0))
    # Operator pushing: X_L = -(I Y Y I X) on {2,3,5}; = -(X I Y Y I) on {1,3,4}
    # Z_L = -(Y I I Y Z) on {1,4,5}. Correlate each with the reference.
    obs.append(("bulk-X on wedge {2,3,5}", SparsePauliOp(
        label({0: "X", 2: "Y", 3: "Y", 5: "X"}), coeffs=[-1]), 1.0))
    obs.append(("bulk-X on wedge {1,3,4}", SparsePauliOp(
        label({0: "X", 1: "X", 3: "Y", 4: "Y"}), coeffs=[-1]), 1.0))
    obs.append(("bulk-Z on wedge {1,4,5}", SparsePauliOp(
        label({0: "Z", 1: "Y", 4: "Y", 5: "Z"}), coeffs=[-1]), 1.0))
    # Null tests: 2-qubit boundary regions must know NOTHING about R.
    obs.append(("null: X_R X1 X2", SparsePauliOp(label({0: "X", 1: "X", 2: "X"})), 0.0))
    obs.append(("null: Z_R Z4 Z5", SparsePauliOp(label({0: "Z", 4: "Z", 5: "Z"})), 0.0))
    obs.append(("null: X_R Z1 Y2", SparsePauliOp(label({0: "X", 1: "Z", 2: "Y"})), 0.0))
    obs.append(("null: Z_R X2 X3", SparsePauliOp(label({0: "Z", 2: "X", 3: "X"})), 0.0))
    return obs


def main() -> None:
    qc = build_prep_circuit()
    obs = observables()
    print(f"Preparation circuit: {qc.num_qubits} qubits, depth {qc.depth()}, "
          f"2q gates: {sum(1 for inst in qc.data if len(inst.qubits) == 2)}")

    # Local exact verification before spending hardware time.
    sv = Statevector(qc)
    print("\nLocal statevector check (must match ideal exactly):")
    ok = True
    for name, op, ideal in obs:
        val = float(np.real(sv.expectation_value(op)))
        good = abs(val - ideal) < 1e-9
        ok &= good
        print(f"   {name:28s} ideal {ideal:+.0f}  exact {val:+.4f}  {'ok' if good else 'MISMATCH'}")
    if not ok:
        raise SystemExit("local verification failed — not submitting to hardware")

    print("\nSubmitting to ibm_kingston ...")
    service = QiskitRuntimeService()
    backend = service.backend("ibm_kingston")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=2)
    isa = pm.run(qc)
    print(f"Transpiled depth {isa.depth()}, "
          f"2q gates: {sum(1 for inst in isa.data if len(inst.qubits) == 2)}")

    estimator = EstimatorV2(mode=backend)
    opts = estimator.options
    opts.default_shots = 10_000
    # Error mitigation stack:
    #   ZNE  — measure at noise factors 1x/3x/5x (gate folding), extrapolate
    #          each expectation value to the zero-noise limit;
    #   Pauli twirling — turn coherent gate errors into stochastic Pauli
    #          noise, which the exponential extrapolation models well;
    #   TREX — twirled readout error extinction;
    #   XY4 dynamical decoupling on idle qubits during the schedule.
    opts.resilience_level = 2
    opts.resilience.zne.noise_factors = (1, 3, 5)
    opts.resilience.zne.extrapolator = "exponential"
    opts.twirling.enable_gates = True
    opts.twirling.enable_measure = True
    opts.dynamical_decoupling.enable = True
    opts.dynamical_decoupling.sequence_type = "XY4"

    pub = (isa, [op.apply_layout(isa.layout) for _, op, _ in obs])
    job = estimator.run([pub])
    print(f"Job {job.job_id()} submitted (ZNE 1x/3x/5x + twirling + DD)...")

    evs = job.result()[0].data.evs

    # Unmitigated baseline: job d94tqhlgc6cc73ffi0eg (default resilience).
    baseline = [0.9300, 0.4235, 0.4466, 0.4221, 0.4450, 0.4036,
                0.4351, 0.7707, 0.3993, 0.0015, -0.0146, 0.0227, -0.0215]

    print(f"\nResults from {backend.name} (mitigated vs unmitigated):")
    print(f"   {'witness':28s} {'ideal':>6} {'raw run':>8} {'mitigated':>10}")
    for (name, _, ideal), ev, base in zip(obs, evs, baseline):
        print(f"   {name:28s} {ideal:+6.0f} {base:+8.4f} {float(ev):+10.4f}")

    wedge = [float(ev) for (n, _, i), ev in zip(obs, evs) if "wedge" in n]
    null = [abs(float(ev)) for (n, _, i), ev in zip(obs, evs) if "null" in n]
    print(f"\n   mean wedge correlator : {np.mean(wedge):+.4f}   (ideal +1, raw was +0.5350)")
    print(f"   mean |null| correlator: {np.mean(null):.4f}   (ideal  0, raw was  0.0151)")
    print("   ZNE trades variance for bias-removal: mitigated values may")
    print("   overshoot; error bars are wider; nulls must STAY at zero —")
    print("   mitigation cannot create information, only recover contrast.")


if __name__ == "__main__":
    main()
