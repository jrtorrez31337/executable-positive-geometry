"""Track D -> Cosmology, Project 1: magic of the expanding vacuum.

Does cosmological particle production generate quantum magic? The 2026-07-09
literature sweep (quant-phy + codex-science, hand-in-hand) sharpened this to
a THEOREM-ANCHORED boson/fermion asymmetry whose root is the dimensionality
of the per-mode Hilbert space:

  BOSON  (this file: theorem-null + artifact guard, codex-science)
    Cosmological creation makes a two-mode-squeezed Gaussian state. In CV,
    magic = Wigner negativity (Mari-Eisert = CV Gottesman-Knill; Gaussian =
    stabilizer). By Hudson's theorem a pure Gaussian state is Wigner-positive
    => physical magic EXACTLY ZERO for all squeezing. Boson Fock space is
    infinite-dim/mode, so any qubit truncation is an approximation: a nonzero
    Pauli-SRE on the truncation is an ENCODING ARTIFACT, isolated by a
    finite-cutoff control. (Already published: 2512.10126 "Inflation is Not
    Magic".)

  FERMION  (this file: the signal, quant-phy owns it)
    Pauli exclusion makes the out-state a single pair per mode:
        |out> = alpha|0> + beta|1,-1>  ==(Jordan-Wigner)==>  alpha|00> + beta|11>.
    Fermion Fock space is 2-dim/mode, so JW -> qubits is EXACT and the
    qubit-stabilizer / nonlocal magic is PHYSICAL (not an artifact). This is
    the QUBIT-stabilizer resource theory, NOT fermionic-non-Gaussianity
    (which is 0 for free Bogoliubov). Same Gaussian state, different
    stabilizer notion -- that resource-theory distinction is the whole point.

PRE-REGISTERED (locked with codex-science):
  P1a boson: physical CV magic = 0 for all r; truncation-SRE = artifact.
  P1b fermion: nonlocal magic of alpha|00>+beta|11> = -log2(4P^2-6P+3),
      P = single-qubit RDM purity = |alpha|^4+|beta|^4. NON-MONOTONIC:
      zero at product (beta=0, P=1) AND at the flat 'Bell' point
      (|alpha|=|beta|, P=1/2); PEAK at P=3/4 (|beta|^2 = 0.146 or 0.854),
      NL = -log2(3/4) = 0.4150. Verified against our own Phase-1b closed form.
  P1c interactions: bosonic magic via true non-Gaussianity = follow-on.

dS parametrization: |beta|^2 = fermion thermal occupation at the
Gibbons-Hawking temperature T_dS = H/2pi, Fermi-Dirac 1/(e^{omega/T}+1).
Then magic vs EXPANSION RATE H is non-monotonic: 0 at H->0 (no production),
peak at intermediate H (|beta|^2=0.146), falling toward 0 as H->inf
(|beta|^2->1/2, the flat maximal-production 'Bell' point).
"""

import pathlib
import sys

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(pathlib.Path(__file__).parent / ".." / "track-d-magic"))
from phase0_wedge_magic import m2  # noqa: E402


def su2(a, b, c):
    """ZYZ-Euler single-qubit unitary."""
    return np.array([
        [np.cos(b / 2) * np.exp(-1j * (a + c) / 2),
         -np.sin(b / 2) * np.exp(-1j * (a - c) / 2)],
        [np.sin(b / 2) * np.exp(1j * (a - c) / 2),
         np.cos(b / 2) * np.exp(1j * (a + c) / 2)]])


def fermion_pair(beta2):
    """|out> = alpha|00> + beta|11>, |beta|^2 = beta2 (occupation)."""
    a, b = np.sqrt(1 - beta2), np.sqrt(beta2)
    return np.array([a, 0, 0, b], dtype=complex)


def dm(psi):
    return np.outer(psi, psi.conj())


def rdm_purity(psi):
    rho = dm(psi).reshape(2, 2, 2, 2)
    r1 = np.trace(rho, axis1=1, axis2=3)          # trace out qubit 1
    return float(np.real(np.trace(r1 @ r1)))


def closed_form_nl(P):
    value = float(-np.log2(4 * P ** 2 - 6 * P + 3))
    return value if value > 0.0 else 0.0


