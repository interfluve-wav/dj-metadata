# Project Tasks

## Done ✓
- [x] Parse Rekordbox XML (636 tracks) → UDMS
- [x] Parse Serato DB V2 binary (382 tracks) → UDMS
- [x] Cross-platform match (143 overlapping tracks)
- [x] Discover Rekordbox BPM 2x bug (27% of tracks)
- [x] Compute cross-platform preservation rates (BPM 89.5%, key 71.3%/100%, genre 54.8%)
- [x] Per-source metadata quality breakdown
- [x] MusicBrainz genre recovery (6% rate)
- [x] Add Knees 2015 + Bogdanov 2011 as comparable prior work
- [x] Restore author name for arXiv submission
- [x] Push arXiv-ready PDF to paper/main.pdf

## Remaining Work

### Paper Improvements ( ranked by impact)

**1. Audio ground-truth validation** ⭐ HIGHEST PRIORITY
- [ ] Run librosa BPM + key detection on 20-30 tracks (stratified sample: electronic, hip-hop, mixed)
- [ ] Compare librosa output against Rekordbox/Serato metadata
- [ ] This answers the reviewer question: "how do you know the data is accurate?"
- [ ] Bezidir et al. (ISMIR 2023) or Knees et al. (2015) as methodological reference
- [ ] Scripts: code/audio_validation.py (new file)

**2. Genre taxonomy fragmentation quantified**
- [ ] Compute Shannon entropy of the 70-genre distribution
- [ ] Levenshtein distance clustering of genre strings → how many effective clusters?
- [ ] Compare against Xu et al. (arXiv 2025): Beatport 35 → 17-20 acoustic clusters
- [ ] Script: code/genre_entropy.py (new file)
- [ ] Update paper Results §Genre section with entropy + cluster numbers

**3. Sharpen 39.8% headline finding**
- [ ] Break down what's driving "missing minimum harmonic mixing metadata"
- [ ] Is it genre-missing? key-missing? BPM-missing?
- [ ] Per-tier source distribution (Standard tier vs Full tier sources)
- [ ] Add to Results §Completeness Tiers

**4. Single-library limitation acknowledged**
- [ ] Add sentence in Limitations: n=1 DJ library, results may not generalize
- [ ] Frame as "pilot study" / "proof of concept" in Conclusion
- [ ] Note: Knees et al. (2015) and Bogdanov (2011) also used single-library studies

**5. Narrative polish**
- [ ] Sharpen intro "so what" — connect to MIR training data reliability
- [ ] Add concrete example in intro: "a DJ library used to train beat-matching models may have systematic BPM errors"
- [ ] Check: does abstract clearly state the 3 contributions upfront?

### arXiv Submission
- [ ] Go to https://arxiv.org/submit
- [ ] Upload files from /tmp/arxiv_submission/ (or repackage from paper/)
- [ ] Set primary category: cs.SD (Sound)
- [ ] Set secondary: cs.ML (Machine Learning)
- [ ] Submit and monitor compile status
- [ ] If compile fails: check arXiv email for specific error, fix, resubmit

### ISMIR 2026 (optional)
- [ ] Deadline: ~May 2026
- [ ] If targeting ISMIR: re-add anonymization (swap back to anonymous author block)
- [ ] ISMIR uses double-blind — arXiv is NOT double-blind so these are incompatible
- [ ] Decision: submit to arXiv first, then ISMIR with revisions

## Key Numbers to Remember

| Finding | Value |
|---------|-------|
| Rekordbox tracks | 636 |
| Serato tracks | 382 |
| Overlapping | 143 |
| BPM preservation (after 2x fix) | 89.5% |
| Key exact match | 71.3% |
| Key harmonically adjacent | 100% |
| Genre exact match (both tagged) | 54.8% |
| Genre both-missing | 28 tracks |
| Genre coverage (Rekordbox) | 63.1% |
| Tracks missing minimum mixing metadata | 39.8% |
| MusicBrainz recovery rate | 6% |
| Rekordbox 2x BPM bug | 39/143 = 27% |

## Comparable Prior Work
- Knees et al. ISMIR 2015: Rekordbox tempo accuracy 74.55%, key 71.85% (664-track ground-truth)
- Bogdanov & Herrera ISMIR 2011: genre filtering → +11% recommendation hit rate (68K tracks)
- Cunningham & Jones ISMIR 2004: personal music collection behavior
- Xu et al. arXiv 2025: Beatport 35 genres → 17-20 acoustic clusters (genre fragmentation)

## Compile Chain (after any .bib or .tex edit)
```bash
cd paper
rm -f main.aux main.bbl main.blg
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```
