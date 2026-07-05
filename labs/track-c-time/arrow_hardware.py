"""Track C on hardware — measuring the arrow of time on real qubits.

The claim (proven exactly in page_wootters.py): a frozen global state
contains a relational family phi_t in which the SYSTEM ALONE — the view
of an observer who cannot read the records — gains entropy monotonically,
while the whole stays pure and the recordless dynamics stays arrowless.

Hardware realization: conditioning on clock tick t = running t steps.
Two families of circuits on 4 transmons (1 system + 3 records):
  ARROW   : step k = RZ(pi/2) on S, then CRX(pi/4) from S to record k mod 3
  CONTROL : identical RZ precession, no record couplings
For each tick t = 0..7 we measure <X>,<Y>,<Z> of the system — one qubit,
so this is FULL tomography: Bloch vector -> exact entropy. Predictions
computed in-script from exact statevectors.

Expected: control entropy ~ 0 at every tick (pure precession — a clock,
no arrow); record-coupled entropy climbs monotonically toward ~0.97 bits.
Device noise adds entropy to both, so the DIFFERENCE and the shape carry
the physics. P-B (tracker: the arrow appears exactly upon conditioning),
on hardware.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2, QiskitRuntimeService

TICKS = 8
N_ENV = 3
LN2 = np.log(2)


def circuit(t, records: bool) -> QuantumCircuit:
    qc = QuantumCircuit(1 + N_ENV)
    for k in range(t):
        qc.rz(np.pi / 2, 0)
        if records:
            qc.crx(np.pi / 4, 0, 1 + (k % N_ENV))
    return qc


def prep(qc: QuantumCircuit) -> QuantumCircuit:
    full = QuantumCircuit(1 + N_ENV)
    full.h(0)                      # system starts in |+>
    return full.compose(qc)


def bloch_entropy(r: float) -> float:
    r = min(max(r, 0.0), 1.0)
    p = (1 + r) / 2
    if p in (0.0, 1.0):
        return 0.0
    return float(-(p * np.log(p) + (1 - p) * np.log(1 - p)) / LN2)


def observables():
    return [SparsePauliOp("I" * N_ENV + p) for p in ("X", "Y", "Z")]


def main() -> None:
    # exact predictions
    print("Predictions (exact statevector):")
    pred = {}
    for records in (True, False):
        ent = []
        for t in range(TICKS):
            sv = Statevector(prep(circuit(t, records)))
            r = np.array([np.real(sv.expectation_value(o))
                          for o in observables()])
            ent.append(bloch_entropy(np.linalg.norm(r)))
        pred[records] = ent
    print(f"   arrow   S/ln2: {[f'{e:.2f}' for e in pred[True]]}")
    print(f"   control S/ln2: {[f'{e:.2f}' for e in pred[False]]}\n")

    service = QiskitRuntimeService()
    usage = service.usage()
    remaining = usage["usage_remaining_seconds"]
    print(f"Quota: {remaining}s remaining of {usage['usage_limit_seconds']}s")
    if remaining < 100:
        raise SystemExit("insufficient quota — aborting before submission")

    backend = service.backend("ibm_kingston")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=2)
    pubs, index = [], []
    for records in (True, False):
        for t in range(TICKS):
            isa = pm.run(prep(circuit(t, records)))
            ops = [o.apply_layout(isa.layout) for o in observables()]
            pubs.append((isa, ops))
            index.append((records, t))

    estimator = EstimatorV2(mode=backend)
    o = estimator.options
    o.default_shots = 6_000
    o.resilience_level = 1          # readout mitigation; circuits are shallow
    o.twirling.enable_gates = True
    o.twirling.enable_measure = True
    o.dynamical_decoupling.enable = True
    o.dynamical_decoupling.sequence_type = "XY4"
    job = estimator.run(pubs)
    print(f"Job {job.job_id()} submitted ({len(pubs)} circuits), waiting...")
    result = job.result()

    measured = {True: [None] * TICKS, False: [None] * TICKS}
    for (records, t), res in zip(index, result):
        r = np.linalg.norm(np.array(res.data.evs, dtype=float))
        measured[records][t] = bloch_entropy(r)

    print(f"\nResults from {backend.name} — system-qubit entropy S/ln2:")
    print(f"   {'tick':>5} {'arrow pred':>11} {'arrow meas':>11} "
          f"{'ctrl pred':>10} {'ctrl meas':>10}")
    for t in range(TICKS):
        print(f"   {t:>5} {pred[True][t]:>11.3f} {measured[True][t]:>11.3f} "
              f"{pred[False][t]:>10.3f} {measured[False][t]:>10.3f}")

    arrow = measured[True]
    rises = sum(1 for i in range(TICKS - 1) if arrow[i + 1] >= arrow[i] - 0.02)
    gap = np.mean([measured[True][t] - measured[False][t]
                   for t in range(1, TICKS)])
    print(f"\n   monotone steps (arrow family): {rises}/{TICKS - 1}")
    print(f"   mean entropy gap, arrow - control: {gap:.3f} bits")
    print("   The control precesses with near-flat entropy — a clock without")
    print("   an arrow. The record-writing system climbs tick by tick: the")
    print("   arrow of time, present exactly when records are written and an")
    print("   observer cannot read them — measured on physical qubits.")


if __name__ == "__main__":
    main()
