#!/usr/bin/env python3
"""Add gap-filler citations to main.tex without mangling LaTeX backslashes."""

with open('/Users/suhaas/Documents/GitHub/dj-metadata-paper/paper/main.tex', 'r') as f:
    tex = f.read()

# ============================================================
# 1. Expand "Audio analysis for metadata" paragraph in Related Work
# ============================================================
old_audio = (
    "\\textbf{Audio analysis for metadata.} "
    "Key detection algorithms~\\citep{silva2025keydetection} and "
    "beat tracking systems~\\citep{heydari2021beatnet,chang2024beast} "
    "provide automated BPM and key annotation. "
    "Audio fingerprinting~\\citep{ke2005audio,kurth2008efficient,jang2009pairwise} "
    "enables track identification for metadata recovery. "
    "Zero-shot tagging~\\citep{choi2019zeroshot} offers genre classification "
    "without platform-specific training."
)
new_audio = (
    "\\textbf{Audio analysis for metadata.} "
    "Automated BPM and key detection underpin DJ software workflows. "
    "B\\\"ock et al.~\\citep{bock2015tempo} introduced RNN-based tempo estimation "
    "with resonating comb filters, establishing the foundation for modern beat-tracking "
    "in MIR. Despite near-perfect MIREX results, Schreiber et al.~\\citep{schreiber2020tempo} "
    "argue that tempo estimation is not fully solved: evaluation metrics use arbitrary "
    "tolerances (4\\% for ACC1), and industry requirements differ from academic benchmarks. "
    "Key detection algorithms similarly vary in accuracy across genres and datasets~\\citep{ismir2015keydetection}. "
    "Krumhansl's cognitive key profiles~\\citep{krumhansl1990cognitive} provide the "
    "psychological grounding for the Krumhansl-Schmuckler key-finding algorithm, "
    "which remains widely used~\\citep{temperley1999key,silva2025keydetection}. "
    "For metadata recovery, audio fingerprinting~\\citep{ke2005audio,kurth2008efficient,jang2009pairwise} "
    "enables track identification and similarity-based enrichment. "
    "Zero-shot tagging~\\citep{choi2019zeroshot} offers genre classification "
    "without platform-specific training."
)
tex = tex.replace(old_audio, new_audio)

# ============================================================
# 2. Add genre taxonomy citation after Genre Taxonomy section
# ============================================================
old_taxonomy_end = (
    "suggesting that genre is the last field to be "
    "annotated---often skipped entirely."
)
new_taxonomy_end = (
    "suggesting that genre is the last field to be "
    "annotated---often skipped entirely. "
    "This fragmentation is not unique to our library: "
    "Xu et al.~\\citep{xu2025edmtaxonomy} find that EDM's commercial taxonomy "
    "(35 Beatport subgenres) is acoustically overspecified, collapsing to 17--20 "
    "natural clusters. This suggests the 70 genre strings in our library reflect "
    "cultural labeling practices rather than objective acoustic distinctions."
)
tex = tex.replace(old_taxonomy_end, new_taxonomy_end)

# ============================================================
# 3. Add DLF metadata quality framework citation
# ============================================================
old_mdq = (
    "Ribov and Hagedorn~\\citep{ribov2022} study metadata quality in digital archives. "
    "We extend this framework to the DJ domain."
)
new_mdq = (
    "Ribov and Hagedorn~\\citep{ribov2022} study metadata quality in digital archives, "
    "identifying completeness, accuracy, and consistency as core quality dimensions. "
    "The DLF Metadata Assessment Framework operationalizes this with seven quality dimensions "
    "(completeness, accuracy, provenance, accessibility, consistency, conformance, "
    "and timeliness)~\\citep{bruce2004metadata}. "
    "We extend this framework to the DJ domain."
)
tex = tex.replace(old_mdq, new_mdq)

# ============================================================
# 4. Add music similarity citation in Introduction
# ============================================================
old_intro_sim = "genre for playlist curation~\\citep{liebman2015djmc} and"
new_intro_sim = "genre for playlist curation~\\citep{liebman2015djmc}, music similarity computation~\\citep{xia2008similarity}, and"
tex = tex.replace(old_intro_sim, new_intro_sim)

with open('/Users/suhaas/Documents/GitHub/dj-metadata-paper/paper/main.tex', 'w') as f:
    f.write(tex)

print("Done.")
print(f"New length: {len(tex)} chars ({tex.count(chr(10))} lines)")
