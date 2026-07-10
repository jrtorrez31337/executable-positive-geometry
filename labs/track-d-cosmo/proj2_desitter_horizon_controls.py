"""Track D -> Cosmology, Project 2 controls: is the de Sitter horizon magical?

This is codex-science/Tobin's control half of the Project-2 split. The
quant-phy half owns the SYK/DSSYK magic computation; this file supplies the
guardrails that keep that signal from being confused with free-field Gaussian
physics, qubit encodings, or mixed-state false positives.

LOCKED PRE-REG, after the 2026-07-10 sweep convergence:
  P2a free-field null/control:
      A free bosonic de Sitter Bunch-Davies/KMS mode is Gaussian, hence has
      zero CV Wigner magic. Any finite Fock-to-qubit Pauli-SRE is an encoding
      artifact, as in Project 1.

      Free fermions are fermionic Gaussian. Their exact Jordan-Wigner image
      can have qubit-stabilizer magic, but that is a resource-theory fact
      about free fermionic Gaussian states, not evidence of interacting
      horizon/DSSYK magic. Thermal free-fermion mixedness must be twin-
      controlled.

  P2b mixed-state discipline:
      Raw mixed-state M2 false-positives on classical mixedness. Thermal rho
      values are compared only after subtracting a same-spectrum stabilizer
      twin, exactly as in Phase 5.

  P2c entropy/dof bridge:
      Do not pre-register a simple T_dS monotone. The honest small-N proxy is
      horizon degrees of freedom: log2 dim for ordinary SYK, and N/p^2 when
      interpreting double-scaled SYK as the dS static-patch model. Compare
      magic density against that proxy, with SYK2/free and stabilizer-twin
      controls.
"""

from __future__ import annotations

import math
import pathlib
import sys
from dataclasses import dataclass

import numpy as np

THIS_DIR = pathlib.Path(__file__).resolve().parent
MAGIC_DIR = THIS_DIR.parent / "track-d-magic"
sys.path.insert(0, str(THIS_DIR))
sys.path.insert(0, str(MAGIC_DIR))

from phase0_wedge_magic import m2  # noqa: E402
from phase5_multipartite_syk_magic import same_spectrum_stabilizer_twin  # noqa: E402
from proj1_expanding_vacuum_magic import (  # noqa: E402
    boson_cutoff_sre,
    boson_cv_wigner_mana,
    boson_squeezing_from_occupation,
    closed_form_nl,
    dm,
    fermion_magic_from_beta2,
    fermion_pair,
    nonaffine_relabel,
    rdm_purity,
)


ZERO_TOL = 1e-10


@dataclass(frozen=True)
class HorizonProxy:
    n_majoranas: int
    log2_dim: float
    dssyk_entropy_proxy: float | None

    @property
    def default_proxy(self) -> float:
        return self.dssyk_entropy_proxy if self.dssyk_entropy_proxy is not None else self.log2_dim


def density(psi: np.ndarray) -> np.ndarray:
    return np.outer(psi, psi.conj())


def twin_controlled_m2(rho: np.ndarray) -> float:
    """Raw mixed-state M2 minus a same-spectrum stabilizer-basis twin."""
    return float(m2(rho) - m2(same_spectrum_stabilizer_twin(rho)))


def ds_temperature(hubble: float) -> float:
    """Gibbons-Hawking temperature T_dS = H / 2 pi."""
    if hubble < 0:
        raise ValueError("H must be nonnegative")
    return hubble / (2.0 * math.pi)


def bose_einstein_occupation(omega: float, hubble: float) -> float:
    """Free boson KMS occupation at the de Sitter temperature."""
    if omega <= 0:
        raise ValueError("omega must be positive")
    temp = ds_temperature(hubble)
    if temp <= 0:
        return 0.0
    x = omega / temp
    if x > 700:
        return 0.0
    return float(1.0 / math.expm1(x))


def fermi_dirac_occupation(omega: float, hubble: float) -> float:
    """Free fermion KMS occupation at the de Sitter temperature."""
    if omega <= 0:
        raise ValueError("omega must be positive")
    temp = ds_temperature(hubble)
    if temp <= 0:
        return 0.0
    x = omega / temp
    if x > 700:
        return 0.0
    return float(1.0 / (math.exp(x) + 1.0))


def boson_thermal_cutoff_density(
    mean_occupation: float,
    qubits_per_mode: int,
    relabel: np.ndarray | None = None,
) -> np.ndarray:
    """Finite qubit encoding of a single-mode Gaussian thermal boson.

    This density matrix is useful only as an artifact diagnostic. The physical
    CV state is Gaussian and has zero Wigner magic; the Pauli-SRE below depends
    on the arbitrary Fock-label-to-qubit-label map.
    """
    if mean_occupation < 0:
        raise ValueError("mean occupation must be nonnegative")
    dim = 2 ** qubits_per_mode
    ratio = mean_occupation / (1.0 + mean_occupation) if mean_occupation > 0 else 0.0
    probs = np.array([(1.0 - ratio) * ratio ** n for n in range(dim)], dtype=float)
    probs = probs / float(np.sum(probs))
    if relabel is not None:
        relabel = np.asarray(relabel, dtype=int)
        if sorted(relabel.tolist()) != list(range(dim)):
            raise ValueError("relabel must be a permutation")
        encoded = np.zeros_like(probs)
        for n, p in enumerate(probs):
            encoded[relabel[n]] = p
        probs = encoded
    return np.diag(probs).astype(complex)


