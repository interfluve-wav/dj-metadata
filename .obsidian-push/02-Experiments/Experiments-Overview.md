---
tags: [experiments, dj-metadata, transfer-study, udms, quantitative]
created: 2026-04-10
related:
  - "[[Paper Draft]]"
  - "[[UDMS Schema Reference]]"
  - "[[Deep Research - ML/AI Intersection]]"
  - "[[Tasks and TODOs]]"
---

# Experiments Overview

**File**: `experiments/experiment_log.md`
**Dataset**: 2,147 tracks | Software: rekordbox 7.1.2, Serato DJ 2.10, Traktor 3.11
**Transfer period**: October 2025 | Platform OS: macOS 14.x

## Dataset Details

| Property | Value |
|---|---|---|
| Total tracks | 2,147 |
| Genres covered | Electronic, Hip-Hop, Rock, Jazz, Latin, Classical |
| BPM range | 60–200 |
| Key coverage | All 24 major/minor keys represented |
| Annotation | 2 domain experts, discrepancies resolved by third |
| Platform versions | rekordbox 7.1.2, Serato DJ 2.10, Traktor 3.11 |
| Transfer period | October 2025 |

## Five Planned Experiments

### Experiment 1: Full Transfer Matrix
- **Claim**: All pairwise platform transfers degrade metadata; Traktor → Rekordbox worst path
- **Design**: 6 transfer paths (R↔S, R↔T, S↔T), both directions, round-trip measurement
- **Key result (expected)**: Traktor → Rekordbox AQS < 0.70; Serato ↔ Rekordbox highest AQS > 0.85
- **Output**: `results/exp1_transfer_matrix/fig_transfer_matrix.pdf`

### Experiment 2: Field-Level Degradation Taxonomy
- **Claim**: Degradation clusters by field type (numeric > categorical > custom)
- **Design**: For each of 18 UDMS fields, measure PR across all 6 paths; cluster by behavior
- **Key result (expected)**: Numeric PR > 0.99; categorical 0.66–0.88; custom < 0.40
- **Output**: `results/exp2_field_taxonomy/fig_field_taxonomy.pdf`

### Experiment 3: Round-Trip Fidelity
- **Claim**: Round-trip transfers (p → q → p) degrade more than single transfers
- **Design**: Same dataset, measure PR for single and double round-trip cycles
- **Key result (expected)**: Round-trip doubles degradation for fields with PR < 0.90 in single transfer
- **Output**: `results/exp3_roundtrip/fig_roundtrip_degradation.pdf`

### Experiment 4: UDMS Validation
- **Claim**: UDMS canonical fields preserve at PR = 1.0 across all paths
- **Design**: UDMS normalization pipeline applied before each export → full transfer matrix
- **Key result (expected)**: UDMS fields achieve PR ≥ 0.98 across all paths
- **Output**: `results/exp4_udms_validation/fig_udms_validation.pdf`

### Experiment 5: Auto-Tag Recovery Study
- **Claim**: External sources (MusicBrainz, Discogs) recover 78% of degraded key/genre metadata
- **Design**: 500 tracks with degraded key/genre → MusicBrainz + Discogs lookup → measure restoration
- **Key result (expected)**: MusicBrainz recovers 71% key; Discogs recovers 83% genre; combined 78%
- **Output**: `results/exp5_autotag_recovery/`

## Expected Figures

| Filename | Description | Paper section |
|---|---|---|
| `fig_transfer_matrix.pdf` | Heatmap of AQS across all 6 transfer paths | Experiments, Figure 1 |
| `fig_field_taxonomy.pdf` | Bar chart of PR by field type | Experiments, Figure 2 |
| `fig_degradation_examples.pdf` | Side-by-side metadata before/after transfer | Problem Statement, Figure 3 |
| `fig_udms_validation.pdf` | UDMS vs baseline AQS comparison | UDMS Section, Figure 4 |
| `fig_roundtrip_degradation.pdf` | Single vs round-trip PR delta | Experiments, Figure 5 |

## Metrics

**Preservation Rate (PR)**:
$$PR(f, p \to q) = \frac{| \{ t \in L_p : value_p(t, f) = value_q(t, f) \} |}{|L_p|}$$

**Aggregate Quality Score (AQS)**:
$$AQS = \frac{1}{|F|} \sum_{f \in F} PR(f, p \to q)$$

## UDMS Normalization Pipeline

```python
def normalize_to_udms(track: Track, source_platform: Platform) -> UDMS:
    udms = UDMS()
    udms.bpm = normalize_bpm(track.get_bpm(source_platform))
    udms.key = normalize_key(track.get_key(source_platform))  # → Camelot
    udms.rating = normalize_rating(track.get_rating(source_platform), source_platform)
    # ... all 18 fields
    return udms
```

## Open Questions

- Does Serato's "analyze" step silently overwrite key/BPM during library import?
- Does rekordbox's "synced to device" flag affect which fields are exported in XML?
- Does Traktor's collection.nms encoding (UTF-8 vs Latin-1) affect non-ASCII artist names?
- Minimum dataset size for statistically significant degradation estimates?
