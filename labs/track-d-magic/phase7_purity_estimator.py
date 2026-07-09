"""Track D, Phase 7 (my half) -- purity-only non-local-magic estimator + budget.

Phase 7 measures the IRREDUCIBLE non-local magic of a two-[[5,1,3]]-tile
logical state from a SINGLE 3-qubit wedge, using randomized-measurement
purity (the robust half; the erasable/SRE-shadow route was too high-variance
at 150x512 -- see species_hardware.py methods note). This module hardens the
estimator and pre-computes everything needed to fire on hardware:

  1. Noiseless validation: the randomized-measurement purity + factor-4 junk
     correction recovers the exact NL = 0.2996 (P_L=0.625) at t=pi/6.
  2. Monte-Carlo shot budget: sigma(NL) as a function of (N_settings, N_shots)
     -> the setting count that resolves the signal within the free-tier window.
  3. Device-noise rehearsal: NL under a Heron-like noise model -> the
     pre-registered EXPECTED hardware value (decoherence -> P_W toward 1/8 ->
     P_L toward 0.5 -> NL toward 0, so we must know how much survives).

Physics: logical rho_L = diag(cos^2 t, sin^2 t) = diag(0.75, 0.25) at t=pi/6;
P_L = 0.625; wedge rho_W = rho_L (x) I/4 (junk maximally mixed, exact Phase 1b)
so P_W = P_L/4 = 0.15625 and P_L = 4 P_W. NL = -log2(4 P_L^2 - 6 P_L + 3).

Interface for phase7_retrieve.py (codex-science half):
  estimate_nl(counts_list, unitaries, wedge=(0,1,2), n_shots=None)
      -> {"P_wedge","P_L","NL","sigma_NL"}
"""

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from species_hardware import (  # noqa: E402
    THETA, WEDGE, closed_form_nl, prep_circuit, shadow_circuits,
)

from qiskit.quantum_info import (  # noqa: E402
    Statevector, partial_trace, random_clifford,
)


def exact_wedge_rdm(theta=THETA):
    sv = Statevector.from_instruction(prep_circuit(theta, magic=True))
    trace_out = [q for q in range(10) if q not in WEDGE]
    return np.asarray(partial_trace(sv, trace_out).data)   # 8x8


def _collision_purity(counts, k):
    """Unbiased randomized-measurement purity from one setting's counts
    (Elben-Vermersch-Brydges). counts: length-2^k integer array."""
    tot = int(counts.sum())
    if tot < 2:
        return np.nan
    s = np.arange(2 ** k)
    d = (s[:, None] ^ s[None, :])
    # popcount of the XOR table
    ham = np.vectorize(lambda x: bin(x).count("1"))(d)
    w = np.outer(counts, counts).astype(float)
    np.fill_diagonal(w, counts * (counts - 1))          # U-statistic diagonal
    est = np.sum(((-2.0) ** (-ham)) * w)
    return est * (2 ** k) / (tot * (tot - 1))


def purity_from_rdm(rho_W, n_settings, n_shots, rng):
    """Simulate the randomized-measurement purity estimate directly from the
    exact wedge RDM (fast path for the Monte-Carlo budget study)."""
    k = len(WEDGE)
    per = np.empty(n_settings)
    for i in range(n_settings):
        U = np.array([[1.0 + 0j]])
        for _ in range(k):
            U = np.kron(U, random_clifford(1, seed=int(rng.integers(1 << 30))).to_matrix())
        probs = np.clip(np.real(np.diag(U @ rho_W @ U.conj().T)), 0, None)
        probs /= probs.sum()
        counts = rng.multinomial(n_shots, probs)
        per[i] = _collision_purity(counts, k)
    return float(np.nanmean(per))


def nl_from_wedge_purity(p_wedge):
    p_l = float(np.clip(4.0 * p_wedge, 0.5, 1.0))
    return p_l, closed_form_nl(p_l)


