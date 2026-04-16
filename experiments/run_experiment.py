#!/usr/bin/env python3
"""
DJ Metadata Transfer Experiment Runner
=======================================
Automates the cross-platform transfer study: export → import → measure → log.

Usage:
    # Run full experiment (all 6 paths)
    python run_experiment.py --tracks annotation.csv --output results/

    # Run single path
    python run_experiment.py --tracks annotation.csv --output results/ --path R-S

    # Dry run (validate setup without transfers)
    python run_experiment.py --tracks annotation.csv --output results/ --dry-run
"""

import argparse
import csv
import json
import os
import sys
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

# ── UDMS inline (avoid import path issues) ──────────────────────────────────

PLATFORMS = ["R", "S", "T"]
PLATFORM_NAMES = {"R": "rekordbox", "S": "serato", "T": "traktor"}
ALL_PATHS = ["R-S", "R-T", "S-R", "S-T", "T-R", "T-S"]

UDMS_FIELDS = [
    "title", "artist", "album", "genre", "bpm", "key", "key_numeric",
    "rating", "energy", "mood", "label", "catalog_no", "duration_sec",
    "bitrate", "sample_rate", "file_path", "playlist_name",
]

# ── Config ──────────────────────────────────────────────────────────────────

@dataclass
class ExperimentConfig:
    tracks_csv: str = "annotation.csv"
    output_dir: str = "results"
    music_library: str = os.path.expanduser("~/Music/DJ-Experiment")
    rekordbox_xml: str = os.path.expanduser("~/Library/Pioneer/rekordbox/rekordbox.xml")
    serato_db: str = os.path.expanduser("~/Music/_Serato_/database V2")
    traktor_nml: str = os.path.expanduser("~/Documents/Native Instruments/Traktor 3.11.0/collection.nml")
    dry_run: bool = False
    path_filter: Optional[str] = None  # e.g., "R-S"
    pilot_size: int = 50


# ── Data structures ─────────────────────────────────────────────────────────

@dataclass
class TrackMeta:
    """Ground-truth UDMS metadata for a track."""
    title: str = ""
    artist: str = ""
    album: str = ""
    genre: str = ""
    bpm: float = 0.0
    key: str = ""
    energy: int = 0
    mood: int = 0
    label: str = ""
    catalog_no: str = ""
    duration_sec: int = 0
    bitrate: int = 0
    sample_rate: int = 44100
    isrc: str = ""
    file_path: str = ""

    @classmethod
    def from_csv_row(cls, row: dict) -> "TrackMeta":
        return cls(
            title=row.get("title", "").strip(),
            artist=row.get("artist", "").strip(),
            album=row.get("album", "").strip(),
            genre=row.get("genre", "").strip(),
            bpm=float(row.get("bpm", 0) or 0),
            key=row.get("key", "").strip(),
            energy=int(row.get("energy", 0) or 0),
            mood=int(row.get("mood", 0) or 0),
            label=row.get("label", "").strip(),
            catalog_no=row.get("catalog_no", "").strip(),
            duration_sec=int(row.get("duration_sec", 0) or 0),
            bitrate=int(row.get("bitrate", 0) or 0),
            sample_rate=int(row.get("sample_rate", 44100) or 44100),
            isrc=row.get("isrc", "").strip(),
        )


@dataclass
class FieldResult:
    """Per-field preservation measurement."""
    field: str
    ground_truth: str
    source_value: str
    dest_value: str
    preserved: bool
    notes: str = ""


@dataclass
class TransferResult:
    """Results for one transfer path."""
    path: str
    timestamp: str
    track_count: int
    field_results: list = field(default_factory=list)

    @property
    def preservation_rates(self) -> dict:
        """Compute per-field PR."""
        by_field = {}
        for fr in self.field_results:
            if fr.field not in by_field:
                by_field[fr.field] = {"total": 0, "preserved": 0}
            by_field[fr.field]["total"] += 1
            if fr.preserved:
                by_field[fr.field]["preserved"] += 1
        return {
            f: d["preserved"] / d["total"] if d["total"] > 0 else 0.0
            for f, d in by_field.items()
        }

    @property
    def aqs(self) -> float:
        """Aggregate Quality Score."""
        rates = self.preservation_rates.values()
        return sum(rates) / len(rates) if rates else 0.0


# ── Export Parsers ──────────────────────────────────────────────────────────

def parse_rekordbox_xml(xml_path: str) -> list[dict]:
    """Parse Rekordbox XML export into list of track dicts."""
    import xml.etree.ElementTree as ET
    tracks = []
    if not os.path.exists(xml_path):
        print(f"  WARNING: Rekordbox XML not found: {xml_path}")
        return tracks
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for track in root.iter("TRACK"):
        tracks.append(dict(track.attrib))
    print(f"  Parsed {len(tracks)} tracks from Rekordbox XML")
    return tracks


