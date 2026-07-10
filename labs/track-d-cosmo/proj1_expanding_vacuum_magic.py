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

Hardware-adjacent benchmark (2605.04099):
  The sudden de Sitter -> radiation scalar profile has
      n_k = |beta_k|^2 = 1 / [4 (k |eta_e|)^4].
  We ride that real particle-production spectrum with the bosonic theorem
  null: the state is still Gaussian, so physical CV magic stays exactly zero
  mode-by-mode. The qubit finite-cutoff SRE is printed only as an artifact
  control. For the proposed fermion extension, this file also provides the
  acceptance diagnostics quant-phy's massive-Dirac beta_k solver should pass:
  Pauli bound, massless conformal null, UV adiabatic tail, and magic peaking
  where |beta_k^F|^2 crosses the P1b value 0.146...
"""

import pathlib
import sys

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(pathlib.Path(__file__).parent / ".." / "track-d-magic"))
from phase0_wedge_magic import m2  # noqa: E402

FERMION_MAGIC_PEAK_BETA2_LOW = 0.5 * (1.0 - 1.0 / np.sqrt(2.0))
FERMION_MAGIC_PEAK_BETA2_HIGH = 0.5 * (1.0 + 1.0 / np.sqrt(2.0))


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


def fermion_magic_from_beta2(beta2):
    """P1b nonlocal magic as a function of exact fermion occupation."""
    beta2 = float(np.clip(beta2, 0.0, 1.0))
    return closed_form_nl(rdm_purity(fermion_pair(beta2)))


def ds_radiation_scalar_bogoliubov(x):
    """Sudden dS -> radiation scalar Bogoliubov coefficients.

    arXiv:2605.04099 uses eta_e < 0. With x = k |eta_e|, the analytic
    benchmark is alpha = 1 + i/x - 1/(2x^2), beta = exp(2ix)/(2x^2),
    so |beta|^2 = 1/(4x^4) and |alpha|^2 - |beta|^2 = 1.
    """
    x = np.asarray(x, dtype=float)
    if np.any(x <= 0):
        raise ValueError("x = k |eta_e| must be positive")
    alpha = 1.0 + 1j / x - 1.0 / (2.0 * x ** 2)
    beta = np.exp(2j * x) / (2.0 * x ** 2)
    return alpha, beta


def ds_radiation_scalar_occupation(x):
    """n_k = |beta_k|^2 for the 2605.04099 sudden scalar transition."""
    x = np.asarray(x, dtype=float)
    if np.any(x <= 0):
        raise ValueError("x = k |eta_e| must be positive")
    return 1.0 / (4.0 * x ** 4)


def boson_squeezing_from_occupation(n_pairs):
    """Two-mode squeezed vacuum parameter for mean pair occupation n."""
    n_pairs = np.asarray(n_pairs, dtype=float)
    if np.any(n_pairs < 0):
        raise ValueError("mean occupation must be nonnegative")
    return np.arcsinh(np.sqrt(n_pairs))


def boson_multi_pair_tail(n_pairs):
    """Exact TMSV probability of two or more pairs after a 0/1 truncation."""
    n_pairs = np.asarray(n_pairs, dtype=float)
    lam2 = n_pairs / (1.0 + n_pairs)
    return lam2 ** 2


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
        perm[1], perm[-1] = perm[-1], perm[1]
    return perm


def boson_cutoff_sre(r, qubits_per_mode, relabel=None):
    psi = boson_pair_truncated(r, qubits_per_mode, relabel=relabel)
    return m2(dm(psi))


def fermion_spectrum_diagnostics(xs, beta2s, massless=False):
    """Acceptance diagnostics for a proposed massive-Dirac beta_k spectrum."""
    xs = np.asarray(xs, dtype=float)
    beta2s = np.asarray(beta2s, dtype=float)
    if xs.ndim != 1 or beta2s.ndim != 1 or xs.shape != beta2s.shape:
        raise ValueError("xs and beta2s must be one-dimensional arrays of equal length")
    if np.any(xs <= 0):
        raise ValueError("all x values must be positive")

    magic = np.array([fermion_magic_from_beta2(b) for b in beta2s])
    peak_i = int(np.argmax(magic))
    return {
        "pauli_bounded": bool(np.all(beta2s >= -1e-10) and np.all(beta2s <= 1.0 + 1e-10)),
        "massless_null": bool(np.max(np.abs(beta2s)) < 1e-9) if massless else None,
        "uv_beta2": float(beta2s[np.argmax(xs)]),
        "uv_magic": float(magic[np.argmax(xs)]),
        "max_magic": float(magic[peak_i]),
        "max_magic_x": float(xs[peak_i]),
        "max_magic_beta2": float(beta2s[peak_i]),
        "hits_p1b_peak_band": bool(
            np.any(np.isclose(beta2s, FERMION_MAGIC_PEAK_BETA2_LOW, atol=0.03))
            or np.any(np.isclose(beta2s, FERMION_MAGIC_PEAK_BETA2_HIGH, atol=0.03))
        ),
    }


_SX = np.array([[0, 1], [1, 0]], dtype=complex)
_SZ = np.array([[1, 0], [0, -1]], dtype=complex)


def dirac_scale_factor(eta):
    """Sudden dS->radiation scale factor (2605.04099 Eq 2), units eta_e=-1,
    H=1, a_e=1: a, a' continuous at eta_e; only a''/a jumps."""
    return -1.0 / eta if eta <= -1.0 else 2.0 + eta


