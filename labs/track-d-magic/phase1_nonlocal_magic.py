"""Track D, Phase 1 — non-local magic: the resource no single wedge holds.

THE QUESTION: Phase 0 showed injected magic is wedge-quantized — it lives
exactly where the bulk point's wedge lives. What happens when the magic
is injected into an ENTANGLED pair of bulk slots? Is there magic that no
single wedge holds — magic living in the correlation itself?

METHODOLOGICAL DISCOVERY (made during design, demonstrated in the
self-test below): the mixed-state SRE diagnostic FALSE-POSITIVES on
classical mixedness — a stabilizer mixture diag(c^2, s^2) reads as
"magic" — and entangled logicals make every wedge reduction mixed. The
fix is twin control: every magic state is paired with its STABILIZER
TWIN (identical amplitudes, phases stripped), whose reductions have
identical mixedness structure. The honest observable is
    Delta(region) = M2(magic state) - M2(twin),
our null-witness methodology ported to magic diagnostics.

PRE-REGISTERED PREDICTIONS:
  T (x) T   (product magic):   Delta(W2) = Delta(W4) = 0.415,
                               Delta(union) = 0.830, non-local part = 0.
  T-Bell (|00> + e^{i pi/4}|11>)/sqrt2:
                               Delta(W2) = Delta(W4) = 0,
                               Delta(union) = 0.415:
                               ALL the magic is non-local.
  Sweep  cos t|00> + e^{i pi/4} sin t|11>: wedge Deltas 0 throughout;
         non-local magic = global logical M2(t), peaking at the Bell
         point. Phase-injected magic in an entangled pair is 100%
         wedge-non-local at every entanglement strength.
"""

import pathlib
import sys
from itertools import product

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent / ".." / "capstone-happy"))
from happy_network import network  # noqa: E402
from phase0_wedge_magic import fwht, m2, reduce_state  # noqa: E402

LN2 = np.log(2)


def m2_pure_2q(psi_L):
    """Exact SRE of a 2-qubit pure logical state (16 Paulis)."""
    rho = np.outer(psi_L, psi_L.conj())
    return m2(rho)


def flower_two_slots(psi_L):
    """Flower with 2-qubit logical state psi_L on slots 2 and 4."""
    psi = np.zeros(2 ** 20, dtype=complex)
    for b2, b4 in product((0, 1), repeat=2):
        amp = psi_L[2 * b2 + b4]
        if abs(amp) < 1e-14:
            continue
        branch = network(0, [0, b2, 0, b4, 0])
        psi = psi + amp * branch / np.linalg.norm(branch)
    return psi / np.linalg.norm(psi)


REGIONS = {
    "wedge 2 (petal-2 block)": tuple(range(4, 8)),
    "wedge 4 (petal-4 block)": tuple(range(12, 16)),
    "union of wedges (8q)": tuple(range(4, 8)) + tuple(range(12, 16)),
    "wedge 2 + petal 3 (8q)": tuple(range(4, 12)),
    "everything else (12q)": (0, 1, 2, 3) + tuple(range(8, 12)) + tuple(range(16, 20)),
}


def self_test_false_positive():
    print("Self-test — the diagnostic's false positive, demonstrated:")
    c2, s2 = np.cos(np.pi / 8) ** 2, np.sin(np.pi / 8) ** 2
    rho_mix = np.diag([c2, s2]).astype(complex)     # stabilizer mixture!
    print(f"   M2(diag({c2:.3f},{s2:.3f})) = {m2(rho_mix):.4f}"
          f"  -> NONZERO on a zero-magic classical mixture.")
    print("   Hence: all results below are twin-controlled differences.\n")


def ledger(psi_L_magic, psi_L_twin, label):
    psiM = flower_two_slots(psi_L_magic)
    psiT = flower_two_slots(psi_L_twin)
    print(f"   {label}")
    print(f"   global logical M2 (= boundary M2 by Clifford invariance): "
          f"{m2_pure_2q(psi_L_magic):.4f}")
    print(f"   {'region':>26} {'M2 magic':>9} {'M2 twin':>8} {'DELTA':>7}")
    deltas = {}
    for name, sub in REGIONS.items():
        vM = m2(reduce_state(psiM, sub, 20))
        vT = m2(reduce_state(psiT, sub, 20))
        deltas[name] = vM - vT
        print(f"   {name:>26} {vM:>9.4f} {vT:>8.4f} {vM - vT:>7.4f}")
    nl = (deltas["union of wedges (8q)"]
          - deltas["wedge 2 (petal-2 block)"]
          - deltas["wedge 4 (petal-4 block)"])
    print(f"   non-local magic (union - wedges): {nl:.4f}\n")
    return nl


def main():
    self_test_false_positive()
    ph = np.exp(1j * np.pi / 4)

    print("STATE 1 — product magic: |T>_2 (x) |T>_4 (twin: |+>|+>)")
    tt = np.kron([1, ph], [1, ph]) / 2
    pp = np.ones(4) / 2
    ledger(tt, pp, "expect fully LOCAL magic")

    print("STATE 2 — T-Bell: (|00> + e^{i pi/4}|11>)/sqrt2 (twin: Bell)")
    tbell = np.array([1, 0, 0, ph]) / np.sqrt(2)
    bell = np.array([1, 0, 0, 1]) / np.sqrt(2)
    ledger(tbell, bell, "expect fully NON-LOCAL magic")

    print("SWEEP — cos t |00> + e^{i pi/4} sin t |11> vs phase-free twin")
    print(f"   {'t/pi':>6} {'logical ent. S/ln2':>18} {'D(W2)':>7} "
          f"{'D(W4)':>7} {'D(union)':>9} {'non-local':>10}")
    for frac in (1 / 12, 1 / 8, 1 / 6, 1 / 4, 1 / 3):
        t = np.pi * frac
        c, s = np.cos(t), np.sin(t)
        magic = np.array([c, 0, 0, ph * s])
        twin = np.array([c, 0, 0, s])
        psiM = flower_two_slots(magic)
        psiT = flower_two_slots(twin)
        d = {}
        for key in ("wedge 2 (petal-2 block)", "wedge 4 (petal-4 block)",
                    "union of wedges (8q)"):
            d[key] = (m2(reduce_state(psiM, REGIONS[key], 20))
                      - m2(reduce_state(psiT, REGIONS[key], 20)))
        nl = (d["union of wedges (8q)"] - d["wedge 2 (petal-2 block)"]
              - d["wedge 4 (petal-4 block)"])
        p = c ** 2
        ent = 0.0 if p in (0, 1) else float(-(p * np.log(p)
                                              + (1 - p) * np.log(1 - p)) / LN2)
        print(f"   {frac:>6.3f} {ent:>18.4f} "
              f"{d['wedge 2 (petal-2 block)']:>7.4f} "
              f"{d['wedge 4 (petal-4 block)']:>7.4f} "
              f"{d['union of wedges (8q)']:>9.4f} {nl:>10.4f}")
    print("\n   Reading: where the wedge Deltas vanish and the union Delta")
    print("   does not, the injected magic is invisible to every single")
    print("   wedge and lives only in their correlation — wedge-resolved")
    print("   non-local magic, measured against its own mixedness control.")


if __name__ == "__main__":
    main()
