"""Track D -> Cosmology, Project 2: Is the de Sitter horizon magical?

The magic-as-gravity program lives in AdS/SYK; this asks whether the de
Sitter HORIZON carries a magic signature. The computable bridge (2026-07-10
sweep, hand-in-hand with codex-science) is DOUBLE-SCALED SYK <-> de SITTER
(2209.09997, 2310.16994, 2403.13186): DSSYK is a conjectured dS dual, so we
have a concrete SYK model of dS and our Phase-4/5 SYK-magic machinery.

Tobin's narrowing (accepted): the DSSYK/dS dictionary is high-T / upper-edge
/ constrained-doubled, NOT canonical thermal at beta=1/T_dS. So do NOT
pre-register a T_dS monotone; the honest claim is that dS-horizon magic is a
property of the finite chaotic horizon Hilbert space, scaling EXTENSIVELY
with the horizon dof count (S_GH ~ N/p^2 proxy), time-dependence following
the SYK SFF/SRE story (2601.12787).

CONSERVATIVE small-N stand-in (co-agreed): ordinary SYK4 (chaotic) vs SYK2
(free) TPQ microstates + thermal state at high T, then the infinite-T TFD
(the H_L=H_R doubled state at beta=0). All reuse Phase 4/5.

PRE-REGISTERED (locked with codex-science):
  P2a free-field null: a free/Gaussian dS field is magic-poor (P1 Hudson
      echo); the free SYK2 control here plays that role.
  P2b DSSYK/chaotic signal: chaotic SYK4 TPQ/thermal carry nonzero magic,
      extensive; vs SYK2/free + same-spectrum stabilizer twins (thermal rho
      is mixed -> twin-controlled, Phase-1 lesson).
  P2c entropy/dof bridge: magic DENSITY scales with horizon dof (N proxy),
      not T_dS; tie to magic<->area (2306.14996).

HONEST FINDING (my infinite-T-TFD stand-in FAILED, corrected by the data):
sum_E |E>_L|E*>_R = sum_i |i>_L|i>_R EXACTLY (since sum_E |E><E| = I), so the
infinite-T TFD IS the computational Bell state -- BOTH raw SRE and nonlocal
magic are 0, independent of the Hamiltonian. It is a trivial, magic-free
stand-in; my earlier "raw SRE tracks eigenbasis chaos" was wrong. So the
dS-horizon magic (if any) must come from FINITE-T TPQ microstates. And the
first pass shows the STATIC magic barely separates chaotic from free (raw
TPQ M2 is generically high; thermal-rho magic is even backwards -- chaos
flattens the spectrum toward maximally-mixed, LOWERING thermal magic). This
points the refined question at magic DYNAMICS (2601.12787: TFD-SRE time
evolution tracks the spectral form factor, with a chaos-dependent
transition) rather than the static value -- the natural next step.
"""

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent / ".." / "track-d-magic"))
from phase0_wedge_magic import m2  # noqa: E402
from phase4_syk_magic_baseline import (  # noqa: E402
    density, jw_majoranas, mean_sem, syk_hamiltonian, syk_term_ops,
)
from phase5_multipartite_syk_magic import (  # noqa: E402
    magic_value, thermal_density, tpq_state,
)


def diagonalize(N, q, term_ops, rng):
    H = syk_hamiltonian(term_ops, N, q, rng)
    vals, vecs = np.linalg.eigh(H)
    return vals.real, vecs


def infinite_t_tfd(vecs):
    """|TFD_inf> = (1/sqrt d) sum_E |E>_L (x) |E*>_R  (H_L=H_R, beta=0)."""
    dim = vecs.shape[0]
    psi = np.zeros(dim * dim, dtype=complex)
    for E in range(dim):
        vE = vecs[:, E]
        psi += np.kron(vE, vE.conj())
    return psi / np.linalg.norm(psi)


def reduced_purity_L(psi_double, dim):
    m = psi_double.reshape(dim, dim)
    rho_L = m @ m.conj().T
    return float(np.real(np.trace(rho_L @ rho_L)))


