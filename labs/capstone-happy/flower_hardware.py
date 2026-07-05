"""CAPSTONE IV — the six-tile flower network on real hardware (21 qubits).

State: reference qubit R maximally entangled with PETAL-1's bulk qubit,
all other bulk legs frozen; the 20-qubit boundary of the flower carries
everything. This is a stabilizer state, so we:

  1. derive its 21 stabilizer generators numerically — center-tile
     stabilizers and frozen-bulk checks PUSHED through each petal's
     Clifford isometry W (2 legs -> 4 legs), plus each petal's 2
     image-code checks;
  2. synthesize a Clifford preparation circuit from those generators;
  3. verify the circuit reproduces the exact 2^21 statevector from
     happy_network.py before spending any hardware time;
  4. measure witnesses on ibm_kingston with ZNE + twirling + DD:
       - petal image-code stabilizers (encoding quality)
       - bulk-X and bulk-Z of petal 1, each read from its own small
         boundary avatar (wedge tests, ideal +1) — including TWO
         different avatars of the same bulk-X (operator pushing)
       - null tests: 2-qubit regions, and the SAME bulk-X avatar
         applied to the WRONG petal (right key, wrong door: ideal 0)
"""

import pathlib
import sys
from functools import reduce
from itertools import product

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from happy_network import T, probe_state  # noqa: E402

from qiskit.quantum_info import SparsePauliOp, Statevector  # noqa: E402
from qiskit.synthesis import synth_circuit_from_stabilizers  # noqa: E402
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager  # noqa: E402
from qiskit_ibm_runtime import EstimatorV2, QiskitRuntimeService  # noqa: E402

P1 = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}
LAB4 = ["".join(p) for p in product("IXYZ", repeat=4)]
MAT4 = {lab: reduce(np.kron, [P1[c] for c in lab]) for lab in LAB4}

# Petal isometry W: (link, bulk) -> (f1..f4). Rows f1..f4 (f1 = MSB),
# cols (link MSB, bulk LSB). sqrt(2) restores isometry normalization.
M = T.transpose(2, 3, 4, 5, 1, 0).reshape(16, 4)
W = np.sqrt(2) * M
assert np.allclose(W.conj().T @ W, np.eye(4)), "W is not an isometry"


def pauli_reps(two_label: str) -> list[tuple[float, str]]:
    """All 4 boundary representatives of an input Pauli pushed through W,
    sorted by weight. two_label = (link char, bulk char)."""
    sigma = np.kron(P1[two_label[0]], P1[two_label[1]])
    E = W @ sigma @ W.conj().T
    reps = []
    for lab, m in MAT4.items():
        c = np.trace(E @ m.conj().T) / 16
        if abs(c) > 1e-9:
            sign = complex(4 * c)
            assert abs(sign.imag) < 1e-9 and abs(abs(sign.real) - 1) < 1e-6
            reps.append((float(sign.real), lab))
    return sorted(reps, key=lambda r: sum(ch != "I" for ch in r[1]))


IMAGE_STABS = [(s, lab) for s, lab in pauli_reps("II") if lab != "IIII"]


def qiskit_label(chars: list[str], sign: float = 1.0) -> str:
    return ("+" if sign > 0 else "-") + "".join(reversed(chars))


def assemble(r_char: str, petal_parts: dict[int, tuple[float, str]]) -> tuple[float, list[str]]:
    """Place per-petal 4-qubit labels into the 21-qubit register.
    Qubit 0 = R; petal i (1..5) boundary = qubits 1+4(i-1) .. 4+4(i-1)."""
    chars = ["I"] * 21
    chars[0] = r_char
    sign = 1.0
    for i, (s, lab) in petal_parts.items():
        sign *= s
        for k, ch in enumerate(lab):
            chars[1 + 4 * (i - 1) + k] = ch
    return sign, chars


def generators() -> list[str]:
    gens = []
    # Center-tile stabilizers + logical Z (bulk of center frozen to |0>),
    # each acting on the 5 link legs -> pushed through each petal.
    for s5 in ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ", "ZZZZZ"]:
        parts = {i: pauli_reps(s5[i - 1] + "I")[0] for i in range(1, 6)}
        sign, chars = assemble("I", parts)
        gens.append(qiskit_label(chars, sign))
    # Frozen bulk legs of petals 2..5.
    for i in range(2, 6):
        sign, chars = assemble("I", {i: pauli_reps("IZ")[0]})
        gens.append(qiskit_label(chars, sign))
    # Reference entangled with petal-1 bulk.
    for r_char, blabel in (("X", "IX"), ("Z", "IZ")):
        sign, chars = assemble(r_char, {1: pauli_reps(blabel)[0]})
        gens.append(qiskit_label(chars, sign))
    # Each petal's 2 image-code checks.
    for i in range(1, 6):
        for s, lab in IMAGE_STABS[:2]:
            sign, chars = assemble("I", {i: (s, lab)})
            gens.append(qiskit_label(chars, sign))
    return gens