def free_fermion_thermal_density(omega: float, hubble: float) -> np.ndarray:
    """One exact JW qubit for a free fermion KMS mode."""
    f = fermi_dirac_occupation(omega, hubble)
    return np.diag([1.0 - f, f]).astype(complex)


def free_fermion_pair_controls(beta2: float) -> dict[str, float]:
    """Qubit-stabilizer diagnostics for a pure free fermionic Gaussian pair."""
    psi = fermion_pair(beta2)
    rho = dm(psi)
    purity = rdm_purity(psi)
    return {
        "beta2": float(beta2),
        "raw_global_m2": float(m2(rho)),
        "phase1b_nonlocal_magic": float(fermion_magic_from_beta2(beta2)),
        "closed_form_nonlocal_magic": float(closed_form_nl(purity)),
        "fermionic_non_gaussianity": 0.0,
    }


def horizon_proxy(n_majoranas: int, p: int | None = None) -> HorizonProxy:
    """Small-N horizon degree-of-freedom proxy for Project 2.

    Ordinary SYK with N Majoranas maps to N/2 qubits, so log2(dim)=N/2.
    In the double-scaled dS dictionary the entropy-like scale is N/p^2; pass p
    only when a DSSYK p-scaling run is actually being interpreted.
    """
    if n_majoranas <= 0 or n_majoranas % 2:
        raise ValueError("n_majoranas must be a positive even integer")
    if p is not None and p <= 0:
        raise ValueError("p must be positive")
    return HorizonProxy(
        n_majoranas=n_majoranas,
        log2_dim=n_majoranas / 2.0,
        dssyk_entropy_proxy=(n_majoranas / (p * p)) if p is not None else None,
    )


def magic_density(magic: float, n_majoranas: int, p: int | None = None) -> float:
    proxy = horizon_proxy(n_majoranas, p).default_proxy
    if proxy <= 0:
        raise ValueError("horizon proxy must be positive")
    return float(magic / proxy)


def run_self_tests() -> None:
    for prob in (0.15, 0.5, 0.85):
        rho = np.diag([prob, 1.0 - prob]).astype(complex)
        if abs(twin_controlled_m2(rho)) > 1e-9:
            raise AssertionError("same-spectrum twin failed on classical mixture")

    for occupation in (0.0, 0.05, 0.4, 2.0):
        r = float(boson_squeezing_from_occupation(occupation))
        if abs(boson_cv_wigner_mana(r)) > ZERO_TOL:
            raise AssertionError("Gaussian boson should have zero CV mana")

    r = 0.9
    dim = 2 ** 3
    binary = boson_cutoff_sre(r, 3)
    relabeled = boson_cutoff_sre(r, 3, relabel=nonaffine_relabel(dim))
    if abs(binary - relabeled) < 1e-3:
        raise AssertionError("finite boson encoding artifact guard did not fire")

    for hubble in (0.2, 1.0, 6.0):
        rho_f = free_fermion_thermal_density(omega=1.0, hubble=hubble)
        if abs(twin_controlled_m2(rho_f)) > 1e-9:
            raise AssertionError("free fermion KMS mixedness should twin-control to zero")


def print_pre_registration() -> None:
    print("Project 2 controls -- de Sitter horizon magic")
    print("codex-science/Tobin half: free-field nulls, twin controls, dof scaling.\n")
    print("PRE-REGISTERED CONTROLS")
    print("  P2a: free bosonic dS KMS/Bunch-Davies modes are Gaussian -> CV magic 0.")
    print("       Finite Fock-to-qubit SRE is an encoding artifact, not horizon magic.")
    print("  P2b: free fermions are fermionic Gaussian. JW qubit magic can be real in")
    print("       qubit resource theory, but it is not interacting/DSSYK horizon magic.")
    print("  P2c: raw thermal-rho M2 is mixed-state unsafe; use same-spectrum twins.")
    print("  P2d: test magic density against horizon dof proxies, not T_dS monotonicity.\n")


