"""Milestone 1 — Bell pair + CHSH test.

The experiment, in the project's paradigm:
  We forge a shared session key (an entangled Bell pair), then Alice and Bob
  each probe their half with one of two "sniffer configurations" (measurement
  angles). Classical hardware — any theory where the qubits carry pre-written
  local state — cannot push the CHSH statistic S above 2. Quantum mechanics
  reaches 2*sqrt(2) ~= 2.828 (Tsirelson's bound). Measuring S > 2 is the proof
  that entanglement is not hidden classical data.

  Equally important: the same run shows Alice's local statistics never depend
  on Bob's setting. Real nonlocal correlation, zero signaling bandwidth.

Bases: measuring "spin along angle theta in the X-Z plane" is implemented by
rotating the qubit with Ry(-theta) and then measuring Z. For the Bell state
|Phi+> = (|00> + |11>)/sqrt(2), theory predicts E(ta, tb) = cos(ta - tb).
"""

import math

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

SHOTS = 20_000

# Optimal CHSH settings: Alice uses {a, a'}, Bob uses {b, b'}.
ANGLES = {
    "a": 0.0,
    "a'": math.pi / 2,
    "b": math.pi / 4,
    "b'": 3 * math.pi / 4,
}


def make_chsh_circuit(theta_a: float, theta_b: float) -> QuantumCircuit:
    """Bell pair |Phi+>, then measure qubit 0 (Alice) and qubit 1 (Bob)
    in bases rotated by theta_a and theta_b."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)          # superposition: |0> -> (|0> + |1>)/sqrt(2)
    qc.cx(0, 1)      # entangle: (|00> + |11>)/sqrt(2)
    qc.ry(-theta_a, 0)
    qc.ry(-theta_b, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def run_setting(theta_a: float, theta_b: float, shots: int = SHOTS) -> dict[str, int]:
    """Run one measurement-setting pair; returns counts like {'00': 5023, '01': ...}.

    Bitstring order is Qiskit little-endian (bit 0 = Alice is the RIGHTMOST
    character), but for the correlator only same-vs-different matters.
    """
    sim = AerSimulator()
    qc = transpile(make_chsh_circuit(theta_a, theta_b), sim)
    return sim.run(qc, shots=shots).result().get_counts()


# ─── YOUR CODE: the physics lives here ────────────────────────────────────────

def correlation(counts: dict[str, int]) -> float:
    """Estimate the correlator E for one setting pair from measurement counts.

    Each shot gives Alice and Bob one outcome each, recorded as bits (0 or 1).
    Physically these represent measurement values +1 (bit 0) and -1 (bit 1).
    E is the expectation value of the PRODUCT of Alice's and Bob's values:
    E = +1 contribution when they agree ('00' or '11'),
        -1 contribution when they disagree ('01' or '10'),
    averaged over all shots. E ranges from -1 (perfect anti-correlation)
    to +1 (perfect correlation).
    """
    total = sum(counts.values())
    agree = counts.get("00", 0) + counts.get("11", 0)
    disagree = counts.get("01", 0) + counts.get("10", 0)
    return (agree - disagree) / total


def chsh_S(E: dict[str, float]) -> float:
    """Combine the four correlators into the CHSH statistic.

    E is keyed by setting pair: E["a,b"], E["a,b'"], E["a',b"], E["a',b'"].
    The CHSH combination adds three of them and SUBTRACTS one — with our
    angles the odd one out is E["a,b'"]. (Why subtraction? A classical local
    strategy can make any three terms large, but only at the cost of the
    fourth — the minus sign is the trap that caps classical hardware at 2.)
    """
    return E["a,b"] - E["a,b'"] + E["a',b"] + E["a',b'"]

# ──────────────────────────────────────────────────────────────────────────────


def alice_prob_zero(counts: dict[str, int]) -> float:
    """P(Alice reads 0), ignoring Bob. Alice is bit 0 = rightmost character."""
    total = sum(counts.values())
    return sum(n for bits, n in counts.items() if bits[-1] == "0") / total


def main() -> None:
    E: dict[str, float] = {}
    all_counts: dict[str, dict[str, int]] = {}
    for alice in ("a", "a'"):
        for bob in ("b", "b'"):
            key = f"{alice},{bob}"
            counts = run_setting(ANGLES[alice], ANGLES[bob])
            all_counts[key] = counts
            E[key] = correlation(counts)
            theory = math.cos(ANGLES[alice] - ANGLES[bob])
            print(f"E({key:5s}) = {E[key]:+.4f}   (theory {theory:+.4f})")

    # No-signaling check: Alice's LOCAL statistics must not depend on which
    # setting Bob chose — otherwise Bob could send messages by switching bases.
    print("\nNo-signaling check (Alice's marginal vs Bob's choice):")
    for alice in ("a", "a'"):
        p_b = alice_prob_zero(all_counts[f"{alice},b"])
        p_bp = alice_prob_zero(all_counts[f"{alice},b'"])
        print(f"  Alice setting {alice:2s}: P(0)={p_b:.4f} when Bob->b, "
              f"{p_bp:.4f} when Bob->b'   (diff {abs(p_b - p_bp):.4f})")

    S = chsh_S(E)
    print(f"\nCHSH S = {S:.4f}")
    print(f"  classical (local realist) bound : 2.0000")
    print(f"  Tsirelson (quantum) bound       : {2 * math.sqrt(2):.4f}")
    if S > 2:
        print("  => Bell inequality VIOLATED: these correlations cannot be")
        print("     produced by any pre-shared classical data.")
    else:
        print("  => no violation — check the correlator sign convention.")


if __name__ == "__main__":
    main()