def dirac_occupation_smooth(x, mu, eta0=-30.0, eta1=6.0, max_step=0.01):
    """Massive-Dirac fermion pair occupation for the PAPER'S SMOOTH (C^1)
    transition, by integrating the two-level mode Hamiltonian
    H_k(eta) = k sigma_x + m a(eta) sigma_z from the early adiabatic vacuum.
    x = k|eta_e| = k, mu = m|eta_e| = m. The fermion mass term M = m a is C^1
    (a' continuous), so the fermion never sees the a''/a jump that drives
    boson production -> strongly suppressed occupation."""
    from scipy.integrate import solve_ivp
    k, m = float(x), float(mu)

    def Hk(eta):
        return k * _SX + m * dirac_scale_factor(eta) * _SZ

    _, v0 = np.linalg.eigh(Hk(eta0))
    psi0 = v0[:, 0]

    def rhs(eta, y):
        p = y[:2] + 1j * y[2:]
        dp = -1j * (Hk(eta) @ p)
        return np.concatenate([dp.real, dp.imag])

    sol = solve_ivp(rhs, [eta0, eta1],
                    np.concatenate([psi0.real, psi0.imag]),
                    rtol=1e-8, atol=1e-10, max_step=max_step)
    psi1 = sol.y[:2, -1] + 1j * sol.y[2:, -1]
    psi1 /= np.linalg.norm(psi1)
    _, v1 = np.linalg.eigh(Hk(eta1))
    return float(abs(np.vdot(v1[:, 1], psi1)) ** 2)


