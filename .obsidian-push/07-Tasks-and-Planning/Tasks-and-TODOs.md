---
tags: [tasks, planning, ismir2026, paper-writing, udms]
created: 2026-04-10
related:
  - "[[Paper Draft]]"
  - "[[Experiments Overview]]"
---

# Tasks and TODOs

**File**: `tasks/TODO.md`
**Target venue**: ISMIR 2026 (deadline ~May 2026)

## Status Summary

- [x] Initial paper structure (LaTeX draft, UDMS schema, experiments, analysis)
- [x] UDMS schema reference implementation (Python)
- [x] Experiment protocol defined (5 experiments)
- [x] 14 references in `references.bib`
- [x] 5 new ML/AI references identified (CUE-DETR, BeatNet, BEAST-1, Kurth+Müller, Ke+)
- [x] Research agent deep research completed
- [ ] All experiments pending execution

---

## Paper Writing

### Abstract & Introduction
- [ ] Refine one-sentence contribution statement
- [ ] Add concrete example of degradation in intro (real track example)
- [ ] Frame ML/AI intersection clearly (UDMS as infrastructure for DJ ML)

### Methods
- [ ] Add pseudocode for UDMS normalization pipeline
- [ ] Document full hyperparameter settings for each platform export
- [ ] Add power analysis for minimum dataset size

### Results
- [ ] Generate Figure 1: Transfer matrix heatmap (`fig_transfer_matrix.pdf`)
- [ ] Generate Figure 2: Field taxonomy bar chart (`fig_field_taxonomy.pdf`)
- [ ] Generate Figure 3: Degradation examples (`fig_degradation_examples.pdf`)
- [ ] Generate Figure 4: UDMS validation comparison (`fig_udms_validation.pdf`)
- [ ] Generate Figure 5: Round-trip degradation (`fig_roundtrip_degradation.pdf`)
- [ ] Add error bars and statistical tests (McNemar's test)

### UDMS Schema
- [ ] Add JSON Schema for machine-readable UDMS validation
- [ ] Complete Serato → UDMS adapter (handle crate_ fields)
- [ ] Complete Traktor → UDMS adapter (handle collection entry format)

---

## Experiments

- [ ] Run Experiment 1: Full Transfer Matrix (2,147 tracks × 6 paths)
- [ ] Run Experiment 2: Field-Level Degradation Taxonomy
- [ ] Run Experiment 3: Round-Trip Fidelity
- [ ] Run Experiment 4: UDMS Validation
- [ ] Run Experiment 5: Auto-Tag Recovery Study
- [ ] Compute statistical significance (McNemar's test) for pairwise comparisons

---

## References

- [ ] Add new ML/AI references to `references.bib`:
  - [ ] CUE-DETR (ISMIR 2024)
  - [ ] BeatNet (ISMIR 2021)
  - [ ] BEAST-1 (ICASSP 2024)
  - [ ] Ke+ (CVPR 2005)
  - [ ] Kurth+Müller (IEEE 2008)
  - [ ] Jang+ (IEEE TIFS 2009)
  - [ ] Music Meta Ontology (arXiv 2023)
  - [ ] TTMR++ (ICASSP 2024) — already in refs
  - [ ] DJ-MC (AAMAS 2015)
  - [ ] Music Metadata LLMs (arXiv 2025)

---

## Key Decisions Pending

1. [ ] **Dataset ownership**: Who owns the 2,147 tracks? IRB approval needed?
2. [ ] **Bonk integration**: Does Bonk app serve as experimental framework?
3. [ ] **Co-authors**: Any collaborators to add?
4. [ ] **License**: UDMS schema/code — MIT or Apache 2.0?

---

## ISMIR 2026 Venue Notes

- **Deadline**: ~May 2026 (comfortable timeline from April 2026)
- **Style**: ISMIR usesismir for LaTeX formatting
- **Review**: Double-blind, ~3 reviewers
- **Audience**: Music IR researchers, MIR practitioners, digital music scholars
- **Track**: Music metadata, library interoperability, MIR systems
- **Fit**: UDMS paper fits "Music Metadata and Digital Libraries" track

---

## BONK Integration Opportunity

The Bonk DJ app (`github.com/interfluve-wav/bonk`) is the practical instantiation of UDMS:
- Implements cross-platform metadata normalization in Python
- rekordbox 6/7 smart MCP with 28 tools
- BPM/key detection, auto-tagging pipeline
- Privacy-preserving (no external APIs)

Could write a short **demo paper** or position paper alongside the main ISMIR paper showing Bonk as the UDMS implementation vehicle.
