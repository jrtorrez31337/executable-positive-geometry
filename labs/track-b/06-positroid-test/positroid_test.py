"""Lab 6 — does the Hoffman map respect positroid structure?

Conventions verified against the full text of Hoffman-Prakash-Prentner,
"Fusions of Consciousness" (Entropy 25:129, 2023), pp. 17-21:

  Definition 1: a decorated permutation is sigma: [n] -> [2n] with
    a <= sigma(a) <= a+n and sigma mod n bijective; fixed points of the
    underlying permutation are decorated sigma(a) = a or a+n.
  Definition 2 (Markov decorated permutations):
    - a transient  -> sigma(a) = a
    - a absorbing (singleton recurrent class) -> sigma(a) = a + n
    - a recurrent in a multi-state class C -> sigma(a) = first b > a such
      that the cyclic window (a, a+1, ..., b) contains all of C.
  Validation: the paper's own 9-state example (p. 20) is reproduced
  exactly, in both its all-recurrent and transient-state variants.

Geometry-side statistic: k = #anti-exceedances = #{a : sigma(a) > n},
which selects the Grassmannian Gr(k, n) whose positroid cells the labels
index. Everything below is exhaustive at n = 4 (no sampling).
"""

from itertools import permutations, product


# ─── Decorated permutations (geometry side) ──────────────────────────────────
# Representation: (perm, upper) with perm a 0-indexed tuple (sigma mod n)
# and upper = frozenset of fixed points decorated sigma(a) = a + n.

def all_decorated_permutations(n):
    out = []
    for p in permutations(range(n)):
        fixed = [i for i in range(n) if p[i] == i]
        for mask in range(2 ** len(fixed)):
            upper = frozenset(f for b, f in enumerate(fixed) if mask >> b & 1)
            out.append((p, upper))
    return out


def k_statistic(p, upper) -> int:
    """Anti-exceedances: sigma_affine(a) >= n, i.e. p[a] < a, or a fixed
    point decorated a+n."""
    return sum(1 for i in range(len(p)) if p[i] < i) + len(upper)


# ─── Markov chains (dynamics side) and the Def-2 map ─────────────────────────

def classes_of(support, n):
    """Communicating classes + recurrent subset from a support digraph
    (tuple of bitmasks; bit j of support[i] = edge i->j)."""
    reach = [support[i] | (1 << i) for i in range(n)]
    for _ in range(n):
        for i in range(n):
            r = reach[i]
            for j in range(n):
                if r >> j & 1:
                    r |= reach[j]
            reach[i] = r
    seen, classes = set(), []
    for i in range(n):
        if i in seen:
            continue
        cls = frozenset(j for j in range(n)
                        if reach[i] >> j & 1 and reach[j] >> i & 1)
        classes.append(cls)
        seen |= cls
    recurrent = {c for c in classes
                 if all(support[i] & ~sum(1 << j for j in c) == 0 for i in c)}
    return classes, recurrent


def def2_affine(support, n):
    """Definition 2, verbatim: returns sigma_affine with values in [a, a+n]."""
    classes, recurrent = classes_of(support, n)
    cls_of = {i: c for c in classes for i in c}
    sig = [None] * n
    for a in range(n):
        c = cls_of[a]
        if c not in recurrent:
            sig[a] = a                      # transient
        elif len(c) == 1:
            sig[a] = a + n                  # absorbing (paper: sigma = a+n)
        else:
            window, b = {a}, a
            while not c <= window:
                b += 1
                window.add(b % n)
            sig[a] = b
    assert sorted(s % n for s in sig) == list(range(n)), "not a permutation"
    return sig


def def2_map(support, n):
    sig = def2_affine(support, n)
    perm = tuple(s % n for s in sig)
    upper = frozenset(a for a in range(n) if sig[a] == a + n)
    return perm, upper


