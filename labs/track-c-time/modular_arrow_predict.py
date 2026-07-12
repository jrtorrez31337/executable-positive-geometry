"""Track C — modular-clock line for the arrow-on-hardware experiment (PREVIEW).

Exact-statevector PREDICTION only (no QPU submission). Extends
arrow_hardware.py with a third family so the eventual hardware run shows three
lines instead of two, making S4's clock-vs-arrow split (labs/.../modular_flow.py)
visible on real qubits:

  ARROW   : write a record each tick (CRX S->record). System-alone entropy
            climbs monotonically -> the manufactured arrow. (P-B)
  MODULAR : write records for the first half (entropy climbs), then switch to
            pure MODULAR FLOW on the system qubit -- e^{i K_S theta}, rotation
            about the reduced state's own Bloch axis, K_S = -log rho_S. This
            leaves rho_S (hence the entropy) invariant: a reversible CLOCK
            riding on the mixed state. Entropy plateaus flat. (P-A / S4 Part 1)
  CONTROL : recordless precession. Entropy ~ 0 (pure) -> the noise floor.

The MODULAR line is the on-hardware witness of "the modular clock leaves the
state stationary" (modular_flow.py Part 1): it sits flat between the rising
arrow and the low control. Only record-writing (the inside view) makes entropy;
the modular clock does not. This file computes the predicted curves exactly;
the hardware submission is a separate, quota-gated step (not run here).
"""

import numpy as np

TICKS = 8
N_ENV = 3
LN2 = np.log(2)

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def rz(theta):
    return np.array([[np.exp(-1j * theta / 2), 0],
                     [0, np.exp(1j * theta / 2)]], dtype=complex)


def rx(theta):
    return np.array([[np.cos(theta / 2), -1j * np.sin(theta / 2)],
                     [-1j * np.sin(theta / 2), np.cos(theta / 2)]], dtype=complex)


def crx(theta, j):
    """System qubit (0) controls RX(theta) on env qubit j (1..N_ENV)."""
    from functools import reduce
    P0, P1 = np.diag([1, 0]).astype(complex), np.diag([0, 1]).astype(complex)
    a = [P0] + [I2] * N_ENV
    b = [P1] + [rx(theta) if k == j else I2 for k in range(N_ENV)]
    return reduce(np.kron, a) + reduce(np.kron, b)


def sys_op(u1):
    from functools import reduce
    return reduce(np.kron, [u1] + [I2] * N_ENV)


def rho_sys(psi):
    m = psi.reshape(2, 2 ** N_ENV)
    return m @ m.conj().T


def entropy_bits(rho):
    w = np.linalg.eigvalsh(rho)
    w = w[w > 1e-13]
    return float(-np.sum(w * np.log(w))) / LN2


def modular_unitary(rho_s, theta):
    """e^{i K_S theta} with K_S = -log rho_S: rotation about rho_S's own axis,
    leaves rho_S invariant (single-qubit modular flow of the reduced state)."""
    w, V = np.linalg.eigh(rho_s)
    w = np.clip(w, 1e-13, None)
    K = (V * (-np.log(w))) @ V.conj().T          # modular Hamiltonian
    # e^{i K theta}
    wk, Vk = np.linalg.eigh(K)
    return (Vk * np.exp(1j * wk * theta)) @ Vk.conj().T


def trajectory(mode):
    """mode in {'arrow','modular','control'} -> list of system-alone entropies."""
    from functools import reduce
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    e0 = np.zeros(2 ** N_ENV, dtype=complex)
    e0[0] = 1
    psi = np.kron(plus, e0)
    ent = [entropy_bits(rho_sys(psi))]
    switch = TICKS // 2                            # modular flow kicks in here
    for k in range(TICKS - 1):
        psi = sys_op(rz(np.pi / 2)) @ psi          # precession, all families
        if mode == "arrow":
            psi = crx(np.pi / 4, k % N_ENV) @ psi
        elif mode == "modular":
            if k < switch:
                psi = crx(np.pi / 4, k % N_ENV) @ psi     # build a mixed state
            else:
                U = modular_unitary(rho_sys(psi), np.pi / 2)  # then modular flow
                psi = sys_op(U) @ psi
        # control: nothing extra
        ent.append(entropy_bits(rho_sys(psi)))
    return ent


def main():
    arrow = trajectory("arrow")
    modular = trajectory("modular")
    control = trajectory("control")

    print("Track C — modular-clock PREVIEW (exact statevector; no QPU spend)\n")
    print(f"   {'tick':>5} {'ARROW':>8} {'MODULAR':>9} {'CONTROL':>9}")
    for t in range(TICKS):
        print(f"   {t:>5} {arrow[t]:>8.3f} {modular[t]:>9.3f} {control[t]:>9.3f}")

    a_mono = all(arrow[i + 1] >= arrow[i] - 1e-9 for i in range(TICKS - 1))
    sw = TICKS // 2
    mod_flat = max(abs(modular[t] - modular[sw]) for t in range(sw, TICKS))
    print(f"\n   ARROW monotone (the manufactured arrow)      : {a_mono}")
    print(f"   MODULAR flat after switch @tick {sw} (the clock) : "
          f"max drift {mod_flat:.2e} bits")
    print(f"   CONTROL stays near 0 (pure precession)       : "
          f"max {max(control):.3f} bits")
    print("\n   Reading: record-writing (ARROW) manufactures entropy; the")
    print("   modular clock (MODULAR, after the switch) rides the mixed state")
    print("   at constant entropy -- reversible, no arrow; control is the floor.")
    print("   On hardware these become three tomography lines. This is the")
    print("   S4 stationarity result (modular_flow.py Part 1) made device-ready.")
    print("\n   [hardware submission is a separate quota-gated step; not run here]")


if __name__ == "__main__":
    main()
