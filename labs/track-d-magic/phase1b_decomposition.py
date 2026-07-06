"""Track D, Phase 1b — the two species of magic and their wedge geography.

The literature correction (see phase1_nonlocal_magic.py footer) split
magic into two components for a bipartite logical state:

  IRREDUCIBLE (non-local magic, lit. definition): min SRE over local
      unitaries; closed form M2NL = -log2(4P^2 - 6P + 3) from the
      reduction purity P (arXiv:2511.15576).
  ERASABLE: the rest — removable by local unitaries; for our sweep
      family, exactly what the twin protocol isolates.

PRE-REGISTERED PREDICTIONS:
  A. Exact decomposition across the sweep: M2(total) = erasable + M2NL,
     with erasable = our twin-Delta and M2NL = the closed form.
  B. The closed form agrees with DIRECT numerical minimization of SRE
     over local unitaries (validates the extracted formula).
  C. Complementary wedge geography: the erasable component is visible
     only in the UNION of wedges (Phase 1); the irreducible component is
     readable from ANY SINGLE wedge via its purity (junk-corrected),
     because purity carries the Schmidt spectrum. The hidden magic is
     the removable one; the readable magic is the unremovable one.
"""

import pathlib
import sys

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent / ".." / "capstone-happy"))
from phase0_wedge_magic import m2, reduce_state  # noqa: E402
from phase1_nonlocal_magic import flower_two_slots, m2_pure_2q  # noqa: E402

LN2 = np.log(2)
PH = np.exp(1j * np.pi / 4)


def closed_form_nl(purity):
    return float(-np.log2(4 * purity ** 2 - 6 * purity + 3))


def logical_purity(psi_L):
    m = psi_L.reshape(2, 2)
    rho = m @ m.conj().T
    return float(np.real(np.trace(rho @ rho)))


def su2(a, b, c):
    return np.array([[np.cos(a) * np.exp(1j * b), np.sin(a) * np.exp(1j * c)],
                     [-np.sin(a) * np.exp(-1j * c),
                      np.cos(a) * np.exp(-1j * b)]])


def min_sre_local(psi_L, restarts=6, seed=0):
    """Direct minimization of SRE over local unitaries U (x) V."""
    rng = np.random.default_rng(seed)

    def cost(p):
        U = np.kron(su2(*p[:3]), su2(*p[3:]))
        return m2_pure_2q(U @ psi_L)
    best = np.inf
    for _ in range(restarts):
        r = minimize(cost, rng.uniform(0, np.pi, 6), method="Nelder-Mead",
                     options={"maxiter": 2000, "xatol": 1e-10, "fatol": 1e-12})
        best = min(best, r.fun)
    return float(best)


def sweep_states(frac):
    t = np.pi * frac
    c, s = np.cos(t), np.sin(t)
    magic = np.array([c, 0, 0, PH * s])
    twin = np.array([c, 0, 0, s])
    return magic, twin


def part_A_B():
    print("A+B. Decomposition identity and closed-form validation (logical)")
    print(f"   {'t/pi':>6} {'total':>7} {'M2NL(P)':>8} {'min-SRE':>8} "
          f"{'erasable=tot-NL':>16} {'twin-Delta':>11}")
    ok_A = ok_B = True
    for frac in (1 / 12, 1 / 8, 1 / 6, 1 / 4, 1 / 3):
        magic, twin = sweep_states(frac)
        total = m2_pure_2q(magic)
        nl_cf = closed_form_nl(logical_purity(magic))
        nl_min = min_sre_local(magic)
        erasable = total - nl_cf
        tdelta = total - m2_pure_2q(twin)
        ok_A &= abs(erasable - tdelta) < 1e-6
        ok_B &= abs(nl_cf - nl_min) < 1e-4
        print(f"   {frac:>6.3f} {total:>7.4f} {nl_cf:>8.4f} {nl_min:>8.4f} "
              f"{erasable:>16.4f} {tdelta:>11.4f}")
    print(f"   A: erasable == twin-Delta across sweep: {ok_A}")
    print(f"   B: closed form == direct local-unitary minimization: {ok_B}\n")


def part_C():
    print("C. Wedge geography of the two species (20-qubit flower)")
    W2 = tuple(range(4, 8))
    SUB3 = (4, 5, 6)
    UNION = tuple(range(4, 8)) + tuple(range(12, 16))

    # junk factor: calibrate wedge purity on a logical product state (P_L = 1)
    cal, _ = sweep_states(0.0)                # |00>: P_L = 1
    psi_cal = flower_two_slots(np.array([1, 0, 0, 0], dtype=complex))
    junk = {}
    for name, sub in (("wedge2 4q", W2), ("sub-wedge 3q", SUB3)):
        rho = reduce_state(psi_cal, sub, 20)
        junk[name] = float(np.real(np.trace(rho @ rho)))
    print(f"   junk purity factors (calibrated at product logical): "
          f"{ {k: round(v, 6) for k, v in junk.items()} }")

    print(f"   {'t/pi':>6} {'NL true':>8} {'NL from wedge2-4q':>18} "
          f"{'NL from sub-wedge3q':>20} {'erasable in W2 (Phase1)':>24}")
    ok = True
    for frac in (1 / 12, 1 / 8, 1 / 6, 1 / 4, 1 / 3):
        magic, twin = sweep_states(frac)
        nl_true = closed_form_nl(logical_purity(magic))
        psiM = flower_two_slots(magic)
        psiT = flower_two_slots(twin)
        row = [nl_true]
        for name, sub in (("wedge2 4q", W2), ("sub-wedge 3q", SUB3)):
            rho = reduce_state(psiM, sub, 20)
            p_est = float(np.real(np.trace(rho @ rho))) / junk[name]
            row.append(closed_form_nl(p_est))
        er_w2 = (m2(reduce_state(psiM, W2, 20))
                 - m2(reduce_state(psiT, W2, 20)))
        ok &= abs(row[1] - nl_true) < 1e-9 and abs(row[2] - nl_true) < 1e-9
        print(f"   {frac:>6.3f} {row[0]:>8.4f} {row[1]:>18.4f} "
              f"{row[2]:>20.4f} {er_w2:>24.4f}")
    print(f"   irreducible magic readable from single wedges (exact): {ok}")
    print("\n   The geography is COMPLEMENTARY: the erasable species hides")
    print("   from every single wedge and appears only in the union")
    print("   (Phase 1); the irreducible species is readable from any")
    print("   single wedge — even 3 qubits of it — via junk-corrected")
    print("   purity. What local operations can remove, single wedges")
    print("   cannot see; what they cannot remove, single wedges cannot")
    print("   miss.")


if __name__ == "__main__":
    part_A_B()
    part_C()