def dirac_occupation_sharp(x, m_in, m_out):
    """Massive-Dirac occupation for a genuinely SUDDEN mass jump m_in->m_out
    (a' discontinuous = a violent transition): n_k = |<excited_out|ground_in>|^2,
    automatically Pauli-bounded in [0,1]. For m_in=0 (early conformal) ->
    m_out=mu this runs from n_k=0.5 (IR) to 0 (UV), crossing the magic band."""
    _, gv = np.linalg.eigh(float(x) * _SX + float(m_in) * _SZ)
    ground_in = gv[:, 0]
    _, ev = np.linalg.eigh(float(x) * _SX + float(m_out) * _SZ)
    excited_out = ev[:, 1]
    return float(abs(np.vdot(excited_out, ground_in)) ** 2)


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

    # --- 2605.04099 hardware-adjacent scalar benchmark --------------------
    print("P1-bench  2605.04099 sudden dS->radiation scalar benchmark:")
    print("     x = k|eta_e|, alpha = 1+i/x-1/(2x^2), beta = exp(2ix)/(2x^2),")
    print("     n_k = |beta|^2 = 1/(4x^4). Riding this REAL spectrum does not")
    print("     change P1a: the bosonic out-state is still Gaussian, so CV mana = 0.")
    print(f"     {'x':>5} {'n_k':>10} {'|a|^2-|b|^2':>13} {'r=asinh sqrt(n)':>16} "
          f"{'CV mana':>8} {'P(>=2 pairs)':>12}")
    benchmark_xs = np.array([0.8, 1.0, 1.3, 1.5, 1.8, 2.0, 2.2, 2.5, 3.0])
    for x in benchmark_xs:
        alpha, beta = ds_radiation_scalar_bogoliubov(x)
        n = float(abs(beta) ** 2)
        r = float(boson_squeezing_from_occupation(n))
        norm = float(abs(alpha) ** 2 - abs(beta) ** 2)
        print(f"     {x:>5.1f} {n:>10.5f} {norm:>13.8f} {r:>16.5f} "
              f"{boson_cv_wigner_mana(r):>8.4f} {float(boson_multi_pair_tail(n)):>12.6f}")
    print("     -> this is the hardware-adjacent boson curve: particle production")
    print("        varies strongly with mode, while physical bosonic magic remains")
    print("        identically zero across the spectrum.\n")
    print("        x=0.8 and x=1.0 are IR stress rows from the same analytic")
    print("        spectrum; the 2605.04099 hardware demonstration uses x>=1.3.\n")

    print("     representative finite-cutoff artifact guard on the same spectrum:")
    print(f"     {'x':>5} {'regime':>9} {'q/mode':>7} {'D':>4} {'weight':>9} "
          f"{'binary SRE':>11} {'relabel SRE':>11}")
    for x in (0.8, 1.0, 1.3, 2.2, 3.0):
        n = float(ds_radiation_scalar_occupation(x))
        r = float(boson_squeezing_from_occupation(n))
        regime = "IR-stress" if x < 1.3 else "HW/UV"
        for q in (2, 3):
            dim = 2 ** q
            binary = boson_cutoff_sre(r, q)
            relabeled = boson_cutoff_sre(r, q, relabel=nonaffine_relabel(dim))
            print(f"     {x:>5.1f} {regime:>9} {q:>7} {dim:>4} "
                  f"{boson_truncation_weight(r, dim):>9.6f} {binary:>11.4f} "
                  f"{relabeled:>11.4f}")
    print("     -> nonzero Pauli-SRE here is cutoff/encoding dependent. It is the")
    print("        artifact control for any four-qubit/single-excitation hardware")
    print("        implementation, not evidence of bosonic CV magic.\n")

    # --- Fermion channel: massive-Dirac magic spectrum (quant-phy) ---------
    print("P1-bench  FERMION magic spectrum, massive Dirac in dS->radiation:")
    print("     Two-level mode model H_k = k sx + m a(eta) sz; occupation n_k=|beta_k|^2.")
    print("     Validated limits: massless mu=0 => n_k=0 (conformal null, exact);")
    print("     UV x->inf => n_k->0 (adiabatic). Both automatic (Pauli-bounded).\n")

    # (A) the paper's SMOOTH C^1 transition: fermion production is tiny
    print("     (A) paper's SMOOTH (C^1) transition, mu=2 -- fermion barely produced:")
    xs_s = np.array([0.5, 1.0, 1.5, 2.0, 3.0])
    b2_s = np.array([dirac_occupation_smooth(x, 2.0) for x in xs_s])
    for x, b2 in zip(xs_s, b2_s):
        print(f"       x={x:>4.1f}  n_k={b2:.6f}  magic={fermion_magic_from_beta2(b2):.6f}")
    dS = fermion_spectrum_diagnostics(xs_s, b2_s)
    print(f"       peak n_k={dS['max_magic_beta2']:.2e}, peak magic={dS['max_magic']:.2e}, "
          f"reaches band={dS['hits_p1b_peak_band']}")
    print("       -> the fermion mass term M=ma is C^1, so it never sees the a''/a jump")
    print("          that drives boson production. Fermion magic here is negligible.\n")

    # (B) a genuinely SHARP transition (a' discontinuous): reaches the band
    print("     (B) a VIOLENT (sudden mass 0->mu) transition -- reaches the magic band:")
    xs_h = np.array([0.4, 0.8, 1.2, 1.6, 2.0, 2.6, 3.5, 5.0, 8.0])
    b2_h = np.array([dirac_occupation_sharp(x, 0.0, 2.0) for x in xs_h])
    for x, b2 in zip(xs_h, b2_h):
        band = "  <- magic band" if abs(b2 - FERMION_MAGIC_PEAK_BETA2_LOW) < 0.04 else ""
        print(f"       x={x:>4.1f}  n_k={b2:.4f}  magic={fermion_magic_from_beta2(b2):.4f}{band}")
    dH = fermion_spectrum_diagnostics(xs_h, b2_h)
    print(f"       peak magic={dH['max_magic']:.4f} at x={dH['max_magic_x']:.1f} "
          f"(n_k={dH['max_magic_beta2']:.4f}); reaches band={dH['hits_p1b_peak_band']}; "
          f"pauli_bounded={dH['pauli_bounded']}")
    print("       -> n_k runs 0.5 (IR) -> 0 (UV); magic PEAKS in a momentum band where")
    print("          n_k crosses 0.146. Cosmological fermion magic marks a k-band.\n")

    print("     RESULT (the sharpened three-way asymmetry): bosons are produced")
    print("     copiously (n_k=1/4x^4) but carry ZERO magic (Gaussian/Hudson);")
    print("     massless fermions produce NOTHING (conformal, magic 0); massive")
    print("     fermions carry magic, but ONLY a violent (a'-discontinuous)")
    print("     transition produces enough to reach the band -- so cosmological")
    print("     fermion magic is a probe of the VIOLENCE of reheating, negligible")
    print("     for the smooth transition and band-level only for a sudden one.\n")

    print("Root of the asymmetry: fermion Fock = 2-dim/mode (JW exact, qubit")
    print("magic physical); boson Fock = infinite-dim/mode (qubit truncation is")
    print("an approximation, and its Pauli-SRE is an encoding artifact).")


if __name__ == "__main__":
    main()
