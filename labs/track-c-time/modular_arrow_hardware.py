"""Track C on hardware — the modular-clock line (Track a, Jon: "run it").

Extends arrow_hardware.py from two families to THREE, putting S4's clock-vs-arrow
split on real qubits (1 system + 3 records, full 1-qubit tomography per tick):

  ARROW   : each tick write a record (CRX S->record). System-alone entropy
            climbs monotonically -> the manufactured arrow. (P-B)
  MODULAR : write records for the first SWITCH ticks (entropy climbs), then apply
            the SYSTEM's own modular flow e^{i K_S theta}, K_S=-log rho_S — a
            rotation about rho_S's Bloch axis that leaves rho_S (and its entropy)
            invariant. Entropy plateaus FLAT: a reversible clock riding the mixed
            state. (S4 Part 1 stationarity, device-ready.)
  CONTROL : recordless precession. Entropy ~ 0 -> the noise floor.

U_mod is computed classically from the exact rho_S at the switch and compiled as
a fixed 1-qubit gate. Predictions are exact statevectors (arrow_hardware.py
convention). Quota-gated; the job_id is persisted the instant it is submitted so
the result is retrievable even if this process dies in the (queued) wait.

Usage:
  python modular_arrow_hardware.py            # submit + wait + report
  python modular_arrow_hardware.py <job_id>   # retrieve a persisted job
"""

import json
import sys
from pathlib import Path

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector, partial_trace
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2, QiskitRuntimeService

TICKS = 8
N_ENV = 3
SWITCH = 4
LN2 = np.log(2)
SHOTS = 4000
BACKEND = "ibm_kingston"
QUOTA_FLOOR = 110          # abort if remaining seconds < this
RUNDIR = Path(__file__).resolve().parent / "modular_arrow_runs"


def modular_unitary(rho_s, theta):
    """e^{i K_S theta}, K_S = -log rho_S: rotation about rho_S's own Bloch axis,
    leaves rho_S invariant (single-qubit modular flow of the reduced state)."""
    w, V = np.linalg.eigh(rho_s)
    w = np.clip(w, 1e-12, None)
    K = (V * (-np.log(w))) @ V.conj().T
    wk, Vk = np.linalg.eigh(K)
    return (Vk * np.exp(1j * wk * theta)) @ Vk.conj().T


def circuit(t, family, U_mod=None):
    qc = QuantumCircuit(1 + N_ENV)
    qc.h(0)                                   # system starts in |+>
    for k in range(t):
        qc.rz(np.pi / 2, 0)
        if family == "arrow":
            qc.crx(np.pi / 4, 0, 1 + (k % N_ENV))
        elif family == "modular":
            if k < SWITCH:
                qc.crx(np.pi / 4, 0, 1 + (k % N_ENV))
            else:
                qc.unitary(U_mod, [0], label="Umod")
        # control: precession only
    return qc


def system_rho(qc):
    sv = Statevector(qc)
    return np.array(partial_trace(sv, list(range(1, 1 + N_ENV))).data)


def bloch_entropy(r):
    r = min(max(float(r), 0.0), 1.0)
    p = (1 + r) / 2
    if p <= 0 or p >= 1:
        return 0.0
    return float(-(p * np.log(p) + (1 - p) * np.log(1 - p)) / LN2)


def u_mod_from_switch():
    rho_s = system_rho(circuit(SWITCH, "arrow"))   # modular == arrow up to SWITCH
    return modular_unitary(rho_s, np.pi / 2)


def exact_predictions(U_mod):
    pred = {}
    for fam in ("arrow", "modular", "control"):
        ent = []
        for t in range(TICKS):
            rho = system_rho(circuit(t, fam, U_mod))
            r = np.linalg.norm([np.real(np.trace(rho @ P))
                                for P in (np.array([[0, 1], [1, 0]]),
                                          np.array([[0, -1j], [1j, 0]]),
                                          np.array([[1, 0], [0, -1]]))])
            ent.append(bloch_entropy(r))
        pred[fam] = ent
    return pred


def observables():
    return [SparsePauliOp("I" * N_ENV + p) for p in ("X", "Y", "Z")]


def build_index():
    return [(fam, t) for fam in ("arrow", "modular", "control")
            for t in range(TICKS)]


