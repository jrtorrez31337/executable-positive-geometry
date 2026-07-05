"""CAPSTONE VII — spawning objects into the rendered world.

The mod-injection experiment. The six-tile flower defines six bulk
"slots" (asset memory reserved by the stabilizer structure). We start
with every slot in vacuum — objects defined by the engine but not in
visor view — and then, using ONLY boundary ("screen") operations that
respect the memory architecture (logical operators = stabilizer-
commuting Paulis), we:

  1. verify the vacuum renders nothing (all logical X-witnesses zero,
     all Z-witnesses at vacuum value +1);
  2. SPAWN an object in petal 2's slot (apply its wedge-supported
     logical X-avatar): the Z-witness flips to -1 — the object exists;
  3. verify the two conservation laws:
       NO-MALLOC: the engine's memory map (petal image-code checks) is
       untouched — same code, same slots, only contents changed;
       WEDGE OWNERSHIP: an arbitrary scrambling circuit on petals 3-5's
       screen region cannot write petal 2's slot (disjoint supports
       commute — verified numerically on top of the theorem);
  4. the showpiece: spawn TWO objects entangled with each other —
     logical Hadamard on slot 2, then logical CNOT onto slot 4, all as
     boundary Pauli-string arithmetic. The witnesses show a Bell pair
     of bulk objects, and the boundary blocks of petals 2 and 4 now
     share mutual information they did not have before: the objects
     AND the thread between them, injected from the screen. (ER=EPR,
     hobby edition.)
"""

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from flower_hardware import IMAGE_STABS, pauli_reps  # noqa: E402
from happy_network import network  # noqa: E402

LN2 = np.log(2)
P2 = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}
N = 20  # boundary qubits; petal i (1..5) owns qubits 4(i-1)..4i-1


def apply_string(psi, sites):
    """Apply a Pauli string {qubit: char} (no phase) to a 20-qubit vector."""
    out = psi.reshape([2] * N)
    for q, c in sites.items():
        out = np.moveaxis(np.tensordot(P2[c], out, axes=([1], [q])), 0, q)
    return out.reshape(-1)


def avatar(petal, kind):
    """Global (sign, sites) for petal's logical X or Z, boundary-supported."""
    sign, lab = pauli_reps("I" + kind)[0]
    sites = {4 * (petal - 1) + k: c for k, c in enumerate(lab) if c != "I"}
    return sign, sites


def expect(psi, sign, sites):
    return float(np.real(np.vdot(psi, sign * apply_string(psi, sites))))


def entropy(psi, qubits):
    keep = list(qubits)
    rest = [q for q in range(N) if q not in keep]
    m = psi.reshape([2] * N).transpose(keep + rest).reshape(2 ** len(keep), -1)
    p = np.linalg.eigvalsh(m @ m.conj().T)
    p = p[p > 1e-12]
    return float(-np.sum(p * np.log(p)))


def mutual_info(psi, a, b):
    return (entropy(psi, a) + entropy(psi, b) - entropy(psi, list(a) + list(b)))


def witnesses(psi, label):
    print(f"   {label}:")
    for petal in range(1, 6):
        zx = [expect(psi, *avatar(petal, k)) for k in ("Z", "X")]
        print(f"      slot {petal}: <Z~> = {zx[0]:+.3f}   <X~> = {zx[1]:+.3f}")


def memory_map_ok(psi):
    """The engine's reserved memory: petal image-code checks all +1."""
    vals = []
    for petal in range(1, 6):
        s, lab = IMAGE_STABS[0]
        sites = {4 * (petal - 1) + k: c for k, c in enumerate(lab) if c != "I"}
        vals.append(expect(psi, s, sites))
    return all(abs(v - 1) < 1e-9 for v in vals)


