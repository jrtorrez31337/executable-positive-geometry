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

Submission-time wedge choice can be rehearsed locally without IBM credentials:

    python phase7_submit.py --backend fake_torino --dry-run --auto-wedge
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
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
MAX_MIXED_WEDGE_FLOOR = 0.125
TIER1_SIGMA_MULTIPLE = 2.0
TIER2_NL_THRESHOLD = 0.10
TILE_A = tuple(range(5))
TILE_B = tuple(range(5, 10))


def phase7_success_criterion(*, n_settings: int, shots: int) -> dict:
    """Pre-registered, noise-aware interpretation for persisted run.json files."""
    return {
        "source": "quant-phy-agent seq84 Phase-7 noise rehearsal",
        "assessment": "noise_dominated_on_free_tier_heron",
        "noiseless_nl_target": EXACT_NL_TARGET,
        "max_mixed_wedge_floor": MAX_MIXED_WEDGE_FLOOR,
        "noise_rehearsal": {
            "model": "FakeTorino / Heron r1 rehearsal",
            "expected_hardware_nl": "~0.01",
            "retained_signal_fraction": "3-6%",
            "optimistic_mitigation_nl_ceiling": "~0.09",
            "conclusion": (
                "At this depth, decoherence drives P_L toward 0.5 in the same "
                "direction as the signal's own mixing; a clean NL measurement "
                "requires a shallower redesign, not just mitigation."
            ),
        },
        "shot_budget": {
            "selected_settings": int(n_settings),
            "selected_shots": int(shots),
            "tier1_default": "150x512 is acceptable for characterization",
            "tier2_reference": "400x1024 gives sigma(NL) about 0.046 in MC",
        },
        "tiers": {
            "tier_1_characterization": {
                "claim": (
                    "Pipeline plus device are characterized: measured P_wedge "
                    "is significantly above the 0.125 max-mixed floor and "
                    "consistent with the registered noise model."
                ),
                "floor": MAX_MIXED_WEDGE_FLOOR,
                "sigma_multiple": TIER1_SIGMA_MULTIPLE,
                "significance_test": (
                    f"P_wedge - {TIER1_SIGMA_MULTIPLE:g}*P_wedge_sigma "
                    f"> {MAX_MIXED_WEDGE_FLOOR:g}"
                ),
                "run_recommendation": (
                    "Fire this Tier-1 characterization run when quota resets."
                ),
            },
            "tier_2_real_non_local_magic": {
                "claim": (
                    "A real non-local-magic readout survives hardware noise."
                ),
                "threshold": TIER2_NL_THRESHOLD,
                "success_test": f"NL > {TIER2_NL_THRESHOLD:g}",
                "run_recommendation": (
                    "Redesign shallower before spending quota if Tier 2 is "
                    "the objective."
                ),
            },
        },
    }


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def twoq_count(circuit) -> int:
    return sum(1 for inst in circuit.data if len(inst.qubits) == 2)


