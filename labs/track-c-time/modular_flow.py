"""Track C, Lab 3 — modular flow: the operator-algebra clock-vs-arrow split (S4).

Executable test of tracker sighting S4 (notes/TIME-ARROW-TRACKER.md; survey
notes/ARROW-EXTENDED-WORK.md). The claim, converged with codex-science (commit
27e3214): Tomita-Takesaki modular theory reproduces the project's OWN structure
in a fifth formalism (von Neumann algebras) — and does it with one construction
from a single cyclic-separating (= self-contained) state:

  CLOCK  (P-A analog): the modular flow sigma_t(a) = Delta^{it} a Delta^{-it}
         is a reversible one-parameter GROUP that leaves the state stationary
         and satisfies the KMS condition at beta = 1. Time, no arrow.

  ARROW  (P-B / S3 / GSL analog): irreversibility is manufactured only by
         RESTRICTION. Relative entropy is monotone non-increasing under data
         processing (coarse-graining / partial trace) — the finite-dim shadow
         of the generalized second law. It is NOT in the flow: the flow
         preserves relative entropy exactly; only restriction contracts it.

  REFLECTION (S2 / Wigner bridge): the modular conjugation J is ANTIUNITARY,
         squares to 1, sends the algebra M to its commutant M', and inverts the
         modular operator (J Delta J = Delta^{-1}). The antiunitary reflection
         native to the structure — the operator-algebra sibling of "time
         reversal is antiunitary."

No gravity, no hardware overclaim: this is the exact finite-dim core of the
crossed-product / GSL story (corpus Front 4), built from a cyclic-separating
state. Everything below is checked to machine precision.
"""

import numpy as np


# ─── linear-algebra helpers ──────────────────────────────────────────────────

def rho_power(rho, it):
    """rho^{i t} for Hermitian PSD rho (unitary since rho is a state)."""
    w, V = np.linalg.eigh(rho)
    w = np.clip(w, 1e-15, None)
    return (V * (w ** (1j * it))) @ V.conj().T


def logm_psd(rho):
    w, V = np.linalg.eigh(rho)
    w = np.clip(w, 1e-15, None)
    return (V * np.log(w)) @ V.conj().T


def rel_entropy(rho, sigma):
    """S(rho||sigma) = tr rho (log rho - log sigma), in bits."""
    val = np.trace(rho @ (logm_psd(rho) - logm_psd(sigma)))
    return float(np.real(val)) / np.log(2)


def entropy(rho):
    w = np.linalg.eigvalsh(rho)
    w = w[w > 1e-12]
    return float(-np.sum(w * np.log(w))) / np.log(2)


def partial_trace_B(rho, nA, nB):
    return np.einsum("ijkj->ik", rho.reshape(nA, nB, nA, nB))


def dephase(X, lam, n):
    """Partial dephasing channel in the computational basis (a CPTP map).
    D_lam(X) = lam*diag(X) + (1-lam)*X.  D_lam compose to larger lam, so a
    lam-sweep is a genuine data-processing chain."""
    return lam * np.diag(np.diag(X)) + (1 - lam) * X


def rand_density(n, rng):
    M = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    rho = M @ M.conj().T
    return rho / np.trace(rho)


# ─── the cyclic-separating state and its modular data ────────────────────────

def modular_data(p):
    """Schmidt state |psi> = sum_i sqrt(p_i) |i>_A |i>_B on H_A (x) H_B.
    Cyclic-separating for M = B(H_A) (x) 1 iff every p_i > 0."""
    n = len(p)
    psi = np.zeros(n * n, dtype=complex)
    for i in range(n):
        psi[i * n + i] = np.sqrt(p[i])
    rho_A = np.diag(p).astype(complex)
    rho_B = np.diag(p).astype(complex)
    Delta = np.kron(rho_A, np.linalg.inv(rho_B))     # modular operator
    return psi, rho_A, rho_B, Delta


def sigma_t(a, rho_A, t):
    """Modular flow of an observable a on H_A: rho_A^{it} a rho_A^{-it}."""
    return rho_power(rho_A, t) @ a @ rho_power(rho_A, -t)


# ─── Part 1: the modular flow is a reversible clock ──────────────────────────

