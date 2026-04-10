---
tags: [index, research, dj-metadata, paper]
created: 2026-04-10
---

# Research Agent: DJ-Metadata Paper

**Folder**: `Research Agent - Paper/` in Obsidian vault
**Source repo**: [github.com/interfluve-wav/dj-metadata-paper](https://github.com/interfluve-wav/dj-metadata-paper)
**Cloned to**: `/tmp/dj-metadata-paper`

## What's in this folder

| File | Description |
|---|---|
| [[00-Paper-Main-Draft]] | Full LaTeX paper text, abstract, contributions, problem statement, UDMS, experiments |
| [[UDMS-Schema-Reference]] | UDMS 18-field schema, platform mappings, key normalization, Python implementation |
| [[Experiments-Overview]] | 5 experiments (transfer matrix, field taxonomy, round-trip, UDMS validation, auto-tag recovery) |
| [[Deep-Research---ML-AI-Intersection]] | ML/AI literature intersection — audio ML, LLMs, ontologies, DJ recommendation |
| [[References]] | All BibTeX entries (14 current + 10 new from research) |
| [[Tasks-and-TODOs]] | ISMIR 2026 writing tasks, experiments, key decisions pending |

## Quick Summary

The paper proposes **UDMS** (Unified DJ Metadata Schema) — a canonical 18-field schema that solves the problem of silent metadata degradation when DJs transfer libraries between Rekordbox, Serato, and Traktor. The paper:

1. Measures what degrades across 2,147 tracks and 6 transfer paths
2. Classifies degradation by field type (numeric > categorical > custom)
3. Proposes UDMS as a lossless cross-platform schema
4. Validates UDMS achieves 100% field preservation

**Target**: ISMIR 2026

## Key Stats

- 2,147 tracks in dataset
- 18 UDMS canonical fields
- 6 pairwise platform transfer paths
- 5 planned experiments
- 14 references → 24 after additions
- 159 lines LaTeX in `main.tex`

## Deep Research Findings

The paper connects to 4 ML/AI areas:
1. **Audio ML** (CUE-DETR, BeatNet, BEAST-1) — DJ-specific audio analysis
2. **Audio Fingerprinting** (Ke+ CVPR 2005, Kurth+Müller, Jang+) — metadata recovery
3. **LLM Metadata Enrichment** (TTMR++, Music Metadata LLMs) — structured input
4. **Ontologies** (Music Meta Ontology, Schema.org, DOREMUS) — schema interoperability

## Wiki-links to all notes

[[Paper Draft]]
[[UDMS Schema Reference]]
[[Experiments Overview]]
[[References]]
[[Deep Research - ML/AI Intersection]]
[[Tasks and TODOs]]
