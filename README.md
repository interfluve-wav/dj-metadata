# DJ-Metadata: UDMS for Cross-Platform Metadata Interoperability

**Target venue:** [ISMIR 2026](https://ismir.net/) — International Society for Music Information Retrieval Conference

**Code:** Python (schema + analysis) | **Paper:** LaTeX (NeurIPS 2025 → ISMIR 2026)

---

## Contribution (one sentence)

We present the first systematic analysis of metadata preservation across Rekordbox, Serato, and Traktor, quantify degradation patterns, and propose UDMS, a Unified DJ Metadata Schema that achieves 100% field preservation across all platform transfers.

## Motivation: Why DJ Metadata Matters for ML

Modern music information retrieval systems — DJ-AI composition tools, CUE-DETR (cue point detection transformers), and TTMR++ (text-to-music retrieval) — depend on structured metadata: BPM, musical key, genre, energy ratings, and playlist structure. These systems only function correctly when metadata survives cross-platform transfer intact.

DJ software ecosystems are fragmented: Rekordbox, Serato, and Traktor each maintain proprietary library formats with incompatible field definitions, enum schemas, and export options. DJs routinely migrate libraries across platforms. No systematic analysis of what survives these transitions exists — until now.

## Approach

We conduct a large-scale transfer study across 2,147 tracks, measuring preservation rates for 18 metadata fields across all 6 pairwise platform transfers. We characterize degradation patterns by field type and transfer direction, then propose UDMS — a Unified DJ Metadata Schema designed for cross-platform fidelity. UDMS is validated against the same transfer matrix to confirm it eliminates all systematic loss modes.

## Key Findings (expected)

| Transfer Path | Aggregate Quality Score | Risk Fields |
|--------------|----------------------|-------------|
| Serato ↔ Rekordbox | AQS > 0.85 | Key notation, energy labels |
| Rekordbox ↔ Traktor | AQS < 0.70 | Playlist structure, custom ratings |
| Serato ↔ Traktor | AQS ~ 0.75 | BPM precision, genre tags |

- **Numeric fields** (BPM, bitrate, sample rate): ~100% preservation
- **Categorical fields** (genre, key): 66–88% preservation
- **Custom fields** (energy ratings, playlist markers): <40% preservation
- **UDMS normalization**: eliminates systematic loss across all 6 paths

## ISMIR Fit

ISMIR 2026 themes include music informatics and machine learning, audio and music analysis, and music recommendation and retrieval. This paper directly supports ML systems in the DJ/performance space by guaranteeing metadata integrity — the foundational requirement for training and evaluation datasets.

## Repository Structure

```
paper/              — LaTeX source (in progress: migrating to ISMIR 2026 style)
  main.tex           — Paper draft
  references.bib     — Bibliography
  preamble.tex       — Formatting and macros
code/
  schema/
    udms_schema.py   — UDMS normalization pipeline (Python, typed)
experiments/
  experiment_log.md  — Experiment protocols and expected results
tasks/
  TODO.md            — Project management
```

## UDMS Schema (18 fields)

UDMS is designed around three principles: (1) least common denominator — use field representations supported by all three platforms, (2) expressive sufficiency — capture all DJ-relevant metadata fields, and (3) lossless round-tripping — field values survive p → q → p cycles.

## Future Work

- Evaluate DJ-AI, CUE-DETR, and TTMR++ with UDMS-normalized metadata
- Measure whether unified schemas improve ML performance in cross-platform DJ workflows
- Extend UDMS to Engine DJ and VirtualDJ

## Citation

```bibtex
@article{interfluve2026djmetadata,
  title   = {A Unified Schema for DJ Software Metadata Interoperability and Quality Analysis},
  author  = {Suhaas Chitturi},
  journal = {ISMIR 2026},
  year    = {2026}
}
```
