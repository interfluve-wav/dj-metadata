# UDMS: Unified DJ Metadata Schema

[![DOI](https://img.shields.io/badge/Zenodo-DOI%20Pending-orange)](https://zenodo.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)
![LaTeX](https://img.shields.io/badge/LaTeX-13%20pages-blue)

**The first systematic metadata quality analysis of real-world DJ libraries.**  
UDMS normalizes and cross-validates metadata across Rekordbox, Serato, Engine DJ, and VirtualDJ — revealing systematic errors, cross-platform losses, and maintenance opportunities.

---

## Key Findings

| Metric | Value |
|--------|-------|
| Title / Artist / Album preservation | **100%** across platforms |
| BPM agreement ( Rekordbox ↔ Serato ) | **89.5%** |
| Key agreement — exact / effective | **71.3%** / **100%** |
| Genre agreement | **79.1%** |
| Rekordbox 2× half-tempo error rate | **27%** of tracks |
| External recovery (MusicBrainz) | **6%** for EDM / dance |

> Rekordbox stores BPM at exactly **2× the actual tempo** for UK dubstep, drum-and-bass, footwork, and Jersey Club genres. Engine DJ and Serato store the correct value. This is a systematic **interpretation difference**, not a transfer bug.

---

## Platforms Analyzed

```
Rekordbox    636 tracks    (XML export)
Serato       382 tracks    (SQLite database)
Engine DJ    112 tracks    (SQLite database)
VirtualDJ    190 tracks    (XML export)
───────────────────────────────
Total        1,320 tracks  across 4 ecosystems
```

**Cross-platform matched tracks:** 143 (Rekordbox ↔ Serato) · 24 (Rekordbox ↔ VirtualDJ)

---

## UDMS — Unified DJ Metadata Schema

Python implementation: `code/schema/udms_schema.py`  
JSON Schema: `schema/udms_schema.json`

**11 canonical fields:**

```
title · artist · album · genre · BPM · key (Camelot) ·
rating · label · duration_sec · bitrate · sample_rate
```

**Key normalizations:**
- OpenKey and Traditional notation → Camelot (e.g., `"Fm"` → `"4A"`)
- Platform-specific rating scales → 0–5 stars
- BPM 2× detection: flags if `1.95 < platform_bpm / reference_bpm < 2.05`

---

## Repository Structure

```
dj-metadata-study/
├── paper/
│   ├── main.tex              — LaTeX paper (13 pages)
│   ├── preamble.tex          — Preamble (packages, macros)
│   └── references.bib        — 23 citations (all cited)
├── code/
│   ├── schema/
│   │   └── udms_schema.py    — UDMS schema + 5 platform adapters
│   ├── compare_platforms.py  — Cross-platform comparison engine
│   └── parse_serato.py       — Parse Serato database V2 binary
├── data/
│   ├── rekordbox_tracks_parsed.json     — 636 Rekordbox tracks (UDMS)
│   ├── serato_tracks.json / .csv        — 382 Serato tracks (UDMS)
│   ├── engine_dj_tracks.csv             — 112 Engine DJ tracks (UDMS)
│   ├── virtual_dj_tracks.csv             — 190 VirtualDJ tracks (UDMS)
│   ├── cross_platform_comparison.json    — 143 matched RB ↔ Serato
│   ├── virtual_dj_comparison.json / .csv — 24 matched RB ↔ VDJ
│   └── engine_dj_comparison.json / .csv  — Engine DJ cross-platform
├── schema/
│   └── udms_schema.json      — Standalone JSON schema definition
├── ARCHITECTURE.md
├── CONTRIBUTING.md
└── .gitignore
```

---

## Quick Start

**Compile the paper:**
```bash
cd paper
pdflatex main.tex && bibtex main.aux && pdflatex main.tex && pdflatex main.tex
```

**Run the analysis:**
```bash
python code/compare_platforms.py \
  --rekordbox path/to/library.xml \
  --serato data/serato_tracks.json \
  --output data/cross_platform_comparison.json
```

Requirements: Python 3.10+.

---

## Companion Tools

**[rekordbox-smart-mcp](https://github.com/interfluve-wav/rekordbox-smart-mcp)** — MCP server for Rekordbox library management. 33 tools covering library queries, smart playlists, BPM cache with multi-algorithm voting, Camelot key normalization, and safe mutations with full audit logging. 20/20 tests passing.

**[Bonk!](https://github.com/suhaas-lokey/bonk)** — Electron+React desktop DJ metadata editor. Reads Rekordbox XML and master.db directly, normalizes BPM/key via aubio and keyfinder-cli, writes back to Rekordbox.

---

## Citation

```bibtex
@article{chitturi2026djmetadata,
  author  = {Suhaas Chitturi},
  title   = {UDMS: A Canonical Schema and Assessment Framework for
             Measuring and Maintaining {DJ} Metadata Quality
             Across Ecosystems},
  year    = {2026},
  publisher = {Zenodo},
  doi     = {10.5281/zenodo.XXXXXXX}
}
```

*(Zenodo DOI to be filled in after upload)*

## License

MIT
