"""Track D, Phase 7 — retrieve and analyze a persisted purity-only run."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

import numpy as np


EXACT_NL_TARGET = 0.2996


def file_sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path):
    return json.loads(path.read_text())


def counts_from_sampler_result(result) -> list[dict[str, int]]:
    counts_list = []
    for pub_result in result:
        data = getattr(pub_result, "data", None)
        if data is None:
            raise TypeError(f"Sampler pub result has no data field: {pub_result!r}")

        register = getattr(data, "meas", None)
        if register is None and hasattr(data, "keys"):
            for key in data.keys():
                candidate = getattr(data, key)
                if hasattr(candidate, "get_counts"):
                    register = candidate
                    break
        if register is None or not hasattr(register, "get_counts"):
            raise TypeError(f"could not find a measured bit register in {data!r}")

        counts_list.append({str(k): int(v) for k, v in register.get_counts().items()})
    return counts_list


def retrieve_runtime_counts(job_id: str) -> list[dict[str, int]]:
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = QiskitRuntimeService()
    job = service.job(job_id)
    return counts_from_sampler_result(job.result())


def brydges_purity_per_setting(counts_list, *, wedge: tuple[int, ...]) -> np.ndarray:
    """Unbiased per-setting collision estimator for the measured wedge purity."""
    k = len(wedge)
    purities = []
    for counts in counts_list:
        total = sum(counts.values())
        if total <= 1:
            raise ValueError("each randomized setting needs at least two shots")
        marg = {}
        for bits, count in counts.items():
            key = tuple(bits[::-1][q] for q in wedge)
            marg[key] = marg.get(key, 0) + int(count)

        est = 0.0
        for s, cs in marg.items():
            for sp, csp in marg.items():
                hamming = sum(a != b for a, b in zip(s, sp))
                weight = cs * csp if s != sp else cs * (cs - 1)
                est += (-2.0) ** (-hamming) * weight
        purities.append((2 ** k) * est / (total * (total - 1)))
    return np.asarray(purities, dtype=float)


def closed_form_nl(purity: float) -> float:
    return float(-np.log2(4 * purity ** 2 - 6 * purity + 3))


def local_estimate_nl(counts_list, _unitaries, *, wedge: tuple[int, ...]) -> dict:
    """Fallback estimator matching the Phase 7 interface until the shared module lands."""
    per_setting = brydges_purity_per_setting(counts_list, wedge=wedge)
    p_wedge = float(np.mean(per_setting))
    sigma_p_wedge = float(np.std(per_setting, ddof=1) / np.sqrt(len(per_setting))) \
        if len(per_setting) > 1 else 0.0

    p_l_raw = 4.0 * p_wedge
    p_l = float(np.clip(p_l_raw, 0.5, 1.0))
    nl = closed_form_nl(p_l)
    denom = 4 * p_l ** 2 - 6 * p_l + 3
    deriv = abs(-(8 * p_l - 6) / (np.log(2) * denom)) if 0.5 < p_l < 1.0 else 0.0
    sigma_nl = float(deriv * 4.0 * sigma_p_wedge)

    return {
        "P_wedge": p_wedge,
        "P_wedge_sigma": sigma_p_wedge,
        "P_L": p_l,
        "P_L_raw": p_l_raw,
        "NL": nl,
        "sigma": sigma_nl,
        "n_settings": int(len(per_setting)),
        "estimator": "phase7_retrieve.local_brydges_fallback",
    }


def load_estimator():
    here = pathlib.Path(__file__).parent
    sys.path.insert(0, str(here))
    try:
        from phase7_purity_estimator import estimate_nl  # type: ignore
    except ModuleNotFoundError as exc:
        if exc.name != "phase7_purity_estimator":
            raise
        print(
            "phase7_purity_estimator unavailable; using local Brydges fallback "
            f"({type(exc).__name__}: {exc})"
        )
        return local_estimate_nl
    return estimate_nl


def normalize_estimate(result) -> dict:
    if not isinstance(result, dict):
        raise TypeError(f"estimate_nl must return a dict, got {type(result).__name__}")
    aliases = {
        "p_wedge": "P_wedge",
        "p_l": "P_L",
        "nl": "NL",
        "sigma_nl": "sigma",
    }
    out = dict(result)
    for src, dst in aliases.items():
        if dst not in out and src in out:
            out[dst] = out[src]
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=pathlib.Path,
                        help="directory created by phase7_submit.py")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = args.run_dir
    meta = load_json(run_dir / "run.json")

    settings_path = run_dir / meta["settings_file"]
    actual_sha = file_sha256(settings_path)
    if actual_sha != meta["settings_sha256"]:
        raise SystemExit(
            f"settings hash mismatch: expected {meta['settings_sha256']} got {actual_sha}"
        )
    unitaries = np.load(settings_path)["unitaries"]

    if "counts_file" in meta:
        counts_list = load_json(run_dir / meta["counts_file"])
    elif "job_id" in meta:
        counts_list = retrieve_runtime_counts(meta["job_id"])
    else:
        raise SystemExit("run has neither counts_file nor job_id")

    if len(counts_list) != int(meta["n_settings"]):
        raise SystemExit(
            f"settings/count mismatch: {meta['n_settings']} settings, "
            f"{len(counts_list)} count dictionaries"
        )
    if unitaries.shape[0] != int(meta["n_settings"]):
        raise SystemExit(
            f"settings/unitary mismatch: {meta['n_settings']} settings, "
            f"{unitaries.shape[0]} unitary rows"
        )

    estimate_nl = load_estimator()
    result = normalize_estimate(
        estimate_nl(counts_list, unitaries, wedge=tuple(meta["wedge"]))
    )

    print(f"Phase 7 purity-only run: {run_dir}")
    print(f"backend={meta['backend']} status={meta['status']} "
          f"settings={meta['n_settings']} shots={meta['shots']}")
    print(f"settings hash verified: {actual_sha[:16]}...")
    print(f"P_wedge={result.get('P_wedge'):.6f}  P_L={result.get('P_L'):.6f}")
    print(f"NL={result.get('NL'):.6f} +/- {result.get('sigma', 0.0):.6f} "
          f"(noiseless target {EXACT_NL_TARGET})")
    print(f"estimator={result.get('estimator', estimate_nl.__module__)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
