"""
Cross-platform metadata comparison: Rekordbox vs Serato

Finds tracks present in both libraries (matched by normalized file path),
then compares UDMS field values to measure preservation quality.
"""

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).parent / "schema"))
from udms_schema import Platform, RekordboxAdapter, normalize_bpm, normalize_key


# ── Rekordbox XML parser ──────────────────────────────────────────────────────

def parse_rekordbox(xml_path: str):
    """Parse Rekordbox XML, return dict of {normalized_path -> track_dict}."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {"rb": ""}

    tracks = {}
    for track in root.findall(".//TRACK"):
        loc = track.get("Location", "")
        # Normalize: file://localhost/Users/... -> /Users/suhaas/Music/...
        if loc.startswith("file://localhost"):
            path = loc.replace("file://localhost", "")
        else:
            path = loc
        path = unquote(path)
        # Normalize to remove volume name if present (e.g. /Volumes/Macintosh HD/...)
        # Keep /Users/suhaas/... style paths
        path = path.strip("/")

        adapter = RekordboxAdapter()
        raw = {attr: track.get(attr, "") for attr in [
            "Name", "Artist", "Album", "Genre", "AverageBpm", "Tonality",
            "Rating", "Label", "TotalTime", "BitRate", "SampleRate", "Location"
        ]}
        udms = adapter.to_udms(raw)
        tracks[path] = udms.to_dict()
    return tracks


# ── Normalize Serato paths ────────────────────────────────────────────────────

def normalize_serato_path(path: str) -> str:
    """'Users/suhaas/Music/...' -> /Users/suhaas/Music/..."""
    path = path.strip("/")
    return path


# ── Load Serato tracks ────────────────────────────────────────────────────────

def load_serato(json_path: str):
    with open(json_path) as f:
        data = json.load(f)
    tracks = {}
    for t in data["tracks"]:
        fp = t.get("file_path", "")
        if fp:
            norm = normalize_serato_path(fp)
            tracks[norm] = t
    return tracks


# ── Matching + comparison ─────────────────────────────────────────────────────

def camelot_adjacent(k1: str, k2: str) -> bool:
    """Return True if two Camelot keys are harmonically adjacent (same bucket or +1/-1)."""
    if not k1 or not k2 or k1 == "Unknown" or k2 == "Unknown":
        return False
    try:
        n1, m1 = int(k1[:-1]), k1[-1]
        n2, m2 = int(k2[:-1]), k2[-1]
        if m1 == m2:  # Same mode: adjacent numbers
            return abs(n1 - n2) <= 1 or abs(n1 - n2) >= 11  # wraps around
        else:  # Different mode: only adjacent if same number
            return n1 == n2
    except (ValueError, IndexError):
        return False


def compare_fields(r_val, s_val, field: str) -> dict:
    """Compare two field values, return dict with match info."""
    if field == "bpm":
        r_val = float(r_val) if r_val else 0.0
        s_val = float(s_val) if s_val else 0.0
        if r_val == 0 and s_val == 0:
            return {"match": True, "both_missing": True, "diff": 0.0}
        if r_val == 0 or s_val == 0:
            return {"match": False, "both_missing": False, "diff": abs(r_val - s_val)}
        diff = abs(r_val - s_val)
        # Handle 2x ratio: Rekordbox sometimes stores BPM at double actual tempo
        # e.g., RB=174, Serato=87 for the same track
        ratio = r_val / s_val if s_val else 0
        if 1.95 < ratio < 2.05:
            match = True  # Same track, just 2x in Rekordbox
        elif 0.48 < ratio < 0.52:
            match = True  # Same track, 0.5x (half time)
        else:
            match = diff < 0.5
        return {"match": match, "both_missing": False, "diff": diff, "is_2x": 1.95 < ratio < 2.05}
    elif field == "key":
        r_val = str(r_val).strip() if r_val else ""
        s_val = str(s_val).strip() if s_val else ""
        if not r_val and not s_val:
            return {"match": True, "both_missing": True}
        if not r_val or not s_val:
            return {"match": False, "both_missing": False}
        exact = r_val == s_val
        # Adjacent keys are harmonically compatible (Camelot wheel)
        adjacent = camelot_adjacent(r_val, s_val)
        return {"match": exact, "both_missing": False, "adjacent": adjacent}
    else:
        r_val = str(r_val).strip() if r_val else ""
        s_val = str(s_val).strip() if s_val else ""
        both_empty = not r_val and not s_val
        return {"match": r_val == s_val, "both_missing": both_empty}


def main():
    repo = Path(__file__).parent.parent

    print("Loading Rekordbox XML...")
    rekordbox_tracks = parse_rekordbox(repo / "TestPaper.xml")
    print(f"  Rekordbox: {len(rekordbox_tracks)} tracks")

    print("Loading Serato JSON...")
    serato_tracks = load_serato(repo / "data" / "serato_tracks.json")
    print(f"  Serato: {len(serato_tracks)} tracks")

    # Try multiple path matching strategies
    # Strategy 1: exact match on normalized path
    # Strategy 2: match on filename only (Artist - Title)

    # Build filename-based index for Serato
    def track_fingerprint(t):
        artist = (t.get("artist") or "").strip().lower()
        title = (t.get("title") or "").strip().lower()
        return f"{artist}|||{title}"

    serato_by_fingerprint = {}
    for path, t in serato_tracks.items():
        fp = track_fingerprint(t)
        if fp not in serato_by_fingerprint:
            serato_by_fingerprint[fp] = []
        serato_by_fingerprint[fp].append((path, t))

    rekordbox_by_fingerprint = {}
    for path, t in rekordbox_tracks.items():
        fp = track_fingerprint(t)
        if fp not in rekordbox_by_fingerprint:
            rekordbox_by_fingerprint[fp] = []
        rekordbox_by_fingerprint[fp].append((path, t))

    # Find overlapping fingerprints
    overlap_fps = set(rekordbox_by_fingerprint.keys()) & set(serato_by_fingerprint.keys())
    print(f"\nOverlapping tracks (by artist+title): {len(overlap_fps)}")

    # Fields to compare
    fields = ["title", "artist", "album", "genre", "bpm", "key", "label"]

    # Collect comparison results
    results = []
    for fp in overlap_fps:
        r_matches = rekordbox_by_fingerprint[fp]
        s_matches = serato_by_fingerprint[fp]
        # Use first match
        r_path, r = r_matches[0]
        s_path, s = s_matches[0]

        comparison = {"title": r.get("title"), "artist": r.get("artist")}
        field_results = {}
        for field in fields:
            comparison[field] = {
                "rekordbox": r.get(field),
                "serato": s.get(field),
            }
            cmp_result = compare_fields(r.get(field), s.get(field), field)
            field_results[field] = cmp_result

        comparison["field_results"] = field_results
        results.append(comparison)

    print(f"\nMatched: {len(results)} tracks")

    # Aggregate statistics
    print("\n" + "="*60)
    print("CROSS-PLATFORM METADATA PRESERVATION")
    print("="*60)

    for field in fields:
        matches = sum(1 for r in results if r["field_results"][field]["match"])
        both_missing = sum(1 for r in results if r["field_results"][field]["both_missing"])
        non_missing = len(results) - both_missing
        effective_total = len(results) - both_missing
        if non_missing > 0:
            eff_rate = sum(1 for r in results
                           if r["field_results"][field]["match"]
                           and not r["field_results"][field]["both_missing"]) / non_missing * 100
        else:
            eff_rate = 0.0
        print(f"  {field:12s}: {matches}/{len(results)} exact ({100*matches/len(results):.1f}%) "
              f"| effective: {eff_rate:.1f}% (excluding {both_missing} both-missing)")

    # BPM differences
    bpm_diffs = [r["field_results"]["bpm"]["diff"] for r in results
                 if not r["field_results"]["bpm"]["both_missing"]]
    bpm_2x = sum(1 for r in results
                 if r["field_results"]["bpm"].get("is_2x", False))
    print("\nBPM comparison:")
    print(f"  <0.5 BPM:  {sum(1 for d in bpm_diffs if d < 0.5)}")
    print(f"  0.5-1.0:   {sum(1 for d in bpm_diffs if 0.5 <= d < 1.0)}")
    print(f"  1.0-2.0:   {sum(1 for d in bpm_diffs if 1.0 <= d < 2.0)}")
    print(f"  >2.0:      {sum(1 for d in bpm_diffs if d >= 2.0)}")
    print(f"  Rekordbox 2x bug: {bpm_2x} tracks (RB stores BPM at double actual tempo)")

    # Key mismatch analysis
    print("\nKey comparison:")
    key_exact = sum(1 for r in results
                    if not r["field_results"]["key"]["both_missing"]
                    and r["field_results"]["key"]["match"])
    key_adjacent = sum(1 for r in results
                       if not r["field_results"]["key"]["both_missing"]
                       and r["field_results"]["key"].get("adjacent", False))
    key_both_missing = sum(1 for r in results
                           if r["field_results"]["key"]["both_missing"])
    print(f"  Exact match: {key_exact}/{len(results)-key_both_missing}")
    print(f"  Adjacent (harmonically compatible): {key_adjacent}/{len(results)-key_both_missing}")
    print(f"  Both missing: {key_both_missing}")

    # Genre comparison
    print("\nGenre comparison:")
    genre_matches = sum(1 for r in results
                        if r["field_results"]["genre"]["match"]
                        and not r["field_results"]["genre"]["both_missing"])
    genre_both_missing = sum(1 for r in results if r["field_results"]["genre"]["both_missing"])
    genre_neither_missing = sum(1 for r in results
                                if not r["field_results"]["genre"]["both_missing"])
    if genre_neither_missing:
        print(f"  Exact match: {genre_matches}/{genre_neither_missing} ({100*genre_matches/genre_neither_missing:.1f}%)")
    print(f"  Both missing genre: {genre_both_missing}/{len(results)}")

    # Save detailed results
    out_path = repo / "data" / "cross_platform_comparison.json"
    with open(out_path, "w") as f:
        json.dump({
            "rekordbox_count": len(rekordbox_tracks),
            "serato_count": len(serato_tracks),
            "matched_count": len(results),
            "results": results,
        }, f, indent=2)
    print(f"\nSaved detailed results: {out_path}")


if __name__ == "__main__":
    main()
