"""Milestone 2, Part 2 — the distance-3 rotated surface code ("surface-17").

Layout: 9 data qubits on a 3x3 grid, indexed q = 3*row + col:

        q0 q1 q2          Z-checks (detect X errors): plaquettes + top/bottom
        q3 q4 q5          X-checks (detect Z errors): plaquettes + left/right
        q6 q7 q8

The logical qubit is stored in no qubit at all — it lives in the topology:
  logical Z = Z2 Z5 Z8   (a string spanning top boundary to bottom)
  logical X = X6 X7 X8   (a string spanning left boundary to right)
Local errors light up parity checks at their ENDPOINTS; the only invisible
attack is a string that crosses the entire lattice. Bigger lattice = longer
required string = exponentially safer. That is topological protection.

Part A: full quantum syndrome extraction (two rounds, 17 qubits) against
        hand-crafted attacks — single X, single Z, Y, an error string, and
        the undetectable logical operator.
Part B: memory experiment under random X noise with a minimum-weight decoder;
        logical error rate scales as O(p^2) because distance 3 corrects any
        single fault.
"""

import math
from itertools import combinations

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error

# Stabilizers (parity checks). Every X-check overlaps every Z-check on an
# even number of qubits, so all checks commute and can be measured together.
Z_STABS = {"Z_A": (0, 1, 3, 4), "Z_B": (4, 5, 7, 8), "Z_C": (1, 2), "Z_D": (6, 7)}
X_STABS = {"X_A": (1, 2, 4, 5), "X_B": (3, 4, 6, 7), "X_C": (0, 3), "X_D": (5, 8)}
STAB_ORDER = list(Z_STABS) + list(X_STABS)          # ancilla index order
LOGICAL_Z = (2, 5, 8)
LOGICAL_X = (6, 7, 8)

SHOTS_A = 1_000
SHOTS_B = 20_000


# ─── Part A: real quantum syndrome extraction ─────────────────────────────────

def measure_round(qc: QuantumCircuit, data, anc, creg) -> None:
    """One full round: measure all 8 stabilizers into creg, then reset ancillas.

    Z-check: CNOTs data->ancilla accumulate the bit-parity on the ancilla.
    X-check: ancilla in |+>, CNOTs ancilla->data, back to Z basis — the
    ancilla picks up the PHASE-parity. Neither reads any data value.
    """
    for i, name in enumerate(STAB_ORDER):
        if name.startswith("Z"):
            for q in Z_STABS[name]:
                qc.cx(data[q], anc[i])
        else:
            qc.h(anc[i])
            for q in X_STABS[name]:
                qc.cx(anc[i], data[q])
            qc.h(anc[i])
        qc.measure(anc[i], creg[i])
    for i in range(8):
        qc.reset(anc[i])


def attack_circuit(attack: list[tuple[str, int]]) -> QuantumCircuit:
    """|0..0> -> round 1 (projects into logical |0>, fixes the X-check frame)
    -> inject attack -> round 2 -> measure data. Syndrome = round2 XOR round1."""
    data, anc = QuantumRegister(9, "d"), QuantumRegister(8, "a")
    r1, r2 = ClassicalRegister(8, "r1"), ClassicalRegister(8, "r2")
    dat = ClassicalRegister(9, "dat")
    qc = QuantumCircuit(data, anc, r1, r2, dat)

    measure_round(qc, data, anc, r1)
    qc.barrier()
    for pauli, q in attack:
        getattr(qc, pauli.lower())(data[q])
    qc.barrier()
    measure_round(qc, data, anc, r2)
    qc.measure(data, dat)
    return qc


def analyze_shot(key: str) -> tuple[frozenset[str], int]:
    """Counts key -> (set of lit stabilizers, logical Z parity)."""
    dat_str, r2_str, r1_str = key.split()      # last-added register leftmost
    lit = frozenset(
        STAB_ORDER[i]
        for i in range(8)
        if int(r1_str[-1 - i]) ^ int(r2_str[-1 - i])
    )
    z_l = sum(int(dat_str[-1 - q]) for q in LOGICAL_Z) % 2
    return lit, z_l


