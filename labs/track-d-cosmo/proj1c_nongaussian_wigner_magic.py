"""Track D -> Cosmology, Project 1c: non-Gaussian bosonic Wigner negativity.

P1a established the free-boson theorem-null: a two-mode-squeezed Gaussian
inflationary state has zero continuous-variable Wigner negativity, even though
it is highly squeezed and entangled.

P1c is the interaction turn-on. Ireland and Vennin (arXiv:2601.22219v2)
compute Wigner functions for inflationary perturbations with primordial
non-Gaussianity and find interference fringes/negative regions, with a^2
growth in ultra-slow-roll backgrounds. This file is not a reproduction of
their EFT calculation. It is the minimal executable resource-theory guard:

  * gamma = 0: a pure Gaussian, Wigner negativity exactly zero.
  * gamma > 0: a cubic-phase non-Gaussian deformation, Wigner negativity
    turns on in the true CV phase-space calculation.
  * linear squeezing changes finite-Fock/qubit Pauli-SRE artifacts but leaves
    the CV Wigner negativity invariant, so the physical conclusion is not
    drawn from the qubit cutoff numbers.

The toy state is

    psi_{sigma,gamma}(x) = sigma^(-1/2) pi^(-1/4)
        exp[-(x/sigma)^2/2 + i gamma (x/sigma)^3 / 3].

The cubic phase is a simple proxy for cubic/higher interaction-generated
non-Gaussianity. The sigma parameter is a linear canonical squeeze.
"""

import pathlib
import sys

import numpy as np
from scipy.special import eval_hermite, gammaln

sys.path.insert(0, str(pathlib.Path(__file__).parent / ".." / "track-d-magic"))
from phase0_wedge_magic import m2  # noqa: E402


def trapz(values, grid, axis=-1):
    if hasattr(np, "trapezoid"):
        return np.trapezoid(values, grid, axis=axis)
    return np.trapz(values, grid, axis=axis)


def dm(psi):
    return np.outer(psi, psi.conj())


def cubic_phase_state(x, sigma, gamma):
    """Normalized cubic-phase Gaussian wavefunction on an x grid."""
    u = x / float(sigma)
    psi = (np.pi ** -0.25 / np.sqrt(sigma)) * np.exp(
        -0.5 * u ** 2 + 1j * gamma * u ** 3 / 3.0
    )
    return psi / np.sqrt(trapz(np.abs(psi) ** 2, x))


def interp_complex(x, values, points):
    """Linear interpolation with zero outside the sampled support."""
    real = np.interp(points, x, values.real, left=0.0, right=0.0)
    imag = np.interp(points, x, values.imag, left=0.0, right=0.0)
    return real + 1j * imag


def wigner_negativity(sigma, gamma, grid_n=221):
    """Compute the CV Wigner negative volume by direct quadrature.

    W(q,p) = pi^-1 int dy psi(q+y) psi*(q-y) exp(-2 i p y).
    The phase-space window is scaled with sigma, so a linear squeeze is a
    numerical change of variables rather than a fake source of negativity.
    """
    sigma = float(sigma)
    gamma = float(gamma)
    x_max = 8.0 * sigma
    p_max = 8.0 / sigma
    x = np.linspace(-x_max, x_max, grid_n)
    y = np.linspace(-x_max, x_max, grid_n)
    p = np.linspace(-p_max, p_max, grid_n)
    psi = cubic_phase_state(x, sigma, gamma)
    phase = np.exp(-2j * np.outer(y, p))

    wigner = np.empty((grid_n, grid_n), dtype=float)
    for i, q in enumerate(x):
        left = interp_complex(x, psi, q + y)
        right = interp_complex(x, psi, q - y)
        kernel = left * right.conj()
        wigner[i, :] = (trapz(kernel[:, None] * phase, y, axis=0) / np.pi).real

    norm = float(trapz(trapz(wigner, p, axis=1), x))
    l1 = float(trapz(trapz(np.abs(wigner), p, axis=1), x))
    negative_volume = max(0.0, 0.5 * (l1 - norm))
    return {
        "norm": norm,
        "l1": l1,
        "negative_volume": negative_volume,
        "log_l1": float(np.log2(l1)),
        "min_wigner": float(np.min(wigner)),
    }


def ho_wavefunction(n, x):
    """Harmonic-oscillator Fock basis wavefunction, hbar=m=omega=1."""
    norm = np.exp(-0.25 * np.log(np.pi) - 0.5 * (n * np.log(2.0) + gammaln(n + 1)))
    return norm * eval_hermite(n, x) * np.exp(-0.5 * x ** 2)


