# UDMS: A canonical schema and assessment framework for DJ metadata quality

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19618271.svg)](https://doi.org/10.5281/zenodo.19618271)
[![Zenodo record](https://img.shields.io/badge/Zenodo-record-blue)](https://zenodo.org/records/19618271)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Python (schema + analysis)** · **LaTeX paper** · **Four DJ platforms (Rekordbox, Serato, Engine DJ, VirtualDJ)**

**Preprint (archived PDF):** [Zenodo record 19618271](https://zenodo.org/records/19618271) · [https://doi.org/10.5281/zenodo.19618271](https://doi.org/10.5281/zenodo.19618271)

*Replication bundle: UDMS (eleven canonical fields) plus adapters for Rekordbox, Serato, Engine DJ, and VirtualDJ, cross-platform comparison code, anonymized parsed exports, JSON Schema, and the LaTeX paper in `paper/`.*

We present the first cross-platform metadata quality analysis of real-world DJ libraries. Using UDMS (Unified DJ Metadata Schema), we analyze 636 Rekordbox tracks, 382 Serato tracks, 112 Engine DJ tracks, and 190 VirtualDJ tracks — matching 143 tracks across Rekordbox and Serato, and 22 tracks across Rekordbox and VirtualDJ — quantifying how reliably metadata is preserved across ecosystem boundaries.

## Key Findings

| Finding | Value |
|---------|-------|
| Genre annotation coverage | 31–69% (varies by platform) |
| Editorial metadata (ratings, labels) | 0–53% (sparse) |
| Musical key coverage | 93–98% (best across platforms) |
| BPM coverage | 100% (Rekordbox) |
| Cross-platform key agreement (exact / effective) | 71.3% / 100% |
| BPM disagreement | Explained by systematic 2× half-tempo interpretation difference in Rekordbox for half-tempo genres |
| Key finding | Title, artist, album are perfectly preserved across platforms (100%) |

Rekordbox applies a 95 BPM threshold heuristic when analyzing half-tempo genres (UK dubstep, drum-and-bass, footwork, Jersey Club), causing it to store BPM at exactly 2× the actual tempo. Engine DJ and Serato store the correct value. This is a systematic interpretation difference, not a cross-platform transfer issue.

## UDMS — Unified DJ Metadata Schema

UDMS normalizes 11 canonical fields across Rekordbox, Serato, Engine DJ, VirtualDJ, and Traktor. The Python implementation is in `code/schema/udms_schema.py`.

**UDMS fields:** title, artist, album, genre, BPM, key (Camelot), rating (0–5), label, duration_sec, bitrate, sample_rate

**Key normalization:** OpenKey and Traditional notations are normalized to Camelot (e.g., "Fm" → "4A"). Rating is normalized from platform-specific scales to 0–5 stars.

**BPM 2× detection:** UDMS flags potential 2× errors by checking if `1.95 < platform_bpm / reference_bpm < 2.05`.

## Repository Structure

```
dj-metadata-study/
├── paper/
│   ├── main.tex              — LaTeX paper (27 pages)
│   ├── preamble.tex          — LaTeX preamble (packages, macros)
│   ├── references.bib        — 35 citations (all cited)
│   ├── cite.sty
│   └── fig_*.pdf             — All figures
├── code/
│   ├── schema/
│   │   └── udms_schema.py    — UDMS schema + 5 platform adapters
│   ├── compare_platforms.py  — Cross-platform comparison engine
│   └── parse_serato.py        — Parse Serato database V2 binary
├── data/
│   ├── rekordbox_tracks_parsed.json    — 636 Rekordbox tracks (UDMS format)
│   ├── serato_tracks.json / .csv       — 382 Serato tracks (UDMS format)
│   ├── engine_dj_tracks.csv            — 112 Engine DJ tracks (UDMS format)
│   ├── virtual_dj_tracks.csv           — 190 VirtualDJ tracks (UDMS format)
│   ├── cross_platform_comparison.json  — 143 matched Rekordbox/Serato tracks
│   ├── engine_dj_comparison.json / .csv — Engine DJ cross-platform results
│   ├── virtual_dj_comparison.json / .csv — VirtualDJ cross-platform results
│   ├── bpm_validation_table.json       — Audio BPM validation subset
│   └── serato_database_v2             — Raw Serato binary DB (input)
├── schema/
│   └── udms_schema.json      — Standalone JSON schema definition
├── ARCHITECTURE.md
├── CONTRIBUTING.md
└── .gitignore
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

The paper compiles to 27 pages with no errors.

## Archiving on Zenodo (code + PDF)

Zenodo’s [GitHub integration](https://zenodo.org/) archives the **git tree at your release tag**. `paper/main.pdf` is gitignored, so a local build is **not** uploaded unless you add a tracked copy.

**One DOI (recommended if the paper is part of the replication bundle)**  
Keep the deposit type **Software** (as in `.zenodo.json`). Before tagging a release:

1. Produce `paper/main.pdf` with your usual LaTeX workflow.
2. Copy it to the tracked filename and commit:

   ```bash
   cp paper/main.pdf paper/Chitturi2026_UDMS_preprint.pdf
   git add paper/Chitturi2026_UDMS_preprint.pdf
   git commit -m "Add frozen PDF for Zenodo release"
   ```

3. Publish a **GitHub Release** on that commit. The Zenodo snapshot will include the PDF alongside code and data.

**Separate DOI for the PDF only**  
If you want a **publication-style** record (conference paper / preprint / article) with its own DOI:

1. On Zenodo choose **New upload** → **Resource type: Publication** → pick a subtype (e.g. **Conference paper** for ISMIR, or **Preprint**).
2. Upload **only** the PDF (and optional LaTeX source as a zip if you like).
3. Under **Related works**, link to the **software** DOI and the GitHub repository so both records stay connected.

Use one strategy or both; two DOIs are fine if you want citations to distinguish “paper” vs “full replication archive.”

## Running the Analysis

```bash
# Cross-platform comparison (requires rekordbox XML + serato JSON)
python code/compare_platforms.py \
  --rekordbox path/to/library.xml \
  --serato data/serato_tracks.json \
  --output data/cross_platform_comparison.json
```

Requirements: Python 3.10+.

## Companion Tools

**[rekordbox-smart-mcp](https://github.com/interfluve-wav/rekordbox-smart-mcp)** — MCP server for Rekordbox library management. 33 tools covering library queries, smart playlists, BPM cache with multi-algorithm voting, Camelot key normalization, and safe mutations with full audit logging. 20/20 tests passing.

**[Bonk!](https://github.com/interfluve-wav/bonk-app)** — Electron+React desktop DJ metadata editor. Reads Rekordbox XML and master.db directly, normalizes BPM/key via aubio and keyfinder-cli, writes back to Rekordbox.

## Citation

```bibtex
@misc{chitturi2026djmetadata,
  author  = {Suhaas Chitturi},
  title   = {UDMS: A canonical schema and assessment framework for {DJ}
             metadata quality},
  year    = {2026},
  publisher = {Zenodo},
  doi     = {10.5281/zenodo.19618271},
  url     = {https://doi.org/10.5281/zenodo.19618271},
}
```

## License

MIT
