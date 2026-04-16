# Architecture

## Overview

The repository contains three layers: a LaTeX paper, a Python analysis pipeline, and a DJ library dataset.

## Paper (`paper/`)

`main.tex` is the arXiv submission. `preamble.tex` holds packages and macros. All figures are pre-generated PDFs committed to the repo (no runtime generation required to compile).

```
paper/
├── main.tex          — arXiv submission (22 pages)
├── preamble.tex      — packages, macros, color definitions
├── references.bib    — BibTeX entries (34 references)
└── fig_*.pdf        — 9 pre-generated figures
```

## Analysis Pipeline (`code/`)

```
code/
├── schema/
│   └── udms_schema.py     — UDMS definition + Platform enum + adapters
├── compare_platforms.py  — Rekordbox XML ↔ Serato JSON comparison
├── parse_serato.py        — Serato DB V2 binary parser
├── bpm_validation.py      — Full-library BPM sanity check
└── bpm_validation_20.py   — 20-track audio BPM validation (aubio + scipy)
```

**UDMS** (Unified DJ Metadata Schema) is the shared data model. It defines 11 canonical fields with normalized types:

| Field | Type | Notes |
|-------|------|-------|
| title | string | |
| artist | string | |
| album | string | |
| genre | string | Free-text; no enum |
| BPM | float | Always stored as half-tempo (87 BPM, not 174) |
| key | string | Camelot notation (e.g., "4A", "11B") |
| rating | int | 0–5 stars |
| label | string | Record label |
| duration_sec | int | Seconds |
| bitrate | int | kbps |
| sample_rate | int | Hz (44100, 48000) |

Platform adapters handle the translation:
- **RekordboxAdapter** — parses XML export, maps fields to UDMS
- **SeratoAdapter** — parses JSON (or binary DB), maps fields to UDMS

The 2× BPM bug: Rekordbox stores ~27% of tracks at double their actual tempo (140 instead of 70 BPM). UDMS detects this by checking if `1.95 < serato_bpm / rekordbox_bpm < 2.05` and flags it, but does not auto-correct Rekordbox values.

## Data (`data/`)

| File | Size | Description |
|------|------|-------------|
| `cross_platform_comparison.json` | ~50KB | 143 matched tracks, UDMS format, paths anonymized |
| `bpm_validation_table.json` | ~5KB | 20-track audio validation results |
| `serato_tracks.json` | ~100KB | All 382 Serato tracks in UDMS format |
| `serato_tracks.csv` | ~80KB | CSV version of above |
| `serato_database_v2` | 278KB | Raw Serato DB V2 binary (input, for reproducibility) |

The Rekordbox XML is **not** committed (contains absolute file paths). The Serato binary is committed for reproducibility.

## Experiments (`experiments/`)

`run_experiment.py` — framework for running cross-platform transfer experiments. Not used in the current paper (planned for future work).

## Companion Systems

```
┌─────────────────────────────────────────────────────────┐
│  Bonk! (Electron desktop app)                          │
│  github.com/suhaas-lokey/bonk                         │
│  aubio BPM + keyfinder-cli key detection               │
│  Direct Rekordbox master.db parsing                    │
└───────────────┬─────────────────────────────────────────┘
                │ UDMS schema alignment
                ▼
┌─────────────────────────────────────────────────────────┐
│  rekordbox-smart-mcp (MCP server)                      │
│  github.com/interfluve-wav/rekordbox-smart-mcp         │
│  33 tools: library queries, BPM cache, smart playlists │
└───────────────┬─────────────────────────────────────────┘
                │ UDMS schema alignment
                ▼
┌─────────────────────────────────────────────────────────┐
│  DJ Metadata Paper (this repo)                         │
│  github.com/interfluve-wav/dj-metadata-paper            │
│  arXiv submission — 22 pages                          │
└─────────────────────────────────────────────────────────┘
```

All three systems use the same 11-field UDMS schema. Bonk! and rekordbox-smart-mcp validate the paper's findings by showing the schema is implementable and the fields are recoverable in practice.
