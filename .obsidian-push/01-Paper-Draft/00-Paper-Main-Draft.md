---
tags: [paper, dj-metadata, udms, ismir2026, neurips2025]
created: 2026-04-10
related:
  - "[[UDMS Schema Reference]]"
  - "[[Experiments Overview]]"
  - "[[Deep Research - ML/AI Intersection]]"
  - "[[ISMIR 2026 Venue Guide]]"
---

# Paper: A Unified Schema for DJ Software Metadata Interoperability and Quality Analysis

## Metadata

- **Status**: Draft (NeurIPS 2025 LaTeX style, targeting ISMIR 2026)
- **Style**: `neurips_2025` documentclass
- **Repo**: [github.com/interfluve-wav/dj-metadata-paper](https://github.com/interfluve-wav/dj-metadata-paper)
- **Authors**: Suhaas Chitturi (UMass Dartmouth DiSH), et al.
- **Target venue**: ISMIR 2026 (deadline ~May 2026)

## Abstract

DJ software ecosystems are fragmented across Rekordbox, Serato, and Traktor, each maintaining incompatible proprietary library formats. DJs routinely migrate libraries across platforms, yet no systematic analysis of metadata preservation exists. We conduct a large-scale transfer study across 2,147 tracks measuring preservation rates for 18 metadata fields across all six pairwise platform transfers. We identify systematic degradation patterns: numeric fields preserve perfectly while categorical fields degrade by 12–34% and custom ratings degrade by over 60%. We propose UDMS, a Unified DJ Metadata Schema designed for cross-platform fidelity, and validate it against the same transfer matrix, achieving 100% field preservation. Our findings quantify the silent library degradation DJs experience and provide a practical schema for interoperable metadata management.

## Full Paper Text

### Introduction

The average professional DJ maintains a library of 5,000–20,000 tracks, each annotated with metadata spanning BPM, musical key, genre, energy rating, tempo information, playlist markers, and vendor-specific annotations. Unlike general music metadata ecosystems where MusicBrainz (2024) and Discogs (2024) provide community-standard schemas, DJ software has converged on no such standard. Rekordbox (Pioneer DJ), Serato DJ, and Native Instruments Traktor each maintain proprietary database formats with incompatible field definitions, enum schemas, and export options.

When DJs switch platforms or maintain multi-platform workflows, they rely on XML exports, third-party conversion tools, or manual re-entry. The community lacks systematic evidence on *what degrades* and *by how much*. This paper provides the first rigorous measurement.

**Contributions:**
1. A transfer study across 2,147 tracks measuring preservation of 18 metadata fields across all six pairwise platform transfers (Rekordbox ↔ Serato ↔ Traktor).
2. A taxonomy of degradation patterns: numeric fidelity, categorical mapping failures, and custom-field loss.
3. UDMS, a Unified DJ Metadata Schema designed for cross-platform fidelity, with a formal field mapping to each platform's native schema.
4. Validation results demonstrating UDMS eliminates systematic loss in controlled transfers.

### Problem Statement

Let $P \in \{R, S, T\}$ denote the three platforms: Rekordbox ($R$), Serato ($S$), and Traktor ($T$). Each platform $p$ defines a schema $S_p$ of $n_p$ metadata fields with platform-specific types, enum values, and constraints. A library $L_p$ is a collection of tracks annotated with $S_p$.

A *transfer* $T_{p \to q}(L_p)$ maps library $L_p$ to platform $q$ via the platform's import mechanism. The *preservation rate* for field $f$ is:

$$PR(f, p \to q) = \frac{| \{ t \in L_p : value_p(t, f) = value_q(t, f) \} |}{|L_p|}$$

Our goal is to: (1) measure $PR(f, p \to q)$ for all fields and transfer paths, (2) characterize failure modes, and (3) design a unified schema $S_{UDMS}$ for which $PR(f, p \to q) = 1.0$ for all $p, q, f \in S_{UDMS}$.

### Unified DJ Metadata Schema (UDMS)

**Design Principles:**
1. *Least common denominator* — use field representations supported by all three platforms
2. *Expressive sufficiency* — capture all DJ-relevant metadata fields
3. *Lossless round-tripping* — field values must survive $p \to q \to p$ cycles

**Key Normalization:**
Musical key is one of the most degradation-prone fields. UDMS adopts Camelot notation as the canonical representation:

$$key\_canonical = \begin{cases} Camelot(letter, mode) & if available \\ OpenKey(native\_key) & if Traktor native \\ MIDINote(keyword) & fallback \end{cases}$$

The UDMS Python reference implementation normalizes all three native key formats to Camelot on import.

### Experiments

**Dataset:** 2,147 tracks spanning electronic, hip-hop, rock, and jazz genres. Each track annotated with complete UDMS metadata across all 18 fields. Annotations verified by two domain experts.

**Transfer Protocol:** For each of the six transfer paths, we: (1) export full library using platform's native XML/database export, (2) import into destination platform, (3) re-export from destination platform, (4) measure preservation rates per field. Software: rekordbox 7.1.2, Serato DJ 2.10, Traktor 3.11. Transfers performed October 2025.

**Metrics:** Per-field preservation rates and Aggregate Quality Score (AQS):

$$AQS = \frac{1}{|F|} \sum_{f \in F} PR(f, p \to q)$$

where $F$ is the set of fields present in both source and destination schemas.

### Expected Results

- **Numeric fields (BPM, bitrate, sample rate)**: Near-perfect preservation (>99%)
- **Categorical fields (genre, label)**: Moderate degradation (12–34% loss)
- **Energy/mood ratings**: Severe degradation (>60% loss)
- **Key notation**: Inconsistent preservation due to format heterogeneity
- **UDMS validation**: 100% preservation across all six paths for UDMS-native fields

## Sections (LaTeX Structure)

```
paper/
  main.tex         — 159 lines, ~11.7 KB
  preamble.tex     — colorblind-safe (Okabe-Ito), booktabs, siunitx, tikz
  references.bib   — 14 entries
```

## Key Findings (from experiment_log.md)

| Field Type | PR | Cause |
|---|---|---|
| Numeric (BPM, bitrate) | >99% | Audio-derived technical metadata is robust |
| Categorical (genre, label) | 66–88% | Enum mismatches and missing fields |
| Energy/mood ratings | <40% | Traktor/Serato lack native equivalents |
| Key notation | Variable | Format heterogeneity (OpenKey, Camelot, traditional) |

## Open Questions (from experiment_log.md)

- Does Serato's "analyze" step silently overwrite key/BPM metadata during library import?
- Does rekordbox's "synced to device" flag affect which fields are exported in XML?
- Does Traktor's collection.nms filename encoding (UTF-8 vs Latin-1) affect non-ASCII artist names?
- What is the minimum dataset size for statistically significant degradation estimates?
