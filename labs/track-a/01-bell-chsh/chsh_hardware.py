"""Milestone 1, hardware edition — CHSH on a real IBM quantum processor.

Same experiment as chsh.py, but the Bell pairs live on physical
superconducting transmons in a dilution refrigerator. Expect S ~ 2.6-2.75
rather than the simulator's 2.83: decoherence, gate errors, and readout
errors all chew on the correlations. The gap between the two numbers is
the entire reason Milestone 2 (error correction) exists.

Prerequisite (one-time): save your IBM Quantum API key —
  QiskitRuntimeService.save_account(token="...", set_as_default=True)
"""

from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

from chsh import ANGLES, SHOTS, chsh_S, correlation, make_chsh_circuit

import math


def main() -> None:
    service = QiskitRuntimeService()
    backend = service.least_busy(operational=True, simulator=False)
    print(f"Backend: {backend.name} ({backend.num_qubits} qubits), "
          f"queue depth {backend.status().pending_jobs}")

    # Compile the 4 setting-pairs down to this chip's native gates and layout.
    pm = generate_preset_pass_manager(backend=backend, optimization_level=2)
    keys, circuits = [], []
    for alice in ("a", "a'"):
        for bob in ("b", "b'"):
            keys.append(f"{alice},{bob}")
            circuits.append(pm.run(make_chsh_circuit(ANGLES[alice], ANGLES[bob])))

    sampler = Sampler(mode=backend)
    job = sampler.run(circuits, shots=SHOTS)
    print(f"Job {job.job_id()} submitted, waiting for the fridge...")
    results = job.result()

    E: dict[str, float] = {}
    for key, res in zip(keys, results):
        counts = res.data.c.get_counts()
        E[key] = correlation(counts)
        theory = math.cos(ANGLES[key.split(",")[0]] - ANGLES[key.split(",")[1]])
        print(f"E({key:5s}) = {E[key]:+.4f}   (ideal {theory:+.4f})")

    S = chsh_S(E)
    print(f"\nCHSH S = {S:.4f}  on {backend.name}")
    print(f"  classical bound : 2.0000")
    print(f"  Tsirelson bound : {2 * math.sqrt(2):.4f}")
    print(f"  simulator run   : ~2.83")
    if S > 2:
        print("  => Bell inequality violated on real hardware.")
    else:
        print("  => S <= 2: noise ate the violation — try a different backend.")


if __name__ == "__main__":
    main()
