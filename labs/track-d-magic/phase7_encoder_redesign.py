"""Project 2, W2 — shallower-encoder redesign candidates (pre-registered).

Per notes/PROJECT-2-MAGIC-WEDGE.md (all-signed 2026-07-27): the current 2-tile
encoder is noise-dominated on Heron-class devices; Tier-2 hardware requires a
redesigned circuit that clears the registered lower-bound gate
NL(rehearsal) - 2*sigma_total > 0.10 (sigma_total = sigma_shot + SEM_rehearsal,
additive). This lab produces CANDIDATES + their P2-A validation and routing
metrics; the gate verdict itself belongs to Tobin's phase7_rehearsal_manifest.

P2-A (hard constraint): every candidate must reproduce the exact noiseless
target — same code, same state, wedge purity P_wedge = 0.15625, logical purity
P_L = 0.625, NL = 0.29956 at the registered test point — or it is discarded.

Candidates:
  C0 baseline: species_hardware.prep_circuit (qiskit default Clifford synth).
  C1 greedy:   per-tile encoder resynthesized with synth_clifford_greedy.
  C2 ag:       synth_clifford_ag (Aaronson-Gottesman reference).
  C3 layers:   synth_clifford_layers (structured-layer synthesis).
Each candidate is then transpiled to a heavy-hex Heron target (FakeTorino)
at optimization_level 3 over several SABRE seeds; we report the best routed
2q-count/depth per candidate. Rehearsal + gate: Tobin's manifest.
"""

# RESULTS (quant-phy, 2026-07-27, FakeTorino heavy-hex, opt3 x 5 SABRE seeds):
#   C0 baseline  PASS  prep 27 2q -> routed 54, depth 74
#   C1 greedy    PASS  prep 27 2q -> routed 53, depth 69   <- best, marginal
#   C2 ag        PASS  prep 31 2q -> routed 54, depth 71
#   C3 layers    PASS  prep 51 2q -> routed 78, depth 80
# HONEST READING: standard Clifford-resynthesis gains are MARGINAL (54->53
# routed 2q). This avenue alone will not close the ~x5 noise gap the registered
# gate requires (point estimate ~0.19 vs rehearsed ~0.01-0.09 at depth ~54).
# Unless Tobin's manifest rehearsal of C1 surprises, the flagship is headed to
# the registered honest-null (quantified noise bound) -- which the W1 note
# already frames. Two facts for the record: (1) DEBUGGING NOTE -- my first
# validator run failed ALL candidates incl. baseline; root cause was MY wrong
# wedge choice (4q guess vs the registered 3q protocol wedge), found by subset
# probe, not a circuit defect. (2) DISCOVERY -- perfect-tensor symmetry means
# ANY 3-of-5 subset of a tile reads the same wedge purity (80 equivalent
# subsets), so the submit step may freely pick the 3 best-calibrated physical
# qubits at run time: a real (if modest) error-rate optimization.

import sys
import pathlib

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Clifford, Statevector, partial_trace
from qiskit.synthesis import (synth_clifford_greedy, synth_clifford_ag,
                              synth_clifford_layers)

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from species_hardware import build_encoder, closed_form_nl  # noqa: E402

THETA = np.pi / 6            # registered test point
SEEDS = (7, 17, 27, 47, 97)
WEDGE = [0, 1, 2]            # the registered 3q protocol wedge (species_hardware WEDGE);
# perfect-tensor symmetry: ANY 3-of-5 subset of a tile reads the same purity


def prep_with_encoder(enc: QuantumCircuit) -> QuantumCircuit:
    qc = QuantumCircuit(10)
    qc.ry(2 * THETA, 0)
    qc.cx(0, 5)
    qc.p(np.pi / 4, 0)
    qc.compose(enc, qubits=range(5), inplace=True)
    qc.compose(enc, qubits=range(5, 10), inplace=True)
    return qc


def validate_p2a(qc: QuantumCircuit) -> tuple[bool, float, float]:
    """Exact statevector check of the registered targets."""
    sv = Statevector(qc)
    rho_w = partial_trace(sv, [q for q in range(10) if q not in WEDGE])
    p_wedge = float(np.real(np.trace(np.asarray(rho_w.data) @
                                     np.asarray(rho_w.data))))
    p_logical = p_wedge / 0.25            # calibrated junk factor: c_W = 0.25
    # for the 3q wedge of this 2-tile geometry (registered in species_hardware)
    nl = closed_form_nl(p_logical)
    ok = abs(p_wedge - 0.15625) < 1e-9 and abs(nl - 0.29956028) < 1e-6
    return ok, p_wedge, nl


def two_q_count(qc: QuantumCircuit) -> int:
    return sum(1 for inst in qc.data if len(inst.qubits) == 2)


def routed_metrics(qc: QuantumCircuit, backend) -> tuple[int, int, int]:
    best = None
    for seed in SEEDS:
        t = transpile(qc, backend=backend, optimization_level=3,
                      seed_transpiler=seed)
        m = (two_q_count(t), t.depth(), seed)
        if best is None or m[:2] < best[:2]:
            best = m
    return best


def main():
    enc0 = build_encoder()
    cliff = Clifford(enc0)
    candidates = {
        "C0 baseline(default)": enc0,
        "C1 greedy": synth_clifford_greedy(cliff),
        "C2 ag": synth_clifford_ag(cliff),
        "C3 layers": synth_clifford_layers(cliff),
    }

    try:
        from qiskit_ibm_runtime.fake_provider import FakeTorino
        backend = FakeTorino()
        have_backend = True
    except Exception as e:                                    # pragma: no cover
        print(f"(no fake backend available: {e}; raw counts only)")
        backend, have_backend = None, False

    print(f"W2 encoder-redesign candidates (registered point theta=pi/6)\n")
    print(f"{'candidate':>22} {'P2-A':>6} {'enc 2q':>7} {'prep 2q':>8} "
          f"{'routed 2q':>10} {'depth':>6} {'seed':>5}")
    results = {}
    for name, enc in candidates.items():
        # decompose to basic gates for counting/transpiling
        enc_b = enc.decompose() if name.startswith("C0") else enc
        prep = prep_with_encoder(enc_b)
        ok, p_w, nl = validate_p2a(prep)
        row = {"p2a": ok, "enc2q": two_q_count(enc_b.decompose()),
               "prep2q": two_q_count(prep.decompose())}
        if have_backend and ok:
            r2q, dep, seed = routed_metrics(prep, backend)
            row.update(routed=r2q, depth=dep, seed=seed)
            print(f"{name:>22} {'PASS' if ok else 'FAIL':>6} "
                  f"{row['enc2q']:>7} {row['prep2q']:>8} {r2q:>10} "
                  f"{dep:>6} {seed:>5}")
        else:
            print(f"{name:>22} {'PASS' if ok else 'FAIL':>6} "
                  f"{row['enc2q']:>7} {row['prep2q']:>8} {'—':>10} "
                  f"{'—':>6} {'—':>5}")
        results[name] = row

    print("\nP2-A gate: candidates failing the exact target are discarded.")
    print("Next: best candidate(s) -> Tobin's phase7_rehearsal_manifest for the")
    print("noise-model gate verdict (NL_reh - 2*sigma_total > 0.10).")


if __name__ == "__main__":
    main()
