"""
Parse Serato 'database V2' binary file and export tracks as UDMS-compatible JSON.

Usage:
    python parse_serato.py [--input PATH] [--output PATH]
    python parse_serato.py  # uses default Serato DB location
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Add schema to path
sys.path.insert(0, str(Path(__file__).parent / "schema"))
from udms_schema import (
    Platform, SERATO_FIELDS, normalize_bpm, normalize_key,
    normalize_duration, normalize_rating, key_to_numeric,
    UDMS,
)


def parse_serato_db(filepath: str) -> list[dict]:
    """Parse a Serato database V2 file using serato-tools."""
    try:
        from serato_tools.database_v2 import DatabaseV2
    except ImportError:
        raise RuntimeError("serato-tools required: pip install serato-tools")

    db = DatabaseV2(filepath)
    tracks_raw = [e[2] for e in db.data if e[0] == "otrk"]

    udms_tracks = []
    for track in tracks_raw:
        udms = UDMS(source_platform=Platform.SERATO, source_raw={})

        for sub in track:
            field = sub[0]
            val = sub[2]

            if field not in SERATO_FIELDS:
                continue

            udms_key = SERATO_FIELDS[field]

            if udms_key == "bpm":
                setattr(udms, udms_key, normalize_bpm(val, Platform.SERATO))
            elif udms_key == "rating":
                setattr(udms, udms_key, normalize_rating(val, Platform.SERATO))
            elif udms_key == "key":
                setattr(udms, udms_key, normalize_key(val))
                udms.key_numeric = key_to_numeric(udms.key)
            elif udms_key == "duration_sec":
                setattr(udms, udms_key, normalize_duration(val, Platform.SERATO))
            elif udms_key == "bitrate":
                if isinstance(val, str):
                    m = re.match(r"([\d.]+)", val)
                    setattr(udms, udms_key, int(float(m.group(1))) if m else 0)
                else:
                    setattr(udms, udms_key, int(val))
            elif udms_key == "sample_rate":
                if isinstance(val, str):
                    m = re.match(r"([\d.]+)", val)
                    setattr(udms, udms_key, int(float(m.group(1)) * 1000) if m else 44100)
                else:
                    setattr(udms, udms_key, int(val))
            else:
                if isinstance(val, str):
                    val = val.strip()
                setattr(udms, udms_key, val)

        # Build raw source dict for reference
        raw_dict = {}
        for sub in track:
            raw_dict[sub[0]] = sub[2]
        udms.source_raw = raw_dict

        udms_tracks.append(udms.to_dict())

    return udms_tracks


def main():
    parser = argparse.ArgumentParser(description="Parse Serato database V2 to UDMS JSON")
    parser.add_argument("--input", "-i", default=None, help="Path to Serato database V2 file")
    parser.add_argument("--output", "-o", default=None, help="Output JSON path")
    args = parser.parse_args()

    if args.input:
        db_path = args.input
    else:
        # Default Serato location on macOS
        db_path = os.path.join(os.path.expanduser("~"), "Music", "_Serato_", "database V2")

    if not os.path.exists(db_path):
        print(f"Error: Serato database not found at {db_path}")
        sys.exit(1)

    print(f"Parsing: {db_path}")
    tracks = parse_serato_db(db_path)
    print(f"Total tracks: {len(tracks)}")

    # Coverage stats
    fields = ["title", "artist", "album", "genre", "bpm", "key", "label",
              "duration_sec", "bitrate", "sample_rate"]
    print("\nField coverage:")
    for f in fields:
        count = sum(1 for t in tracks if t.get(f))
        print(f"  {f}: {count}/{len(tracks)} ({100*count/len(tracks):.1f}%)")

    if args.output:
        out = args.output
    else:
        out = Path(__file__).parent.parent / "data" / "serato_tracks.json"

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump({"platform": "serato", "track_count": len(tracks), "tracks": tracks}, f, indent=2)
    print(f"\nSaved: {out}")

    # Also save a simple CSV for quick inspection
    csv_path = out.with_suffix(".csv")
    import csv
    all_fields = ["title", "artist", "album", "genre", "bpm", "key", "key_numeric",
                  "rating", "label", "duration_sec", "bitrate", "sample_rate",
                  "file_type", "file_path"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(tracks)
    print(f"Saved: {csv_path}")


if __name__ == "__main__":
    main()