def parse_serato_db(db_path: str) -> list[dict]:
    """Parse Serato database V2 into list of track dicts."""
    tracks = []
    if not os.path.exists(db_path):
        print(f"  WARNING: Serato DB not found: {db_path}")
        return tracks
    # Serato DB is a binary format — use serato-parser if available
    try:
        subprocess.run(["python3", "-c", "import serato_parser"], check=True,
                       capture_output=True)
        result = subprocess.run(
            ["python3", "-c", f"""
import serato_parser, json
db = serato_parser.Database("{db_path}")
tracks = []
for t in db.tracks():
    tracks.append({{
        "title": t.title or "",
        "artist": t.artist or "",
        "album": t.album or "",
        "genre": t.genre or "",
        "bpm": t.bpm or 0,
        "key": t.key or "",
        "rating": t.rating or 0,
        "label": t.label or "",
        "length": t.length or 0,
        "path": str(t.path or ""),
    }})
print(json.dumps(tracks))
"""],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            tracks = json.loads(result.stdout)
            print(f"  Parsed {len(tracks)} tracks from Serato DB")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  WARNING: serato-parser not installed. Install with: pip install serato-parser")
    return tracks


def parse_traktor_nml(nml_path: str) -> list[dict]:
    """Parse Traktor NML collection into list of track dicts."""
    import xml.etree.ElementTree as ET
    tracks = []
    if not os.path.exists(nml_path):
        print(f"  WARNING: Traktor NML not found: {nml_path}")
        return tracks
    tree = ET.parse(nml_path)
    root = tree.getroot()
    for entry in root.iter("ENTRY"):
        track = {}
        # Basic attributes
        for attr in ["TITLE", "ARTIST", "ALBUM", "GENRE"]:
            track[attr] = entry.get(attr, "")
        # AUDIO element
        audio = entry.find("AUDIO")
        if audio is not None:
            track["Bitrate"] = audio.get("BITRATE", "0")
            track["SampleRate"] = audio.get("SAMPLE_RATE", "44100")
            track["Length_ms"] = audio.get("LENGTH", "0")
            track["Location"] = audio.get("FILE", "")
        # TEMPO element
        tempo = entry.find("TEMPO")
        if tempo is not None:
            track["BPM"] = tempo.get("BPM", "0")
        # INFO element for key
        info = entry.find("INFO")
        if info is not None:
            track["Key"] = info.get("KEY", "")
            track["Label"] = info.get("LABEL", "")
            track["Rating"] = info.get("RATING", "0")
        tracks.append(track)
    print(f"  Parsed {len(tracks)} tracks from Traktor NML")
    return tracks


PARSERS = {
    "R": parse_rekordbox_xml,
    "S": parse_serato_db,
    "T": parse_traktor_nml,
}


# ── Comparison Engine ───────────────────────────────────────────────────────

# Ground truth field → platform field mapping
FIELD_MAPS = {
    "R": {
        "title": "TrackName", "artist": "Artist", "album": "Album",
        "genre": "Genre", "bpm": "AverageBpm", "key": "Tonality",
        "rating": "RatingByte", "energy": "Energy", "mood": "Mood",
        "label": "Label", "catalog_no": "CatalogNo",
        "duration_sec": "TotalTime", "bitrate": "BitRate",
        "sample_rate": "SampleRate",
    },
    "S": {
        "title": "title", "artist": "artist", "album": "album",
        "genre": "genre", "bpm": "bpm", "key": "key",
        "rating": "rating", "label": "label",
        "duration_sec": "length", "bitrate": "bit_rate",
        "sample_rate": "sample_rate",
    },
    "T": {
        "title": "Title", "artist": "Artist", "album": "Album",
        "genre": "Genre", "bpm": "BPM", "key": "Key",
        "rating": "Rating", "label": "Label",
        "duration_sec": "Length_ms", "bitrate": "Bitrate",
        "sample_rate": "SampleRate",
    },
}


def compare_field(field: str, ground_truth: TrackMeta, platform: str,
                  exported_tracks: list[dict]) -> FieldResult:
    """Compare a single field between ground truth and exported data."""
    gt_value = str(getattr(ground_truth, field, ""))

    # Map ground truth field to platform field name
    pmap = FIELD_MAPS.get(platform, {})
    platform_field = pmap.get(field)

    if not platform_field:
        return FieldResult(
            field=field, ground_truth=gt_value,
            source_value="N/A", dest_value="N/A",
            preserved=True, notes="field not applicable"
        )

    # Find matching track in export (by title + artist)
    dest_value = ""
    for track in exported_tracks:
        t_title = ""
        t_artist = ""
        # Try common field names
        for key in ["TrackName", "title", "Title", "TRACK"]:
            if key in track:
                t_title = track[key]
                break
        for key in ["Artist", "artist", "ARTIST"]:
            if key in track:
                t_artist = track[key]
                break

        if (t_title.lower().strip() == ground_truth.title.lower().strip() and
            t_artist.lower().strip() == ground_truth.artist.lower().strip()):
            dest_value = str(track.get(platform_field, ""))
            break

    if not dest_value:
        return FieldResult(
            field=field, ground_truth=gt_value,
            source_value=gt_value, dest_value="MISSING",
            preserved=False, notes="track not found in export"
        )

    # Normalize for comparison
    preserved = _values_match(field, gt_value, dest_value)

    return FieldResult(
        field=field, ground_truth=gt_value,
        source_value=gt_value, dest_value=dest_value,
        preserved=preserved,
    )


def _values_match(field: str, gt: str, exported: str) -> bool:
    """Fuzzy comparison accounting for platform-specific normalizations."""
    if not gt or gt == "0":
        return True  # Can't lose what you don't have
    gt_l = gt.strip().lower()
    ex_l = exported.strip().lower()

    if gt_l == ex_l:
        return True

    # BPM: allow rounding to 1 decimal
    if field == "bpm":
        try:
            return abs(float(gt) - float(ex_l)) < 0.2
        except ValueError:
            return False

    # Duration: allow ±2 second tolerance
    if field == "duration_sec":
        try:
            return abs(int(gt) - int(ex_l)) <= 2
        except ValueError:
            return False

    # Numeric fields: exact match after stripping
    if field in ("bitrate", "sample_rate", "rating", "energy", "mood"):
        try:
            return int(float(gt)) == int(float(ex_l))
        except ValueError:
            return gt_l == ex_l

    # String fields: case-insensitive, strip whitespace
    return gt_l == ex_l


# ── Experiment Runner ───────────────────────────────────────────────────────

def load_tracks(csv_path: str) -> list[TrackMeta]:
    """Load ground-truth tracks from annotation CSV."""
    tracks = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("title", "").strip():
                tracks.append(TrackMeta.from_csv_row(row))
    print(f"Loaded {len(tracks)} tracks from {csv_path}")
    return tracks


def run_single_path(path: str, ground_truth: list[TrackMeta],
                    config: ExperimentConfig) -> TransferResult:
    """Run one transfer path: export from source, measure in destination."""
    src, dst = path.split("-")
    src_name = PLATFORM_NAMES[src]
    dst_name = PLATFORM_NAMES[dst]

    print(f"\n{'='*60}")
    print(f"  Path: {src_name} → {dst_name}")
    print(f"  Tracks: {len(ground_truth)}")
    print(f"{'='*60}")

    if config.dry_run:
        print("  [DRY RUN] Skipping actual transfer")
        return TransferResult(
            path=path, timestamp=datetime.now().isoformat(),
            track_count=len(ground_truth),
        )

    # Step 1: Export from source platform
    print(f"\n  Step 1: Export from {src_name}")
    export_path = {
        "R": config.rekordbox_xml,
        "S": config.serato_db,
        "T": config.traktor_nml,
    }[src]

    parser = PARSERS[src]
    exported = parser(export_path)

    if not exported:
        print(f"  ERROR: No tracks exported from {src_name}")
        return TransferResult(
            path=path, timestamp=datetime.now().isoformat(),
            track_count=0,
        )

    # Step 2: Manual import step
    print(f"\n  Step 2: IMPORT into {dst_name}")
    print(f"  >>> Open {dst_name} and import: {export_path}")
    print(f"  >>> Wait for import to complete, then press Enter...")
    if not config.dry_run:
        input("  [Press Enter when import is complete] ")

    # Step 3: Export from destination
    print(f"\n  Step 3: Re-export from {dst_name}")
    dst_export_path = {
        "R": config.rekordbox_xml,
        "S": config.serato_db,
        "T": config.traktor_nml,
    }[dst]

    dst_parser = PARSERS[dst]
    dst_exported = dst_parser(dst_export_path)

    if not dst_exported:
        print(f"  ERROR: No tracks exported from {dst_name}")
        return TransferResult(
            path=path, timestamp=datetime.now().isoformat(),
            track_count=0,
        )

    # Step 4: Compare
    print(f"\n  Step 4: Comparing {len(ground_truth)} tracks × {len(UDMS_FIELDS)} fields")
    result = TransferResult(
        path=path,
        timestamp=datetime.now().isoformat(),
        track_count=len(ground_truth),
    )

    for track in ground_truth:
        for field_name in UDMS_FIELDS:
            fr = compare_field(field_name, track, dst, dst_exported)
            result.field_results.append(fr)

    # Report
    print(f"\n  Results:")
    print(f"  AQS: {result.aqs:.3f}")
    print(f"  Per-field PR:")
    for f, pr in sorted(result.preservation_rates.items()):
        status = "OK" if pr > 0.95 else "WARN" if pr > 0.70 else "FAIL"
        print(f"    {f:15s}  {pr:.1%}  [{status}]")

    return result


def save_results(results: list[TransferResult], output_dir: str):
    """Save experiment results to JSON and CSV."""
    os.makedirs(output_dir, exist_ok=True)

    # Save detailed JSON
    json_path = os.path.join(output_dir, "transfer_results.json")
    data = []
    for r in results:
        data.append({
            "path": r.path,
            "timestamp": r.timestamp,
            "track_count": r.track_count,
            "aqs": r.aqs,
            "preservation_rates": r.preservation_rates,
            "field_results": [asdict(fr) for fr in r.field_results],
        })
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nSaved detailed results to {json_path}")

    # Save summary CSV (for easy figure generation)
    csv_path = os.path.join(output_dir, "summary.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["path", "aqs", "track_count"] + UDMS_FIELDS
        writer.writerow(header)
        for r in results:
            row = [r.path, f"{r.aqs:.4f}", r.track_count]
            for field_name in UDMS_FIELDS:
                pr = r.preservation_rates.get(field_name, 0.0)
                row.append(f"{pr:.4f}")
            writer.writerow(row)
    print(f"Saved summary to {csv_path}")

    # Save experiment log
    log_path = os.path.join(output_dir, "experiment_log.md")
    with open(log_path, "w") as f:
        f.write(f"# Experiment Log\n\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Tracks: {results[0].track_count if results else 0}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"| Path | AQS | Best Field | Worst Field |\n")
        f.write(f"|------|-----|------------|-------------|\n")
        for r in results:
            rates = r.preservation_rates
            if rates:
                best = max(rates, key=rates.get)
                worst = min(rates, key=rates.get)
                f.write(f"| {r.path} | {r.aqs:.3f} | {best} ({rates[best]:.0%}) | {worst} ({rates[worst]:.0%}) |\n")
        f.write(f"\n## Per-Field Detail\n\n")
        for r in results:
            f.write(f"\n### {r.path}\n\n")
            f.write(f"| Field | PR |\n")
            f.write(f"|-------|----|\n")
            for field_name, pr in sorted(r.preservation_rates.items()):
                f.write(f"| {field_name} | {pr:.1%} |\n")
    print(f"Saved experiment log to {log_path}")


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="DJ Metadata Transfer Experiment Runner")
    parser.add_argument("--tracks", default="annotation.csv", help="Path to track annotation CSV")
    parser.add_argument("--output", default="results/", help="Output directory")
    parser.add_argument("--path", help="Single path to run (e.g., R-S). Default: all 6")
    parser.add_argument("--dry-run", action="store_true", help="Validate without transfers")
    parser.add_argument("--music-library", default=os.path.expanduser("~/Music/DJ-Experiment"),
                        help="Path to music library directory")
    parser.add_argument("--rekordbox-xml", help="Path to Rekordbox XML export")
    parser.add_argument("--serato-db", help="Path to Serato database directory")
    parser.add_argument("--traktor-nml", help="Path to Traktor NML collection file")
    args = parser.parse_args()

    config = ExperimentConfig(
        tracks_csv=args.tracks,
        output_dir=args.output,
        music_library=args.music_library,
        dry_run=args.dry_run,
    )
    if args.rekordbox_xml:
        config.rekordbox_xml = args.rekordbox_xml
    if args.serato_db:
        config.serato_db = args.serato_db
    if args.traktor_nml:
        config.traktor_nml = args.traktor_nml

    # Load tracks
    ground_truth = load_tracks(args.tracks)
    if not ground_truth:
        print("ERROR: No tracks loaded. Check your annotation CSV.")
        sys.exit(1)

    # Determine paths to run
    paths = [args.path] if args.path else ALL_PATHS

    print(f"\nDJ Metadata Transfer Experiment")
    print(f"{'='*40}")
    print(f"  Tracks: {len(ground_truth)}")
    print(f"  Paths: {', '.join(paths)}")
    print(f"  Output: {config.output_dir}")
    print(f"  Dry run: {config.dry_run}")
    print(f"{'='*40}")

    # Run experiments
    all_results = []
    for path in paths:
        result = run_single_path(path, ground_truth, config)
        all_results.append(result)

        # Save incrementally (in case of interruption)
        save_results(all_results, config.output_dir)

    # Final summary
    print(f"\n{'='*60}")
    print(f"  EXPERIMENT COMPLETE")
    print(f"{'='*60}")
    print(f"  Paths run: {len(all_results)}")
    print(f"  Mean AQS: {sum(r.aqs for r in all_results) / len(all_results):.3f}")
    print(f"  Results in: {config.output_dir}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
