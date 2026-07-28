"""Track D, Phase 7/P2 -- candidate rehearsal manifests for the magic-wedge gate.

Project 2's W2 gate is intentionally stricter than the old Phase 7 point
estimate: each encoder candidate must persist routed metrics, circuit hashes,
shot/rehearsal uncertainties, and the lower-confidence-bound verdict

    NL_rehearsal - 2 * sigma_total > 0.10.

The registered sigma_total is conservative: purity-estimator shot sigma plus
the ensemble SEM across independent rehearsal repeats. The current reference
candidate is expected to fail; this script makes that failure reproducible and
gives future shallower candidates the same manifest format.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from datetime import datetime, timezone
from typing import Any

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from phase7_purity_estimator import (  # noqa: E402
    estimate_nl,
    heron_like_noise_model,
)
from phase7_encoder_redesign import (  # noqa: E402
    prep_with_encoder,
    validate_p2a,
)
from phase7_submit import (  # noqa: E402
    DEFAULT_SEED,
    EXACT_NL_TARGET,
    MAX_MIXED_WEDGE_FLOOR,
    TIER2_NL_THRESHOLD,
    parse_wedge,
    build_shadow_circuits,
    metric_summary,
    transpile_for_backend,
)
from species_hardware import THETA, WEDGE, build_encoder  # noqa: E402
from qiskit.quantum_info import Clifford  # noqa: E402
from qiskit.synthesis import (  # noqa: E402
    synth_clifford_ag,
    synth_clifford_greedy,
    synth_clifford_layers,
)


RUN_ROOT = pathlib.Path(__file__).with_name("phase7_rehearsals")
REFERENCE_SIGMA_NL_400x1024 = 0.046


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def jsonable(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"real": float(value.real), "imag": float(value.imag)}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    return value


def write_json(path: pathlib.Path, payload: dict) -> None:
    path.write_text(json.dumps(jsonable(payload), indent=2, sort_keys=True) + "\n")


def _inst_parts(item):
    if hasattr(item, "operation"):
        return item.operation, item.qubits, item.clbits
    operation = item[0]
    qubits = item[1]
    clbits = item[2] if len(item) > 2 else []
    return operation, qubits, clbits


def circuit_payload(circuit) -> list[dict[str, Any]]:
    """Stable enough for manifest hashing without depending on QASM exporters."""
    qubit_index = {bit: idx for idx, bit in enumerate(circuit.qubits)}
    clbit_index = {bit: idx for idx, bit in enumerate(circuit.clbits)}
    rows: list[dict[str, Any]] = []
    for item in circuit.data:
        operation, qubits, clbits = _inst_parts(item)
        params = []
        for param in getattr(operation, "params", []):
            if isinstance(param, (int, float, np.floating)):
                params.append(round(float(param), 15))
            else:
                params.append(str(param))
        rows.append({
            "name": str(operation.name),
            "qubits": [qubit_index[q] for q in qubits],
            "clbits": [clbit_index[c] for c in clbits],
            "params": params,
        })
    return rows


def sha256_json(payload: Any) -> str:
    raw = json.dumps(jsonable(payload), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def circuit_sha256(circuit) -> str:
    return sha256_json(circuit_payload(circuit))


def circuits_sha256(circuits) -> str:
    digest = hashlib.sha256()
    for circuit in circuits:
        digest.update(json.dumps(circuit_payload(circuit),
                                 sort_keys=True, separators=(",", ":")).encode())
        digest.update(b"\n")
    return digest.hexdigest()


def build_candidate(name: str):
    normalized = name.lower().replace("_", "-")
    enc0 = build_encoder()
    cliff = Clifford(enc0)
    candidate_specs = {
        "c0": {
            "label": "C0 baseline",
            "encoder": enc0.decompose(),
            "description": (
                "Baseline two-tile [[5,1,3]] encoder from species_hardware; "
                "P2-A validated control for the W2 rehearsal gate."
            ),
        },
        "c1": {
            "label": "C1 greedy",
            "encoder": synth_clifford_greedy(cliff),
            "description": (
                "Greedy Clifford resynthesis candidate from phase7_encoder_redesign; "
                "marginal best routed-depth/2q candidate."
            ),
        },
        "c2": {
            "label": "C2 ag",
            "encoder": synth_clifford_ag(cliff),
            "description": "Aaronson-Gottesman Clifford resynthesis candidate.",
        },
        "c3": {
            "label": "C3 layers",
            "encoder": synth_clifford_layers(cliff),
            "description": "Structured-layer Clifford resynthesis candidate.",
        },
    }
    aliases = {
        "reference": "c0",
        "phase7-reference": "c0",
        "current": "c0",
        "baseline": "c0",
        "c0-baseline": "c0",
        "c1-greedy": "c1",
        "greedy": "c1",
        "c2-ag": "c2",
        "ag": "c2",
        "c3-layers": "c3",
        "layers": "c3",
    }
    key = aliases.get(normalized, normalized)
    if key in candidate_specs:
        spec = candidate_specs[key]
        base = prep_with_encoder(spec["encoder"])
        ok, p_wedge, nl = validate_p2a(base)
        if not ok:
            raise SystemExit(
                f"{spec['label']} failed P2-A exact target: "
                f"P_wedge={p_wedge:.8f}, NL={nl:.8f}"
            )
        return base, {
            "candidate": key,
            "label": spec["label"],
            "p2a_validated": True,
            "p2a_P_wedge": p_wedge,
            "p2a_NL": nl,
            "description": spec["description"],
        }
    raise SystemExit(
        f"unknown candidate {name!r}; implemented: C0, C1, C2, C3"
    )


def load_rehearsal_backend(label: str):
    """Return (backend_for_routing, noise_model, noise_label)."""
    key = label.lower()
    if key == "aer":
        return None, None, "ideal AerSimulator"
    if key in {"generic-heron", "heron"}:
        noise_model, noise_label = heron_like_noise_model()
        return None, noise_model, noise_label
    if key in {"fake-torino", "torino", "fake_heron"}:
        try:
            from qiskit_ibm_runtime.fake_provider import FakeTorino
            from qiskit_aer.noise import NoiseModel

            backend = FakeTorino()
            return backend, NoiseModel.from_backend(backend), "FakeTorino routed noise"
        except Exception:
            noise_model, noise_label = heron_like_noise_model()
            return None, noise_model, f"{noise_label} (FakeTorino unavailable)"

    from qiskit_ibm_runtime import QiskitRuntimeService
    from qiskit_aer.noise import NoiseModel

    service = QiskitRuntimeService()
    backend = service.backend(label)
    return backend, NoiseModel.from_backend(backend), f"{label} backend noise model"


def transpile_for_rehearsal(circuits, backend, noise_model, optimization_level: int):
    if backend is not None:
        return transpile_for_backend(
            circuits,
            backend,
            optimization_level=optimization_level,
        )

    from qiskit import transpile
    from qiskit_aer import AerSimulator

    sim = AerSimulator(noise_model=noise_model) if noise_model is not None else AerSimulator()
    return [transpile(qc, sim, optimization_level=optimization_level) for qc in circuits]


def run_aer_counts(circuits, *, noise_model, shots: int) -> list[dict[str, int]]:
    from qiskit_aer import AerSimulator

    sim = AerSimulator(noise_model=noise_model) if noise_model is not None else AerSimulator()
    result = sim.run(circuits, shots=shots).result()
    return [
        {str(k): int(v) for k, v in result.get_counts(i).items()}
        for i in range(len(circuits))
    ]


def mean_sem(values: list[float]) -> tuple[float, float]:
    arr = np.asarray(values, dtype=float)
    mean = float(np.mean(arr))
    if arr.size < 2:
        return mean, 0.0
    return mean, float(np.std(arr, ddof=1) / np.sqrt(arr.size))


def gate_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    nls = [float(r["estimate"]["NL"]) for r in results]
    pws = [float(r["estimate"]["P_wedge"]) for r in results]
    sigmas = [float(r["estimate"].get("sigma", 0.0)) for r in results]
    nl_mean, nl_sem = mean_sem(nls)
    pw_mean, pw_sem = mean_sem(pws)
    shot_sigma = float(np.mean(sigmas)) if sigmas else 0.0
    sigma_total_additive = shot_sigma + nl_sem
    sigma_total_quadrature = float(np.hypot(shot_sigma, nl_sem))
    lower_bound = nl_mean - 2.0 * sigma_total_additive
    tier2_pass = lower_bound > TIER2_NL_THRESHOLD
    tier1_lower = pw_mean - 2.0 * pw_sem
    return {
        "NL_mean": nl_mean,
        "NL_rehearsal_SEM": nl_sem,
        "NL_shot_sigma_mean": shot_sigma,
        "sigma_total_registered_additive": sigma_total_additive,
        "sigma_total_quadrature_reference": sigma_total_quadrature,
        "tier2_threshold": TIER2_NL_THRESHOLD,
        "tier2_lower_bound": lower_bound,
        "tier2_pass": tier2_pass,
        "P_wedge_mean": pw_mean,
        "P_wedge_SEM": pw_sem,
        "tier1_floor": MAX_MIXED_WEDGE_FLOOR,
        "tier1_floor_lower_bound": tier1_lower,
        "tier1_floor_pass": tier1_lower > MAX_MIXED_WEDGE_FLOOR,
        "reference_sigma_note": (
            "At 400x1024, prior Phase 7 MC gave sigma(NL) about "
            f"{REFERENCE_SIGMA_NL_400x1024:.3f}; with that budget the point "
            "estimate must be roughly 0.192 to clear NL - 2sigma > 0.10."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", default="reference")
    parser.add_argument("--backend", default="generic-heron",
                        help="aer, generic-heron, fake-torino, or an IBM backend")
    parser.add_argument("--settings", type=int, default=120)
    parser.add_argument("--shots", type=int, default=512)
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--optimization-level", type=int, default=2)
    parser.add_argument("--wedge", type=parse_wedge, default=tuple(WEDGE),
                        help="virtual wedge qubits, e.g. 0,1,2")
    parser.add_argument("--out", type=pathlib.Path, default=None)
    parser.add_argument("--metrics-only", action="store_true",
                        help="persist hashes/routed metrics without running Aer")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.settings <= 0 or args.shots <= 1 or args.reps <= 0:
        raise SystemExit("settings and reps must be positive; shots must exceed 1")

    base, candidate_meta = build_candidate(args.candidate)
    backend, noise_model, noise_label = load_rehearsal_backend(args.backend)
    run_dir = args.out or RUN_ROOT / f"p2_{candidate_meta['candidate']}_{utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=False)

    routed_base = transpile_for_rehearsal(
        [base],
        backend,
        noise_model,
        args.optimization_level,
    )[0]
    manifest: dict[str, Any] = {
        "project": "PROJECT-2-MAGIC-WEDGE W2 rehearsal gate",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidate": candidate_meta,
        "backend": args.backend,
        "noise_model": noise_label,
        "theta": float(THETA),
        "wedge": list(args.wedge),
        "wedge_selection_note": (
            "Default rehearsal uses the registered 3q wedge. Hardware submit "
            "may choose an equivalent 3-of-5 tile subset from backend "
            "calibration; run.json persists that selected wedge for retrieval."
        ),
        "settings": int(args.settings),
        "shots": int(args.shots),
        "reps": int(args.reps),
        "seed": int(args.seed),
        "optimization_level": int(args.optimization_level),
        "exact_nl_target": EXACT_NL_TARGET,
        "gate": "NL_rehearsal - 2*(shot_sigma + rehearsal_SEM) > 0.10",
        "base_circuit_sha256": circuit_sha256(base),
        "routed_base_circuit_sha256": circuit_sha256(routed_base),
        "base_metrics": metric_summary([base]),
        "routed_base_metrics": metric_summary([routed_base]),
        "replicates": [],
    }

    if args.metrics_only:
        manifest["status"] = "metrics_only"
        write_json(run_dir / "manifest.json", manifest)
        print(f"P2 metrics manifest written: {run_dir / 'manifest.json'}")
        return 0

    for rep in range(args.reps):
        rep_seed = int(args.seed + 1009 * rep)
        rng = np.random.default_rng(rep_seed)
        circuits, clifford_seeds, unitaries = build_shadow_circuits(
            base,
            rng=rng,
            n_settings=args.settings,
        )
        routed_circuits = transpile_for_rehearsal(
            circuits,
            backend,
            noise_model,
            args.optimization_level,
        )
        counts = run_aer_counts(routed_circuits, noise_model=noise_model, shots=args.shots)
        estimate = estimate_nl(counts, unitaries, wedge=args.wedge)
        manifest["replicates"].append({
            "rep": rep,
            "seed": rep_seed,
            "clifford_seed_sha256": sha256_json(clifford_seeds),
            "measurement_circuits_sha256": circuits_sha256(circuits),
            "routed_measurement_circuits_sha256": circuits_sha256(routed_circuits),
            "measurement_metrics": metric_summary(circuits),
            "routed_measurement_metrics": metric_summary(routed_circuits),
            "estimate": estimate,
        })
        print(
            f"rep {rep + 1}/{args.reps}: NL={estimate['NL']:.4f} "
            f"+/- {estimate.get('sigma', 0.0):.4f}, "
            f"P_wedge={estimate['P_wedge']:.5f}"
        )

    manifest["summary"] = gate_summary(manifest["replicates"])
    manifest["status"] = "complete"
    write_json(run_dir / "manifest.json", manifest)

    s = manifest["summary"]
    verdict = "PASS" if s["tier2_pass"] else "FAIL"
    print("\nP2 W2 registered gate")
    print(f"  NL_rehearsal = {s['NL_mean']:.4f}")
    print(f"  shot sigma mean = {s['NL_shot_sigma_mean']:.4f}")
    print(f"  rehearsal SEM = {s['NL_rehearsal_SEM']:.4f}")
    print(f"  lower bound = {s['tier2_lower_bound']:.4f} "
          f"(threshold {TIER2_NL_THRESHOLD:.2f}) -> {verdict}")
    print(f"manifest written: {run_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
