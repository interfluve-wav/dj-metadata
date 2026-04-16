"""
Parse VirtualDJ database.xml and export tracks as UDMS-compatible JSON.

VirtualDJ stores metadata in a flat XML structure:
  <Song FilePath=... FileSize=...>
    <Tags Author=... Title=... Album=... Genre=... Year=...
          TrackNumber=... Label=... Remix=... Key=... Bpm=... Flag=... />
    <Infos SongLength=... LastModified=... FirstSeen=... Bitrate=... Cover=... />
    <Scan Version=... Bpm=... Phase=... AltBpm=... Volume=... Key=... AudioSig=... Flag=... />
    <Poi ... />
  </Song>

BPM conversion: Scan.Bpm is stored as a decimal fraction.
  reported_bpm = scan_bpm * 282
  Confirmed against 8 tracks from Suhaas's library (all within 0.1 BPM).

Usage:
  python parse_virtualdj.py [--input PATH] [--output PATH]
  python parse_virtualdj.py  # uses default backup location
"""

import argparse
import csv
import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "schema"))
from udms_schema import (
    Platform, VirtualDJAdapter, normalize_bpm_virtualdj,
    normalize_key, key_to_numeric,
)


def parse_virtualdj_db(xml_path: str) -> list[dict]:
    """
    Parse VirtualDJ database.xml and return a list of UDMS track dicts.

    VirtualDJ BPM conversion factor (confirmed with 8 tracks):
      Scan.Bpm (decimal fraction) × 282 = reported BPM
      E.g., 0.461519 × 282 = 130.1 BPM

    For each <Song>, the adapter reads:
      - Tags: Author, Title, Album, Genre, Year, TrackNumber, Label, Remix, Key, Bpm
      - Infos: SongLength, Bitrate
      - Scan: Bpm, AltBpm, Key (audio analysis takes priority over Tags for BPM/key)
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    tracks = []
    for song in root.findall("Song"):
        raw = {}

        # FilePath and FileSize are attributes on <Song>
        raw["FilePath"] = song.get("FilePath", "")
        raw["FileSize"] = song.get("FileSize", "")

        # <Tags> sub-element: user/metadata fields
        tags = song.find("Tags")
        if tags is not None:
            for attr in ["Author", "Title", "Album", "Genre", "Year",
                         "TrackNumber", "Label", "Remix", "Key", "Bpm", "Flag"]:
                raw[attr] = tags.get(attr, "")
            # Store Tags.Key separately to distinguish from Scan.Key
            if tags.get("Key"):
                raw["Tags_Key"] = tags.get("Key")

        # <Infos> sub-element: file metadata
        infos = song.find("Infos")
        if infos is not None:
            for attr in ["SongLength", "Bitrate", "LastModified", "FirstSeen", "Cover"]:
                raw[attr] = infos.get(attr, "")

        # <Scan> sub-element: audio analysis
        # Prefix all scan attrs with Scan_ to distinguish from Tags attrs
        scan = song.find("Scan")
        if scan is not None:
            for attr in ["Version", "Bpm", "Phase", "AltBpm", "Volume", "Key",
                         "AudioSig", "Flag"]:
                raw["Scan_" + attr] = scan.get(attr, "")

        adapter = VirtualDJAdapter()
        udms = adapter.to_udms(raw)
        tracks.append(udms.to_dict())

    return tracks


def field_coverage(tracks: list[dict]) -> dict:
    """Return coverage statistics for all UDMS fields."""
    n = len(tracks)
    if n == 0:
        return {}
    fields = [
        "title", "artist", "album", "genre", "bpm", "key",
        "bpm_manual", "bpm_alt",
        "duration_sec", "bitrate", "label", "year", "track_number", "remix",
        "file_path",
    ]
    return {f: (sum(1 for t in tracks if t.get(f)), n) for f in fields}


def main():
    parser = argparse.ArgumentParser(
        description="Parse VirtualDJ database.xml to UDMS JSON")
    parser.add_argument("--input", "-i", default=None,
                        help="Path to VirtualDJ database.xml")
    parser.add_argument("--output", "-o", default=None,
                        help="Output JSON path")
    args = parser.parse_args()

    if args.input:
        xml_path = args.input
    else:
        # Default: most recent VirtualDJ backup
        backup_dir = Path.home() / "Music" / "Virtual DJ Backup"
        if not backup_dir.exists():
            print(f"Error: Default backup dir not found: {backup_dir}")
            print("Specify --input manually")
            sys.exit(1)
        # Find most recent backup
        backups = sorted(backup_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        if not backups:
            print(f"Error: No backups found in {backup_dir}")
            sys.exit(1)
        xml_path = str(backups[0] / "database.xml")

    if not os.path.exists(xml_path):
        print(f"Error: File not found: {xml_path}")
        sys.exit(1)

    print(f"Parsing: {xml_path}")
    tracks = parse_virtualdj_db(xml_path)
    print(f"Total tracks: {len(tracks)}")

    # Coverage stats
    cov = field_coverage(tracks)
    print("\nField coverage:")
    print(f"  {'Field':<16} {'Filled':>8} {'Coverage':>10}")
    print(f"  {'-'*16} {'-'*8} {'-'*10}")
    for f, (count, total) in sorted(cov.items(), key=lambda x: -x[1][0]):
        pct = 100 * count / total if total > 0 else 0
        print(f"  {f:<16} {count:>5}/{total} {pct:>9.1f}%")

    # BPM coverage detail
    bpm_count = sum(1 for t in tracks if t.get("bpm", 0) > 0)
    bpm_manual_count = sum(1 for t in tracks if t.get("bpm_manual", 0) > 0)
    alt_bpm_count = sum(1 for t in tracks if t.get("bpm_alt", 0) > 0)
    print(f"\nBPM detail:")
    print(f"  Scan BPM (×282):   {bpm_count}/{len(tracks)} ({100*bpm_count/len(tracks):.1f}%)")
    print(f"  Tags BPM (manual): {bpm_manual_count}/{len(tracks)} ({100*bpm_manual_count/len(tracks):.1f}%)")
    print(f"  AltBPM (Scan):     {alt_bpm_count}/{len(tracks)} ({100*alt_bpm_count/len(tracks):.1f}%)")

    # Key coverage detail
    key_scan_count = sum(1 for t in tracks if t.get("key") and t.get("key") != "Unknown")
    print(f"\nKey detail:")
    print(f"  Key (Scan audio analysis): {key_scan_count}/{len(tracks)} ({100*key_scan_count/len(tracks):.1f}%)")

    # Save JSON
    if args.output:
        out = Path(args.output)
    else:
        out = Path(__file__).parent.parent / "data" / "virtualdj_tracks.json"

    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump({
            "platform": "virtualdj",
            "track_count": len(tracks),
            "tracks": tracks,
        }, f, indent=2)
    print(f"\nSaved: {out}")

    # Save CSV for quick inspection
    csv_path = out.with_suffix(".csv")
    all_fields = [
        "title", "artist", "album", "genre", "bpm", "bpm_manual", "bpm_alt",
        "key", "key_numeric", "label", "year", "track_number", "remix",
        "duration_sec", "bitrate", "file_path",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(tracks)
    print(f"Saved: {csv_path}")


if __name__ == "__main__":
    main()