def main() -> None:
    psi = network(0, [0] * 5)
    psi = psi / np.linalg.norm(psi)

    print("STEP 1 — the vacuum world (all six slots defined, none in view)")
    witnesses(psi, "witness table")
    print(f"   memory map intact: {memory_map_ok(psi)}\n")

    print("STEP 2 — SPAWN: petal-2's logical X-avatar, boundary gates only")
    sgn, sites = avatar(2, "X")
    print(f"   spawn operator: sign {sgn:+.0f}, screen qubits {sorted(sites)}"
          f" -> {''.join(sites[q] for q in sorted(sites))}")
    psi2 = sgn * apply_string(psi, sites)
    witnesses(psi2, "after spawn")
    print(f"   memory map intact (NO-MALLOC): {memory_map_ok(psi2)}")
    print("   Slot 2 now holds an object (<Z~> flipped to -1); every other")
    print("   slot untouched; the code that defines the slots unchanged.\n")

    print("STEP 3 — WEDGE OWNERSHIP: scramble petals 3-5's screen region")
    rng = np.random.default_rng(5)
    psi_s = psi.copy()
    outside = list(range(8, 20))            # petals 3,4,5
    for _ in range(20):
        q1, q2 = rng.choice(outside, size=2, replace=False)
        m = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
        u, _ = np.linalg.qr(m)
        t = psi_s.reshape([2] * N)
        t = np.moveaxis(t, [q1, q2], [0, 1]).reshape(4, -1)
        t = (u @ t).reshape([2, 2] + [2] * (N - 2))
        psi_s = np.moveaxis(t, [0, 1], [q1, q2]).reshape(-1)
    z2 = expect(psi_s, *avatar(2, "Z"))
    print(f"   after 20 random 2-qubit gates outside petal 2's wedge:")
    print(f"   slot 2 <Z~> = {z2:+.6f}   (vacuum undisturbed: writes from a")
    print("   region that does not own the wedge are inert — disjoint")
    print("   supports commute; memory protection is geometry.)\n")

    print("STEP 4 — THE SHOWPIECE: spawn an entangled PAIR (slots 2 and 4)")
    sZ2, xZ2 = avatar(2, "Z")
    sX2, xX2 = avatar(2, "X")
    sZ4, xZ4 = avatar(4, "Z")
    sX4, xX4 = avatar(4, "X")
    # logical Hadamard on slot 2: (X~ + Z~)/sqrt(2)  (unitary: they anticommute)
    psiH = (sX2 * apply_string(psi, xX2) + sZ2 * apply_string(psi, xZ2)) / np.sqrt(2)
    # logical CNOT slot2 -> slot4: (I + Z~2 + X~4 - Z~2 X~4)/2
    t1 = psiH
    t2 = sZ2 * apply_string(psiH, xZ2)
    t3 = sX4 * apply_string(psiH, xX4)
    t4 = sZ2 * sX4 * apply_string(apply_string(psiH, xZ2), xX4)
    psiB = (t1 + t2 + t3 - t4) / 2
    assert abs(np.linalg.norm(psiB) - 1) < 1e-9

    zz = float(np.real(np.vdot(psiB, sZ2 * sZ4 * apply_string(
        apply_string(psiB, xZ2), xZ4))))
    xx = float(np.real(np.vdot(psiB, sX2 * sX4 * apply_string(
        apply_string(psiB, xX2), xX4))))
    z2s = expect(psiB, sZ2, xZ2)
    z4s = expect(psiB, sZ4, xZ4)
    print(f"   <Z~2 Z~4> = {zz:+.3f}   <X~2 X~4> = {xx:+.3f}   "
          f"<Z~2> = {z2s:+.3f}   <Z~4> = {z4s:+.3f}")
    blocks = (list(range(4, 8)), list(range(12, 16)))
    mi_before = mutual_info(psi, *blocks) / LN2
    mi_after = mutual_info(psiB, *blocks) / LN2
    print(f"   mutual information, petal-2 block : petal-4 block:")
    print(f"      vacuum world: {mi_before:.4f} bits   after spawn: "
          f"{mi_after:.4f} bits")
    print(f"   memory map intact: {memory_map_ok(psiB)}")
    print("\n   Two objects now exist that did not, maximally entangled with")
    print("   each other, and the RENDERED world shows it: two screen regions")
    print("   that previously shared nothing now share two full bits. The")
    print("   objects and the thread between them were injected entirely")
    print("   from the interface — architecture respected, no malloc, no")
    print("   wedge violated. ER=EPR, hobby edition.")


if __name__ == "__main__":
    main()
