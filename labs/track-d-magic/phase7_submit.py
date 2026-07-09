"""Track D, Phase 7 — submit the purity-only non-local-magic run.

This is the fire-when-ready half of the Phase 7 hardware prep.  It builds the
validated two-tile [[5,1,3]] magic-state preparation from species_hardware.py,
generates one classical-shadows data set for the magic state only, and persists
the job id plus every random setting needed for later analysis.

Default use is the real pinned backend:

    python phase7_submit.py

Quota-free rehearsal uses the same persisted format:

    python phase7_submit.py --backend aer --settings 12 --shots 128
    python phase7_retrieve.py labs/track-d-magic/phase7_runs/<run-dir>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from datetime import datetime, timezone

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from species_hardware import THETA, WEDGE, prep_circuit  # noqa: E402

from qiskit.quantum_info import random_clifford  # noqa: E402


RUN_ROOT = pathlib.Path(__file__).with_name("phase7_runs")
DEFAULT_SEED = 20260709
EXACT_NL_TARGET = 0.2996


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def twoq_count(circuit) -> int:
    return sum(1 for inst in circuit.data if len(inst.qubits) == 2)


def write_json(path: pathlib.Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def file_sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_shadow_circuits(base, *, rng: np.random.Generator, n_settings: int):
    """Return randomized-measurement circuits and persisted Clifford settings."""
    circuits = []
    seed_table = []
    unitaries = np.empty((n_settings, base.num_qubits, 2, 2), dtype=np.complex128)

    for setting in range(n_settings):
        seeds = [int(rng.integers(1 << 30)) for _ in range(base.num_qubits)]
        qc = base.copy()
        for q, seed in enumerate(seeds):
            cliff = random_clifford(1, seed=seed)
            qc.compose(cliff.to_circuit(), qubits=[q], inplace=True)
            unitaries[setting, q] = np.asarray(cliff.to_matrix(), dtype=np.complex128)
        qc.measure_all()
        circuits.append(qc)
        seed_table.append(seeds)

    return circuits, seed_table, unitaries


def save_settings(run_dir: pathlib.Path, unitaries: np.ndarray) -> tuple[str, str]:
    settings_path = run_dir / "settings.npz"
    np.savez_compressed(settings_path, unitaries=unitaries)
    return settings_path.name, file_sha256(settings_path)


def save_counts(run_dir: pathlib.Path, counts_list: list[dict[str, int]]) -> str:
    counts_path = run_dir / "counts.json"
    counts_path.write_text(json.dumps(counts_list, indent=2, sort_keys=True) + "\n")
    return counts_path.name


def run_aer(circuits, *, shots: int) -> list[dict[str, int]]:
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    sim = AerSimulator()
    counts = []
    for qc in circuits:
        result = sim.run(transpile(qc, sim), shots=shots).result()
        counts.append({str(k): int(v) for k, v in result.get_counts().items()})
    return counts


def transpile_for_backend(circuits, backend, *, optimization_level: int):
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    pm = generate_preset_pass_manager(
        backend=backend,
        optimization_level=optimization_level,
    )
    return [pm.run(qc) for qc in circuits]


def metric_summary(circuits) -> dict:
    depths = [int(qc.depth()) for qc in circuits]
    twoqs = [int(twoq_count(qc)) for qc in circuits]
    return {
        "n_circuits": len(circuits),
        "depth_min": min(depths),
        "depth_median": float(np.median(depths)),
        "depth_max": max(depths),
        "twoq_min": min(twoqs),
        "twoq_median": float(np.median(twoqs)),
        "twoq_max": max(twoqs),
    }


def get_service():
    from qiskit_ibm_runtime import QiskitRuntimeService

    return QiskitRuntimeService()


def quota_remaining(service) -> dict | None:
    try:
        usage = service.usage()
    except Exception as exc:  # pragma: no cover - account dependent
        print(f"quota check unavailable: {type(exc).__name__}: {exc}")
        return None
    return {
        "usage_remaining_seconds": usage.get("usage_remaining_seconds"),
        "usage_limit_seconds": usage.get("usage_limit_seconds"),
    }


def submit_runtime_job(isa_circuits, backend, *, shots: int):
    from qiskit_ibm_runtime import SamplerV2

    sampler = SamplerV2(mode=backend)
    return sampler.run(isa_circuits, shots=shots)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="ibm_kingston",
                        help="'aer' for local rehearsal, otherwise IBM backend name")
    parser.add_argument("--settings", type=int, default=150,
                        help="number of randomized measurement settings")
    parser.add_argument("--shots", type=int, default=512,
                        help="shots per randomized measurement setting")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help="RNG seed for Clifford settings")
    parser.add_argument("--out", type=pathlib.Path, default=None,
                        help="output run directory")
    parser.add_argument("--optimization-level", type=int, default=2)
    parser.add_argument("--min-quota-seconds", type=int, default=150,
                        help="minimum remaining quota before submitting hardware")
    parser.add_argument("--skip-quota-check", action="store_true")
    parser.add_argument("--dry-run", action="store_true",
                        help="build/transpile/persist settings but do not submit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.settings <= 0 or args.shots <= 1:
        raise SystemExit("settings must be positive and shots must exceed 1")

    backend_name = args.backend
    run_dir = args.out or RUN_ROOT / f"phase7_{backend_name}_{utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=False)

    rng = np.random.default_rng(args.seed)
    base = prep_circuit(THETA, magic=True)
    circuits, clifford_seeds, unitaries = build_shadow_circuits(
        base,
        rng=rng,
        n_settings=args.settings,
    )
    settings_file, settings_sha = save_settings(run_dir, unitaries)

    base_metrics = metric_summary([base])
    measured_metrics = metric_summary(circuits)
    metadata = {
        "phase": "Track D Phase 7 purity-only non-local magic",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "backend": backend_name,
        "status": "prepared",
        "theta": float(THETA),
        "magic_state_only": True,
        "exact_nl_target": EXACT_NL_TARGET,
        "wedge": list(WEDGE),
        "n_qubits": int(base.num_qubits),
        "n_settings": int(args.settings),
        "shots": int(args.shots),
        "seed": int(args.seed),
        "clifford_seeds": clifford_seeds,
        "settings_file": settings_file,
        "settings_sha256": settings_sha,
        "pre_registered_success_criterion": (
            "Use phase7_purity_estimator variance/noise study when present; "
            "retrieve reports NL and sigma against the noiseless 0.2996 target."
        ),
        "base_circuit_metrics": base_metrics,
        "measured_circuit_metrics": measured_metrics,
        "optimization_level": int(args.optimization_level),
    }

    if backend_name.lower() == "aer":
        counts = run_aer(circuits, shots=args.shots)
        metadata["counts_file"] = save_counts(run_dir, counts)
        metadata["status"] = "aer_complete"
        metadata["transpiled_metrics"] = measured_metrics
        write_json(run_dir / "run.json", metadata)
        print(f"Aer rehearsal complete: {run_dir}")
        print(f"settings={args.settings}, shots={args.shots}, exact_NL={EXACT_NL_TARGET}")
        return 0

    service = get_service()
    usage = None if args.skip_quota_check or args.dry_run else quota_remaining(service)
    if usage:
        metadata["quota"] = usage
        remaining = usage.get("usage_remaining_seconds")
        print(f"quota remaining: {remaining}s / {usage.get('usage_limit_seconds')}s")
        if remaining is not None and remaining < args.min_quota_seconds:
            metadata["status"] = "quota_insufficient"
            write_json(run_dir / "run.json", metadata)
            raise SystemExit(
                f"insufficient quota ({remaining}s); prepared settings at {run_dir}"
            )

    backend = service.backend(backend_name)
    isa_circuits = transpile_for_backend(
        circuits,
        backend,
        optimization_level=args.optimization_level,
    )
    metadata["transpiled_metrics"] = metric_summary(isa_circuits)
    print(f"{backend_name} transpiled metrics: {metadata['transpiled_metrics']}")

    if args.dry_run:
        metadata["status"] = "dry_run_transpiled"
        write_json(run_dir / "run.json", metadata)
        print(f"dry run complete: {run_dir}")
        return 0

    job = submit_runtime_job(isa_circuits, backend, shots=args.shots)
    metadata["status"] = "submitted"
    metadata["job_id"] = job.job_id()
    write_json(run_dir / "run.json", metadata)
    print(f"submitted {len(isa_circuits)} circuits to {backend_name}: {job.job_id()}")
    print(f"persisted job and settings: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
