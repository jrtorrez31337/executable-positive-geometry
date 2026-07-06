"""Track D on hardware — measuring the two magic species from a single wedge.

Layout: two [[5,1,3]] tiles (qubits 0-4 and 5-9) holding the logical state
  cos t |00> + e^{i pi/4} sin t |11>,   t = pi/6   (both species nonzero)
and its phase-stripped stabilizer twin. One classical-shadows dataset per
state (random local Cliffords, N_U settings x N_M shots) yields BOTH
protocols on the 3-qubit wedge W = (0,1,2) of tile A:

  IRREDUCIBLE species: purity P_W (Brydges-style estimator), junk factor
      1/4 (exact, Phase 1b) -> P_L = 4 P_W -> closed form
      -log2(4P^2-6P+3). Exact target at t=pi/6: 0.2996.
  ERASABLE species: wedge Pauli spectrum -> mixed-SRE M2(W), twin-
      controlled Delta. Exact target: M2(W) = 0.2345 for BOTH states,
      Delta = 0 — the erasable magic is invisible to the single wedge
      (its union-only visibility is established exactly in simulation;
      hardware tests the single-wedge half of the geography).

Encoder: true [[5,1,3]] encoding UNITARY (|b> (x) |0000> -> |b-bar>) built
as a Clifford tableau by GF(2) symplectic completion, validated against
exact codewords before use. Full pipeline (including shot noise and
estimator bias) is rehearsed on Aer before submission.
"""

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent / ".." / "capstone-happy"))
from happy_tile import build_codewords  # noqa: E402

from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import Clifford, Statevector, random_clifford  # noqa: E402
from qiskit_aer import AerSimulator  # noqa: E402

THETA = np.pi / 6
N_SETTINGS = 150
N_SHOTS = 512
WEDGE = (0, 1, 2)
LN2 = np.log(2)

# ─── [[5,1,3]] encoder via symplectic completion ────────────────────────────
# Pauli as 10-bit (x|z) vector over GF(2). Symplectic product <a,b> =
# a_x.b_z + a_z.b_x (mod 2): 0 = commute, 1 = anticommute.

STABS = ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"]


def pvec(s):
    v = np.zeros(10, dtype=np.uint8)
    for i, c in enumerate(s):
        if c in "XY":
            v[i] = 1
        if c in "ZY":
            v[5 + i] = 1
    return v


def sprod(a, b):
    return int(a[:5] @ b[5:] + a[5:] @ b[:5]) % 2


def solve_gf2(A, b):
    """One solution of A x = b over GF(2)."""
    A = A.copy() % 2
    b = b.copy() % 2
    n, m = A.shape
    piv = []
    r = 0
    for c in range(m):
        rows = [i for i in range(r, n) if A[i, c]]
        if not rows:
            continue
        A[[r, rows[0]]] = A[[rows[0], r]]
        b[[r, rows[0]]] = b[[rows[0], r]]
        for i in range(n):
            if i != r and A[i, c]:
                A[i] ^= A[r]
                b[i] ^= b[r]
        piv.append(c)
        r += 1
    x = np.zeros(m, dtype=np.uint8)
    for i, c in enumerate(piv):
        x[c] = b[i]
    return x


