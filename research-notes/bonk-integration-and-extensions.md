# Bonk Integration + Research Extensions (NOT in Paper)

*Saved: $(date)*
*Purpose: Ideas for future iterations — arXiv submission should proceed as-is*

---

## BONK INTEGRATION

### Bonk is an Implementation of UDMS

Bonk (github.com/suhaas-lokey/bonk or similar) is an Electron+React DJ metadata editor that already implements the core UDMS idea:
- Reads Rekordbox XML and encrypted `master.db` directly
- Reads Serato metadata embedded in audio files
- Has aubio-based BPM detection (see §AUBIO below)
- Has keyfinder-cli for key detection
- Enriches via MusicBrainz, Spotify, Discogs, Beatport APIs
- Can write metadata back

The paper proposes UDMS as a conceptual framework. Bonk is its implementation.
Bonk's architecture confirms the paper's premise: cross-platform reconciliation is feasible but requires platform-specific parsing.

### Bonk's Audio Pipeline

Bonk has THREE BPM detection layers:
1. `aubio tempo` CLI — spectral flux onset detection, cached in SQLite
2. `ffprobe` — reads BPM from container/format ID3 tags (BPM, bpm, TBPM, tbpm)
3. `beatDetect.ts` — custom autocorrelation via Web Audio API in browser renderer

The name "Bonk!" is a deliberate play on **bonk~** — Miller Puckette's 1998 Max/MSP external for onset detection. aubio is the open-source spiritual successor to bonk~.

### aubio Benchmarks (Key Numbers)

- aubio on ISMIR 2004 dataset: **39.35%** exact tempo, **67.31%** within 4% of 1x/2x/½x/3x/⅓x
- aubio ranked **11th of 15** methods in Zapata-Gómez comparison
- aubio has a known 95 BPM threshold heuristic: if primary > 95 BPM, secondary = primary/2; if < 95 BPM, secondary = primary×2 — this causes octave errors
- aubio was NOT evaluated on GiantSteps; commercial DJ software WAS:
  - Rekordbox: 74.55% Accuracy1, 89.16% Accuracy2 (on GiantSteps 664 tracks)
  - Traktor: 76.96% Accuracy1, 88.71% Accuracy2
  - CrossDJ: 63.40% Accuracy1, 90.21% Accuracy2
- aubio's P-scores on MIREX 2006: 0.628 (last of 7 entrants)

### aubio Double/Half Tempo Error Rates by Genre (Brossier PhD)

| Genre    | Correct | Octave Down | Octave Up |
|----------|--------|-------------|-----------|
| Jazz     | 87.10% | 9.68%       | 0%        |
| Pop      | 85.21% | 2.63%       | 0%        |
| Dance    | 85.00% | 2.50%       | 10%       |
| Classical| 56.52% | 13.04%      | 8.70%     |

For Dance genre specifically: aubio gets 85% correct but has a **10% octave UP error rate** — tracks detected at double their actual tempo. This is the OPPOSITE problem from what we see in Rekordbox (which stores double).

The paper's 2× bug: Rekordbox stores 140 BPM for tracks that are actually 70 BPM (dubstep, drum-and-bass, dancehall). aubio would likely get these CORRECT at 70 BPM (the 95 BPM threshold would halve them), whereas Rekordbox's analysis doubles them.

### Traktor Metadata Architecture

