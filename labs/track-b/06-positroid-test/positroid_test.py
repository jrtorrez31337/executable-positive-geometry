"""Lab 6 skeleton — does the Hoffman map respect positroid structure?

See DESIGN.md. Everything here is n=4, exhaustive (no sampling): 65
decorated permutations on the geometry side, 50,625 support digraphs on
the dynamics side. Conventions per DESIGN.md "interpretive repairs".
"""

from itertools import permutations, product

N = 4


# ─── Geometry side: the positroid census ─────────────────────────────────────

def all_decorated_permutations(n: int):
    """(perm tuple, frozenset of loop-decorated fixed pts). Non-loop fixed
    points are coloops. perm is 0-indexed."""
    out = []
    for p in permutations(range(n)):
        fixed = [i for i in range(n) if p[i] == i]
        for mask in range(2 ** len(fixed)):
            loops = frozenset(f for b, f in enumerate(fixed) if mask >> b & 1)
            out.append((p, loops))
    return out


def k_statistic(p, loops) -> int:
    """k = #anti-exceedances: sigma(i) < i, plus loop-decorated fixed points.
    This selects which Gr(k,n) the cell lives in (Postnikov convention)."""
    return sum(1 for i in range(len(p)) if p[i] < i) + len(loops)


def census(n: int) -> dict[int, int]:
    c: dict[int, int] = {}
    for p, loops in all_decorated_permutations(n):
        k = k_statistic(p, loops)
        c[k] = c.get(k, 0) + 1
    return c


# ─── Dynamics side: chains, classes, and the Def-2 map ───────────────────────

def classes_of(support) -> tuple[list[frozenset[int]], set[frozenset[int]]]:
    """Communicating classes and the subset that is recurrent.
    support: tuple of N bitmasks; bit j of support[i] = edge i->j."""
    reach = [support[i] | (1 << i) for i in range(N)]
    for _ in range(N):  # transitive closure
        for i in range(N):
            r = reach[i]
            for j in range(N):
                if r >> j & 1:
                    r |= reach[j]
            reach[i] = r
    seen, classes = set(), []
    for i in range(N):
        if i in seen:
            continue
        cls = frozenset(j for j in range(N)
                        if reach[i] >> j & 1 and reach[j] >> i & 1)
        classes.append(cls)
        seen |= cls
    recurrent = {c for c in classes
                 if all((support[i] & ~sum(1 << j for j in c)) == 0 for i in c)}
    return classes, recurrent


def def2_map(support):
    """Hoffman Def. 2 (repaired conventions, see DESIGN.md):
    transient -> loop fixed point; singleton recurrent -> coloop fixed
    point; recurrent in class C -> endpoint of minimal cyclic window
    from that state covering C. Returns (perm, loops) or None if the
    window rule fails to produce a bijection."""
    classes, recurrent = classes_of(support)
    cls_of = {i: c for c in classes for i in c}
    sigma, loops = [None] * N, set()
    for a in range(N):
        c = cls_of[a]
        if c not in recurrent:
            sigma[a] = a
            loops.add(a)
        elif len(c) == 1:
            sigma[a] = a          # coloop (recurrent fixed point)
        else:
            window = {a}
            b = a
            while not c <= window:
                b = (b + 1) % N
                window.add(b)
            sigma[a] = b
    if sorted(sigma) != list(range(N)):
        return None
    return tuple(sigma), frozenset(loops)


def all_supports():
    """Every support digraph with at least one outgoing edge per state."""
    rows = [m for m in range(1, 2 ** N)]
    yield from product(rows, repeat=N)


# ─── The tests ────────────────────────────────────────────────────────────────

def main() -> None:
    print("Census (geometry side): decorated permutations of [4] by k")
    c = census(N)
    print(f"   {dict(sorted(c.items()))}   total {sum(c.values())}")
    assert c == {0: 1, 1: 15, 2: 33, 3: 15, 4: 1}, "positroid census mismatch"
    print("   matches positroid cell counts of Gr>=0(k,4): (1,15,33,15,1) ok\n")

    print("H1 coverage + H2 statistic (exhaustive over 50,625 supports)")
    image: dict[tuple, int] = {}
    k_vs_classes: dict[tuple[int, int], int] = {}
    failures = 0
    for s in all_supports():
        dp = def2_map(s)
        if dp is None:
            failures += 1
            continue
        image[dp] = image.get(dp, 0) + 1
        classes, recurrent = classes_of(s)
        k = k_statistic(*dp)
        k_vs_classes[(k, len(recurrent))] = k_vs_classes.get((k, len(recurrent)), 0) + 1
    print(f"   window-rule bijection failures: {failures}")
    print(f"   distinct labels in image: {len(image)} / 65 possible")
    ks = {}
    for dp in image:
        ks[k_statistic(*dp)] = ks.get(k_statistic(*dp), 0) + 1
    print(f"   image labels by k: {dict(sorted(ks.items()))}"
          f"   (full census: {dict(sorted(c.items()))})")
    print(f"   (k, #recurrent classes) joint counts over chains:")
    for key in sorted(k_vs_classes):
        print(f"      k={key[0]}, R={key[1]}: {k_vs_classes[key]:>6}")

    print("\nH4 compression: dynamically distinct chains per label")
    top = sorted(image.items(), key=lambda kv: -kv[1])[:3]
    for dp, cnt in top:
        print(f"   label perm={dp[0]} loops={sorted(dp[1])}: {cnt} supports "
              f"(x infinitely many probability assignments each)")
    print("   Def-2 reads NO transition probabilities: spectral gaps, mixing")
    print("   times, stationary distributions are all invisible to the label.\n")

    print("H3 compositionality: tensor product vs direct sum (all 81 pairs, n=2)")
    def def2_n(support, n):
        global N
        old, N = N, n
        r = def2_map(support)
        N = old
        return r
    def direct_sum(dp1, dp2, n1):
        p = tuple(list(dp1[0]) + [x + n1 for x in dp2[0]])
        return (p, frozenset(set(dp1[1]) | {x + n1 for x in dp2[1]}))
    match, total = 0, 0
    for s1 in product([1, 2, 3], repeat=2):
        for s2 in product([1, 2, 3], repeat=2):
            d1, d2 = def2_n(s1, 2), def2_n(s2, 2)
            if d1 is None or d2 is None:
                continue
            # tensor-product chain on 4 states, state (i,j) -> 2i + j
            prod_support = tuple(
                sum(1 << (2 * a + b)
                    for a in range(2) if s1[i] >> a & 1
                    for b in range(2) if s2[j] >> b & 1)
                for i in range(2) for j in range(2))
            dprod = def2_map(prod_support)
            total += 1
            if dprod == direct_sum(d1, d2, 2):
                match += 1
    print(f"   dp(P1 x P2) == dp(P1) (+) dp(P2): {match}/{total} pairs")
    print("   (the amplituhedron's composition is BCFW/direct-sum-like;")
    print("   Hoffman's is a tensor product — structurally different maps.)")


if __name__ == "__main__":
    main()