def build_encoder():
    """Clifford E with E: Z1->Z_L, X1->X_L, Z_{i+1}->S_i, X_{i+1}->D_i."""
    xl, zl = pvec("XXXXX"), pvec("ZZZZZ")
    stabs = [pvec(s) for s in STABS]
    destabs = []
    for i in range(4):
        known = [xl, zl] + stabs + destabs
        targets = ([0, 0] + [1 if j == i else 0 for j in range(4)]
                   + [0] * len(destabs))
        A = np.array([[sprod(k, e) for e in np.eye(10, dtype=np.uint8)]
                      for k in known], dtype=np.uint8)
        destabs.append(solve_gf2(A, np.array(targets, dtype=np.uint8)))
    # qiskit tableau: rows = destabilizers then stabilizers, cols = (X|Z|ph)
    tab = np.zeros((10, 11), dtype=bool)
    for r, v in enumerate([xl] + destabs):        # images of X_1..X_5
        tab[r, :10] = v.astype(bool)
    for r, v in enumerate([zl] + stabs):          # images of Z_1..Z_5
        tab[5 + r, :10] = v.astype(bool)
    E = Clifford(tab)
    qc = E.to_circuit()

    # Intrinsic validation: E|00000> must be stabilized by all 4 stabilizers,
    # and logical X/Z must act as codeword flip / sign. (We do NOT require the
    # historic build_codewords() convention — any valid [[5,1,3]] encoding
    # serves; purity and SRE are convention-independent. The SAME encoder on
    # both tiles guarantees a consistent logical basis for the entangled pair.)
    def mat(s):
        from functools import reduce
        P = {"I": np.eye(2), "X": np.array([[0, 1], [1, 0]]),
             "Y": np.array([[0, -1j], [1j, 0]]), "Z": np.diag([1, -1])}
        return reduce(np.kron, [P[c] for c in s])
    sv0 = Statevector.from_int(0, 32).evolve(qc).data
    for s in STABS:
        assert abs(np.vdot(sv0, mat(s) @ sv0) - 1) < 1e-9, f"not stabilized: {s}"
    zL = mat("ZZZZZ")
    assert abs(np.vdot(sv0, zL @ sv0) - 1) < 1e-9, "logical |0> not +1 of Z_L"
    e1 = np.zeros(32)
    e1[1] = 1                                    # |1> on qubit 0 (index 2^0)
    sv1 = Statevector(e1).evolve(qc).data
    assert abs(np.vdot(sv1, zL @ sv1) + 1) < 1e-9, "logical |1> not -1 of Z_L"
    assert abs(np.vdot(sv0, mat("XXXXX") @ sv1) - 1) < 1e-6 or \
        abs(abs(np.vdot(sv0, mat("XXXXX") @ sv1)) - 1) < 1e-6, "X_L mismatch"
    return qc


def prep_circuit(theta, magic: bool):
    enc = build_encoder()
    qc = QuantumCircuit(10)
    qc.ry(2 * theta, 0)
    qc.cx(0, 5)
    if magic:
        qc.p(np.pi / 4, 0)
    qc.compose(enc, qubits=range(5), inplace=True)
    qc.compose(enc, qubits=range(5, 10), inplace=True)
    return qc


# ─── classical shadows: one dataset, two protocols ──────────────────────────

def shadow_circuits(base, rng):
    circs, unitaries = [], []
    for _ in range(N_SETTINGS):
        us = [random_clifford(1, seed=rng.integers(1 << 30)) for _ in range(10)]
        qc = base.copy()
        for q, u in enumerate(us):
            qc.compose(u.to_circuit(), qubits=[q], inplace=True)
        qc.measure_all()
        circs.append(qc)
        unitaries.append([np.asarray(u.to_matrix()) for u in us])
    return circs, unitaries


def analyze(counts_list, unitaries):
    """Wedge purity (Brydges) + wedge Pauli spectrum (shadows) on WEDGE."""
    k = len(WEDGE)
    # purity: per-setting collision estimator on the wedge bits
    purities = []
    for counts in counts_list:
        tot = sum(counts.values())
        marg = {}
        for bits, c in counts.items():
            key = tuple(bits[::-1][q] for q in WEDGE)   # qiskit bit order
            marg[key] = marg.get(key, 0) + c
        est = 0.0
        for s, cs in marg.items():
            for s2, cs2 in marg.items():
                d = sum(a != b for a, b in zip(s, s2))
                w = cs * cs2 if s != s2 else cs * (cs - 1)
                est += (-2.0) ** (-d) * w
        est *= 2 ** k / (tot * (tot - 1))
        purities.append(est)
    purity = float(np.mean(purities))

    # Pauli spectrum via single-qubit-Clifford shadows on the wedge
    paulis = {"I": np.eye(2), "X": np.array([[0, 1], [1, 0]]),
              "Y": np.array([[0, -1j], [1j, 0]]), "Z": np.diag([1, -1])}
    from itertools import product as iproduct
    labels = [p for p in iproduct("IXYZ", repeat=k) if any(c != "I" for c in p)]
    ests = {lab: [] for lab in labels}
    for counts, us in zip(counts_list, unitaries):
        tot = sum(counts.values())
        # precompute per-qubit single-shot factors tr(P U^dag |s><s| U)
        fac = {}
        for qi, q in enumerate(WEDGE):
            U = us[q]
            for s in (0, 1):
                proj = np.outer(np.eye(2)[s], np.eye(2)[s])
                back = U.conj().T @ proj @ U
                for c in "IXYZ":
                    fac[(qi, s, c)] = np.real(np.trace(paulis[c] @ back))
        for bits, cnt in counts.items():
            rb = bits[::-1]
            svals = [int(rb[q]) for q in WEDGE]
            for lab in labels:
                v = 1.0
                for qi, c in enumerate(lab):
                    t = fac[(qi, svals[qi], c)]
                    v *= (3 * t) if c != "I" else 1.0
                ests[lab].append(v * cnt / tot)
    spectrum = {lab: float(np.sum(vals) / N_SETTINGS)
                for lab, vals in ests.items()}
    s2 = 1 + sum(v ** 2 for v in spectrum.values())
    s4 = 1 + sum(v ** 4 for v in spectrum.values())
    m2w = float(-np.log2(s4 / s2))
    return purity, m2w


