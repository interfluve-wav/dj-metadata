#!/usr/bin/env python3
"""Prepare arXiv submission from anonymized ISMIR draft."""

BASE = "/Users/suhaas/Documents/GitHub/dj-metadata-paper"

with open(f"{BASE}/paper/main.tex", "r") as f:
    tex = f.read()

# 1. Remove [submission] flag from ismir package
tex = tex.replace(r"\usepackage[submission]{ismir}", r"\usepackage{ismir}")

# 2. Replace anonymized author block with real author
OLD_AUTHOR = r"""\oneauthor
  {Anonymous Authors}
  {Anonymous Affiliations\\\texttt{anonymous@ismir.net}}"""
NEW_AUTHOR = r"""\oneauthor
  {Suhaas Chitturi}
  {University of Massachusetts Dartmouth\\\texttt{schitturi@umb.edu}}"""
tex = tex.replace(OLD_AUTHOR, NEW_AUTHOR)

# 3. Replace author name for CC-BY notice
tex = tex.replace(r"\def\authorname{F. Author, S. Author, and T. Author}",
                  r"\def\authorname{Suhaas Chitturi}")

# 4. Remove double-blind note
tex = tex.replace(
    "% Note: double-blind submission — author names anonymized automatically\n"
    "% For camera-ready: remove [submission] option from ismir package\n",
    "% Author: Suhaas Chitturi, University of Massachusetts Dartmouth\n"
    "% Submitted to arXiv — remove ISMIR conference references for general distribution\n"
)

# 5. Update reproducibility line — was ISMIR-specific
tex = tex.replace(
    "ISMIR 2026 requires code availability for reproducibility. "
    "The repository is public and will be archived with a Zenodo DOI prior to submission.",
    "This work was submitted to arXiv for open dissemination. "
    "The repository is public and will be archived with a Zenodo DOI upon acceptance."
)

with open(f"{BASE}/paper/main.tex", "w") as f:
    f.write(tex)

print("main.tex updated for arXiv")