def part_a() -> None:
    print("=" * 70)
    print("PART A — syndrome fingerprints on the d=3 surface code (17 qubits)")

    attacks = [
        ("clean run          ", []),
        ("X on q4 (bit flip) ", [("X", 4)]),
        ("Z on q4 (phase flip", [("Z", 4)]),
        ("Y on q4 (both)     ", [("Y", 4)]),
        ("string X2-X5       ", [("X", 2), ("X", 5)]),
        ("logical X6-X7-X8   ", [("X", 6), ("X", 7), ("X", 8)]),
    ]
    sim = AerSimulator()
    for label, attack in attacks:
        qc = transpile(attack_circuit(attack), sim, optimization_level=0)
        counts = sim.run(qc, shots=SHOTS_A).result().get_counts()

        outcomes: dict[tuple[frozenset[str], int], int] = {}
        for key, n in counts.items():
            o = analyze_shot(key)
            outcomes[o] = outcomes.get(o, 0) + n
        (lit, z_l), n = max(outcomes.items(), key=lambda kv: kv[1])
        determinism = n / SHOTS_A
        syn = ",".join(sorted(lit)) if lit else "SILENT"
        print(f"  {label} -> syndrome [{syn:>12s}]  logical Z parity = {z_l}"
              f"   ({determinism:.0%} of shots)")

    print("\n  Single errors light adjacent checks; the string lights only its")
    print("  ENDPOINTS; the spanning string lights nothing yet flips the logical")
    print("  qubit — the only undetectable attack crosses the whole lattice.")


# ─── Part B: memory experiment with a minimum-weight decoder ──────────────────

def x_syndrome(flipped: frozenset[int]) -> tuple[int, ...]:
    return tuple(len(set(s) & flipped) % 2 for s in Z_STABS.values())


def build_decoder() -> dict[tuple[int, ...], frozenset[int]]:
    """Brute-force minimum-weight decoder: for each of the 16 possible
    Z-check syndromes, the lightest X-error pattern that explains it."""
    table: dict[tuple[int, ...], frozenset[int]] = {}
    for weight in range(4):                    # weight 3 covers all 16 syndromes
        for qs in combinations(range(9), weight):
            s = x_syndrome(frozenset(qs))
            table.setdefault(s, frozenset(qs))
    return table


def part_b() -> None:
    print("\n" + "=" * 70)
    print("PART B — logical error rate under random bit-flip noise (rate p)")
    print(f"{'p':>8} {'p_L surface d=3':>16} {'p_L/p^2':>9} {'repetition-3':>13} {'bare':>7}")

    decoder = build_decoder()
    sim_template = QuantumCircuit(9, 9)
    for q in range(9):
        sim_template.id(q)
    sim_template.measure(range(9), range(9))

    for p in (0.01, 0.03, 0.05, 0.10, 0.20):
        nm = NoiseModel()
        nm.add_all_qubit_quantum_error(pauli_error([("X", p), ("I", 1 - p)]), "id")
        sim = AerSimulator(noise_model=nm)
        counts = sim.run(transpile(sim_template, sim, optimization_level=0),
                         shots=SHOTS_B).result().get_counts()

        failures = 0
        for key, n in counts.items():
            flipped = frozenset(q for q in range(9) if key[-1 - q] == "1")
            correction = decoder[x_syndrome(flipped)]
            residual = flipped ^ correction    # actual error minus our guess
            if len(residual & set(LOGICAL_Z)) % 2:   # residual crosses Z_L?
                failures += n
        p_l = failures / SHOTS_B
        rep3 = 3 * p**2 - 2 * p**3
        print(f"{p:>8.2f} {p_l:>16.4f} {p_l / p**2:>9.2f} {rep3:>13.4f} {p:>7.2f}")

    print("\n  p_L/p^2 ~ constant: distance 3 kills ALL single faults, so only")
    print("  unlucky pairs (probability ~ p^2) can sneak a logical flip through.")
    print("  Distance d kills (d-1)/2 faults -> p_L ~ p^((d+1)/2): grow the")
    print("  lattice, suppress errors exponentially. This is why Google/IBM")
    print("  build surface codes, and why HaPPY bulk geometry is robust.")


if __name__ == "__main__":
    part_a()
    part_b()
