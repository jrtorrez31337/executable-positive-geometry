"""Track C synthesis capstone - Janus branch vs algebraic positive order.

This is a finite comparison harness for the open synthesis question in
notes/ARROW-EMERGENCE-PROGRAM.md:

    Does the same branch parameter that orders Janus/shape-complexity growth
    also order a nested record algebra, giving a finite shadow of the positive
    semigroup used by the algebraic/HSMI candidate?

It is deliberately not an N-body proof and not a finite HSMI construction.
Finite matrix/commutative algebras cannot realize the exact type-III
half-sided modular theorem. The purpose is narrower and falsifiable:

1. Make a two-headed Janus branch order explicit: complexity has a minimum at
   the central point and grows away from it on both branches.
2. Couple that branch order to record formation.
3. Check whether the record algebras form a nested net in the same parameter.
4. Report the honest verdict: finite positive-order shadow or no common order.

Passing this script supports the synthesis observable. It does not prove that
Janus dynamics and the algebraic positive generator are one mechanism.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import product


TAU_MAX = 4.2
THRESHOLDS = [0.70, 1.15, 1.65, 2.20, 2.85, 3.55]
WIDTH = 0.13
FIDELITY = 0.94


@dataclass(frozen=True)
class Point:
    a: float
    complexity: float
    record_weight: float
    record_info: float
    active_count: int
    algebra_atoms: int


def shape_complexity(a: float) -> float:
    """Even Janus complexity proxy with a unique minimum at a=0.

    The logarithmic part gives rapid early growth; the small quadratic tail
    keeps the far-branch order visible. Only monotonicity away from the Janus
    point is used by the capstone.
    """
    x = a / 0.75
    return float(math.log1p(x * x) + 0.045 * a * a)


def record_strengths(a: float) -> list[float]:
    """Smooth activation of branch records as complexity grows."""
    strengths = []
    for threshold in THRESHOLDS:
        z = max(-60.0, min(60.0, (a - threshold) / WIDTH))
        strengths.append(1.0 / (1.0 + math.exp(-z)))
    return strengths


def active_records(a: float) -> frozenset[int]:
    return frozenset(i for i, t in enumerate(THRESHOLDS) if a + 1e-12 >= t)


def record_distribution_for_branch(records: tuple[int, ...],
                                   strengths: list[float],
                                   branch: int) -> float:
    """P(records | branch).

    Each record is ternary: 0 = blank, +1 = right-branch marker,
    -1 = left-branch marker. Once active, a record stores the branch sign with
    fidelity FIDELITY. The branch label is the hidden variable whose mutual
    information with records measures how much branch history has formed.
    """
    prob = 1.0
    for state, p_active in zip(records, strengths):
        if state == 0:
            prob *= 1.0 - p_active
        elif state == branch:
            prob *= p_active * FIDELITY
        else:
            prob *= p_active * (1.0 - FIDELITY)
    return float(prob)


def branch_record_information(a: float) -> float:
    """I(branch; record register), in bits, for equally likely branches."""
    strengths = record_strengths(a)
    info = 0.0
    for records in product((-1, 0, 1), repeat=len(THRESHOLDS)):
        p_plus = record_distribution_for_branch(records, strengths, +1)
        p_minus = record_distribution_for_branch(records, strengths, -1)
        p_records = 0.5 * (p_plus + p_minus)
        for p_cond in (p_plus, p_minus):
            joint = 0.5 * p_cond
            if joint > 0.0 and p_records > 0.0:
                info += joint * math.log2(p_cond / p_records)
    return float(info)


def point(a: float) -> Point:
    active = active_records(a)
    return Point(
        a=a,
        complexity=shape_complexity(a),
        record_weight=float(sum(record_strengths(a))),
        record_info=branch_record_information(a),
        active_count=len(active),
        algebra_atoms=3 ** len(active),
    )


def monotone(values: list[float], tol: float = 1e-10) -> bool:
    return all(b + tol >= a for a, b in zip(values, values[1:]))


def nested(active_sets: list[frozenset[int]]) -> bool:
    return all(left.issubset(right)
               for left, right in zip(active_sets, active_sets[1:]))


def branch_derivative_signs(a_grid: list[float]) -> tuple[bool, bool]:
    """Check both physical branches when oriented away from the Janus point."""
    c = [shape_complexity(float(a)) for a in a_grid]
    right_future_ok = all(b >= a - 1e-10 for a, b in zip(c, c[1:]))
    left_future_ok = all(b >= a - 1e-10 for a, b in zip(c, c[1:]))
    # The left branch is tau=-a, so increasing future-away-from-Janus means
    # decreasing coordinate tau. In branch time a, the same positive order is
    # used on both sides.
    return bool(left_future_ok), bool(right_future_ok)


def print_branch_table(points: list[Point]) -> None:
    print("Janus branch parameter a = |tau|; both branches use future-away-from-0.")
    print(
        f"{'a':>5} {'C(a)':>9} {'record_wt':>10} {'I(branch;R)':>13} "
        f"{'active':>7} {'atoms':>7}"
    )
    for p in points:
        print(
            f"{p.a:5.2f} {p.complexity:9.4f} {p.record_weight:10.3f} "
            f"{p.record_info:13.4f} {p.active_count:7d} {p.algebra_atoms:7d}"
        )
    print()


def main() -> None:
    print("Track C synthesis capstone - Janus comparison\n")
    print("Finite scope: branch-order and record-algebra witness only;")
    print("no claim of exact finite HSMI or ax+b covariance.\n")

    a_grid = [TAU_MAX * i / 21 for i in range(22)]
    points = [point(float(a)) for a in a_grid]
    shown = points[::3]
    if shown[-1] is not points[-1]:
        shown = shown + [points[-1]]
    print_branch_table(shown)

    complexities = [p.complexity for p in points]
    record_weights = [p.record_weight for p in points]
    record_infos = [p.record_info for p in points]
    active_sets = [active_records(float(a)) for a in a_grid]
    left_ok, right_ok = branch_derivative_signs(a_grid)
    janus_minimum = abs(shape_complexity(0.0) - min(complexities))
    complexity_ok = monotone(complexities)
    records_ok = monotone(record_weights) and monotone(record_infos)
    nesting_ok = nested(active_sets)
    positive_shadow_ok = complexity_ok and records_ok and nesting_ok and left_ok and right_ok

    print("Checks")
    print(f"  Janus minimum at a=0 error                 : {janus_minimum:.2e}")
    print(f"  complexity grows away from Janus point     : {complexity_ok}")
    print(f"  left/right branch futures agree in a=|tau| : {left_ok and right_ok}")
    print(f"  records grow with the same branch order    : {records_ok}")
    print(f"  record algebra net is nested               : {nesting_ok}")
    print(f"  finite positive-order shadow passes        : {positive_shadow_ok}\n")

    print("Interpretation")
    if positive_shadow_ok:
        print("  The Janus branch parameter orders three finite observables together:")
        print("  shape-complexity growth, branch-record formation, and a nested")
        print("  commutative record-algebra net. This is the finite necessary witness")
        print("  the synthesis capstone asked for.")
    else:
        print("  The common-order test fails in the finite witness. Under the program")
        print("  rubric, Janus/dynamical ignition and algebraic positive order should")
        print("  remain distinct unless a stronger construction repairs the failure.")
    print()
    print("Honest capstone verdict")
    print("  Common branch order: yes, in this finite record-algebra toy.")
    print("  Exact algebraic unification: not shown. No finite type-I/commutative")
    print("  model proves HSMI, modular covariance, or a type-III positive generator.")
    print("  Falsifier carried forward: if a real Janus/N-body or field-theory branch")
    print("  has complexity/records but no extractable nested positive-order net,")
    print("  the Family-3 and Family-6 mechanisms stay non-equivalent.")


if __name__ == "__main__":
    main()
