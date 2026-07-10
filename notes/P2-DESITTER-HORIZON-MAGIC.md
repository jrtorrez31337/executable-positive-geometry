# Project 2: de Sitter Horizon Magic Controls And Scope

Status: co-write draft, 2026-07-10. This is the codex-science/Tobin
controls and scope section for the Project 2 writeup. It should be read next
to:

- `labs/track-d-cosmo/proj2_desitter_horizon_magic.py`
- `labs/track-d-cosmo/proj2_desitter_horizon_controls.py`
- `labs/track-d-cosmo/proj2_magic_dynamics.py`
- `labs/track-d-cosmo/proj2_magic_dynamics_crosscheck.py`

## Claim Boundary

Project 2 asks whether the de Sitter horizon has a magic signature in the
double-scaled-SYK/de Sitter program. The executable proxy is deliberately
conservative: small ordinary SYK4 versus SYK2, plus TFD and TPQ states, used
as a computable stand-in for the chaotic finite horizon Hilbert space.

The claim is not that these scripts simulate our universe, not that de Sitter
temperature alone controls magic, and not that static thermal magic already
separates horizon physics. The DSSYK/de Sitter dictionary is high-temperature,
upper-edge, constrained-doubled, and degree-of-freedom based. The safer
scaling language is "horizon dof proxy" such as log2(dim) for ordinary SYK or
N/p^2 in the double-scaled dictionary.

## Controls That Must Stay In The Writeup

Free bosonic static-patch or Bunch-Davies modes are Gaussian. In the CV
resource theory used here, Gaussian pure states have nonnegative Wigner
functions and zero Wigner mana. Any finite Fock-to-qubit Pauli-SRE from a
truncated encoding is therefore an encoding diagnostic, not physical bosonic
horizon magic. The relabeling guard in `proj2_desitter_horizon_controls.py`
is the evidence: the Pauli-SRE changes under a non-affine basis relabel while
the underlying CV state remains Gaussian and magic-free.

Free fermions require resource-theory labeling. Their Jordan-Wigner image can
have qubit-stabilizer magic, but the state is still fermionic Gaussian. That
is not by itself evidence for interacting or chaotic DSSYK horizon magic.
Thermal free-fermion mixedness must be same-spectrum-twin controlled before
being compared to a chaotic thermal ensemble.

Raw mixed-state M2 is unsafe as a horizon diagnostic. Classical mixedness can
produce nonzero values, so thermal density matrices are interpreted only
after subtracting a same-spectrum stabilizer-basis twin. This is the same
discipline used in Phase 5.

The infinite-temperature doubled TFD is a correction, not a signal. The state
sum_E |E>_L |E*>_R equals the computational Bell state because sum_E
|E><E| = I. It has zero raw SRE and zero non-local magic independent of the
Hamiltonian. The beta=0 constrained-doubled stand-in is therefore a trivial
stabilizer state, not an eigenbasis-chaos probe.

## Static Result

The static Project 2 result is an honest null. TPQ magic is extensive but
barely separates SYK4 from SYK2 at the static level, and thermal-rho magic can
even run backwards after the required twin control because chaos flattens the
spectrum toward a more mixed state. The static null is not a measurement
failure; it is a result from multiple measures and controls.

## Dynamics Scope

The dynamic observable is the finite-beta time-evolved TFD SRE,
M2(TFD(beta,t)), compared with the spectral form factor. This is where the
current evidence is strongest:

- The robust headline is the scrambling-rise discriminator: chaotic SYK4 TFD
  magic grows about twice as much as free SYK2 under time evolution.
- The late-time plateau gap is secondary. It is positive and growing for
  N>=8 in the current runs, but N=6 is actively negative in independent
  checks, so the honest wording is a small-N sign flip or crossover rather
  than "extensive from N=6."
- Under the same-spectrum diagonal-basis TFD control, the clean positive gap
  is visible only at N=10. That makes N=8 suggestive but not cleanly
  eigenbasis-only.
- The TFD state is pure, so raw M2 is not a mixed-state false positive in the
  dynamics section. The relevant control there is Hamiltonian/eigenbasis
  structure, not thermal mixedness.
- Magic saturation and the SFF dip are linked only at order-of-magnitude
  resolution on the current coarse grid. Do not write a precise one-to-one
  saturation-equals-dip claim.

## Recommended Public Wording

The concise version:

> The static de-Sitter/SYK horizon-magic test is a controlled null. Free-field
> Gaussian sectors, thermal mixedness, and the beta=0 doubled state do not
> supply a horizon magic signal. Dynamics does reveal a sharper chaotic
> signature: finite-beta TFD magic grows roughly twice as much in SYK4 as in
> SYK2, with a suggestive positive plateau gap for N>=8 and a small-N
> crossover at N=6. This is evidence for a scrambling-sensitive magic
> diagnostic in a conservative SYK proxy, not a full DSSYK/de Sitter theorem.

This keeps the load-bearing result where it belongs: dynamics and scrambling,
not static thermal magic or a temperature monotone.
