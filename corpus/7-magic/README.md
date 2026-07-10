# 7-magic: SYK Magic Baseline Sources

Verified against the arXiv API on 2026-07-09 before the Track D Phase 4
baseline was written.

## SYK Magic Baseline

| Paper | arXiv | Role in Phase 4 |
|---|---|---|
| Bera and Schiro, "Non-Stabilizerness of Sachdev-Ye-Kitaev Model" | [2502.01582](https://arxiv.org/abs/2502.01582) | Primary source for the SYK4/SYK2 magic separation: chaotic SYK4 has a Gaussian-like connected Majorana spectrum and larger SRE, while free SYK2 has a Laplace-like spectrum. |
| Jasser, Odavic and Hamma, "Stabilizer Entropy and entanglement complexity in the Sachdev-Ye-Kitaev model" | [2502.03093](https://arxiv.org/abs/2502.03093) | Independent SYK4+SYK2 interpolation source for the Majorana-Hamiltonian convention, SRE scaling, and the claim that SYK4 has more non-stabilizer structure than the integrable/free endpoint. |

## Cosmological Boson/Fermion Magic

Project 1 sources were verified against the arXiv API before the cosmology
labs were written or extended.

| Paper | arXiv | Role in Project 1 |
|---|---|---|
| Ireland and Vennin, "When inflationary perturbations refuse to classicalise: the role of non-Gaussianity in Wigner negativity" | [2601.22219](https://arxiv.org/abs/2601.22219) | Primary source for P1c: pure Gaussian perturbations have nonnegative Wigner functions, while interaction-generated non-Gaussianity produces Wigner-negative interference fringes; the paper reports a^2 growth of negativity in ultra-slow-roll backgrounds. |

Phase 4 uses the real-Majorana convention

```text
H_q = i^(q/2) sum_{i1 < ... < iq} J_{i1...iq} chi_i1 ... chi_iq,
Var(J) = (q-1)! J^2 / N^(q-1), J = 1.
```

This is the convention of the Jasser-Odavic-Hamma SYK-q presentation and is
close to the Majorana-spectrum language in Bera-Schiro. It is not a reproduction
of Bera-Schiro's complex-fermion half-filling numerics; it is the minimal
Majorana-SYK baseline requested for the executable lab.
