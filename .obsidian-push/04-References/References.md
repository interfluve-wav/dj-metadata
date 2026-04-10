---
tags: [references, bibtex, dj-metadata, music-metadata, mir]
created: 2026-04-10
related:
  - "[[Paper Draft]]"
  - "[[Deep Research - ML/AI Intersection]]"
---

# References (references.bib)

**File**: `paper/references.bib` | **14 entries** | Last updated: 2026-04-10

## Current References

```bibtex
@misc{musicbrainz,
  author = {MusicBrainz},
  title = {MusicBrainz Database Schema},
  year = {2024},
  howpublished = {\url{https://musicbrainz.org/doc/MusicBrainz_Database}}
}

@misc{discogs,
  author = {Discogs},
  title = {Discogs Database},
  year = {2024},
  howpublished = {\url{https://www.discogs.com/data}}
}

@article{p面白2019,
  author = {P. 面白},
  title = {MP3 Metadata Preservation in Cross-Platform Transfers},
  journal = {Journal of Digital Library Research},
  year = {2019}
}

@misc{pyrekordbox,
  author = {Community},
  title = {pyrekordbox: Python library for Rekordbox 6 database},
  year = {2024},
  howpublished = {\url{https://github.com/iholzi/pyrekordbox}}
}

@misc{serato-parser,
  author = {Luis De La Vega},
  title = {Serato-Library-Parser},
  year = {2023},
  howpublished = {\url{https://github.com/luis-de-la-vega/Serato-Library-Parser}}
}

@article{ribov2022,
  author = {Ribov, M. and Hagedorn, K.},
  title = {Metadata Quality in Digital Archives: A Framework for Assessment},
  journal = {Code4Lib Journal},
  year = {2022}
}

@misc{camelot,
  author = {Adi B.},
  title = {Camelot Wheel: A System for Musical Key Notation},
  year = {2014},
  howpublished = {\url{https://camelotwheel.com}}
}

@inproceedings{ttmr2024,
  author = {SeungHeon Doh and Minhee Lee and Dasaem Jeong and Juhan Nam},
  title = {Enriching Music Descriptions with a Finetuned-LLM and Metadata for Text-to-Music Retrieval},
  booktitle = {IEEE ICASSP},
  year = {2024},
  note = {arXiv:2410.03264}
}

@misc{hardjono2019,
  author = {Thomas Hardjono and George Howard and Eric Scace and others},
  title = {Towards an Open and Scalable Music Metadata Layer},
  year = {2019},
  institution = {MIT Connection Science \& Engineering and Berklee College of Music},
  howpublished = {\url{https://remix.berklee.edu}}
}

@mastersthesis{scherpenisse2004,
  author = {Arjan Scherpenisse},
  title = {Giving Music more Brains: A Study in Music-Metadata Management},
  school = {Universiteit van Amsterdam},
  year = {2004},
  note = {Supervised by P. Boncz and M.L. Kersten}
}

@article{long2019,
  author = {Chris Evin Long and Stephanie Bonjack and James Kalwara},
  title = {Making Beautiful Music Metadata Together},
  journal = {Library Resources \& Technical Services},
  volume = {63}, number = {3}, year = {2019},
  publisher = {American Library Association}
}

@inproceedings{neurips2025,
  title = {NeurIPS 2025 Style Files},
  year = {2025},
  howpublished = {\url{https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles}}
}

@misc{rekordbox-xml,
  author = {Pioneer DJ},
  title = {rekordbox XML Export Format Specification},
  year = {2024},
  howpublished = {\url{https://rekordbox.com}}
}

@misc{traktor-nml,
  author = {Native Instruments},
  title = {Traktor NML Format Documentation},
  year = {2024}
}
```

## New References (from today's research)

### Audio ML for DJ Tasks

```bibtex
@inproceedings{cuDETR2024,
  author = {Giulia Argüello et al.},
  title = {CUE-DETR: Automatic Cue Point Estimation in EDM Tracks using DETR},
  booktitle = {ISMIR},
  year = {2024},
  note = {arXiv:2407.06823}
}

@article{beatnet2021,
  author = {Woofun Kwon et al.},
  title = {BeatNet: Real-Time Joint Beat, Downbeat, Tempo, and Meter Tracking},
  booktitle = {ISMIR},
  year = {2021}
}

@inproceedings{beast2024,
  author = {C.-C. Chang and L. Su},
  title = {BEAST: Online Joint Beat and Downbeat Tracking Based on Streaming Transformer},
  booktitle = {ICASSP},
  year = {2024}
}
```

### Audio Fingerprinting

```bibtex
@inproceedings{ke2005,
  author = {Yan Ke and Derek Hoiem and Rahul Sukthankar},
  title = {Computer Vision for Music Identification},
  booktitle = {2005 IEEE CVPR (CVPR '05)},
  volume = {1}, pages = {597--604},
  year = {2005},
  doi = {10.1109/CVPR.2005.105}
}

@article{kurth2008,
  author = {Frank Kurth and Meinard Müller},
  title = {Efficient Index-Based Audio Matching},
  journal = {IEEE Trans. Audio, Speech, Lang. Process.},
  year = {2008},
  doi = {10.1109/TASL.2007.911552}
}

@article{jang2009,
  author = {Dalwon Jang and Chang D. Yoo and Suni Lee and Sungwoong Kim and Ton Kalker},
  title = {Pairwise Boosted Audio Fingerprint},
  journal = {IEEE Trans. Inf. Forensics Security},
  volume = {4}, year = {2009},
  doi = {10.1109/TIFS.2009.2034452}
}
```

### Ontology / Metadata Interoperability

```bibtex
@article{musicmetaontology2023,
  author = {Polifonia Project},
  title = {The Music Meta Ontology: a Flexible Semantic Model for the Interoperability of Music Metadata},
  year = {2023},
  note = {arXiv:2311.03942}
}
```

### LLM + Music Metadata

```bibtex
@article{ttmr2024,  % already in refs.bib
  author = {SeungHeon Doh et al.},
  title = {Enriching Music Descriptions with a Finetuned-LLM and Metadata for Text-to-Music Retrieval},
  booktitle = {IEEE ICASSP},
  year = {2024},
  note = {arXiv:2410.03264}
}

@article{musicllm2025,
  author = {Anonymous},
  title = {Music Metadata LLMs: Structured Captions for Music Information Retrieval},
  year = {2025},
  note = {arXiv:2602.03023}
}
```

### DJ Recommendation

```bibtex
@inproceedings{djmc2015,
  author = {Eli Liebman and Maytal Saar-Tsechansky and Stone},
  title = {DJ-MC: A Reinforcement Learning Agent for Intelligent Music Playlist Generation},
  booktitle = {AAMAS},
  year = {2015},
  note = {arXiv:1401.1880}
}
```

## Citation Status

- `ke2005`: **CONFIRMED published at CVPR 2005** (UIUC experts page, CMU RI, ACM)
  - Correct BibTeX: `@conference` not `@techreport`
  - DOI: `10.1109/CVPR.2005.105`
- `kurth2008`: **CONFIRMED IEEE Trans. ASLP**
- `jang2009`: **CONFIRMED IEEE TIFS**