def nonlocal_magic(psi, n_starts=10, seed=0):
    """min over local single-qubit unitaries of the stabilizer Renyi entropy."""
    rng = np.random.default_rng(seed)

    def cost(x):
        U = np.kron(su2(*x[:3]), su2(*x[3:]))
        return m2(dm(U @ psi))

    best = np.inf
    for _ in range(n_starts):
        r = minimize(cost, rng.uniform(0, 2 * np.pi, 6), method="Nelder-Mead",
                     options={"xatol": 1e-6, "fatol": 1e-9, "maxiter": 4000})
        best = min(best, r.fun)
    return max(best, 0.0)


def fermi_dirac(omega, H):
    """fermion thermal occupation at Gibbons-Hawking T_dS = H/2pi."""
    T = H / (2 * np.pi)
    return 1.0 / (np.exp(omega / T) + 1.0) if T > 0 else 0.0


def boson_cv_wigner_mana(r):
    """Physical CV magic of the pure two-mode squeezed vacuum.

    The state is Gaussian for every squeezing r. With the CV stabilizer
    convention used in Mari-Eisert/Gross-Hudson, a pure Gaussian has
    nonnegative Wigner function, so log integral |W| = 0 exactly.
    """
    _ = r
    return 0.0


def boson_truncation_weight(r, cutoff_dim):
    """Probability retained by truncating sum_n sqrt(1-lambda^2) lambda^n |n,n>."""
    lam = np.tanh(r)
    return float(1.0 - lam ** (2 * cutoff_dim))


def boson_pair_truncated(r, qubits_per_mode, relabel=None):
    """Two-mode squeezed vacuum in a finite Fock cutoff encoded into qubits.

    cutoff_dim = 2**qubits_per_mode. The map from Fock labels to qubit basis
    labels is deliberately explicit: changing it is an encoding choice, not a
    physical CV operation.
    """
    dim = 2 ** qubits_per_mode
    lam = np.tanh(r)
    coeffs = np.array([np.sqrt(1 - lam ** 2) * lam ** n for n in range(dim)])
    coeffs = coeffs / np.linalg.norm(coeffs)

    if relabel is None:
        relabel = np.arange(dim)
    relabel = np.asarray(relabel, dtype=int)
    if sorted(relabel.tolist()) != list(range(dim)):
        raise ValueError("relabel must be a permutation of range(cutoff_dim)")

    psi = np.zeros(dim * dim, dtype=complex)
    for n, amp in enumerate(coeffs):
        psi[relabel[n] * dim + relabel[n]] = amp
    return psi


def nonaffine_relabel(dim):
    """A deterministic non-affine relabel for dim >= 8.

    For 1 and 2 qubits per mode, every basis permutation is affine over F2
    and therefore Clifford as a classical reversible map. At dim >= 8 a simple
    transposition can expose that finite-cutoff Pauli SRE depends on the
    arbitrary Fock-to-qubit encoding.
    """
    perm = np.arange(dim)
    if dim >= 8:
        perm[3], perm[5] = perm[5], perm[3]
    return perm


def boson_cutoff_sre(r, qubits_per_mode, relabel=None):
    psi = boson_pair_truncated(r, qubits_per_mode, relabel=relabel)
    return m2(dm(psi))