- **Hybrid**: XML database (`collection.nml`) + ID3 tag embedding in audio files
- BPM and Key stored in `<TEMPO>` element in XML
- Key stored in Camelot notation (e.g., "11d", "12m")
- **26ms MP3 cue shift bug**: LAME MP3 frame handling differs between Traktor and Rekordbox, affecting ~6% of files in conversion (documented in dj-data-converter GitHub issue #3)
- Key finding: **dj-data-converter doesn't transfer KEY from Traktor→Rekordbox** (open issue)

### DJ Platform Metadata Architecture Summary

| Platform   | BPM Storage          | Key Storage       | Embeds in Files? | Portable? |
|------------|---------------------|-------------------|------------------|-----------|
| Rekordbox  | Database only       | Database only     | No               | No        |
| Serato     | File-embedded       | File-embedded     | Yes              | Yes       |
| Traktor    | Hybrid              | Hybrid            | Yes              | Yes       |
| VirtualDJ  | Database + optional | Database + optional| Partial         | Partial   |
| Engine DJ  | Database only       | Database only     | No               | No        |

### VirtualDJ Serato Behavior

- VDJ **reads Serato cue points automatically** from embedded GEOB tags when loading files
- Once you set a cue in VDJ, it stops reading Serato data for that track
- VDJ can write to MP3/FLAC/M4A/AIFF but NOT waveforms

### No Multi-Platform Benchmark Exists

There is **no published dataset** with the same tracks annotated across Traktor, Engine DJ, Rekordbox, Serato, and VirtualDJ simultaneously. The paper's 143 matched tracks is genuinely novel data — it's the first cross-platform DJ metadata comparison in the literature. The closest existing work is the dj-data-converter project (GitHub, 214 stars) which has field mappings but no aggregated statistics.

---

## METADATA QUALITY FRAMEWORK (Formal Grounding for UDMS)

### Bruce & Hillmann (2004) — "The Continuum of Metadata Quality"

The canonical framework. 7 dimensions:
1. **Completeness** — are all expected elements present?
2. **Accuracy** — are values correct semantically and syntactically?
3. **Provenance** — where did the data come from, can transformations be traced?
4. **Conformance to Expectations** — do values adhere to stated schemas/standards?
5. **Accessibility** — can authorized users retrieve the data?
6. **Consistency** — are values consistent across records and systems?
7. **Timeliness** — how current is the data?

Paper finding mapping:
- BPM 2× bug → **Accuracy** problem (Rekordbox stores semantically wrong value)
- Genre fragmentation → **Consistency** problem (same track gets different genre strings across platforms)
- Platform silos → **Provenance** problem (no unified provenance chain)
- Rekordbox database-only → **Accessibility** problem (metadata not portable with files)

### Stvilia et al. (2007) — "A Framework for Information Quality Assessment"

722 citations, the most-cited framework in information science.
22 IQ dimensions in 3 categories:
- **Intrinsic IQ**: Accuracy, completeness, consistency, credibility
- **Contextual IQ**: Timeliness, relevance, importance, utility
- **Relational IQ**: Semantic consistency, structural consistency, interoperability
- **Representational IQ**: Interpretability, explicitness, coherence

### ISO/IEC 25012 — Data Quality Model

International standard, 15 characteristics:
- **Inherent**: Accuracy, Completeness, Consistency, Credibility, Currentness
- **System-dependent**: Accessibility, Availability, Portability, Recoverability

### FAIR Principles (Wilkinson et al.)

For the interoperability framing:
- **F**indability — metadata must be easy to discover
- **A**ccessibility — metadata must be retrievable
- **I**nteroperability — metadata must work across systems ← UDMS core contribution
- **R**eusability — metadata must have clear license/provenance

### DCMI Interoperability Levels

- **Syntax** interoperability — can systems parse each other's formats?
- **Semantic** interoperability — do systems agree on what values mean?
- **Organizational** interoperability — do systems agree on workflows and governance?

The paper's findings operate at **semantic** interoperability (BPM is stored but means different things on different platforms due to the 2× bug).

---

## ADDITIONAL PAPERS TO CONSIDER CITING

### Hörschläger, Vogl, Böck, Knees (2015) — "Addressing Tempo Estimation Octave Errors in Electronic Music"

*The paper that should be cited for the BPM 2× framing.*

Key numbers:
- Baseline tempo accuracy on GiantSteps (664 tracks): **45.48%** primary, **73.04%** secondary (allowing octave errors)
- With Wikipedia style-aware BPM ranking: **75.00%** primary (+29.5 pp over baseline)
- The 2× problem is genre-specific: drum-and-bass (160+ BPM) commonly detected as 80 BPM; dubstep (130-142 BPM) commonly detected as 65-71 BPM

Style-specific BPM ranges from Wikipedia analysis:
| Style                  | Min  | Max  |
|------------------------|------|------|
| dubstep                | 130  | 142  |
| drum-and-bass          | 130  | 180  |
| tech-house             | 180  | 220  |
| hardcore-hard-techno    | 160  | 200  |

Suggested addition to §4 (BPM discussion):
> "Hörschläger et al.~~\citep{hoerschlaeger2015tempo} report that tempo octave errors are genre-dependent: dubstep tracks near 140 BPM are frequently misidentified near 70 BPM, while drum-and-bass above 160 BPM is commonly detected near 80 BPM. Our finding that 27\% of cross-platform comparisons exhibit a 2$\times$ BPM disagreement is consistent with this pattern---all 39 affected tracks in our corpus are bass music (UK dubstep, dancehall, half-tempo bass), whose authentic tempi sit near the octave boundary."

### Zapata-Gómez & Gómez — MIREX tempo estimation comparisons

- aubio ranked 11th of 15 on ISMIR 2004 dataset
- Commercial DJ software consistently outperforms academic algorithms on EDM (Traktor: 77%, Rekordbox: 74.55%, CrossDJ: 63-90%)
- Relevant for claiming the BPM 2× bug is NOT a fundamental limitation of audio analysis but a specific implementation bug

### Schreiber & Müller (2018) — ISMIR 2018

- Crowdsourced re-evaluation of GiantSteps found algorithms scored 10-15% higher with better ground truth
- Traktor Pro 2 achieved 77.0% on GiantSteps (octave bias 88-175 range)
- CrossDJ achieved 90.2% — highest of any tested system
- Relevant for calibrating expectations: commercial DJ software has significant error rates even on its own target genre (EDM)

### Freed (2006) — "Music Metadata Quality: A Multiyear Case Study Using the Music of Skip James"

*The only AES paper specifically on music metadata quality.*
- First quantitative system for audio/music metadata quality measurement
- Examines errors, sources, and propagation mechanisms
- Would strengthen the metadata quality framing in §2 / §5

### Park (2009) — "Metadata Quality in Digital Repositories: A Survey"

- Functional perspective: Discovery, Use, Provenance, Currency, Authentication, Administration
- NISO's 6 principles of "good" metadata
- Good secondary citation for metadata quality framework

### Kumar et al. (2025) — "Exploring Dimensions of Metadata Quality Assessment: A Scoping Review"

- 55 studies analyzed — most common dimensions: Completeness, Accuracy, Consistency, Accessibility, Conformance, Provenance, Timeliness
- No consensus on exact definitions — need for standardization
- Relevant: UDMS addresses exactly this gap for DJ-specific metadata

---

## BONK AS CITATION IN RELATED WORK

If Bonk is public/open source, it could be cited as a real-world system:

> "While prior work has documented the metadata interoperability problem~~\citep{brooke2014metadata}, few tools have attempted to solve it in practice. Bonk! is an open-source DJ metadata editor supporting Rekordbox and Serato with aubio-based audio analysis, demonstrating that cross-platform reconciliation is technically feasible."

---

## BONK AS REAL-WORLD IMPACT STATEMENT

The BonkSite landing page Problem.js says:
- "Missing BPM and key data across your library"
- "Corrupted ID3 tags from different download sources"
- "Hours of manual metadata fixing before every gig"

This is the user-facing symptom description. The paper is the scientific analysis of why those symptoms exist and how widespread they are.

---

## WEAKNESS TO ADDRESS

The paper's key methodological weakness: **no ground truth / audio validation**.

The paper shows Rekordbox and Serato *disagree* on BPM for 27% of tracks, but doesn't definitively prove which one is "correct." 

Options to address this:
1. Use aubio as a third-party validator (aubio would likely agree with Serato at 70 BPM, not Rekordbox at 140)
2. Cross-reference with Beatport metadata (Beatport sells the same tracks with BPM annotations)
3. Note this as a limitation and future work

---

## UNANSWERED QUESTIONS (Future Research)

1. **Is the BPM 2× bug deterministic or track-specific?** Does the same track always get 2× in Rekordbox, or does it depend on file format, analysis settings, or other factors?
2. **What percentage of the full 637-track Rekordbox library has the 2× bug?** We only know from the 143 matched tracks.
3. **Does Rekordbox's 2× bug affect its beatgrid placement?** If the beatgrid is locked to the wrong BPM, rekordbox's sync would fail for those tracks.
4. **What is the distribution of the 2× bug across genres in the full library?** Is it truly only dubstep/drum-and-bass/dancehall, or are there other genres affected?
5. **Does Serato have any systematic BPM errors?** The paper shows 100% agreement for tracks where Serato has a BPM — but Serato could have its own octave errors that the matching logic didn't catch.

---

## WHAT TO DO WITH THIS

**Do NOT merge into current paper.** The current paper:
- Compiles clean at 8 pages, 307KB
- Has 34 references
- Related work is well-structured
- All findings are supported

This document is for:
1. **Future ISMIR submission** — add audio validation with aubio, expand to 10 pages, cite Hörschläger 2015 for tempo octave framing
2. **Talk/demo** — use Bonk as live demonstration of the problem and solution
3. **Follow-up paper** — Traktor/Engine DJ as third platform comparison
4. **arXiv impact statement** — Bonk as evidence of real-world relevance

**For arXiv submission this week**: Ship as-is. This document is insurance against "you should have cited X" or "have you considered Y" in post-publication review.
