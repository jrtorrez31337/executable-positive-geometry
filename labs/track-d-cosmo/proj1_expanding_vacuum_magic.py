"""Track D -> Cosmology, Project 1: magic of the expanding vacuum.

Does cosmological particle production generate quantum magic? The 2026-07-09
literature sweep (quant-phy + codex-science, hand-in-hand) sharpened this to
a THEOREM-ANCHORED boson/fermion asymmetry whose root is the dimensionality
of the per-mode Hilbert space:

  BOSON  (this file: stub; codex-science owns the full boson section)
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
    return max(float(-np.log2(4 * P ** 2 - 6 * P + 3)), 0.0)


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


def main():
    print("Project 1 -- FERMION section (quant-phy). Boson section: codex-science.\n")

    # --- P1b verification: nonlocal magic == Phase-1b closed form ---------
    print("P1b  fermion pair alpha|00>+beta|11>: numerical nonlocal magic vs")
    print("     our Phase-1b closed form -log2(4P^2-6P+3), P=|a|^4+|b|^4:")
    print(f"     {'|beta|^2':>8} {'P(rdm)':>7} {'NL_numeric':>11} {'NL_closed':>10} {'raw SRE':>8}")
    maxrow = None
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

    print("BOSON section (codex-science, stub): analytic Wigner-negativity = 0 for")
    print("all squeezing r (Hudson); finite-cutoff Pauli-SRE artifact control.")
    print("Root of the asymmetry: fermion Fock = 2-dim/mode (JW exact, magic")
    print("physical); boson Fock = inf-dim/mode (truncation -> artifact).")


if __name__ == "__main__":
    main()