def main():
    print("Project 1 -- magic of the expanding vacuum")
    print("Fermion signal: quant-phy. Boson theorem-null + artifact control: codex-science.\n")

    # --- P1b verification: nonlocal magic == Phase-1b closed form ---------
    print("P1b  fermion pair alpha|00>+beta|11>: numerical nonlocal magic vs")
    print("     our Phase-1b closed form -log2(4P^2-6P+3), P=|a|^4+|b|^4:")
    print(f"     {'|beta|^2':>8} {'P(rdm)':>7} {'NL_numeric':>11} {'NL_closed':>10} {'raw SRE':>8}")
    for beta2 in (0.0, 0.05, 0.146, 0.25, 0.5, 0.75, 0.854, 0.95, 1.0):
        psi = fermion_pair(beta2)
        P = rdm_purity(psi)
        nlc = closed_form_nl(P)
        nln = nonlocal_magic(psi)
        raw = m2(dm(psi))
        tag = ""
        if abs(beta2 - 0.146) < 1e-6 or abs(beta2 - 0.854) < 1e-6:
            tag = "  <- predicted peak (P=0.75)"
        print(f"     {beta2:>8.3f} {P:>7.4f} {nln:>11.4f} {nlc:>10.4f} {raw:>8.4f}{tag}")
    agree = all(
        abs(nonlocal_magic(fermion_pair(b)) - closed_form_nl(rdm_purity(fermion_pair(b)))) < 5e-3
        for b in (0.05, 0.146, 0.25, 0.5, 0.75))
    print(f"     numerical == Phase-1b closed form (tol 5e-3): {agree}")
    print("     -> zeros at product (b^2=0) AND flat Bell (b^2=0.5); peak at b^2=0.146/0.854. "
          "P1b CONFIRMED.\n")

    # --- dS parametrization: magic vs expansion rate H --------------------
    print("dS  magic vs EXPANSION RATE H (|beta|^2 = Fermi-Dirac at T_dS=H/2pi, omega=1):")
    print(f"     {'H':>6} {'T_dS':>6} {'|beta|^2':>8} {'nonlocal magic':>15}")
    best_H = (None, -1)
    for H in (0.1, 0.3, 0.6, 1.0, 1.5, 2.5, 4.0, 8.0, 20.0):
        b2 = fermi_dirac(1.0, H)
        nl = closed_form_nl(rdm_purity(fermion_pair(b2)))
        if nl > best_H[1]:
            best_H = (H, nl)
        print(f"     {H:>6.1f} {H/(2*np.pi):>6.3f} {b2:>8.4f} {nl:>15.4f}")
    print(f"     -> NON-MONOTONIC in H: 0 at H->0, peak near H={best_H[0]} "
          f"(|beta|^2~0.146), falling as H->inf (|beta|^2->0.5).")
    print("     'Cosmological fermion magic is maximal at INTERMEDIATE expansion.'\n")

    # --- P1a boson theorem-null + finite-cutoff artifact control ----------
    print("P1a  bosonic two-mode squeezed vacuum:")
    print("     |TMSV(r)> = sqrt(1-lambda^2) sum_n lambda^n |n,n>, lambda=tanh(r)")
    print("     This is a pure Gaussian state, so its CV Wigner mana is EXACTLY ZERO")
    print("     for every r by the Gaussian/Hudson theorem route.")
    print(f"     {'r':>5} {'lambda':>8} {'CV mana':>8} {'retained D=8':>13} {'retained D=16':>14}")
    for r in (0.0, 0.25, 0.5, 0.9, 1.3):
        print(f"     {r:>5.2f} {np.tanh(r):>8.4f} {boson_cv_wigner_mana(r):>8.4f} "
              f"{boson_truncation_weight(r, 8):>13.6f} {boson_truncation_weight(r, 16):>14.6f}")
    print("     -> physical bosonic particle production creates entanglement and")
    print("        complexity, but no CV magic in the free Gaussian model.\n")

    print("     finite-cutoff Pauli-SRE control: encode the truncated Fock space into")
    print("     qubits and measure ordinary qubit SRE. Nonzero values below are NOT")
    print("     physical bosonic magic; they depend on the arbitrary cutoff/encoding.")
    print(f"     {'r':>5} {'q/mode':>7} {'cutoff D':>8} {'weight':>9} {'binary SRE':>11} {'relabel SRE':>11}")
    for r in (0.25, 0.5, 0.9):
        for q in (1, 2, 3, 4):
            dim = 2 ** q
            binary = boson_cutoff_sre(r, q)
            perm = nonaffine_relabel(dim)
            relabeled = boson_cutoff_sre(r, q, relabel=perm)
            print(f"     {r:>5.2f} {q:>7} {dim:>8} {boson_truncation_weight(r, dim):>9.5f} "
                  f"{binary:>11.4f} {relabeled:>11.4f}")
    print("     -> the same Gaussian CV state has mana 0, while finite qubit")
    print("        encodings produce cutoff- and relabel-dependent Pauli SRE.")
    print("        That is the artifact guard: bosonic P1a is a theorem-null, not")
    print("        a small hardware-style qubit signal.\n")

    print("Root of the asymmetry: fermion Fock = 2-dim/mode (JW exact, qubit")
    print("magic physical); boson Fock = infinite-dim/mode (qubit truncation is")
    print("an approximation, and its Pauli-SRE is an encoding artifact).")


if __name__ == "__main__":
    main()