def part_1_clock(psi, rho_A, n, rng):
    print("PART 1 — the modular flow is a CLOCK (reversible, stationary, KMS)")
    m = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    a = m + m.conj().T                                # generic observable on A
    m2 = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    b = m2 + m2.conj().T

    # group law: sigma_s . sigma_t = sigma_{s+t}
    s, t = 0.7, 1.3
    grp = np.max(np.abs(sigma_t(sigma_t(a, rho_A, t), rho_A, s)
                        - sigma_t(a, rho_A, s + t)))
    # reversibility: sigma_{-t} undoes sigma_t
    rev = np.max(np.abs(sigma_t(sigma_t(a, rho_A, t), rho_A, -t) - a))

    A = np.kron(a, np.eye(n))
    # stationarity: <psi| sigma_t(a) |psi> = <psi| a |psi> for all t
    base = np.vdot(psi, A @ psi)
    drift = max(abs(np.vdot(psi, np.kron(sigma_t(a, rho_A, tt), np.eye(n)) @ psi)
                    - base) for tt in (0.3, 1.1, 2.7, 5.0))
    # KMS at beta = 1:  <psi| a sigma_{-i}(b) |psi> = <psi| b a |psi>
    sig_minus_i_b = rho_A @ b @ np.linalg.inv(rho_A)   # sigma_{-i}(b)
    lhs = np.vdot(psi, np.kron(a @ sig_minus_i_b, np.eye(n)) @ psi)
    rhs = np.vdot(psi, np.kron(b @ a, np.eye(n)) @ psi)
    kms = abs(lhs - rhs)

    print(f"   group law  sigma_s.sigma_t = sigma_(s+t) : max err {grp:.2e}")
    print(f"   reversible sigma_-t . sigma_t = id       : max err {rev:.2e}")
    print(f"   state stationary under the flow          : max drift {drift:.2e}")
    print(f"   KMS(beta=1) <a sigma_-i(b)> = <b a>       : err {kms:.2e}")
    print("   -> a reversible one-parameter group; the state is a fixed point;")
    print("      KMS holds. A clock, not an arrow.  (P-A analog.)\n")
    return a, b


# ─── Part 2: the arrow is manufactured by restriction ────────────────────────

def part_2_arrow(n, rng):
    print("PART 2 — the ARROW is manufactured by RESTRICTION (data processing)")
    rho = rand_density(n * n, rng)
    sig = rand_density(n * n, rng)

    # (i) a monotone staircase: relative entropy under a coarse-graining chain
    lams = [0.0, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.0]
    chain = [rel_entropy(dephase(rho, L, n * n), dephase(sig, L, n * n))
             for L in lams]
    monotone = all(chain[i + 1] <= chain[i] + 1e-9 for i in range(len(chain) - 1))
    print("   coarse-graining lambda :", " ".join(f"{L:>5.2f}" for L in lams))
    print("   S(rho||sigma) [bits]   :", " ".join(f"{c:>5.2f}" for c in chain))
    print(f"   monotone non-increasing (the arrow)      : {monotone}")

    # (ii) restriction to the subalgebra A (partial trace) can only lose it
    full = rel_entropy(rho, sig)
    restr = rel_entropy(partial_trace_B(rho, n, n), partial_trace_B(sig, n, n))
    print(f"   S(rho||sigma) full={full:.3f}  ->  restricted to A={restr:.3f}"
          f"  (drop {full - restr:.3f})")
    print("   -> distinguishability is monotone under coarse-graining/restriction:")
    print("      the finite-dim shadow of the GSL. The arrow lives in the")
    print("      inside-view, not in the dynamics.  (P-B / S3 / GSL analog.)\n")
    return rho, sig


# ─── Part 3: clock and arrow are orthogonal ──────────────────────────────────

def part_3_orthogonal(rho, sig, rho_A, n):
    print("PART 3 — CLOCK and ARROW are orthogonal")
    Delta_flow = lambda X, t: (np.kron(rho_power(rho_A, t), np.eye(n)) @ X
                               @ np.kron(rho_power(rho_A, -t), np.eye(n)))
    base = rel_entropy(rho, sig)
    preserved = max(abs(rel_entropy(Delta_flow(rho, t), Delta_flow(sig, t)) - base)
                    for t in (0.5, 1.7, 4.0))
    restr = rel_entropy(partial_trace_B(rho, n, n), partial_trace_B(sig, n, n))
    print(f"   flow preserves relative entropy          : max err {preserved:.2e}")
    print(f"   restriction contracts it                 : {base:.3f} -> {restr:.3f}")
    print("   -> the clock is an isometry of distinguishability (reversible);")
    print("      only restriction contracts it (the arrow). S4's split, exact.\n")


