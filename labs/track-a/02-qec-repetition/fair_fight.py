"""Milestone 2, Part 3 — the fair fight.

Part B of surface17.py used X-only noise: the one attack the repetition code
can see. Here every memory faces the same symmetric adversary — independent
X and Z errors, each at rate p per qubit — and must protect an ARBITRARY
stored state (so any uncorrected logical X or Z is a failure).

Method note: under pure Pauli noise, stabilizer codes are exactly classically
simulable (Gottesman-Knill), so we Monte-Carlo error patterns and decode in
software. Predictions:
  bare qubit    fails ~ 2p        (any error is fatal)
  repetition-3  fails ~ 3p + 3p^2 (Z errors pass straight through: WORSE
                                   than bare — armor on one flank only)
  surface-17    fails ~ 26p^2     (both flanks covered; only pairs get in)
"""

import random
from itertools import combinations

from surface17 import LOGICAL_X, LOGICAL_Z, X_STABS, Z_STABS

TRIALS = 200_000


def build_lookup(stabs: list[tuple[int, ...]]) -> dict[tuple[int, ...], frozenset[int]]:
    """Minimum-weight decoder table: syndrome -> lightest explaining pattern."""
    table: dict[tuple[int, ...], frozenset[int]] = {}
    for weight in range(4):
        for qs in combinations(range(9), weight):
            s = tuple(len(set(st) & set(qs)) % 2 for st in stabs)
            table.setdefault(s, frozenset(qs))
    return table


DECODE_X = build_lookup(list(Z_STABS.values()))   # Z-checks catch X errors
DECODE_Z = build_lookup(list(X_STABS.values()))   # X-checks catch Z errors


def sample_errors(n_qubits: int, p: float) -> tuple[frozenset[int], frozenset[int]]:
    x = frozenset(q for q in range(n_qubits) if random.random() < p)
    z = frozenset(q for q in range(n_qubits) if random.random() < p)
    return x, z


def bare_fails(p: float) -> bool:
    x, z = sample_errors(1, p)
    return bool(x or z)


def repetition_fails(p: float) -> bool:
    x, z = sample_errors(3, p)
    x_fail = len(x) >= 2          # majority vote loses to 2+ bit flips
    z_fail = len(z) % 2 == 1      # ANY odd # of phase flips = logical Z, unseen
    return x_fail or z_fail


def surface_fails(p: float) -> bool:
    x, z = sample_errors(9, p)
    syn_x = tuple(len(set(st) & x) % 2 for st in Z_STABS.values())
    residual_x = x ^ DECODE_X[syn_x]
    x_fail = len(residual_x & set(LOGICAL_Z)) % 2 == 1

    syn_z = tuple(len(set(st) & z) % 2 for st in X_STABS.values())
    residual_z = z ^ DECODE_Z[syn_z]
    z_fail = len(residual_z & set(LOGICAL_X)) % 2 == 1
    return x_fail or z_fail


def main() -> None:
    print("Symmetric noise: X and Z errors each at rate p, arbitrary stored state")
    print(f"{'p':>8} {'bare':>8} {'repetition-3':>13} {'surface-17':>11}   winner")
    for p in (0.005, 0.01, 0.02, 0.05, 0.10):
        rates = {
            "bare": sum(bare_fails(p) for _ in range(TRIALS)) / TRIALS,
            "repetition-3": sum(repetition_fails(p) for _ in range(TRIALS)) / TRIALS,
            "surface-17": sum(surface_fails(p) for _ in range(TRIALS)) / TRIALS,
        }
        winner = min(rates, key=rates.get)
        print(f"{p:>8.3f} {rates['bare']:>8.4f} {rates['repetition-3']:>13.4f} "
              f"{rates['surface-17']:>11.4f}   {winner}")

    print("\n  Repetition-3 is now WORSE than doing nothing (unseen Z errors on")
    print("  3 qubits ~ 3p vs the bare qubit's ~2p). Surface-17 pays a p^2")
    print("  prefactor premium and wins everywhere its hardware is decent —")
    print("  full-spectrum armor beats thick armor on one flank.")


if __name__ == "__main__":
    main()