def report(pred, measured):
    print(f"\nResults from {BACKEND} — system-qubit entropy S/ln2:")
    print(f"   {'tick':>4} | {'arrowP':>7}{'arrowM':>7} | "
          f"{'modP':>7}{'modM':>7} | {'ctrlP':>7}{'ctrlM':>7}")
    for t in range(TICKS):
        print(f"   {t:>4} | {pred['arrow'][t]:>7.3f}{measured['arrow'][t]:>7.3f} | "
              f"{pred['modular'][t]:>7.3f}{measured['modular'][t]:>7.3f} | "
              f"{pred['control'][t]:>7.3f}{measured['control'][t]:>7.3f}")
    a = measured["arrow"]
    m = measured["modular"]
    a_mono = sum(1 for i in range(TICKS - 1) if a[i + 1] >= a[i] - 0.02)
    m_flat = max(abs(m[t] - m[SWITCH]) for t in range(SWITCH, TICKS))
    print(f"\n   ARROW monotone steps          : {a_mono}/{TICKS - 1}")
    print(f"   MODULAR flatness after switch : max drift {m_flat:.3f} bits")
    print(f"   CONTROL max entropy           : {max(measured['control']):.3f} bits")
    print("   The modular clock holds entropy flat where the arrow keeps climbing.")


def retrieve(job_id, service):
    meta = json.loads((RUNDIR / f"{job_id}.json").read_text())
    pred = meta["pred"]
    index = [tuple(x) for x in meta["index"]]
    result = service.job(job_id).result()
    measured = {f: [None] * TICKS for f in ("arrow", "modular", "control")}
    for (fam, t), res in zip(index, result):
        r = np.linalg.norm(np.array(res.data.evs, dtype=float))
        measured[fam][t] = bloch_entropy(r)
    report(pred, measured)
    (RUNDIR / f"{job_id}_measured.json").write_text(json.dumps(measured, indent=2))


def main():
    service = QiskitRuntimeService()
    if len(sys.argv) > 1:                          # retrieve mode
        retrieve(sys.argv[1], service)
        return

    U_mod = u_mod_from_switch()
    pred = exact_predictions(U_mod)
    print("Predictions (exact statevector):")
    for fam in ("arrow", "modular", "control"):
        print(f"   {fam:>7} S/ln2: {[f'{e:.2f}' for e in pred[fam]]}")

    usage = service.usage()
    rem = usage["usage_remaining_seconds"]
    print(f"\nQuota: {rem}s remaining of {usage['usage_limit_seconds']}s")
    if rem < QUOTA_FLOOR:
        raise SystemExit(f"insufficient quota ({rem}s < {QUOTA_FLOOR}s) — aborting")

    backend = service.backend(BACKEND)
    pm = generate_preset_pass_manager(backend=backend, optimization_level=2)
    index = build_index()
    pubs = []
    for fam, t in index:
        isa = pm.run(circuit(t, fam, U_mod))
        ops = [o.apply_layout(isa.layout) for o in observables()]
        pubs.append((isa, ops))

    estimator = EstimatorV2(mode=backend)
    o = estimator.options
    o.default_shots = SHOTS
    o.resilience_level = 1                          # readout mitigation
    o.twirling.enable_measure = True
    o.dynamical_decoupling.enable = True
    o.dynamical_decoupling.sequence_type = "XY4"
    job = estimator.run(pubs)
    job_id = job.job_id()

    RUNDIR.mkdir(exist_ok=True)
    (RUNDIR / f"{job_id}.json").write_text(json.dumps(
        {"job_id": job_id, "backend": BACKEND, "shots": SHOTS,
         "ticks": TICKS, "switch": SWITCH, "pred": pred, "index": index},
        indent=2))
    print(f"\nJob {job_id} submitted ({len(pubs)} circuits); job_id persisted to")
    print(f"  {RUNDIR / (job_id + '.json')}")
    print("Waiting for result (queued; retrievable later with the job_id)...")

    result = job.result()
    measured = {f: [None] * TICKS for f in ("arrow", "modular", "control")}
    for (fam, t), res in zip(index, result):
        r = np.linalg.norm(np.array(res.data.evs, dtype=float))
        measured[fam][t] = bloch_entropy(r)
    report(pred, measured)
    (RUNDIR / f"{job_id}_measured.json").write_text(json.dumps(measured, indent=2))


if __name__ == "__main__":
    main()
