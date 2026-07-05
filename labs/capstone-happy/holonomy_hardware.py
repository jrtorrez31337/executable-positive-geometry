"""CAPSTONE VI on hardware — measuring a code-space holonomy on real qubits.

The experiment: prepare the reference-entangled [[5,1,3]] tile state, then
transport the code around a closed loop in rulebook-space — a transversal
Clifford K applied to all five code qubits, where K cycles X -> Y -> Z.
K^x5 maps the stabilizer group exactly to itself (verified in-script), so
the code comes home; the logical frame does not. Prediction (exact, from
Capstone VI): the 3x3 frame of correlators F_ab = <sigma_a^R Pauli-avatar_b>
returns rotated by 120 degrees — the holonomy, visible as the diagonal
pattern of F migrating onto a cyclic off-diagonal.

Hardware cost is almost insultingly small: the loop itself is ONE layer of
single-qubit gates (~0.02% error each) on top of the tile preparation we
have flown twice. The permutation part of the automorphism group would be
free entirely (software relabeling); this loop needs none.
"""

import pathlib
import sys
from functools import reduce

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from happy_hardware import build_prep_circuit  # noqa: E402
from happy_tile import build_codewords  # noqa: E402

from qiskit.circuit.library import UnitaryGate  # noqa: E402
from qiskit.quantum_info import SparsePauliOp, Statevector  # noqa: E402
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager  # noqa: E402
from qiskit_ibm_runtime import EstimatorV2, QiskitRuntimeService  # noqa: E402

PAULI = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}

# ─── Pauli-string algebra for avatar search ──────────────────────────────────
MUL = {("I", p): (1, p) for p in "IXYZ"}
MUL.update({(p, "I"): (1, p) for p in "XYZ"})
MUL.update({(p, p): (1, "I") for p in "XYZ"})
MUL.update({("X", "Y"): (1j, "Z"), ("Y", "X"): (-1j, "Z"),
            ("Y", "Z"): (1j, "X"), ("Z", "Y"): (-1j, "X"),
            ("Z", "X"): (1j, "Y"), ("X", "Z"): (-1j, "Y")})


def pmul(a, b):
    phase, chars = a[0] * b[0], []
    for x, y in zip(a[1], b[1]):
        ph, c = MUL[(x, y)]
        phase *= ph
        chars.append(c)
    return phase, "".join(chars)


STABS = [(1, s) for s in ("XZZXI", "IXZZX", "XIXZZ", "ZXIXZ")]
GROUP = [(1, "IIIII")]
for g in STABS:
    GROUP += [pmul(g, h) for h in GROUP]


def min_weight_logical(L):
    cands = [pmul(L, g) for g in GROUP]
    best = min(cands, key=lambda p: (sum(c != "I" for c in p[1]), p[1]))
    assert best[0] in (1, -1)
    return best


X_T = min_weight_logical((1, "XXXXX"))
Z_T = min_weight_logical((1, "ZZZZZ"))
Y_T = min_weight_logical(pmul((1j, "XXXXX"), (1, "ZZZZZ")))
AVATARS = {"X": X_T, "Y": Y_T, "Z": Z_T}


def observable(r_char, avatar):
    """SparsePauliOp on 6 qubits: sigma_r on R (qubit 0) x avatar on code."""
    sign, string = avatar
    chars = ["I"] * 6
    chars[0] = r_char
    for k, c in enumerate(string):
        chars[1 + k] = c
    return SparsePauliOp("".join(reversed(chars)), coeffs=[sign])


# ─── the loop gate K: X -> Y -> Z -> X ───────────────────────────────────────

def find_K():
    Hm = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    Sm = np.diag([1, 1j]).astype(complex)
    seen, frontier = {}, [np.eye(2, dtype=complex)]
    while frontier:
        m = frontier.pop()
        key = tuple(np.round(m / (m.flat[np.argmax(np.abs(m) > 1e-9)]
                                  / abs(m.flat[np.argmax(np.abs(m) > 1e-9)])), 8).ravel())
        if key in seen:
            continue
        seen[key] = m
        frontier += [g @ m for g in (Hm, Sm)]
    for m in seen.values():
        if (np.allclose(m @ PAULI["X"] @ m.conj().T, PAULI["Y"])
                and np.allclose(m @ PAULI["Z"] @ m.conj().T, PAULI["X"])):
            return m
    raise RuntimeError("K not found")