# ─── Part 4: the antiunitary modular conjugation (S2 bridge) ──────────────────

def part_4_antiunitary(psi, Delta, rho_A, n):
    print("PART 4 — the modular conjugation J is ANTIUNITARY (S2 / Wigner bridge)")
    # SWAP on H_A (x) H_B
    SWAP = np.zeros((n * n, n * n))
    for i in range(n):
        for j in range(n):
            SWAP[j * n + i, i * n + j] = 1.0
    J = lambda v: SWAP @ np.conjugate(v)              # antiunitary: SWAP o conj

    # antiunitary: <Ju,Jv> = conj(<u,v>) = <v,u>;  J^2 = 1
    rng = np.random.default_rng(0)
    u = rng.normal(size=n * n) + 1j * rng.normal(size=n * n)
    v = rng.normal(size=n * n) + 1j * rng.normal(size=n * n)
    anti = abs(np.vdot(J(u), J(v)) - np.vdot(v, u))
    invol = np.max(np.abs(J(J(u)) - u))

    # J maps the algebra M = B(H_A)(x)1 onto its commutant M' = 1(x)B(H_B):
    #   J (a (x) 1) J = 1 (x) conj(a)
    m = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    a = m + m.conj().T
    JaJ = SWAP @ np.conjugate(np.kron(a, np.eye(n))) @ SWAP
    to_commutant = np.max(np.abs(JaJ - np.kron(np.eye(n), np.conjugate(a))))
    # commutes with all of M (checked on a basis element b (x) 1)
    b = (m - m.conj().T) * 1j
    comm = np.max(np.abs(JaJ @ np.kron(b, np.eye(n))
                         - np.kron(b, np.eye(n)) @ JaJ))

    # J Delta J = Delta^{-1}: the antiunitary reflection inverts the flow
    JDJ = SWAP @ np.conjugate(Delta) @ SWAP
    reflect = np.max(np.abs(JDJ - np.linalg.inv(Delta)))

    print(f"   antiunitary  <Ju,Jv> = <v,u>             : err {anti:.2e}")
    print(f"   involution   J^2 = 1                     : err {invol:.2e}")
    print(f"   J M J = M'   (algebra -> commutant)      : err {to_commutant:.2e}")
    print(f"      and J M J commutes with M             : err {comm:.2e}")
    print(f"   J Delta J = Delta^-1 (inverts the flow)  : err {reflect:.2e}")
    print("   -> the antiunitary reflection native to the modular structure:")
    print("      the operator-algebra sibling of S2 (time reversal is")
    print("      antiunitary, Wigner). Clock, arrow, and antiunitary reflection")
    print("      all fall out of ONE cyclic-separating state.\n")


def run(n, seed):
    rng = np.random.default_rng(seed)
    p = rng.random(n) + 0.3
    p = np.sort(p / p.sum())[::-1]                     # Schmidt spectrum, all > 0
    psi, rho_A, rho_B, Delta = modular_data(p)
    print("=" * 70)
    print(f"dim_A = dim_B = {n}  ({2 * int(np.log2(n)) if n & (n-1) == 0 else '~'} "
          f"qubits), Schmidt spectrum p = {np.round(p, 3)}")
    print(f"cyclic-separating check ||Delta|psi> - |psi>|| = "
          f"{np.linalg.norm(Delta @ psi - psi):.2e}   (all p_i > 0)")
    print("=" * 70)
    a, b = part_1_clock(psi, rho_A, n, rng)
    rho, sig = part_2_arrow(n, rng)
    part_3_orthogonal(rho, sig, rho_A, n)
    part_4_antiunitary(psi, Delta, rho_A, n)


if __name__ == "__main__":
    run(n=2, seed=1)     # 2 qubits
    run(n=4, seed=7)     # 4 qubits (2 per side) — same structure, generic