def paper_example_check() -> None:
    """The authors' own 9-state example, p. 20 (converted to 0-indexed)."""
    n = 9
    # cycles (158)(2)(34)(6)(79), 1-indexed -> successor map, 0-indexed:
    succ = {0: 4, 4: 7, 7: 0, 1: 1, 2: 3, 3: 2, 5: 5, 6: 8, 8: 6}
    support = tuple(1 << succ[i] for i in range(n))
    got = [s + 1 for s in def2_affine(support, n)]        # back to 1-indexed
    assert got == [8, 11, 4, 12, 10, 15, 9, 14, 16], got
    # variant: state 2 (1-indexed) transient — give it an exit to state 1
    support2 = list(support)
    support2[1] = 1 << 0
    got2 = [s + 1 for s in def2_affine(tuple(support2), n)]
    assert got2 == [8, 2, 4, 12, 10, 15, 9, 14, 16], got2
    print("Validation: paper's 9-state example reproduced exactly "
          "(both variants).\n")


# ─── The tests (n = 4, exhaustive) ───────────────────────────────────────────

N = 4


def main() -> None:
    paper_example_check()

    print("Census (geometry side): decorated permutations of [4] by k")
    c: dict[int, int] = {}
    for p, u in all_decorated_permutations(N):
        c[k_statistic(p, u)] = c.get(k_statistic(p, u), 0) + 1
    print(f"   {dict(sorted(c.items()))}   total {sum(c.values())}")
    assert c == {0: 1, 1: 15, 2: 33, 3: 15, 4: 1}
    print("   matches positroid cell counts of Gr>=0(k,4): (1,15,33,15,1)\n")

    print("H1 coverage + H2 statistic (all 50,625 supports)")
    image: dict[tuple, int] = {}
    relation_holds = True
    for s in product(range(1, 2 ** N), repeat=N):
        dp = def2_map(s, N)
        image[dp] = image.get(dp, 0) + 1
        classes, recurrent = classes_of(s, N)
        rec_states = sum(len(cc) for cc in recurrent)
        multi = sum(1 for cc in recurrent if len(cc) > 1)
        if k_statistic(*dp) != rec_states - multi:
            relation_holds = False
    ks: dict[int, int] = {}
    for dp in image:
        ks[k_statistic(*dp)] = ks.get(k_statistic(*dp), 0) + 1
    print(f"   distinct labels in image: {len(image)} / 65")
    print(f"   image by k: {dict(sorted(ks.items()))}   (census: {dict(sorted(c.items()))})")
    print(f"   k == (#recurrent states) - (#multi-state recurrent classes)"
          f" in ALL cases: {relation_holds}")
    print("   k = 0 (the bottom cell) is unreachable: every chain has a")
    print("   recurrent class, and each class contributes >= 1 to k. The")
    print("   k-statistic reads class-counting, nothing dynamical.\n")

    print("H4 compression: supports per label (top 3)")
    for dp, cnt in sorted(image.items(), key=lambda kv: -kv[1])[:3]:
        print(f"   perm={dp[0]} upper={sorted(dp[1])}: {cnt} supports")
    print("   Def-2 never reads a transition probability: spectra, mixing")
    print("   times, stationary measures are invisible to the label.\n")

    print("H3 compositionality: tensor product vs direct sum (81 pairs, n=2)")
    def direct_sum(d1, d2, n1):
        p = tuple(list(d1[0]) + [x + n1 for x in d2[0]])
        return p, frozenset(set(d1[1]) | {x + n1 for x in d2[1]})
    match = total = 0
    mismatches = []
    for s1 in product((1, 2, 3), repeat=2):
        for s2 in product((1, 2, 3), repeat=2):
            d1, d2 = def2_map(s1, 2), def2_map(s2, 2)
            prod_support = tuple(
                sum(1 << (2 * a + b)
                    for a in range(2) if s1[i] >> a & 1
                    for b in range(2) if s2[j] >> b & 1)
                for i in range(2) for j in range(2))
            dprod = def2_map(prod_support, 4)
            total += 1
            if dprod == direct_sum(d1, d2, 2):
                match += 1
            elif len(mismatches) < 2:
                mismatches.append((s1, s2, d1, d2, dprod))
    print(f"   dp(P1 x P2) == dp(P1) (+) dp(P2): {match}/{total} pairs")
    for s1, s2, d1, d2, dprod in mismatches:
        print(f"     e.g. supports {s1},{s2}: dp1={d1}, dp2={d2}, "
              f"dp(product)={dprod}")


if __name__ == "__main__":
    main()