def op(chars):
    return reduce(np.kron, [PAULI[c] for c in chars])


def main() -> None:
    K = find_K()
    # verify the loop closes: K^x5 maps every stabilizer into the group
    K5 = reduce(np.kron, [K] * 5)
    gens = [op(s) for _, s in STABS]
    group_m = [op(s) * ph for ph, s in GROUP]
    for g in gens:
        img = K5 @ g @ K5.conj().T
        assert any(np.allclose(img, h) for h in group_m), "loop does not close"
    print("Loop verified: K^x5 maps the stabilizer group to itself "
          "(closed path in rulebook-space).")
    print(f"Avatars: X~ = {X_T}, Y~ = {Y_T}, Z~ = {Z_T}\n")

    qc0 = build_prep_circuit()
    qc1 = qc0.copy()
    for q in range(1, 6):
        qc1.append(UnitaryGate(K, label="K"), [q])

    # exact predictions for both frames
    frames_pred = {}
    for tag, qc in (("before", qc0), ("after", qc1)):
        sv = Statevector(qc)
        F = np.zeros((3, 3))
        for a, ra in enumerate("XYZ"):
            for b, ab in enumerate("XYZ"):
                F[a, b] = np.real(sv.expectation_value(
                    observable(ra, AVATARS[ab])))
        frames_pred[tag] = np.round(F, 6)
        print(f"predicted frame ({tag}):\n{frames_pred[tag]}")
    print("\nThe holonomy: the 'before' diagonal pattern migrates one column")
    print("cyclically — X-correlation moves to the Y avatar, etc.\n")

    service = QiskitRuntimeService()
    usage = service.usage()
    print(f"Quota: {usage['usage_remaining_seconds']}s remaining of "
          f"{usage['usage_limit_seconds']}s")
    backend = service.backend("ibm_kingston")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=2)
    isa0, isa1 = pm.run(qc0), pm.run(qc1)
    print(f"Transpiled 2q gates: before={sum(1 for g in isa0.data if len(g.qubits) == 2)}, "
          f"after={sum(1 for g in isa1.data if len(g.qubits) == 2)}")

    obs = [(ra, ab) for ra in "XYZ" for ab in "XYZ"]
    estimator = EstimatorV2(mode=backend)
    o = estimator.options
    o.default_shots = 10_000
    o.resilience_level = 2
    o.resilience.zne.noise_factors = (1, 3, 5)
    o.resilience.zne.extrapolator = "exponential"
    o.twirling.enable_gates = True
    o.twirling.enable_measure = True
    o.dynamical_decoupling.enable = True
    o.dynamical_decoupling.sequence_type = "XY4"
    pubs = []
    for isa in (isa0, isa1):
        ops = [observable(ra, AVATARS[ab]).apply_layout(isa.layout)
               for ra, ab in obs]
        pubs.append((isa, ops))
    job = estimator.run(pubs)
    print(f"Job {job.job_id()} submitted, waiting for the fridge...")
    result = job.result()

    for tag, res in zip(("before", "after"), result):
        F = np.array(res.data.evs, dtype=float).reshape(3, 3)
        print(f"\nmeasured frame ({tag}):\n{np.round(F, 3)}")
        print(f"predicted:\n{frames_pred[tag]}")
        overlap = float(np.sum(F * frames_pred[tag]) / 3)
        wrong = frames_pred["before" if tag == "after" else "after"]
        overlap_wrong = float(np.sum(F * wrong) / 3)
        print(f"   match with prediction: {overlap:+.3f}   "
              f"match with the other frame: {overlap_wrong:+.3f}")

    print("\nIf the 'after' frame matches its rotated prediction and not the")
    print("unrotated one, the holonomy — the twist acquired by a closed loop")
    print("through rulebook-space — has been measured on physical qubits.")


if __name__ == "__main__":
    main()