def print_boson_null_table() -> None:
    print("A. FREE BOSON STATIC-PATCH/KMS NULL")
    print("   Free boson states are Gaussian; physical CV Wigner mana is exactly 0.")
    print(f"   {'H':>5} {'T_dS':>7} {'n_BE(omega=1)':>14} {'r':>8} {'CV mana':>8}")
    for hubble in (0.2, 0.6, 1.0, 2.0, 4.0, 8.0):
        nbar = bose_einstein_occupation(omega=1.0, hubble=hubble)
        r = float(boson_squeezing_from_occupation(nbar))
        print(
            f"   {hubble:>5.1f} {ds_temperature(hubble):>7.4f} "
            f"{nbar:>14.6f} {r:>8.4f} {boson_cv_wigner_mana(r):>8.4f}"
        )
    print("   -> no amount of free bosonic thermal occupation creates CV magic.\n")

    print("   finite-cutoff artifact guard for the same Gaussian thermal mode:")
    print(f"   {'H':>5} {'q/mode':>7} {'raw Pauli M2':>13} {'relabel M2':>11}")
    for hubble in (1.0, 4.0, 8.0):
        nbar = bose_einstein_occupation(omega=1.0, hubble=hubble)
        for q in (2, 3, 4):
            dim = 2 ** q
            rho_binary = boson_thermal_cutoff_density(nbar, q)
            rho_relabel = boson_thermal_cutoff_density(
                nbar, q, relabel=nonaffine_relabel(dim)
            )
            print(
                f"   {hubble:>5.1f} {q:>7} {m2(rho_binary):>13.4f} "
                f"{m2(rho_relabel):>11.4f}"
            )
    print("   -> these numbers are cutoff/encoding diagnostics only; the CV answer is 0.\n")


def print_fermion_controls() -> None:
    print("B. FREE FERMION CONTROLS")
    print("   Thermal free-fermion KMS mode: raw M2 can be nonzero from mixedness;")
    print("   same-spectrum twin control removes it exactly.")
    print(f"   {'H':>5} {'T_dS':>7} {'f_FD':>8} {'raw M2':>8} {'twin-ctl M2':>12}")
    for hubble in (0.6, 1.0, 2.0, 4.0, 8.0):
        rho = free_fermion_thermal_density(omega=1.0, hubble=hubble)
        f = float(np.real(rho[1, 1]))
        print(
            f"   {hubble:>5.1f} {ds_temperature(hubble):>7.4f} {f:>8.4f} "
            f"{m2(rho):>8.4f} {twin_controlled_m2(rho):>12.4f}"
        )
    print("   -> a free thermal fermion is not a positive horizon-magic signal.\n")

    print("   Pure free fermionic Gaussian pair alpha|00>+beta|11> under exact JW:")
    print(f"   {'|beta|^2':>9} {'global M2':>10} {'NL magic':>10} {'f-nonGauss':>11}")
    for beta2 in (0.0, 0.05, 0.1464466, 0.25, 0.5):
        row = free_fermion_pair_controls(beta2)
        print(
            f"   {row['beta2']:>9.4f} {row['raw_global_m2']:>10.4f} "
            f"{row['phase1b_nonlocal_magic']:>10.4f} "
            f"{row['fermionic_non_gaussianity']:>11.4f}"
        )
    print("   -> JW qubit magic is physical for qubit stabilizers, but the state is")
    print("      still fermionic Gaussian. P2 must not count this as chaotic DSSYK magic.\n")


def print_horizon_scaling_rule() -> None:
    print("C. HORIZON-DOF SCALING SANITY")
    print("   Compare magic density to the dS/SYK dof proxy; do not fit a simple")
    print("   monotone in T_dS until the DSSYK dictionary is fixed.")
    print(f"   {'N Majoranas':>11} {'log2 dim':>9} {'N/p^2 p=2':>11} {'N/p^2 p=3':>11}")
    for n_majoranas in (8, 10, 12, 14):
        p2 = horizon_proxy(n_majoranas, p=2)
        p3 = horizon_proxy(n_majoranas, p=3)
        print(
            f"   {n_majoranas:>11} {p2.log2_dim:>9.2f} "
            f"{p2.dssyk_entropy_proxy:>11.3f} {p3.dssyk_entropy_proxy:>11.3f}"
        )
    print("   Required comparison when quant-phy's SYK/DSSYK rows arrive:")
    print("      density = twin_controlled_magic / proxy")
    print("      proxy = log2(dim) for ordinary SYK; proxy = N/p^2 for DSSYK.")
    print("      controls = SYK2/free + same-spectrum stabilizer twins.\n")


def main() -> None:
    run_self_tests()
    print_pre_registration()
    print_boson_null_table()
    print_fermion_controls()
    print_horizon_scaling_rule()
    print("VERDICT")
    print("  The free bosonic static-patch/KMS sector is a theorem-null: Gaussian,")
    print("  CV magic zero. Free fermions require resource-theory labeling: exact JW")
    print("  qubit magic can be nonzero, but fermionic non-Gaussianity is zero, and")
    print("  thermal mixedness twin-controls away. Therefore a positive P2 horizon")
    print("  signal must come from the chaotic/interacting SYK/DSSYK sector and be")
    print("  reported as a twin-controlled density against the horizon-dof proxy.")


if __name__ == "__main__":
    main()