def estimate_nl(counts_list, unitaries, wedge=WEDGE, n_shots=None):
    """Estimator consumed by phase7_retrieve.py. counts_list: list of dict
    (qiskit bitstring->count) or length-2^k arrays; unitaries only needed for
    the (deferred) erasable route -- purity needs just the wedge marginals."""
    k = len(wedge)
    per = []
    for counts in counts_list:
        if isinstance(counts, dict):
            marg = np.zeros(2 ** k, dtype=float)
            for bits, c in counts.items():
                rb = bits[::-1]
                idx = 0
                for j, q in enumerate(wedge):
                    idx |= (int(rb[q]) << j)
                marg[idx] += c
        else:
            marg = np.asarray(counts, dtype=float)
        per.append(_collision_purity(marg, k))
    per = np.array([p for p in per if not np.isnan(p)])
    p_wedge = float(np.mean(per))
    sigma_pw = float(np.std(per, ddof=1) / np.sqrt(len(per))) if len(per) > 1 else 0.0
    p_l, nl = nl_from_wedge_purity(p_wedge)
    # propagate sigma analytically: sigma_NL = |d NL/d P_L| * 4 * sigma_P_wedge,
    # d NL/d P_L = -(8 P_L - 6)/(ln2 * (4 P_L^2 - 6 P_L + 3)).
    denom = 4 * p_l ** 2 - 6 * p_l + 3
    deriv = abs((8 * p_l - 6) / (np.log(2) * denom)) if 0.5 < p_l < 1.0 else 0.0
    sigma_nl = float(deriv * 4.0 * sigma_pw)
    return {"P_wedge": p_wedge, "P_wedge_sigma": sigma_pw, "P_L": p_l,
            "NL": nl, "sigma": sigma_nl, "n_settings": int(len(per)),
            "estimator": "phase7_purity_estimator.estimate_nl"}


def heron_like_noise_model():
    """A calibrated Heron noise model if a fake backend is available, else a
    generic Heron-scale depolarizing+readout model (labeled as such)."""
    try:
        from qiskit_ibm_runtime.fake_provider import FakeTorino
        from qiskit_aer.noise import NoiseModel
        return NoiseModel.from_backend(FakeTorino()), "FakeTorino (Heron r1)"
    except Exception:
        from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
        nm = NoiseModel()
        nm.add_all_qubit_quantum_error(depolarizing_error(2e-4, 1), ["sx", "x", "rz", "ry", "p"])
        nm.add_all_qubit_quantum_error(depolarizing_error(3e-3, 2), ["cx", "cz", "ecr"])
        nm.add_all_qubit_readout_error(ReadoutError([[0.99, 0.01], [0.012, 0.988]]))
        return nm, "generic Heron-scale (2q depol 3e-3, ro 1e-2)"


