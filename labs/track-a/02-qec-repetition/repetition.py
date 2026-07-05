"""Milestone 2, Part 1 — the 3-qubit repetition code (bit-flip code).

The experiment, in the project's paradigm:
  We store one logical qubit redundantly across three physical qubits:
  |psi>_L = a|000> + b|111>. An attacker (noise) flips physical bits. Our
  intrusion-detection system measures PARITIES (Z0Z1 and Z1Z2) via ancilla
  qubits. Crucially, a parity check reads "are these two bits equal?" without
  reading what the bits ARE — so it localizes the intrusion (the error)
  while never touching the encoded message (the superposition survives).
  That syndrome -> locate -> repair loop is quantum error correction, and
  scaled up to a 2D grid of parity checks it becomes the surface code.

Part A: deterministic demo — inject a known bit-flip, watch the syndrome
        fingerprint it, verify the logical superposition comes through intact.
Part B: threshold sweep — random bit-flips at rate p on every data qubit;
        does the encoded ("hardened") qubit beat a bare physical qubit?
        Theory: logical error rate p_L = 3p^2 - 2p^3, which beats p for
        p < 1/2 and LOSES above it. Redundancy only helps good hardware.
"""

import math

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error

SHOTS = 20_000
THETA = 2 * math.pi / 3  # logical state Ry(THETA)|0>_L : P(0)=0.25, P(1)=0.75


def build_circuit(inject_on: int | None = None, noisy_ids: bool = False) -> QuantumCircuit:
    """Encode Ry(THETA)|0> into 3 qubits, optionally inject/expose errors,
    then extract the syndrome and measure everything."""
    data = QuantumRegister(3, "data")
    anc = QuantumRegister(2, "anc")
    syn = ClassicalRegister(2, "syn")
    dat = ClassicalRegister(3, "dat")
    qc = QuantumCircuit(data, anc, syn, dat)

    # Encode: a|0> + b|1>  ->  a|000> + b|111>
    qc.ry(THETA, data[0])
    qc.cx(data[0], data[1])
    qc.cx(data[0], data[2])
    qc.barrier()

    # The "attack surface": either one deterministic flip (Part A),
    # or identity gates that the noise model turns into random flips (Part B).
    if inject_on is not None:
        qc.x(data[inject_on])
    if noisy_ids:
        for q in data:
            qc.id(q)
    qc.barrier()

    # Syndrome extraction: ancilla 0 learns parity Z0Z1, ancilla 1 learns Z1Z2.
    # CNOTs copy PARITY onto the ancilla, never the data value itself.
    qc.cx(data[0], anc[0])
    qc.cx(data[1], anc[0])
    qc.cx(data[1], anc[1])
    qc.cx(data[2], anc[1])
    qc.measure(anc, syn)
    qc.measure(data, dat)
    return qc


# Syndrome table: (s0, s1) -> which data qubit took the hit.
#   s0 checks pair (0,1), s1 checks pair (1,2).
SYNDROME_TO_QUBIT = {
    (0, 0): None,  # all parities clean
    (1, 0): 0,     # only pair (0,1) broken -> qubit 0
    (1, 1): 1,     # both pairs broken -> the shared qubit, 1
    (0, 1): 2,     # only pair (1,2) broken -> qubit 2
}


def decode(key: str) -> tuple[tuple[int, int], int]:
    """Turn one counts key into (syndrome, corrected logical value).

    Key format: 'ddd ss' — registers print last-added leftmost, and within
    a register the rightmost character is bit 0.
    """
    dat_str, syn_str = key.split()
    s0, s1 = int(syn_str[-1]), int(syn_str[-2])
    bits = [int(dat_str[-1]), int(dat_str[-2]), int(dat_str[-3])]

    flip = SYNDROME_TO_QUBIT[(s0, s1)]
    if flip is not None:
        bits[flip] ^= 1                     # repair the located error
    logical = 1 if sum(bits) >= 2 else 0    # majority vote readout
    return (s0, s1), logical


def run(qc: QuantumCircuit, noise_model: NoiseModel | None = None) -> dict[str, int]:
    sim = AerSimulator(noise_model=noise_model)
    return sim.run(transpile(qc, sim, optimization_level=0), shots=SHOTS).result().get_counts()


def part_a() -> None:
    print("=" * 68)
    print("PART A — syndrome fingerprinting (deterministic single flips)")
    print(f"Logical state: cos({THETA:.3f}/2)|0>_L + sin({THETA:.3f}/2)|1>_L")
    print(f"Expected logical readout: P(0)=0.250, P(1)=0.750\n")

    for target in (None, 0, 1, 2):
        counts = run(build_circuit(inject_on=target))
        syndromes: dict[tuple[int, int], int] = {}
        logical_ones = 0
        for key, n in counts.items():
            syn, logical = decode(key)
            syndromes[syn] = syndromes.get(syn, 0) + n
            logical_ones += n * logical
        top_syn = max(syndromes, key=syndromes.get)
        p1 = logical_ones / SHOTS
        label = "no error " if target is None else f"X on q{target}"
        print(f"  attack: {label} -> syndrome {top_syn} "
              f"(points at {SYNDROME_TO_QUBIT[top_syn]}), "
              f"corrected P(1) = {p1:.3f}")
    print("\n  Superposition survives every attack: the parity checks located")
    print("  each intruder without ever reading the encoded message.")


def part_b() -> None:
    print("\n" + "=" * 68)
    print("PART B — threshold sweep: hardened qubit vs bare qubit")
    print(f"{'p (physical)':>13} {'p_L (measured)':>15} {'3p^2-2p^3 (theory)':>19} {'wins?':>6}")

    for p in (0.01, 0.05, 0.10, 0.20, 0.30, 0.45, 0.55):
        nm = NoiseModel()
        nm.add_all_qubit_quantum_error(pauli_error([("X", p), ("I", 1 - p)]), "id")
        counts = run(build_circuit(noisy_ids=True), noise_model=nm)

        # Logical error = corrected readout disagrees with the ideal
        # distribution's outcome per shot; for a clean estimate we compare
        # against the no-noise encoded value shot-by-shot via majority.
        # Since data collapse gives 000/111 (+ flips), a logical error is a
        # majority flip: P(1) should be 0.75; excess symmetric flips move it
        # toward 0.5. Estimate p_L from the observed P(1):
        #   P(1)_obs = 0.75(1 - p_L) + 0.25 p_L  =>  p_L = (0.75 - P) / 0.5
        logical_ones = sum(n * decode(k)[1] for k, n in counts.items())
        p1 = logical_ones / SHOTS
        p_logical = (0.75 - p1) / 0.5
        theory = 3 * p**2 - 2 * p**3
        verdict = "YES" if p_logical < p else "no"
        print(f"{p:>13.2f} {p_logical:>15.4f} {theory:>19.4f} {verdict:>6}")

    print("\n  Below p=0.5 the code wins; above, redundancy AMPLIFIES errors.")
    print("  Every QEC scheme has such a threshold — the surface code's is")
    print("  ~1e-2, which is why it, and not this code, runs on real hardware.")


if __name__ == "__main__":
    part_a()
    part_b()