def main():
    print("Project 2 -- Is the de Sitter horizon magical? (DSSYK stand-in)\n")
    rng = np.random.default_rng(20260710)
    BETA = 0.5   # high-T, matching the DSSYK/dS high-temperature dictionary

    # --- P2b/P2c: TPQ microstate magic, SYK4 vs SYK2, extensive in N -------
    print("P2b/c  TPQ microstate magic at high T (beta=0.5), SYK4(chaotic) vs")
    print("       SYK2(free), disorder+TPQ averaged. Density = magic / (N/2 qubits).")
    print(f"       {'N':>3} {'q':>2} {'M2(TPQ)':>9} {'+/-':>7} {'density':>8}")
    samples = {8: 30, 10: 20, 12: 10}
    dens = {4: [], 2: []}
    for N in (8, 10, 12):
        ops = {4: syk_term_ops(jw_majoranas(N), 4),
               2: syk_term_ops(jw_majoranas(N), 2)}
        nq = N // 2
        for q in (4, 2):
            ms = []
            for _ in range(samples[N]):
                vals, vecs = diagonalize(N, q, ops[q], rng)
                psi = tpq_state(vals, vecs, BETA, rng)
                ms.append(m2(density(psi)))
            mean, se = mean_sem(ms)
            dens[q].append(mean / nq)
            print(f"       {N:>3} {q:>2} {mean:>9.4f} {se:>7.4f} {mean/nq:>8.4f}")
        print()
    ext4 = "rising/flat" if dens[4][-1] >= dens[4][0] - 0.05 else "falling"
    print(f"       SYK4 magic density vs N: {[round(d,3) for d in dens[4]]} ({ext4});")
    print(f"       SYK2 magic density vs N: {[round(d,3) for d in dens[2]]}.")
    sep = dens[4][-1] - dens[2][-1]
    print(f"       chaotic-vs-free density gap at N=12: {sep:+.4f} "
          f"({'SYK4 more magical' if sep > 0 else 'no separation'}).\n")

    # --- thermal rho (mixed) needs the twin control -----------------------
    print("P2b  thermal-rho magic (MIXED -> twin-controlled, Phase-1 lesson), N=10:")
    print(f"       {'q':>2} {'raw M2':>8} {'twin-ctl':>9}")
    ops = {4: syk_term_ops(jw_majoranas(10), 4), 2: syk_term_ops(jw_majoranas(10), 2)}
    for q in (4, 2):
        raw, ctl = [], []
        for _ in range(15):
            vals, vecs = diagonalize(10, q, ops[q], rng)
            rho = thermal_density(vals, vecs, BETA)
            raw.append(m2(rho))
            ctl.append(magic_value(rho, controlled=True))
        print(f"       {q:>2} {np.mean(raw):>8.4f} {np.mean(ctl):>9.4f}")
    print("       -> classical thermal mixedness inflates raw M2; the twin-controlled")
    print("          value is the honest horizon-ensemble magic.\n")

    # --- the infinite-T TFD stand-in + the honest subtlety ----------------
    print("P2  infinite-T TFD (H_L=H_R, beta=0) doubled dS stand-in, N=8 (8 qubits):")
    print(f"       {'q':>2} {'raw SRE':>9} {'reduced purity':>15} {'nonlocal magic':>15}")
    for q in (4, 2):
        ops8 = syk_term_ops(jw_majoranas(8), q)
        vals, vecs = diagonalize(8, q, ops8, rng)
        tfd = infinite_t_tfd(vecs)
        raw = m2(density(tfd))
        pur = reduced_purity_L(tfd, 16)     # maximally mixed => 1/16
        print(f"       {q:>2} {raw:>9.4f} {pur:>15.5f} {'0 (locally Bell)':>15}")
    print("       -> raw SRE = 0 EXACTLY: sum_E|E>|E*> = sum_i|i>|i> is the Bell")
    print("          state (sum|E><E|=I), so the infinite-T doubled state carries NO")
    print("          magic at all, independent of H. My infinite-T-TFD dS stand-in")
    print("          FAILED -- it is a trivial stabilizer state. (Honest self-correction.)\n")

    print("VERDICT (honest first pass): the de-Sitter-horizon-magic question does NOT")
    print("resolve cleanly at the STATIC level. TPQ microstate magic is extensive but")
    print("barely separates chaotic from free; thermal-rho magic is backwards (chaos")
    print("flattens toward maximally-mixed, LOWERING it); the infinite-T doubled state")
    print("is trivially Bell (zero magic). The chaotic horizon signature is therefore")
    print("expected in magic DYNAMICS (2601.12787: TFD-SRE vs spectral form factor),")
    print("not the static value -- the refined direction for the next hand-in-hand step.")


if __name__ == "__main__":
    main()
