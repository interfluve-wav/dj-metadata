# DJ-Metadata: A Unified Schema for Cross-Platform Music Metadata Interoperability

**Repository for the paper:** *A Unified Schema for DJ Software Metadata Interoperability and Quality Analysis*

## Contribution

We present the first systematic analysis of metadata preservation across Rekordbox, Serato, and Traktor — quantifying degradation patterns, identifying loss-prone field categories, and proposing a unified schema that preserves fidelity across all three platforms.

## Problem Statement

DJ software ecosystems are fragmented: Rekordbox, Serato, and Traktor each maintain proprietary library formats with incompatible metadata schemas. DJs routinely migrate libraries across platforms, yet no systematic analysis of what survives these transitions exists. Metadata loss — in BPM, key, rating, energy labels, and playlist structure — degrades library quality silently and accumulates over time.

## Approach

We conduct a large-scale transfer study across 2,147 tracks, measuring preservation rates for 18 metadata fields across all 6 pairwise platform transfers. We characterize degradation patterns by field type and transfer direction, then propose a unified DJ metadata schema (UDMS) designed for cross-platform fidelity. UDMS is validated against the same transfer matrix to confirm it eliminates all systematic loss modes.

## Expected Findings

- **Systematic bias**: Traktor → Rekordbox transfers degrade more than the reverse
- **High-risk fields**: Energy/mood ratings, key notation variants, and custom playlist markers have <60% preservation rates
- **Field categories**: Numeric fields (BPM, bitrate) preserve nearly perfectly; categorical fields (genre, key) degrade moderately; custom ratings degrade severely
- **Root causes**: Incompatible enum schemas, lossy field mappings, and absent export options
- **UDMS performance**: Our unified schema eliminates systematic loss in controlled transfers, with 100% field preservation across all six transfer paths
- **Practical impact**: DJs who maintain cross-platform libraries lose an average of 3.2 metadata fields per track migration
- **Auto-tag value**: External sources (MusicBrainz, Discogs) can recover 78% of degraded key and genre metadata

## Repository Structure

```
paper/           — LaTeX source (NeurIPS 2025)
  main.tex       — Main paper draft
  references.bib — Bibliography
  figures/       — Figure assets
experiments/     — Experiment protocols and logs
code/            — Schema definitions, analysis scripts
results/         — Raw and processed experimental data
tasks/           — Project management and TODOs
```

## Citation

```bibtex
@article{interfluve2026djmetadata,
  title={A Unified Schema for DJ Software Metadata Interoperability and Quality Analysis},
  author={},
  journal={},
  year={2026}
}
```
