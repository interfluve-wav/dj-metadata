# Contributing

Contributions are welcome. Please read this guide before submitting PRs.

## What to contribute

- **Bug fixes** — broken links, compilation errors, incorrect statistics
- **Paper improvements** — clearer writing, stronger claims, missing related work
- **Analysis extensions** — new validation scripts, additional tracks, cross-platform coverage
- **UDMS schema** — field additions, platform adapters for Traktor or other DJ software

## Paper vs. Code

The paper is in `paper/main.tex`. It uses a standard `article` LaTeX class (arXiv compatible). All packages are loaded directly — no conference style files.

To recompile after edits:
```bash
cd paper
rm -f aux bbl blg log
pdflatex main.tex
bibtex main.aux
pdflatex main.tex
pdflatex main.tex
```

## Code conventions

- `code/schema/udms_schema.py` — UDMS schema definition and platform adapters
- `code/compare_platforms.py` — cross-platform comparison runner
- All scripts read from `data/` (JSON/CSV) and write to `data/` (JSON/CSV)
- No external API calls in core scripts (MusicBrainz lookup is optional, rate-limited)

## Data conventions

- `data/cross_platform_comparison.json` — 143 matched tracks, paths anonymized
- `data/bpm_validation_table.json` — 20-track audio validation results
- All file paths in JSON are anonymized (original paths replaced with `ANON_TRACK_001` etc.)

## Adding a new platform adapter

1. Add to `code/schema/udms_schema.py` — new `Platform` enum entry and `PlatformAdapter` subclass
2. Add parser in `code/` (e.g., `parse_traktor.py`)
3. Add comparison in `code/compare_platforms.py`
4. Update `paper/main.tex` §UDMS if schema fields change
5. Update this CONTRIBUTING.md

## Reporting issues

- **Paper claims feel wrong** — open an issue with the specific claim and your evidence
- **Script fails** — include Python version, error trace, and sample data (anonymized)
- **Missing methodology detail** — open a discussion, not an issue

## Before submitting

- [ ] Paper compiles with `pdflatex` + `bibtex` (no errors, one caption warning is OK)
- [ ] `code/compare_platforms.py` runs on the JSON in `data/`
- [ ] No new `\input{}` or `\include{}` without updating `paper/main.tex`
- [ ] No hardcoded personal paths (e.g., `/Users/suhaas/...`)