def main():
    rng = np.random.default_rng(7)
    rho_W = exact_wedge_rdm()
    P_W_exact = float(np.real(np.trace(rho_W @ rho_W)))
    p_l_exact, nl_exact = nl_from_wedge_purity(P_W_exact)
    print("Track D Phase 7 -- purity-only NL estimator + shot budget\n")
    print(f"1. NOISELESS VALIDATION (exact wedge RDM):")
    print(f"   P_wedge = {P_W_exact:.5f}  (analytic 0.15625)")
    print(f"   P_L = 4 P_wedge = {p_l_exact:.5f}  (analytic 0.625)")
    print(f"   NL = {nl_exact:.5f}  (analytic 0.2996)  "
          f"[{'OK' if abs(nl_exact - 0.2996) < 1e-3 else 'MISMATCH'}]\n")

    print("2. MONTE-CARLO SHOT BUDGET (30 reps per config, direct-RDM sim):")
    print(f"   {'N_set':>6} {'N_shot':>7} {'<NL>':>8} {'sigma(NL)':>10} {'bias':>8}")
    budget = []
    for n_set, n_shot in [(100, 256), (150, 512), (250, 512), (400, 512), (400, 1024)]:
        nls = []
        for _ in range(30):
            pw = purity_from_rdm(rho_W, n_set, n_shot, rng)
            nls.append(nl_from_wedge_purity(pw)[1])
        nls = np.array(nls)
        budget.append((n_set, n_shot, nls.mean(), nls.std()))
        print(f"   {n_set:>6} {n_shot:>7} {nls.mean():>8.4f} {nls.std():>10.4f} "
              f"{nls.mean() - nl_exact:>+8.4f}")
    # recommend the smallest setting count with sigma(NL) <~ 0.05
    ok = [b for b in budget if b[3] < 0.05]
    rec = min(ok, key=lambda b: b[0] * b[1]) if ok else min(budget, key=lambda b: b[3])
    print(f"   -> RECOMMEND N_settings={rec[0]}, N_shots={rec[1]} "
          f"(sigma(NL)~{rec[3]:.3f}); ~{rec[0]} circuits fit a 600s window.\n")

    print("3. DEVICE-NOISE REHEARSAL (predicted hardware NL under decoherence):")
    nm, nm_label = heron_like_noise_model()
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    base = prep_circuit(THETA, True)
    t2q = sum(1 for g in transpile(base, basis_gates=["sx", "rz", "cz", "x"],
                                   optimization_level=1).data if len(g.qubits) == 2)
    print(f"   prep transpiled 2q-gate count (no routing) ~{t2q}; hardware routing on")
    print(f"   heavy-hex adds SWAPs, so the real depth is higher than this floor.")
    sim = AerSimulator(noise_model=nm)
    n_set_noise = 120
    circs, _ = shadow_circuits(base, np.random.default_rng(3))
    per = []
    for qc in circs[:n_set_noise]:
        cnt = sim.run(transpile(qc, sim, optimization_level=1), shots=512).result().get_counts()
        marg = np.zeros(8)
        for bits, c in cnt.items():
            rb = bits[::-1]; idx = sum(int(rb[q]) << j for j, q in enumerate(WEDGE))
            marg[idx] += c
        per.append(_collision_purity(marg, 3))
    pw_noise = float(np.nanmean(per))
    pl_noise, nl_noise = nl_from_wedge_purity(pw_noise)
    retain = 100 * nl_noise / nl_exact
    print(f"   noise model: {nm_label}")
    print(f"   P_wedge(noisy) = {pw_noise:.4f} (max-mixed floor 0.125) -> "
          f"P_L = {pl_noise:.4f} -> NL(noisy) = {nl_noise:.4f}")
    print(f"   ideal NL 0.2996; decoherence retains ~{retain:.0f}% of the signal.\n")

    # optimistic-mitigation bracket: twirl+TREX+DD ~ reduced 2q error + fixed
    # readout. Tells us whether Tier 2 (NL>0.10) is even reachable at this depth.
    from qiskit_aer.noise import NoiseModel, depolarizing_error
    nm_opt = NoiseModel()
    nm_opt.add_all_qubit_quantum_error(depolarizing_error(1e-4, 1), ["sx", "x", "rz", "ry", "p"])
    nm_opt.add_all_qubit_quantum_error(depolarizing_error(8e-4, 2), ["cx", "cz", "ecr"])
    sim_opt = AerSimulator(noise_model=nm_opt)
    per_opt = []
    for qc in circs[:n_set_noise]:
        cnt = sim_opt.run(transpile(qc, sim_opt, optimization_level=1), shots=512).result().get_counts()
        marg = np.zeros(8)
        for bits, c in cnt.items():
            rb = bits[::-1]; idx = sum(int(rb[q]) << j for j, q in enumerate(WEDGE))
            marg[idx] += c
        per_opt.append(_collision_purity(marg, 3))
    nl_opt = nl_from_wedge_purity(float(np.nanmean(per_opt)))[1]
    print(f"   optimistic-mitigation bracket (2q 8e-4, DD-idealized, no readout): "
          f"NL ~ {nl_opt:.3f}")
    print(f"   => Tier 2 (NL>0.10) reachable with strong mitigation: "
          f"{nl_opt > 0.10}\n")

    survives = nl_noise > 2 * rec[3]
    print("CRITICAL PREP FINDING:")
    if not survives:
        print(f"   As designed, the run is NOISE-DOMINATED: predicted NL {nl_noise:.3f} is")
        print(f"   below the sampling resolution 2*sigma~{2*rec[3]:.3f}. A naive submission")
        print(f"   would read ~noise floor. DO NOT burn quota on the naive circuit.")
        print("   MITIGATION PATH before firing (in order of leverage):")
        print("   (a) error mitigation that worked at 21-42 2q gates before: Pauli")
        print("       twirling + TREX readout + XY4 DD (raises effective purity);")
        print("   (b) shallower encoding / single-tile variant to cut the ~"
              f"{t2q}+routing 2q depth (purity ~ (1-p)^(2*#2q), so depth is the lever);")
        print("   (c) if unmitigated, treat the run as DEVICE CHARACTERIZATION: measure")
        print("       P_wedge above the 0.125 floor and check it matches this model.")
    else:
        print(f"   Signal survives: predicted NL {nl_noise:.3f} > 2*sigma. Fire as designed.")

    print("\nPRE-REGISTRATION (Phase 7 purity-only, honest two-tier):")
    print(f"   - Prep: two [[5,1,3]] tiles, logical cos(pi/6)|00>+e^(i pi/4)sin(pi/6)|11>.")
    print(f"   - Measure: randomized single-qubit Cliffords, N_settings={rec[0]} x "
          f"{rec[1]} shots, wedge W=(0,1,2), + twirl/TREX/DD mitigation.")
    print(f"   - Report: NL from P_L=4 P_wedge via -log2(4 P_L^2-6 P_L+3). Noiseless")
    print(f"     0.2996; sampling sigma ~{rec[3]:.3f}; UNMITIGATED noise prediction ~{nl_noise:.3f}.")
    print(f"   - TIER 1 (achievable): P_wedge measurably > 0.125 max-mixed floor AND")
    print(f"     consistent with the noise model -> pipeline + device understood.")
    print(f"   - TIER 2 (stretch, needs mitigation): NL > 0.10 at >=2 sigma -> the")
    print(f"     unremovable magic read from ONE wedge survives decoherence.")
    print(f"   - Erasable species stays simulation-established (single-wedge Delta=0);")
    print(f"     SRE-shadow route too high-variance for this window (deferred).")


if __name__ == "__main__":
    main()
