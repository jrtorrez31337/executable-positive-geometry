#!/usr/bin/env bash
# Rebuild the paper corpus from arXiv. Every ID was verified against the
# arXiv API (title match) before being added; see README.md for the
# annotated index with evidence tiers. Rate-limited per arXiv's request.
set -euo pipefail
cd "$(dirname "$0")"

fetch() {  # fetch <arxiv-id> <target-path>
    if [ -f "$2" ]; then echo "skip (exists): $2"; return; fi
    curl -sL "https://arxiv.org/pdf/$1" -o "$2"
    head -c 4 "$2" | grep -q "%PDF" || { echo "FAILED: $2"; exit 1; }
    echo "ok: $2"
    sleep 3
}

fetch 1312.2007        "1-positive-geometry/2013-arkani-hamed-trnka-amplituhedron.pdf"
fetch 1312.7878        "1-positive-geometry/2013-arkani-hamed-trnka-into-the-amplituhedron-loops.pdf"
fetch 1711.09102       "1-positive-geometry/2017-abhy-scattering-forms-kinematic-associahedron.pdf"
fetch 1703.04541       "1-positive-geometry/2017-arkani-hamed-bai-lam-positive-geometries-canonical-forms.pdf"
fetch 1709.02813       "1-positive-geometry/2017-arkani-hamed-benincasa-postnikov-cosmological-polytopes.pdf"
fetch 2007.15650       "1-positive-geometry/2020-kojima-rao-2loop-mhv-amplituhedron-trivialization.pdf"
fetch 2410.11501       "1-positive-geometry/2024-dian-mazzucchelli-tellander-two-loop-amplituhedron.pdf"
fetch hep-th/9711200   "2-holography-emergence/1997-maldacena-large-n-ads-cft.pdf"
fetch hep-th/0603001   "2-holography-emergence/2006-ryu-takayanagi-holographic-entanglement-entropy.pdf"
fetch 0905.1317        "2-holography-emergence/2009-swingle-entanglement-renormalization-holography.pdf"
fetch 1005.3035        "2-holography-emergence/2010-van-raamsdonk-building-spacetime-entanglement.pdf"
fetch 1411.7041        "2-holography-emergence/2014-almheiri-dong-harlow-bulk-locality-qec-adscft.pdf"
fetch 1505.05515       "2-holography-emergence/2015-czech-etal-integral-geometry-kinematic-space.pdf"
fetch 1503.06237       "2-holography-emergence/2015-happy-holographic-quantum-error-correcting-codes.pdf"
fetch quant-ph/9707021 "3-qec-topological/1997-kitaev-fault-tolerant-anyons-toric-code.pdf"
fetch 1208.0928        "3-qec-topological/2012-fowler-etal-surface-codes-practical.pdf"
fetch 1304.3061        "4-quantum-computing/2013-peruzzo-etal-vqe-variational-eigensolver.pdf"
fetch 2509.19772       "5-tqnn-bridge/2025-fields-glazebrook-marciano-tqnn-amplituhedron.pdf"

# Pillar 6 (Hoffman program — open-access, non-arXiv sources)
fetch_url() { if [ -f "$2" ]; then echo "skip (exists): $2"; return; fi; curl -sL -A "Mozilla/5.0" "$1" -o "$2"; head -c 4 "$2" | grep -q "%PDF" || { echo "FAILED: $2"; exit 1; }; echo "ok: $2"; sleep 2; }
fetch_url "https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2014.00577/pdf" "6-perception-interface/2014-hoffman-prakash-objects-of-consciousness.pdf"
fetch_url "https://link.springer.com/content/pdf/10.3758/s13423-015-0890-8.pdf" "6-perception-interface/2015-hoffman-singh-prakash-interface-theory-of-perception.pdf"
fetch_url "https://europepmc.org/articles/PMC9858210?pdf=render" "6-perception-interface/2023-hoffman-prakash-prentner-fusions-of-consciousness.pdf"

# Pillar 7 (Track D: magic and holography)
fetch 2106.12587 "7-magic/2022-leone-oliviero-hamma-stabilizer-renyi-entropy.pdf"
fetch 2306.14996 "7-magic/2024-cao-etal-area-operators-require-nonlocal-magic.pdf"
fetch 2403.07056 "7-magic/2024-gravitational-backreaction-is-magical.pdf"
fetch 2511.15576 "7-magic/2025-experimental-nonlocal-magic-superconducting.pdf"


# Pillar 6 additions (Trace Institute-hosted)
fetch_url "https://traceinstitute.org/papers/foundational/2025-hoffman-et-al-traces-of-consciousness.pdf" "6-perception-interface/2025-hoffman-prakash-chattopadhyay-traces-of-consciousness.pdf"
fetch_url "https://traceinstitute.org/papers/foundational/2020-prakash-et-al-fitness-beats-truth.pdf" "6-perception-interface/2021-prakash-etal-fitness-beats-truth.pdf"
fetch_url "https://traceinstitute.org/papers/TRACE_INSTITUTE_WHITE_PAPER.pdf" "6-perception-interface/2025-trace-institute-white-paper.pdf"

fetch 2502.01582 "7-magic/2025-bera-schiro-syk-nonstabilizerness.pdf"
fetch 2502.03093 "7-magic/2025-jasser-odavic-hamma-syk-stabilizer-entropy.pdf"
fetch 2601.03076 "7-magic/2026-malvimat-sarkis-suk-yoon-multipartite-nonlocal-magic-syk.pdf"
fetch 2604.10090 "7-magic/2026-byun-kim-lee-tw-teleportation-sparse-syk.pdf"
fetch 2412.05367 "7-magic/2024-collura-etal-nonstabilizerness-fermionic-gaussian.pdf"
fetch 2604.27049 "7-magic/2026-iannotti-etal-nonlocal-magic-fermionic-gaussian.pdf"
fetch 2512.10126 "7-magic/2025-haque-jafari-underwood-inflation-not-magic.pdf"
fetch 2601.22219 "7-magic/2026-ireland-vennin-nongaussianity-wigner-negativity.pdf"
fetch 2406.06418 "7-magic/2024-bridging-magic-nongaussian-gkp.pdf"
fetch 2605.04099 "7-magic/2026-alavirad-desitter-radiation-particle-creation-sim.pdf"
fetch 2603.13475 "7-magic/2026-cao-etal-state-dependent-geometries-magic-enriched-codes.pdf"
fetch 1704.05069 "1-positive-geometry/2017-arkani-hamed-thomas-trnka-unwinding-amplituhedron-binary.pdf"
echo "corpus complete: $(find . -name '*.pdf' | wc -l)/40 papers"