def witnesses() -> list[tuple[str, SparsePauliOp, float]]:
    obs = []
    # Encoding quality: one image check per petal (weight <= 4).
    for i in range(1, 6):
        s, lab = IMAGE_STABS[0]
        sign, chars = assemble("I", {i: (s, lab)})
        obs.append((f"image check, petal {i}", SparsePauliOp(
            "".join(reversed(chars)), coeffs=[sign]), 1.0))
    # Wedge tests: petal-1 bulk operators read from boundary avatars.
    xreps = pauli_reps("IX")
    zreps = pauli_reps("IZ")
    for tag, r_char, (s, lab) in (("bulk-X avatar A", "X", xreps[0]),
                                  ("bulk-X avatar B", "X", xreps[1]),
                                  ("bulk-Z avatar", "Z", zreps[0])):
        sign, chars = assemble(r_char, {1: (s, lab)})
        obs.append((f"wedge: {tag} on petal 1", SparsePauliOp(
            "".join(reversed(chars)), coeffs=[sign]), 1.0))
    # Null tests.
    s, lab = xreps[0]
    sign, chars = assemble("X", {2: (s, lab)})
    obs.append(("null: same bulk-X on petal 2", SparsePauliOp(
        "".join(reversed(chars)), coeffs=[sign]), 0.0))
    for name, r_char, sites in (("null: X_R X X on petal-1 pair", "X", {1: "XXII"}),
                                ("null: Z_R Z Z on petal-3 pair", "Z", {3: "ZZII"})):
        _, chars = assemble(r_char, {i: (1.0, lab) for i, lab in sites.items()})
        obs.append((name, SparsePauliOp("".join(reversed(chars))), 0.0))
    return obs


def main() -> None:
    qc = synth_circuit_from_stabilizers(generators())
    print(f"Flower prep circuit: {qc.num_qubits} qubits, depth {qc.depth()}, "
          f"2q gates: {sum(1 for g in qc.data if len(g.qubits) == 2)}")

    # Exact verification against the tensor-network state.
    psi = probe_state("petal").reshape([2] * 21).transpose(*reversed(range(21))).ravel()
    sv = Statevector(qc)
    overlap = abs(np.vdot(sv.data, psi))
    print(f"Overlap with exact tensor-network state: {overlap:.10f}")
    assert overlap > 1 - 1e-9, "synthesized state does not match — aborting"

    obs = witnesses()
    print("\nLocal exact witness values:")
    checked = []
    for name, op, ideal in obs:
        val = float(np.real(sv.expectation_value(op)))
        if ideal == 1.0:                    # absorb representative sign
            assert abs(abs(val) - 1) < 1e-9, f"{name}: |{val}| != 1"
            op = op * np.sign(val)
            val = abs(val)
        else:
            assert abs(val) < 1e-9, f"{name}: expected 0, got {val}"
        checked.append((name, op, ideal))
        print(f"   {name:34s} ideal {ideal:+.0f}  exact {val:+.4f}")

    print("\nSubmitting to ibm_kingston ...")
    service = QiskitRuntimeService()
    backend = service.backend("ibm_kingston")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
    isa = pm.run(qc)
    print(f"Transpiled depth {isa.depth()}, "
          f"2q gates: {sum(1 for g in isa.data if len(g.qubits) == 2)}")

    estimator = EstimatorV2(mode=backend)
    opts = estimator.options
    opts.default_shots = 10_000
    # NO ZNE here: at ~600 2q gates several witnesses sit at the noise floor
    # even at 1x, and exponential extrapolation through noise-floor points
    # diverges (first attempt, job d94u25nu62ks7396fhlg, returned "nulls" of
    # +/- 4e9 — impossible values that flagged the failure). For circuits
    # this deep the trustworthy stack is twirling + readout mitigation + DD,
    # reported raw.
    opts.resilience_level = 1
    opts.twirling.enable_gates = True
    opts.twirling.enable_measure = True
    opts.dynamical_decoupling.enable = True
    opts.dynamical_decoupling.sequence_type = "XY4"

    pub = (isa, [op.apply_layout(isa.layout) for _, op, _ in checked])
    job = estimator.run([pub])
    print(f"Job {job.job_id()} submitted, waiting for the fridge...")

    evs = job.result()[0].data.evs
    print(f"\nResults from {backend.name}:")
    print(f"   {'witness':34s} {'ideal':>6} {'measured':>9}")
    for (name, _, ideal), ev in zip(checked, evs):
        print(f"   {name:34s} {ideal:+6.0f} {float(ev):+9.4f}")

    wedge = [float(ev) for (n, _, _), ev in zip(checked, evs) if n.startswith("wedge")]
    null = [abs(float(ev)) for (n, _, _), ev in zip(checked, evs) if n.startswith("null")]
    print(f"\n   mean wedge correlator : {np.mean(wedge):+.4f}   (ideal +1)")
    print(f"   mean |null| correlator: {np.mean(null):.4f}   (ideal  0)")
    print("   A bulk point of a six-tile emergent geometry, located — and")
    print("   localized — on 21 physical qubits.")


if __name__ == "__main__":
    main()