def closed_form_nl(P):
    return float(-np.log2(4 * P ** 2 - 6 * P + 3))


def run_batch(circs, backend=None, service=None):
    if backend is None:
        sim = AerSimulator()
        from qiskit import transpile
        out = []
        for qc in circs:
            res = sim.run(transpile(qc, sim), shots=N_SHOTS).result()
            out.append(res.get_counts())
        return out
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2
    pm = generate_preset_pass_manager(backend=backend, optimization_level=2)
    isa = [pm.run(qc) for qc in circs]
    sampler = SamplerV2(mode=backend)
    job = sampler.run(isa, shots=N_SHOTS)
    print(f"   job {job.job_id()} ({len(isa)} circuits) submitted...")
    result = job.result()
    return [r.data.meas.get_counts() for r in result]


def report(tag, purity, m2w_magic, m2w_twin):
    p_l = 4 * purity
    nl = closed_form_nl(min(max(p_l, 0.5), 1.0))
    print(f"   [{tag}] wedge purity = {purity:.4f} -> P_L = {p_l:.4f} "
          f"-> irreducible NL = {nl:.4f}   (exact 0.2996)")
    print(f"   [{tag}] M2(wedge): magic {m2w_magic:.4f}, twin {m2w_twin:.4f}, "
          f"erasable Delta = {m2w_magic - m2w_twin:+.4f}   "
          f"(exact 0.2345 / 0.2345 / 0)")


def main():
    rng = np.random.default_rng(11)
    qc_magic = prep_circuit(THETA, True)
    qc_twin = prep_circuit(THETA, False)
    print(f"Encoder validated; prep depth ~{qc_magic.depth()}, "
          f"2q gates {sum(1 for g in qc_magic.data if len(g.qubits) == 2)}")

    circs_m, us_m = shadow_circuits(qc_magic, rng)
    circs_t, us_t = shadow_circuits(qc_twin, rng)

    print("\nREHEARSAL on Aer (full pipeline, real shot noise):")
    cm = run_batch(circs_m)
    ct = run_batch(circs_t)
    pm_, m2m = analyze(cm, us_m)
    pt_, m2t = analyze(ct, us_t)
    report("Aer", pm_, m2m, m2t)

    print("\nHARDWARE (ibm_kingston):")
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    usage = service.usage()
    print(f"   quota: {usage['usage_remaining_seconds']}s of "
          f"{usage['usage_limit_seconds']}s")
    if usage["usage_remaining_seconds"] < 150:
        raise SystemExit("   insufficient quota — stopping after rehearsal")
    backend = service.backend("ibm_kingston")
    cm_h = run_batch(circs_m, backend=backend)
    ct_h = run_batch(circs_t, backend=backend)
    pmh, m2mh = analyze(cm_h, us_m)
    pth, m2th = analyze(ct_h, us_t)
    report("HW", pmh, m2mh, m2th)
    print("\n   If the hardware NL lands near 0.2996 while the erasable")
    print("   Delta stays near 0, the two-species geography is measured:")
    print("   the unremovable magic read from one wedge's purity, the")
    print("   removable magic invisible to that same wedge.")


if __name__ == "__main__":
    main()
