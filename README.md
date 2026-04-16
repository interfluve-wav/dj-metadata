# DJ Metadata Quality: A Rekordbox XML Study Using UDMS

**Published on arXiv** | Python (schema + analysis) | LaTeX paper

We present the first systematic metadata quality analysis of a real-world DJ library, and the first cross-platform DJ metadata interoperability study. Using UDMS (Unified DJ Metadata Schema), we analyze 636 Rekordbox tracks and 382 Serato tracks from the same DJ — matching 143 tracks across both platforms — and quantify how reliably metadata is preserved across ecosystem boundaries.

## Key Findings

| Finding | Value |
|---------|-------|
| Tracks ready for automated harmonic mixing | 60.2% (386/636) |
| Genre coverage | 63.1% |
| BPM coverage | 92.3% |
| Musical key coverage | 93.2% |
| Cross-platform BPM agreement (after 2× correction) | **89.5%** |
| Cross-platform key agreement (exact / effective) | **71.3% / 100%** |
| Rekordbox 2× BPM bug | Affects **27% of tracks** (39/143) |
| MusicBrainz genre recovery rate | **6%** (34% track match, 6% genre tag) |

The 2× BPM bug stores 140–174 BPM in Rekordbox for tracks whose actual tempo is 70–87 BPM (UK dubstep, drum-and-bass, footwork, Jersey Club). This is a Rekordbox-specific tempo detection or storage bug, not a cross-platform transfer issue.

## UDMS — Unified DJ Metadata Schema

UDMS normalizes 11 canonical fields across Rekordbox, Serato, and Traktor. The Python implementation is in `code/schema/udms_schema.py`.

**UDMS fields:** title, artist, album, genre, BPM, key (Camelot), rating (0–5), label, duration_sec, bitrate, sample_rate

**Key normalization:** OpenKey and Traditional notations are normalized to Camelot (e.g., "Fm" → "4A"). Rating is normalized from platform-specific scales to 0–5 stars.

**BPM 2× detection:** UDMS flags potential 2× errors by checking if `1.95 < serato_bpm / rekordbox_bpm < 2.05`.

## Repository Structure

```
dj-metadata-paper/
├── paper/
│   ├── main.tex              — arXiv submission (22 pages)
│   ├── preamble.tex          — LaTeX preamble (packages, macros)
│   ├── references.bib        — 34 citations
│   └── fig_*.pdf             — All figures (pre-generated)
├── code/
│   ├── schema/
│   │   └── udms_schema.py    — UDMS schema + Rekordbox/Serato adapters
│   ├── compare_platforms.py  — Cross-platform comparison (143 matched tracks)
│   ├── bpm_validation_20.py  — Audio BPM validation (aubio + scipy, 20 tracks)
│   ├── bpm_validation.py     — BPM validation on full library
│   └── parse_serato.py       — Parse Serato database V2 binary
├── data/
│   ├── cross_platform_comparison.json  — 143 matched tracks (anonymized)
│   ├── bpm_validation_table.json       — 20-track audio validation results
│   ├── serato_tracks.json / .csv      — Serato database export
│   └── serato_database_v2             — Raw Serato binary DB (input)
├── experiments/
│   ├── run_experiment.py      — Cross-platform transfer experiment runner
│   ├── annotation_template.csv
│   └── experiment_log.md
├── research-notes/
│   └── bonk-integration-and-extensions.md  — Bonk! app + UDMS implementation
└── tasks/
    └── TODO.md                — Paper improvement roadmap
```

## Compiling the Paper

```bash
cd paper
rm -f aux bbl blg
pdflatex main.tex
bibtex main.aux
pdflatex main.tex
pdflatex main.tex
```

The paper compiles to 22 pages with no errors.

## Running the Analysis

```bash
# Cross-platform comparison
python code/compare_platforms.py \
  --rekordbox path/to/library.xml \
  --serato data/serato_tracks.json \
  --output data/cross_platform_comparison.json

# BPM audio validation (requires aubio and scipy)
python code/bpm_validation_20.py \
  --tracks data/bpm_validation_table.json \
  --audio-dir /path/to/audio/files
```

Requirements: Python 3.10+, `aubio`, `scipy`, `numpy`, `matplotlib` (for validation scripts).

## Companion Tools

**[rekordbox-smart-mcp](https://github.com/interfluve-wav/rekordbox-smart-mcp)** — MCP server for Rekordbox library management. 33 tools covering library queries, smart playlists, BPM cache with multi-algorithm voting (aubio + Rekordbox DB), Camelot key normalization, and safe mutations with full audit logging. 20/20 tests passing.

**[Bonk!](https://github.com/suhaas-lokey/bonk)** — Electron+React desktop DJ metadata editor. Reads Rekordbox XML and master.db directly, normalizes BPM/key via aubio and keyfinder-cli, writes back to Rekordbox. Validates UDMS field coverage on real libraries.

## Citation

```bibtex
@article{chitturi2026djmetadata,
  author  = {Suhaas Chitturi},
  title   = {Metadata Quality Analysis of {DJ} Software Libraries:
             A {Rekordbox} {XML} Study Using the Unified {DJ} Metadata Schema},
  year    = {2026},
  eprint  = {XXXXX.XXXXX},
  archiveprefix = {arXiv},
  primaryclass  = {cs.SD}
}
```

*(arXiv ID to be filled in after submission)*

## License

MIT