def parse_wedge(text: str) -> tuple[int, ...]:
    try:
        wedge = tuple(int(part.strip()) for part in text.split(",") if part.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid wedge {text!r}") from exc
    if len(wedge) != 3 or len(set(wedge)) != 3 or any(q < 0 or q >= 10 for q in wedge):
        raise argparse.ArgumentTypeError("wedge must be three distinct qubits in 0..9")
    return wedge


def wedge_candidates(mode: str) -> list[tuple[int, ...]]:
    key = mode.lower().replace("_", "-")
    if key == "registered":
        return [tuple(WEDGE)]
    if key == "tile-a":
        return list(itertools.combinations(TILE_A, 3))
    if key == "tile-b":
        return list(itertools.combinations(TILE_B, 3))
    if key == "both-tiles":
        return list(itertools.combinations(TILE_A, 3)) + list(itertools.combinations(TILE_B, 3))
    raise argparse.ArgumentTypeError(
        "wedge candidate mode must be registered, tile-a, tile-b, or both-tiles"
    )


def virtual_to_physical_map(source_circuit, transpiled_circuit) -> dict[int, int]:
    layout = getattr(transpiled_circuit, "layout", None)
    initial_layout = getattr(layout, "initial_layout", layout)
    if initial_layout is None or not hasattr(initial_layout, "get_virtual_bits"):
        return {}

    mapping = {}
    for virtual_bit, physical in initial_layout.get_virtual_bits().items():
        try:
            virtual_index = source_circuit.find_bit(virtual_bit).index
        except Exception:
            continue
        mapping[int(virtual_index)] = int(physical)
    return mapping


def qubit_calibration_error(backend, physical_qubit: int) -> float | None:
    try:
        props = backend.properties()
    except Exception:
        props = None
    if props is not None:
        errors = []
        try:
            errors.append(float(props.readout_error(physical_qubit)))
        except Exception:
            pass
        for gate in ("sx", "x"):
            try:
                errors.append(float(props.gate_error(gate, physical_qubit)))
            except Exception:
                pass
        if errors:
            return float(sum(errors))
    return None


def choose_calibrated_wedge(
    backend,
    source_circuit,
    transpiled_circuit,
    candidates: list[tuple[int, ...]],
) -> dict:
    v2p = virtual_to_physical_map(source_circuit, transpiled_circuit)
    scored = []
    for wedge in candidates:
        physical = [v2p.get(q) for q in wedge]
        if any(q is None for q in physical):
            continue
        errors = [qubit_calibration_error(backend, int(q)) for q in physical]
        if any(err is None for err in errors):
            continue
        scored.append({
            "wedge": list(wedge),
            "physical_qubits": [int(q) for q in physical],
            "score": float(sum(float(err) for err in errors)),
            "per_qubit_error": [float(err) for err in errors],
        })
    if not scored:
        return {
            "selected_wedge": list(WEDGE),
            "status": "fallback_registered_wedge",
            "reason": "layout or calibration data unavailable",
            "candidate_count": len(candidates),
        }
    scored.sort(key=lambda row: row["score"])
    best = scored[0]
    return {
        "selected_wedge": best["wedge"],
        "status": "selected_from_calibration",
        "candidate_count": len(candidates),
        "scored_count": len(scored),
        "physical_qubits": best["physical_qubits"],
        "score": best["score"],
        "per_qubit_error": best["per_qubit_error"],
    }


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
    parser.add_argument("--wedge", type=parse_wedge, default=tuple(WEDGE),
                        help="virtual wedge qubits, e.g. 0,1,2")
    parser.add_argument("--auto-wedge", action="store_true",
                        help="choose the best calibrated equivalent 3-of-5 wedge after hardware transpilation")
    parser.add_argument("--wedge-candidates", default="tile-a",
                        help="registered, tile-a, tile-b, or both-tiles")
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
        "wedge": list(args.wedge),
        "wedge_selection": {
            "status": "fixed_cli_wedge",
            "selected_wedge": list(args.wedge),
            "note": (
                "The [[5,1,3]] perfect-tensor symmetry makes any 3-of-5 tile "
                "subset an equivalent purity wedge; --auto-wedge can choose "
                "among equivalent subsets from backend calibration at submit time."
            ),
        },
        "n_qubits": int(base.num_qubits),
        "n_settings": int(args.settings),
        "shots": int(args.shots),
        "seed": int(args.seed),
        "clifford_seeds": clifford_seeds,
        "settings_file": settings_file,
        "settings_sha256": settings_sha,
        "pre_registered_success_criterion": phase7_success_criterion(
            n_settings=args.settings,
            shots=args.shots,
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

    backend_key = backend_name.lower().replace("_", "-")
    fake_backend = backend_key in {"fake-torino", "torino", "fake-heron"}
    if fake_backend:
        from qiskit_ibm_runtime.fake_provider import FakeTorino

        backend = FakeTorino()
        metadata["backend_kind"] = "fake_provider"
    else:
        service = get_service()
        backend = service.backend(backend_name)
        metadata["backend_kind"] = "ibm_runtime"

    usage = None
    if not fake_backend and not args.skip_quota_check and not args.dry_run:
        usage = quota_remaining(service)
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

    isa_circuits = transpile_for_backend(
        circuits,
        backend,
        optimization_level=args.optimization_level,
    )
    if args.auto_wedge:
        selection = choose_calibrated_wedge(
            backend,
            circuits[0],
            isa_circuits[0],
            wedge_candidates(args.wedge_candidates),
        )
        metadata["wedge_selection"] = selection
        metadata["wedge"] = list(selection["selected_wedge"])
    metadata["transpiled_metrics"] = metric_summary(isa_circuits)
    print(f"selected wedge: {metadata['wedge']} ({metadata['wedge_selection']['status']})")
    print(f"{backend_name} transpiled metrics: {metadata['transpiled_metrics']}")

    if fake_backend and not args.dry_run:
        metadata["status"] = "fake_backend_transpiled"
        write_json(run_dir / "run.json", metadata)
        raise SystemExit(
            "fake provider backend is for local dry-runs only; pass --dry-run "
            "or choose a real IBM backend for submission"
        )

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