def fock_coefficients(sigma, gamma, cutoff_dim, grid_n=6001):
    """Project the CV state to the first cutoff_dim oscillator levels."""
    x_max = max(9.0, 9.0 * float(sigma))
    x = np.linspace(-x_max, x_max, grid_n)
    psi = cubic_phase_state(x, sigma, gamma)
    coeffs = np.array([
        trapz(ho_wavefunction(n, x) * psi, x)
        for n in range(cutoff_dim)
    ])
    retained = float(np.sum(np.abs(coeffs) ** 2))
    return coeffs / np.sqrt(retained), retained


def finite_fock_pauli_sre(sigma, gamma, qubits):
    """Qubit Pauli-SRE after an arbitrary finite Fock cutoff/encoding.

    This is deliberately an artifact diagnostic. It is sensitive to the
    oscillator basis and cutoff, unlike the true CV Wigner negative volume.
    """
    coeffs, retained = fock_coefficients(sigma, gamma, 2 ** qubits)
    return m2(dm(coeffs)), retained


def main():
    print("Project 1c -- bosonic non-Gaussianity turns on Wigner negativity")
    print("Primary source: Ireland & Vennin, arXiv:2601.22219v2.")
    print("Lab status: minimal CV resource-theory proxy, not a full EFT reproduction.\n")

    cache = {}

    def neg(sigma, gamma):
        key = (float(sigma), float(gamma))
        if key not in cache:
            cache[key] = wigner_negativity(*key)
        return cache[key]

    print("P1c-A  cubic-phase non-Gaussian turn-on in true CV phase space")
    print(f"       {'gamma':>7} {'int W':>10} {'min W':>12} "
          f"{'neg volume':>12} {'log2 ||W||1':>13}")
    for gamma in (0.0, 0.12, 0.24, 0.40, 0.70):
        row = neg(1.0, gamma)
        print(f"       {gamma:>7.2f} {row['norm']:>10.8f} {row['min_wigner']:>12.4e} "
              f"{row['negative_volume']:>12.4e} {row['log_l1']:>13.4e}")
    print("       -> gamma=0 is Gaussian and nonnegative. Cubic non-Gaussianity")
    print("          makes Wigner-negative regions visible in the CV calculation.\n")

    print("P1c-B  ultra-slow-roll-style growth proxy")
    print("       Ireland-Vennin find negativity growing like a^2 in USR.")
    print("       Here gamma_eff = gamma0 exp(2 DeltaN) is only the executable")
    print("       scaling proxy; it tests the resource-theory turn-on, not their")
    print("       background solution.")
    print(f"       {'DeltaN':>7} {'gamma_eff':>10} {'neg volume':>12} {'min W':>12}")
    gamma0 = 0.08
    for delta_n in (0.0, 0.3, 0.6, 0.9, 1.1):
        gamma_eff = gamma0 * np.exp(2.0 * delta_n)
        row = neg(1.0, gamma_eff)
        print(f"       {delta_n:>7.2f} {gamma_eff:>10.4f} "
              f"{row['negative_volume']:>12.4e} {row['min_wigner']:>12.4e}")
    print("       -> once the cubic non-Gaussianity is appreciable, the CV")
    print("          negative volume grows rapidly. This is the P1c complement")
    print("          to the free-boson theorem-null.\n")

    print("P1c-C  artifact guard: finite Fock-to-qubit Pauli-SRE is not the claim")
    print("       A linear squeeze is a Gaussian/symplectic operation. It should")
    print("       not change CV Wigner negativity, but it can strongly change")
    print("       finite-cutoff qubit Pauli-SRE in the oscillator basis.")
    print(f"       {'gamma':>7} {'sigma':>7} {'CV neg':>12} {'q':>3} "
          f"{'retained':>10} {'Pauli SRE':>10}")
    for gamma in (0.0, 0.24, 0.40):
        for sigma in (0.5, 1.0, 2.0):
            cv_neg = neg(sigma, gamma)["negative_volume"]
            sre, retained = finite_fock_pauli_sre(sigma, gamma, qubits=4)
            print(f"       {gamma:>7.2f} {sigma:>7.2f} {cv_neg:>12.4e} "
                  f"{4:>3} {retained:>10.6f} {sre:>10.4f}")
    print("       -> for gamma=0, CV negativity stays zero while Pauli-SRE becomes")
    print("          nonzero under a mere Gaussian squeeze. Therefore the bosonic")
    print("          interaction result must be stated in CV Wigner-negativity")
    print("          language; finite Fock/qubit SRE remains an encoding artifact.\n")

    print("RESULT:")
    print("  Free bosonic cosmological particle production remains magic-free in")
    print("  the CV/Wigner sense. True bosonic magic turns on only with genuine")
    print("  non-Gaussianity/interactions. The executable claim is Wigner-negative")
    print("  CV phase space, not a finite-cutoff Pauli-SRE number.")


if __name__ == "__main__":
    main()
